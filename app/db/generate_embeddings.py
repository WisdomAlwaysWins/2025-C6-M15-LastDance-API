"""
기존 작품들의 임베딩을 일괄 생성하는 스크립트
"""

import logging
from sqlalchemy import text
from app.database import SessionLocal
from app.models.artwork import Artwork
from app.utils.lambda_client import lambda_client
import base64
import requests
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_image_as_base64(url: str) -> str:
    """S3 URL에서 이미지 다운로드하여 base64로 변환"""
    try:
        logger.info(f"이미지 다운로드 중: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        image_base64 = base64.b64encode(response.content).decode()
        size_mb = len(image_base64) / 1024 / 1024
        logger.info(f"다운로드 완료: {size_mb:.2f}MB")
        
        return image_base64
    except Exception as e:
        logger.error(f"이미지 다운로드 실패: {e}")
        raise


def resize_base64_image(base64_string: str, max_size: int = 800) -> str:
    """
    base64 이미지 리사이즈
    
    Args:
        base64_string: base64 인코딩된 이미지
        max_size: 최대 가로/세로 크기 (px)
        
    Returns:
        str: 리사이즈된 base64 이미지
    """
    try:
        # base64 → 이미지
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # RGB로 변환
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        
        # 현재 크기
        width, height = image.size
        
        # 리사이즈 필요한지 확인
        if width > max_size or height > max_size:
            # 비율 유지하며 리사이즈
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 이미지 → base64
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85, optimize=True)
            resized_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            size_before = len(base64_string) / 1024 / 1024
            size_after = len(resized_base64) / 1024 / 1024
            logger.info(f"리사이즈: {size_before:.2f}MB → {size_after:.2f}MB")
            
            return resized_base64
        
        return base64_string
        
    except Exception as e:
        logger.error(f"이미지 리사이즈 실패: {e}, 원본 사용")
        return base64_string


def generate_all_embeddings():
    """모든 작품의 임베딩 생성"""
    db = SessionLocal()
    
    try:
        # 임베딩이 없는 작품 조회
        artworks = db.query(Artwork).filter(
            Artwork.embedding.is_(None),
            Artwork.thumbnail_url.isnot(None)
        ).all()
        
        logger.info(f"총 {len(artworks)}개 작품의 임베딩 생성 시작")
        logger.info("=" * 70)
        
        success_count = 0
        fail_count = 0
        
        for i, artwork in enumerate(artworks, 1):
            try:
                logger.info(f"\n[{i}/{len(artworks)}] 작품: '{artwork.title}' (ID: {artwork.id})")
                
                # 1. 이미지 다운로드
                image_base64 = download_image_as_base64(artwork.thumbnail_url)
                
                # 2. 리사이즈 (6MB 제한 대응)
                image_base64 = resize_base64_image(image_base64, max_size=800)
                
                # 3. Lambda로 임베딩 생성
                logger.info("Lambda 호출: 임베딩 생성 중...")
                embedding = lambda_client.generate_embedding(image_base64)
                logger.info(f"임베딩 생성 완료: {len(embedding)}차원")
                
                # 4. DB 저장 (raw SQL 사용)
                db.execute(
                    text("""
                        UPDATE artworks 
                        SET embedding = CAST(:embedding AS vector), 
                            updated_at = now() 
                        WHERE id = :id
                    """),
                    {"embedding": str(embedding), "id": artwork.id}
                )
                db.commit()
                
                success_count += 1
                logger.info(f"✅ '{artwork.title}' 임베딩 저장 완료")
                
            except Exception as e:
                fail_count += 1
                logger.error(f"❌ '{artwork.title}' 임베딩 생성 실패: {e}")
                db.rollback()
                continue
        
        logger.info("\n" + "=" * 70)
        logger.info(f"완료: 성공 {success_count}개, 실패 {fail_count}개")
        
        if success_count > 0:
            logger.info(f"\n🎉 {success_count}개 작품의 임베딩이 DB에 저장되었습니다!")
        
        if fail_count > 0:
            logger.warning(f"\n⚠️  {fail_count}개 작품 처리 실패. 위 로그 확인 필요.")
        
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_embeddings()