# app/scripts/generate_embeddings.py

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.artwork import Artwork
from app.utils.clip_service import clip_service
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_all_embeddings():
    """모든 작품의 임베딩 생성"""
    db = SessionLocal()
    
    try:
        # 임베딩이 없는 작품들 조회
        artworks = db.query(Artwork).filter(
            Artwork.thumbnail_url.isnot(None),
            Artwork.embedding.is_(None)
        ).all()
        
        logger.info(f"🎨 총 {len(artworks)}개 작품의 임베딩 생성 시작")
        
        success_count = 0
        fail_count = 0
        
        for idx, artwork in enumerate(artworks, 1):
            try:
                logger.info(f"[{idx}/{len(artworks)}] {artwork.title} 처리 중...")
                
                # S3에서 이미지 다운로드
                response = requests.get(artwork.thumbnail_url, timeout=30)
                if response.status_code != 200:
                    logger.error(f"❌ 이미지 다운로드 실패: {artwork.thumbnail_url}")
                    fail_count += 1
                    continue
                
                image_bytes = response.content
                
                # 임베딩 생성
                embedding = clip_service.generate_embedding(image_bytes)
                
                if embedding:
                    # DB에 저장
                    artwork.embedding = embedding
                    db.commit()
                    success_count += 1
                    logger.info(f"✅ {artwork.title} 임베딩 생성 완료 (유사도: {len(embedding)}차원)")
                else:
                    logger.error(f"❌ {artwork.title} 임베딩 생성 실패")
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"❌ {artwork.title} 처리 중 오류: {e}")
                fail_count += 1
                db.rollback()
                continue
        
        logger.info(f"""
        
🎉 임베딩 생성 완료!
        
📊 결과:
   - ✅ 성공: {success_count}개
   - ❌ 실패: {fail_count}개
   - 📈 성공률: {success_count / len(artworks) * 100:.1f}%
        """)
        
    except Exception as e:
        logger.error(f"❌ 전체 처리 중 오류: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🚀 CLIP 임베딩 생성 시작")
    logger.info("=" * 50)
    generate_all_embeddings()