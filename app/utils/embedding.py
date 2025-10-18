# app/services/embedding.py
"""HuggingFace API 임베딩 서비스 (DINOv2 + 재시도 로직)"""
import requests
import numpy as np
from PIL import Image
import io
import time
from typing import Union
from app.config import settings

class HuggingFaceEmbeddingService:
    """
    HuggingFace Inference API를 사용한 DINOv2 임베딩
    (EC2 프리티어 최적화)
    """
    
    def __init__(self, model_name: str = "facebook/dinov2-small"):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"
        }
        print(f"🤗 HuggingFace API 초기화: {model_name}")
    
    def get_embedding(
        self, 
        image: Union[Image.Image, bytes, str],
        max_retries: int = 5
    ) -> np.ndarray:
        """
        이미지에서 임베딩 벡터 추출 (재시도 로직 포함)
        
        Args:
            image: PIL Image, bytes, 또는 이미지 경로
            max_retries: 최대 재시도 횟수
            
        Returns:
            numpy array: 임베딩 벡터 (384차원)
        """
        # 이미지 로드 및 변환
        if isinstance(image, bytes):
            image_bytes = image
            image = Image.open(io.BytesIO(image)).convert("RGB")
        elif isinstance(image, str):
            image = Image.open(image).convert("RGB")
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            image_bytes = buffered.getvalue()
        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            image_bytes = buffered.getvalue()
        else:
            raise ValueError("Invalid image type")
        
        # API 호출 (재시도 포함)
        for attempt in range(max_retries):
            try:
                print(f"📤 HuggingFace API 호출 중... (시도 {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    data=image_bytes,
                    params={"wait_for_model": "true"},  # 모델 로딩 대기
                    timeout=60
                )
                
                # 상태 코드 확인
                if response.status_code == 503:
                    error_msg = response.json().get("error", "")
                    if "loading" in error_msg.lower():
                        wait_time = 20
                        print(f"⏳ 모델 로딩 중... {wait_time}초 대기")
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                
                # 응답 파싱
                result = response.json()
                print(f"✅ API 응답 받음: {type(result)}")
                
                # DINOv2 응답 형식 처리
                if isinstance(result, list):
                    # Feature extraction 결과가 리스트로 올 수 있음
                    embedding = np.array(result[0]) if len(result) > 0 else np.array(result)
                elif isinstance(result, dict):
                    # 딕셔너리 형태일 경우
                    if "embeddings" in result:
                        embedding = np.array(result["embeddings"][0])
                    elif "last_hidden_state" in result:
                        embedding = np.array(result["last_hidden_state"][0])
                    else:
                        # 첫 번째 값 시도
                        embedding = np.array(list(result.values())[0])
                else:
                    embedding = np.array(result)
                
                print(f"✅ 임베딩 생성 완료! Shape: {embedding.shape}")
                return embedding.squeeze()
                
            except requests.exceptions.HTTPError as e:
                print(f"❌ HTTP 에러: {e}")
                print(f"   Response: {e.response.text[:500]}")
                
                if e.response.status_code == 404:
                    raise RuntimeError(
                        f"모델 '{self.model_name}'을 찾을 수 없습니다. "
                        "Inference API에서 지원하지 않는 모델일 수 있습니다."
                    )
                
                if attempt == max_retries - 1:
                    raise
                
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)
        
        raise RuntimeError(f"{max_retries}번 시도 후 실패")
    
    def compute_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """코사인 유사도 계산"""
        embedding1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        embedding2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        similarity = np.dot(embedding1_norm, embedding2_norm)
        return float(similarity)


class PrecomputedEmbeddingService:
    """사전 계산된 임베딩 관리 (pgvector 검색)"""
    
    @staticmethod
    def compute_similarity(
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """코사인 유사도 계산"""
        embedding1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        embedding2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        similarity = np.dot(embedding1_norm, embedding2_norm)
        return float(similarity)
    
    @staticmethod
    def find_similar_artworks(
        db,
        query_embedding: np.ndarray,
        top_k: int = 10,
        exhibition_id: int = None
    ):
        """pgvector로 유사 작품 검색"""
        from app.models import Artwork, exhibition_artworks
        
        query = db.query(
            Artwork,
            Artwork.embedding.cosine_distance(query_embedding.tolist()).label("distance")
        ).filter(
            Artwork.embedding.isnot(None)
        )
        
        if exhibition_id:
            query = query.join(
                exhibition_artworks,
                exhibition_artworks.c.artwork_id == Artwork.id
            ).filter(
                exhibition_artworks.c.exhibition_id == exhibition_id
            )
        
        results = query.order_by(
            Artwork.embedding.cosine_distance(query_embedding.tolist())
        ).limit(top_k).all()
        
        return [
            {
                "artwork": artwork,
                "similarity": float(1 - distance)
            }
            for artwork, distance in results
        ]


# 싱글톤
_embedding_service = None

def get_embedding_service() -> HuggingFaceEmbeddingService:
    """HuggingFace 임베딩 서비스"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = HuggingFaceEmbeddingService()
    return _embedding_service