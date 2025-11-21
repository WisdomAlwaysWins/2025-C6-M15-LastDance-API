"""
작품 임베딩 일괄 생성 스크립트 (Lambda 사용)

Lambda 함수를 호출하여 임베딩을 생성합니다.

사용법:
    docker-compose run --rm api python app/utils/generate_missing_embeddings.py
"""

import sys

sys.path.insert(0, "/app")

import base64
from io import BytesIO
import logging

from PIL import Image
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.generate_embeddings import resize_base64_image
from app.utils.lambda_client import lambda_client

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# DB 연결
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_artworks_without_embedding():
    """임베딩이 없는 작품 조회"""
    db = SessionLocal()
    try:
        query = text(
            """
            SELECT id, title, thumbnail_url, artist_id
            FROM artworks
            WHERE embedding IS NULL
            ORDER BY id
        """
        )

        result = db.execute(query)
        artworks = result.fetchall()

        logger.info(f"📊 임베딩 생성 대상: {len(artworks)}개 작품")
        return artworks

    finally:
        db.close()


def generate_embedding_for_artwork(artwork_id: int, title: str, thumbnail_url: str):
    """작품의 임베딩 생성 (Lambda 사용)"""
    db = SessionLocal()

    try:
        logger.info(f"{'='*60}")
        logger.info(f"작품 ID: {artwork_id}")
        logger.info(f"제목: {title}")
        logger.info(f"이미지 URL: {thumbnail_url}")

        # 1. 이미지 다운로드
        logger.info("🔄 이미지 다운로드 중...")
        response = requests.get(thumbnail_url, timeout=30)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGB")
        logger.info(f"✅ 이미지 다운로드 완료: {image.size}")

        # 2. Base64 변환 및 리사이즈
        logger.info("🔄 이미지 변환 중...")
        image_base64 = base64.b64encode(response.content).decode()
        image_base64 = resize_base64_image(image_base64, max_size=800)

        size_mb = len(image_base64) / 1024 / 1024
        logger.info(f"✅ 이미지 크기: {size_mb:.2f}MB")

        # 3. Lambda로 임베딩 생성
        logger.info("🔄 Lambda 호출 중 (임베딩 생성)...")
        embedding = lambda_client.generate_embedding(image_base64)

        logger.info(f"✅ 임베딩 생성 완료: {len(embedding)}차원")

        # 4. DB 저장
        logger.info("💾 DB 저장 중...")

        db.execute(
            text(
                """
                UPDATE artworks
                SET embedding = CAST(:embedding AS vector),
                    updated_at = NOW()
                WHERE id = :id
            """
            ),
            {"embedding": str(embedding), "id": artwork_id},
        )
        db.commit()

        logger.info(f"✅ '{title}' (ID: {artwork_id}) 임베딩 저장 완료!")
        return True

    except requests.RequestException as e:
        logger.error(f"❌ 이미지 다운로드 실패: {e}")
        db.rollback()
        return False

    except Exception as e:
        logger.error(f"❌ 임베딩 생성 실패: {e}", exc_info=True)
        db.rollback()
        return False

    finally:
        db.close()


def verify_embeddings():
    """임베딩 생성 결과 확인"""
    db = SessionLocal()

    try:
        logger.info("\n" + "=" * 60)
        logger.info("🔍 임베딩 생성 결과 확인")
        logger.info("=" * 60)

        query = text(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(embedding) as with_embedding,
                COUNT(*) - COUNT(embedding) as without_embedding
            FROM artworks
        """
        )

        result = db.execute(query).fetchone()
        total, with_emb, without_emb = result

        logger.info(f"\n📊 작품 임베딩 통계:")
        logger.info(f"  - 전체 작품: {total}개")
        logger.info(f"  - 임베딩 있음: {with_emb}개")
        logger.info(f"  - 임베딩 없음: {without_emb}개")

        if without_emb == 0:
            logger.info("\n✅ 모든 작품에 임베딩이 생성되었습니다!")
        else:
            logger.info(f"\n⚠️  {without_emb}개 작품에 임베딩이 없습니다.")

            # 임베딩 없는 작품 리스트
            query2 = text(
                """
                SELECT id, title
                FROM artworks
                WHERE embedding IS NULL
                ORDER BY id
            """
            )

            artworks = db.execute(query2).fetchall()

            logger.info("\n임베딩 없는 작품:")
            for artwork_id, title in artworks:
                logger.info(f"  - ID {artwork_id}: {title}")

    finally:
        db.close()


def main():
    """메인 실행"""
    logger.info("=" * 60)
    logger.info("🚀 작품 임베딩 일괄 생성 스크립트 (Lambda)")
    logger.info("=" * 60)

    # 설정 정보 출력
    logger.info(f"\n📋 설정 정보:")
    logger.info(f"  - DATABASE: {settings.POSTGRES_DB}")
    logger.info(f"  - Lambda Region: {settings.AWS_LAMBDA_REGION}")
    logger.info(f"  - S3 Bucket: {settings.S3_BUCKET_NAME}")

    # 임베딩 없는 작품 조회
    artworks = get_artworks_without_embedding()

    if not artworks:
        logger.info("\n✅ 모든 작품에 임베딩이 이미 생성되어 있습니다!")
        return

    logger.info(f"\n📝 총 {len(artworks)}개 작품의 임베딩을 생성합니다.")
    logger.info("⏱️  각 작품당 약 5-10초 소요 예상...\n")

    # 각 작품별 임베딩 생성
    success_count = 0
    fail_count = 0

    for idx, (artwork_id, title, thumbnail_url, artist_id) in enumerate(artworks, 1):
        logger.info(f"\n[{idx}/{len(artworks)}] 처리 중...")

        if generate_embedding_for_artwork(artwork_id, title, thumbnail_url):
            success_count += 1
        else:
            fail_count += 1

    # 결과 출력
    logger.info("\n" + "=" * 60)
    logger.info("✅ 임베딩 생성 완료!")
    logger.info("=" * 60)
    logger.info(f"\n📊 결과:")
    logger.info(f"  - 성공: {success_count}개")
    logger.info(f"  - 실패: {fail_count}개")
    logger.info(f"  - 전체: {len(artworks)}개")

    # 최종 확인
    verify_embeddings()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {e}", exc_info=True)
        raise
