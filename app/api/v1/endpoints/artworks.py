# app/api/v1/endpoints/artworks.py
import base64
import io
import logging
from typing import List, Optional

from PIL import Image
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_api_key
from app.database import SessionLocal, get_db
from app.models.artist import Artist
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
from app.models.reaction import Reaction
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkDetail,
    ArtworkMatchRequest,
    ArtworkMatchResponse,
    ArtworkResponse,
    ArtworkUpdate,
)
from app.utils.embedding_utils import generate_embedding_background
from app.utils.lambda_client import lambda_client
from app.utils.s3_client import s3_client
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/artworks", tags=["Artworks"])


@router.get(
    "",
    response_model=List[ArtworkResponse],
    summary="작품 목록 조회",
    description="작품 목록을 조회합니다. artist_id와 exhibition_id로 필터링 가능합니다.",
)
def get_artworks(
    artist_id: Optional[int] = Query(None, description="작가 ID"),
    exhibition_id: Optional[int] = Query(None, description="전시 ID"),
    db: Session = Depends(get_db),
):
    """
    작품 목록 조회 (가벼운 버전)

    Args:
        artist_id: 작가 ID로 필터링
        exhibition_id: 전시 ID로 필터링

    Returns:
        List[ArtworkResponse]: 작품 목록 (artist_name, reaction_count 포함)

    Raises:
        404: 존재하지 않는 artist_id 또는 exhibition_id
    """
    # Artist 존재 여부 확인
    if artist_id:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
            )

    # Exhibition 존재 여부 확인
    if exhibition_id:
        exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
            )

    # 쿼리 구성 (artist와 reaction_count join)
    query = (
        db.query(
            Artwork,
            Artist.name.label("artist_name"),
            func.count(Reaction.id).label("reaction_count"),
        )
        .join(Artist, Artwork.artist_id == Artist.id)
        .outerjoin(Reaction, Artwork.id == Reaction.artwork_id)
        .group_by(Artwork.id, Artist.name)
    )

    if artist_id:
        query = query.filter(Artwork.artist_id == artist_id)

    if exhibition_id:
        query = query.join(Artwork.exhibitions).filter(Exhibition.id == exhibition_id)

    results = query.order_by(Artwork.id).all()

    # ArtworkResponse 형식으로 변환
    artworks = []
    for artwork, artist_name, reaction_count in results:
        artworks.append(
            {
                "id": artwork.id,
                "title": artwork.title,
                "artist_id": artwork.artist_id,
                "artist_name": artist_name,
                "description": artwork.description,
                "year": artwork.year,
                "thumbnail_url": artwork.thumbnail_url,
                "reaction_count": reaction_count,
                "created_at": artwork.created_at,
                "updated_at": artwork.updated_at,
            }
        )

    return artworks


@router.get(
    "/{artwork_id}",
    response_model=ArtworkDetail,
    summary="작품 상세 조회",
    description="작품 ID로 상세 정보를 조회합니다. 작가 및 전시 정보 포함.",
)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """
    작품 상세 조회 (전체 정보)

    Args:
        artwork_id: 작품 ID

    Returns:
        ArtworkDetail: 작품 상세 정보 (artist, exhibitions, reaction_count 포함)

    Raises:
        404: 작품을 찾을 수 없음
    """
    # 작품 조회 (관계 데이터 포함)
    artwork = (
        db.query(Artwork)
        .options(
            joinedload(Artwork.artist),
            joinedload(Artwork.exhibitions).joinedload(Exhibition.venue),
            joinedload(Artwork.reactions),
        )
        .filter(Artwork.id == artwork_id)
        .first()
    )

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # ArtworkDetail 형식으로 변환
    result = {
        "id": artwork.id,
        "title": artwork.title,
        "artist_id": artwork.artist_id,
        "artist": artwork.artist,
        "description": artwork.description,
        "year": artwork.year,
        "thumbnail_url": artwork.thumbnail_url,
        "reaction_count": len(artwork.reactions),
        "exhibitions": [
            {
                "id": ex.id,
                "title": ex.title,
                "venue_name": ex.venue.name if ex.venue else "",
                "start_date": ex.start_date,
                "end_date": ex.end_date,
                "cover_image_url": ex.cover_image_url,
            }
            for ex in artwork.exhibitions
        ],
        "created_at": artwork.created_at,
        "updated_at": artwork.updated_at,
    }

    return result


@router.post(
    "",
    response_model=ArtworkDetail,
    status_code=status.HTTP_201_CREATED,
    summary="작품 생성",
    description="새 작품을 등록합니다. 이미지 업로드 및 임베딩 자동 생성. (관리자 전용, API Key 필요)",
)
async def create_artwork(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="작품 제목"),
    artist_id: int = Form(..., description="작가 ID"),
    description: Optional[str] = Form(None, description="작품 설명"),
    year: Optional[int] = Form(None, description="제작 연도"),
    thumbnail: UploadFile = File(..., description="썸네일 이미지 파일"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 생성 (관리자)

    Args:
        background_tasks: 백그라운드 작업
        title: 작품 제목
        artist_id: 작가 ID
        description: 작품 설명 (선택)
        year: 제작 연도 (선택)
        thumbnail: 썸네일 이미지 파일

    Returns:
        ArtworkDetail: 생성된 작품 정보 (작가, 전시 포함)

    Raises:
        404: 존재하지 않는 artist_id
        500: S3 업로드 실패

    Note:
        - 이미지는 S3 artworks 폴더에 저장
        - 임베딩은 백그라운드에서 자동 생성 (약 3초)
    """
    # Artist 존재 여부 확인
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
        )

    # S3에 썸네일 업로드
    try:
        thumbnail_url = await s3_client.upload_file(file=thumbnail, folder="artworks")
        logger.info(f"S3 업로드 성공: {thumbnail_url}")
    except Exception as e:
        logger.error(f"S3 업로드 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 업로드 실패: {str(e)}",
        )

    # Artwork 생성
    new_artwork = Artwork(
        title=title,
        artist_id=artist_id,
        description=description,
        year=year,
        thumbnail_url=thumbnail_url,
    )
    db.add(new_artwork)
    db.commit()
    db.refresh(new_artwork)

    # 백그라운드에서 임베딩 생성
    logger.info(f"임베딩 생성 예약: Artwork ID {new_artwork.id}")
    background_tasks.add_task(
        generate_embedding_background,
        artwork_id=int(new_artwork.id),
        thumbnail_url=thumbnail_url,
        title=title,
        db=SessionLocal(),
    )

    # 생성 후 상세 정보 조회하여 반환
    return get_artwork(int(new_artwork.id), db)


@router.put(
    "/{artwork_id}",
    response_model=ArtworkDetail,
    summary="작품 수정",
    description="작품 정보를 수정합니다. 이미지 수정 시 기존 S3 이미지 삭제 및 임베딩 재생성. (관리자 전용, API Key 필요)",
)
async def update_artwork(
    artwork_id: int,
    background_tasks: BackgroundTasks,
    title: Optional[str] = Form(None, description="작품 제목"),
    artist_id: Optional[int] = Form(None, description="작가 ID"),
    description: Optional[str] = Form(None, description="작품 설명"),
    year: Optional[int] = Form(None, description="제작 연도"),
    thumbnail: Optional[UploadFile] = File(None, description="새 썸네일 이미지"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 정보 수정 (관리자)

    Args:
        artwork_id: 작품 ID
        background_tasks: 백그라운드 작업
        title: 작품 제목 (선택)
        artist_id: 작가 ID (선택)
        description: 작품 설명 (선택)
        year: 제작 연도 (선택)
        thumbnail: 새 썸네일 이미지 (선택)

    Returns:
        ArtworkDetail: 수정된 작품 정보 (작가, 전시 포함)

    Raises:
        404: 작품 또는 작가를 찾을 수 없음
        500: S3 업로드 실패

    Note:
        - 이미지 교체 시 기존 S3 이미지 삭제
        - 이미지 교체 시 임베딩 재생성
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # Artist 존재 여부 확인
    if artist_id:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
            )

    # 필드 수정
    if title is not None:
        artwork.title = title  # type: ignore
    if artist_id is not None:
        artwork.artist_id = artist_id  # type: ignore
    if description is not None:
        artwork.description = description  # type: ignore
    if year is not None:
        artwork.year = year  # type: ignore

    # 썸네일 이미지 교체
    if thumbnail is not None:
        # 기존 S3 이미지 삭제
        old_thumbnail_url = artwork.thumbnail_url
        if old_thumbnail_url:
            try:
                s3_client.delete_file(str(old_thumbnail_url))
                logger.info(f"기존 썸네일 삭제 성공: {old_thumbnail_url}")
            except Exception as e:
                logger.warning(f"기존 썸네일 삭제 실패 (계속 진행): {e}")

        # 새 이미지 업로드
        try:
            new_thumbnail_url = await s3_client.upload_file(
                file=thumbnail, folder="artworks"
            )
            artwork.thumbnail_url = new_thumbnail_url  # type: ignore
            logger.info(f"새 썸네일 업로드 성공: {new_thumbnail_url}")

            # 백그라운드에서 임베딩 재생성
            logger.info(f"임베딩 재생성 예약: Artwork ID {artwork_id}")
            background_tasks.add_task(
                generate_embedding_background,
                artwork_id=artwork_id,
                thumbnail_url=new_thumbnail_url,
                title=artwork.title,
                db=SessionLocal(),
            )
        except Exception as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 실패: {str(e)}",
            )

    db.commit()
    db.refresh(artwork)

    # 수정 후 상세 정보 조회하여 반환
    return get_artwork(artwork_id, db)


@router.delete(
    "/{artwork_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="작품 삭제",
    description="작품을 삭제합니다. S3 이미지도 함께 삭제. (관리자 전용, API Key 필요)",
)
async def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 삭제 (관리자)

    Args:
        artwork_id: 작품 ID

    Raises:
        404: 작품을 찾을 수 없음

    Note:
        S3에 저장된 썸네일 이미지도 함께 삭제됩니다
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # S3에서 썸네일 삭제
    if artwork.thumbnail_url:
        try:
            s3_client.delete_file(str(artwork.thumbnail_url))
            logger.info(f"S3 썸네일 삭제 성공: {artwork.thumbnail_url}")
        except Exception as e:
            logger.warning(f"S3 썸네일 삭제 실패 (계속 진행): {e}")

    # DB에서 작품 삭제
    db.delete(artwork)
    db.commit()

    logger.info(f"Artwork ID {artwork_id} 삭제 완료")
    return None


def resize_base64_image_smart(base64_string: str, max_size: int = 1024) -> str:
    """
    조건부 이미지 리사이즈 (1MB 이하는 스킵)

    Args:
        base64_string: base64 인코딩된 이미지
        max_size: 최대 가로/세로 크기 (px)

    Returns:
        str: 리사이즈된 base64 이미지 (또는 원본)
    """
    size_mb = len(base64_string) / 1024 / 1024

    # 1MB 이하면 원본 사용
    if size_mb <= 1.0:
        return base64_string

    try:
        # base64 → 이미지
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        # RGB로 변환
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        # 리사이즈 (비율 유지)
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # 이미지 → base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        resized_base64 = base64.b64encode(buffer.getvalue()).decode()

        return resized_base64

    except Exception as e:
        logger.error(f"이미지 리사이즈 실패: {e}, 원본 사용")
        return base64_string


@router.post(
    "/match",
    response_model=ArtworkMatchResponse,
    summary="작품 이미지 매칭",
    description="업로드된 이미지와 유사한 작품을 전체 작품에서 찾습니다. (pgvector 유사도 검색)",
)
async def match_artwork(request: ArtworkMatchRequest, db: Session = Depends(get_db)):
    """
    이미지 매칭 (pgvector 기반)

    1. lambda로 사용자 이미지 임베딩 생성
    2. DB에서 pgvector 유사도 검색
    3. 결과 반환
    """
    try:
        # 매칭 시작 로깅
        logger.info("=" * 60)
        logger.info("🔍 작품 이미지 매칭 시작")
        logger.info(f"   📊 요청 Threshold: {request.threshold}")
        
        # 1. 입력 검증
        if not request.image_base64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지가 제공되지 않았습니다.",
            )

        size_mb = len(request.image_base64) / 1024 / 1024
        logger.info(f"   🖼️  원본 이미지 크기: {size_mb:.2f}MB")
        
        if size_mb > 50:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"이미지 크기가 너무 큽니다: {size_mb:.2f}MB (최대 50MB)",
            )

        # 2. 조건부 리사이즈 (1MB 이하면 스킵)
        if size_mb > 1.0:
            logger.info(f"   🔄 이미지 리사이즈 중... ({size_mb:.2f}MB)")
            resized_image = resize_base64_image_smart(
                request.image_base64, max_size=1024
            )
            new_size_mb = len(resized_image) / 1024 / 1024
            logger.info(f"   ✅ 리사이즈 완료: {size_mb:.2f}MB → {new_size_mb:.2f}MB")
        else:
            logger.info("   ✅ 리사이즈 생략 (1MB 이하)")
            resized_image = request.image_base64

        # 3. Lambda로 사용자 이미지 임베딩 생성
        logger.info("   🔄 Lambda 호출 중 (임베딩 생성)...")
        user_embedding = lambda_client.generate_embedding(resized_image)
        logger.info(f"   ✅ 임베딩 생성 완료: {len(user_embedding)}차원")

        # 4. DB에서 pgvector 유사도 검색
        logger.info(f"   🔍 DB 유사도 검색 중 (threshold >= {request.threshold})...")

        # pgvector 코사인 유사도 검색
        # 1 - (embedding <=> user_embedding) = 코사인 유사도
        query = text(
            """
            SELECT 
                a.id,
                a.title,
                a.artist_id,
                a.thumbnail_url,
                1 - (a.embedding <=> CAST(:user_embedding AS vector)) as similarity
            FROM artworks a
            WHERE a.embedding IS NOT NULL
                AND 1 - (a.embedding <=> CAST(:user_embedding AS vector)) >= :threshold
            ORDER BY a.embedding <=> CAST(:user_embedding AS vector)
            LIMIT 10
        """
        )

        results = db.execute(
            query,
            {
                "user_embedding": str(user_embedding),
                "threshold": request.threshold,
            },
        ).fetchall()

        # 검색 결과 상세 로깅
        logger.info(f"   📊 검색 결과: {len(results)}개 작품 매칭")
        
        if results:
            # 유사도 통계
            similarities = [float(r.similarity) for r in results]
            max_sim = max(similarities)
            min_sim = min(similarities)
            avg_sim = sum(similarities) / len(similarities)
            
            logger.info(f"   📈 유사도 통계:")
            logger.info(f"      - 최고: {max_sim:.4f}")
            logger.info(f"      - 최저: {min_sim:.4f}")
            logger.info(f"      - 평균: {avg_sim:.4f}")
            logger.info(f"      - 범위: {min_sim:.4f} ~ {max_sim:.4f}")
            
            # 상위 3개 결과 로깅
            logger.info(f"   🎯 상위 매칭 작품:")
            for idx, r in enumerate(results[:3], 1):
                logger.info(
                    f"      [{idx}] {r.title} "
                    f"(유사도: {r.similarity:.4f}, ID: {r.id})"
                )
            
            # 전체 결과는 DEBUG 레벨에
            if len(results) > 3:
                logger.debug(f"   📋 전체 매칭 결과:")
                for idx, r in enumerate(results, 1):
                    logger.debug(
                        f"      [{idx}] {r.title} - "
                        f"유사도: {r.similarity:.4f} "
                        f"(ID: {r.id})"
                    )
        else:
            logger.warning(
                f"   ⚠️  매칭된 작품 없음 "
                f"(threshold {request.threshold} 이상인 작품 없음)"
            )

        # 5. 결과에 상세 정보 추가
        matched_artworks = []

        for row in results:
            # 작품 상세 정보 조회
            artwork = (
                db.query(Artwork)
                .options(
                    joinedload(Artwork.artist),
                    joinedload(Artwork.exhibitions).joinedload(Exhibition.venue),
                )
                .filter(Artwork.id == row.id)
                .first()
            )

            if artwork:
                matched_artworks.append(
                    {
                        "artwork_id": artwork.id,
                        "title": artwork.title,
                        "artist_id": artwork.artist_id,
                        "artist_name": artwork.artist.name if artwork.artist else "",
                        "thumbnail_url": artwork.thumbnail_url,
                        "similarity": float(row.similarity),
                        "exhibitions": [
                            {
                                "id": ex.id,
                                "title": ex.title,
                                "venue_name": ex.venue.name if ex.venue else "",
                                "start_date": ex.start_date,
                                "end_date": ex.end_date,
                                "cover_image_url": ex.cover_image_url,
                            }
                            for ex in artwork.exhibitions
                        ],
                    }
                )

        # 최종 결과 로깅
        logger.info("   " + "=" * 56)
        logger.info(
            f"   ✅ 매칭 완료: "
            f"매칭 여부={len(matched_artworks) > 0}, "
            f"총 {len(matched_artworks)}개, "
            f"사용 Threshold={request.threshold}"
        )
        logger.info("=" * 60)

        return {
            "matched": len(matched_artworks) > 0,
            "total_matches": len(matched_artworks),
            "threshold": request.threshold,
            "results": matched_artworks,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ 작품 매칭 실패: {str(e)}", exc_info=True)
        logger.error("=" * 60)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 매칭 중 오류가 발생했습니다: {str(e)}",
        )