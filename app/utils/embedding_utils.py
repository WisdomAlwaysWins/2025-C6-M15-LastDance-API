"""
작품 임베딩 생성 유틸리티

작품 생성 시 자동으로 임베딩을 생성합니다.
- BackgroundTasks를 사용하여 비동기 처리
- S3 이미지 다운로드 → base64 변환 → Lambda 호출 → DB 저장
"""

import base64
import logging

import requests
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.generate_embeddings import resize_base64_image
from app.utils.lambda_client import lambda_client

logger = logging.getLogger(__name__)


# S3 이미지 경로 예시:
# - artworks: https://lastdance-artworks.s3.ap-northeast-2.amazonaws.com/artworks/{uuid}.jpg
# - reactions: https://lastdance-artworks.s3.ap-northeast-2.amazonaws.com/reactions/test/exhibition_1/visitor_1_1234567890_abc123.jpg


def generate_embedding_background(
    artwork_id: int, thumbnail_url: str, title: str, db: Session
) -> None:
    """
    백그라운드에서 작품 임베딩 생성

    Args:
        artwork_id: 작품 ID
        thumbnail_url: 썸네일 S3 URL
        title: 작품 제목
        db: DB 세션 (BackgroundTasks에서는 새 세션 필요)
    """
    try:
        logger.info(f"임베딩 생성 시작: Artwork ID {artwork_id} - '{title}'")

        # 1. 썸네일 다운로드
        logger.info(f"이미지 다운로드: {thumbnail_url}")
        response = requests.get(thumbnail_url, timeout=10)
        response.raise_for_status()

        # 2. base64 변환 & 리사이즈
        image_base64 = base64.b64encode(response.content).decode()
        image_base64 = resize_base64_image(image_base64, max_size=800)

        size_mb = len(image_base64) / 1024 / 1024
        logger.info(f"이미지 크기: {size_mb:.2f}MB")

        # 3. Lambda로 임베딩 생성
        logger.info("Lambda 호출: 임베딩 생성 중...")
        embedding = lambda_client.generate_embedding(image_base64)
        logger.info(f"임베딩 생성 완료: {len(embedding)}차원")

        # 4. DB 저장 (raw SQL 사용)
        db.execute(
            text(
                """
                UPDATE artworks
                SET embedding = CAST(:embedding AS vector),
                    updated_at = now()
                WHERE id = :id
            """
            ),
            {"embedding": str(embedding), "id": artwork_id},
        )
        db.commit()

        logger.info(f"✅ Artwork '{title}' (ID: {artwork_id}) 임베딩 저장 완료")

    except requests.RequestException as e:
        logger.error(f"⚠️ Artwork '{title}' 이미지 다운로드 실패: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"⚠️ Artwork '{title}' 임베딩 생성 실패: {e}")
        db.rollback()
    finally:
        db.close()


async def generate_embedding_sync(
    artwork_id: int, thumbnail_url: str, title: str, db: Session
) -> bool:
    """
    동기적으로 작품 임베딩 생성 (응답 대기)

    Args:
        artwork_id: 작품 ID
        thumbnail_url: 썸네일 S3 URL
        title: 작품 제목
        db: DB 세션

    Returns:
        bool: 성공 여부
    """
    try:
        logger.info(f"임베딩 생성 시작: Artwork ID {artwork_id} - '{title}'")

        # 1. 썸네일 다운로드
        response = requests.get(thumbnail_url, timeout=10)
        response.raise_for_status()

        # 2. base64 변환 & 리사이즈
        image_base64 = base64.b64encode(response.content).decode()
        image_base64 = resize_base64_image(image_base64, max_size=800)

        # 3. Lambda로 임베딩 생성
        embedding = lambda_client.generate_embedding(image_base64)

        # 4. DB 저장
        db.execute(
            text(
                """
                UPDATE artworks
                SET embedding = CAST(:embedding AS vector),
                    updated_at = now()
                WHERE id = :id
            """
            ),
            {"embedding": str(embedding), "id": artwork_id},
        )
        db.commit()

        logger.info(f"✅ Artwork '{title}' 임베딩 저장 완료")
        return True

    except Exception as e:
        logger.error(f"⚠️ Artwork '{title}' 임베딩 생성 실패: {e}")
        db.rollback()
        return False
