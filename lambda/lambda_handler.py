"""
AWS Lambda 함수: 실시간 이미지 매칭
업로드된 이미지 vs 전시의 작품들
"""
import json
import torch
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np
import io
import base64
import requests
from typing import List, Dict
import os

# Lambda /tmp 폴더 사용 (쓰기 가능)
os.environ['TRANSFORMERS_CACHE'] = '/tmp/huggingface'
os.environ['HF_HOME'] = '/tmp/huggingface'

# DINOv2 모델 (글로벌 변수 - 콜드 스타트 최적화)
MODEL = None
PROCESSOR = None
DEVICE = None


def load_model():
    """DINOv2 모델 로드 (첫 실행 시 한 번만)"""
    global MODEL, PROCESSOR, DEVICE
    
    if MODEL is None:
        print("🦖 DINOv2 모델 로딩 중...")
        
        DEVICE = torch.device("cpu")
        model_name = "facebook/dinov2-small"
        
        PROCESSOR = AutoImageProcessor.from_pretrained(model_name)
        MODEL = AutoModel.from_pretrained(model_name).to(DEVICE)
        MODEL.eval()
        
        print("✅ 모델 로딩 완료!")


def get_embedding(image: Image.Image) -> np.ndarray:
    """이미지에서 임베딩 추출"""
    inputs = PROCESSOR(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = MODEL(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    
    return embedding.squeeze()


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """코사인 유사도 계산"""
    dot_product = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    return float(dot_product / (norm1 * norm2))


def download_image_from_url(url: str) -> Image.Image:
    """URL에서 이미지 다운로드"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


def handler(event, context):
    """
    Lambda 핸들러
    
    Request:
    {
        "image_base64": "iVBORw0KGgoAAAANS...",
        "artworks": [
            {
                "id": 1,
                "title": "작품명",
                "artist_id": 1,
                "thumbnail_url": "https://..."
            }
        ],
        "threshold": 0.7
    }
    
    Response:
    {
        "matched": true,
        "total_matches": 2,
        "threshold": 0.7,
        "results": [
            {
                "artwork_id": 1,
                "title": "작품명",
                "artist_id": 1,
                "thumbnail_url": "https://...",
                "similarity": 0.8523
            }
        ]
    }
    """
    
    print(f"📨 Lambda 실행 시작")
    
    # CORS 헤더
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        # OPTIONS 요청 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS' or event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # 모델 로드
        load_model()
        
        # Body 파싱
        body_str = event.get('body', '{}')
        
        # API Gateway v2는 base64 인코딩 가능
        if event.get('isBase64Encoded', False):
            body_str = base64.b64decode(body_str).decode('utf-8')
        
        body = json.loads(body_str)
        image_base64 = body.get('image_base64')
        artworks = body.get('artworks', [])
        threshold = float(body.get('threshold', 0.7))
        
        # Validation
        if not image_base64:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'image_base64 필드가 필요합니다',
                    'example': {
                        'image_base64': 'base64_encoded_image_string',
                        'artworks': [{'id': 1, 'thumbnail_url': '...'}],
                        'threshold': 0.7
                    }
                })
            }
        
        if not artworks:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'artworks 필드가 필요합니다 (작품 목록)',
                    'example': {
                        'image_base64': 'base64_encoded_image_string',
                        'artworks': [
                            {
                                'id': 1,
                                'title': '작품명',
                                'artist_id': 1,
                                'thumbnail_url': 'https://...'
                            }
                        ],
                        'threshold': 0.7
                    }
                })
            }
        
        print(f"🖼️  이미지 디코딩 중... (threshold: {threshold})")
        
        # Base64 디코딩
        try:
            image_bytes = base64.b64decode(image_base64)
            uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            print(f"✅ 업로드 이미지 로드: {uploaded_image.size}")
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'이미지 디코딩 실패: {str(e)}'})
            }
        
        # 업로드된 이미지의 임베딩 생성
        print(f"🧠 업로드 이미지 임베딩 생성 중...")
        uploaded_embedding = get_embedding(uploaded_image)
        print(f"✅ 임베딩 생성 완료: shape {uploaded_embedding.shape}")
        
        print(f"📊 총 {len(artworks)}개 작품과 비교 중...")
        
        # 각 작품과 유사도 계산
        matches = []
        processed = 0
        skipped = 0
        
        for artwork in artworks:
            artwork_id = artwork.get('id')
            thumbnail_url = artwork.get('thumbnail_url')
            
            if not thumbnail_url:
                skipped += 1
                continue
            
            try:
                # 작품 이미지 다운로드
                artwork_image = download_image_from_url(thumbnail_url)
                
                # 작품 이미지 임베딩 생성
                artwork_embedding = get_embedding(artwork_image)
                
                # 유사도 계산
                similarity = cosine_similarity(uploaded_embedding, artwork_embedding)
                
                processed += 1
                print(f"🎨 작품 {artwork_id} ({artwork.get('title')}): 유사도 {similarity:.4f}")
                
                if similarity >= threshold:
                    matches.append({
                        'artwork_id': artwork_id,
                        'title': artwork.get('title'),
                        'artist_id': artwork.get('artist_id'),
                        'thumbnail_url': thumbnail_url,
                        'similarity': round(float(similarity), 4)
                    })
            
            except Exception as e:
                print(f"⚠️  작품 {artwork_id} 처리 실패: {e}")
                skipped += 1
                continue
        
        # 유사도 높은 순 정렬
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"✅ 매칭 완료: 처리 {processed}개, 스킵 {skipped}개, 매칭 {len(matches)}개")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'matched': len(matches) > 0,
                'total_matches': len(matches),
                'threshold': threshold,
                'processed_artworks': processed,
                'skipped_artworks': skipped,
                'results': matches
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }