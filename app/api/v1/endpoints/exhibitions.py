# app/api/v1/endpoints/exhibitions.py
from datetime import date
import logging
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_api_key
from app.database import get_db
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
from app.models.venue import Venue
from app.schemas.exhibition import (
    ExhibitionCreate,
    ExhibitionDetail,
    ExhibitionResponse,
    ExhibitionUpdate,
)
from app.utils.s3_client import s3_client
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exhibitions", tags=["Exhibitions"])


@router.get(
    "",
    response_model=List[ExhibitionResponse],
    summary="전시 목록 조회",
    description="전시 목록을 조회합니다. status와 venue_id로 필터링 가능합니다.",
)
def get_exhibitions(
    status: Optional[str] = Query(None, description="ongoing/upcoming/past"),
    venue_id: Optional[int] = Query(None, description="전시 장소 ID"),
    db: Session = Depends(get_db),
):
    """
    전시 목록 조회 (가벼운 버전)

    Args:
        status: 전시 상태 (ongoing/upcoming/past)
        venue_id: 전시 장소 ID로 필터링

    Returns:
        List[ExhibitionResponse]: 전시 목록 (venue_name, artists 포함)

    Raises:
        404: 존재하지 않는 venue_id
    """
    # Venue 존재 여부 확인
    if venue_id:
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 장소 ID {venue_id}를 찾을 수 없습니다",
            )

    # 쿼리 구성 (venue, artworks, artists join)
    query = db.query(Exhibition).options(
        joinedload(Exhibition.venue),
        joinedload(Exhibition.artworks).joinedload(Artwork.artist),
    )

    if venue_id:
        query = query.filter(Exhibition.venue_id == venue_id)

    today = date.today()
    if status == "ongoing":
        query = query.filter(
            Exhibition.start_date <= today, Exhibition.end_date >= today
        )
    elif status == "upcoming":
        query = query.filter(Exhibition.start_date > today)
    elif status == "past":
        query = query.filter(Exhibition.end_date < today)

    exhibitions = query.order_by(Exhibition.id).all()

    # ExhibitionResponse 형식으로 변환
    results = []
    for exhibition in exhibitions:
        # 참여 작가 목록 (중복 제거)
        artists_dict = {}
        for artwork in exhibition.artworks:
            if artwork.artist and artwork.artist.id not in artists_dict:
                artists_dict[artwork.artist.id] = {
                    "id": artwork.artist.id,
                    "name": artwork.artist.name,
                    "bio": artwork.artist.bio,
                }

        results.append(
            {
                "id": exhibition.id,
                "title": exhibition.title,
                "description_text": exhibition.description_text,
                "start_date": exhibition.start_date,
                "end_date": exhibition.end_date,
                "venue_id": exhibition.venue_id,
                "venue_name": exhibition.venue.name if exhibition.venue else "",
                "cover_image_url": exhibition.cover_image_url,
                "artists": list(artists_dict.values()),
                "created_at": exhibition.created_at,
                "updated_at": exhibition.updated_at,
            }
        )

    return results


@router.get(
    "/{exhibition_id}",
    response_model=ExhibitionDetail,
    summary="전시 상세 조회",
    description="전시 ID로 상세 정보를 조회합니다. 장소 및 작품 목록 포함",
)
def get_exhibition(exhibition_id: int, db: Session = Depends(get_db)):
    """
    전시 상세 조회 (전체 정보)

    Args:
        exhibition_id: 전시 ID

    Returns:
        ExhibitionDetail: 전시 상세 정보 (venue, artworks, artists 포함)

    Raises:
        404: 전시를 찾을 수 없음
    """
    # 전시 조회 (관계 데이터 포함)
    exhibition = (
        db.query(Exhibition)
        .options(
            joinedload(Exhibition.venue),
            joinedload(Exhibition.artworks).joinedload(Artwork.artist),
        )
        .filter(Exhibition.id == exhibition_id)
        .first()
    )

    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
        )

    # 참여 작가 목록 (중복 제거)
    artists_dict = {}
    for artwork in exhibition.artworks:
        if artwork.artist and artwork.artist.id not in artists_dict:
            artists_dict[artwork.artist.id] = {
                "id": artwork.artist.id,
                "name": artwork.artist.name,
                "bio": artwork.artist.bio,
            }

    # ExhibitionDetail 형식으로 변환
    result = {
        "id": exhibition.id,
        "title": exhibition.title,
        "description_text": exhibition.description_text,
        "start_date": exhibition.start_date,
        "end_date": exhibition.end_date,
        "venue_id": exhibition.venue_id,
        "venue": exhibition.venue,
        "cover_image_url": exhibition.cover_image_url,
        "artworks": [
            {
                "id": artwork.id,
                "title": artwork.title,
                "artist_name": artwork.artist.name if artwork.artist else "",
                "year": artwork.year,
                "thumbnail_url": artwork.thumbnail_url,
            }
            for artwork in exhibition.artworks
        ],
        "artists": list(artists_dict.values()),
        "created_at": exhibition.created_at,
        "updated_at": exhibition.updated_at,
    }

    return result


@router.post(
    "",
    response_model=ExhibitionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="전시 생성",
    description="새 전시를 생성합니다. 커버 이미지 업로드 포함. (관리자 전용, API Key 필요)",
)
async def create_exhibition(
    title: str = Form(..., description="전시 제목"),
    start_date: date = Form(..., description="시작일"),
    end_date: date = Form(..., description="종료일"),
    venue_id: int = Form(..., description="전시 장소 ID"),
    description_text: Optional[str] = Form(None, description="전시 설명"),
    cover_image: Optional[UploadFile] = File(None, description="커버 이미지 파일"),
    artwork_ids: Optional[str] = Form(None, description="작품 ID 목록 (JSON 문자열)"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 생성 (관리자)

    Args:
        title: 전시 제목
        start_date: 시작일
        end_date: 종료일
        venue_id: 전시 장소 ID
        description_text: 전시 설명 (선택)
        cover_image: 커버 이미지 파일 (선택)
        artwork_ids: 작품 ID 목록 JSON 문자열 (예: "[1,2,3]") (선택)

    Returns:
        ExhibitionDetail: 생성된 전시 정보 (장소, 작품, 작가 포함)

    Raises:
        400: 날짜 검증 실패
        404: 존재하지 않는 venue_id 또는 artwork_ids
        500: S3 업로드 실패
    """
    # 날짜 검증
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작 날짜는 종료 날짜보다 이전이어야 합니다",
        )

    # Venue 존재 여부 확인
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 장소 ID {venue_id}를 찾을 수 없습니다",
        )

    # 커버 이미지 업로드
    cover_image_url = None
    if cover_image:
        try:
            cover_image_url = await s3_client.upload_file(
                file=cover_image, folder="exhibitions"
            )
            logger.info(f"S3 업로드 성공: {cover_image_url}")
        except Exception as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 실패: {str(e)}",
            )

    # Exhibition 생성
    new_exhibition = Exhibition(
        title=title,
        description_text=description_text,
        start_date=start_date,
        end_date=end_date,
        venue_id=venue_id,
        cover_image_url=cover_image_url,
    )
    db.add(new_exhibition)
    db.commit()
    db.refresh(new_exhibition)

    # Artwork 연결
    if artwork_ids:
        import json

        try:
            artwork_id_list = json.loads(artwork_ids)
            artworks = (
                db.query(Artwork).filter(Artwork.id.in_(artwork_id_list)).all()
            )

            found_ids = {artwork.id for artwork in artworks}
            missing_ids = set(artwork_id_list) - found_ids
            if missing_ids:
                # 생성된 Exhibition 삭제
                db.delete(new_exhibition)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"작품 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                )

            new_exhibition.artworks.extend(artworks)
            db.commit()
            db.refresh(new_exhibition)
        except json.JSONDecodeError:
            db.delete(new_exhibition)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="artwork_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    # 생성 후 상세 정보 조회하여 반환
    return get_exhibition(int(new_exhibition.id), db)


@router.put(
    "/{exhibition_id}",
    response_model=ExhibitionDetail,
    summary="전시 수정",
    description="전시 정보를 수정합니다. 커버 이미지 교체 포함. (관리자 전용, API Key 필요)",
)
async def update_exhibition(
    exhibition_id: int,
    title: Optional[str] = Form(None, description="전시 제목"),
    description_text: Optional[str] = Form(None, description="전시 설명"),
    start_date: Optional[date] = Form(None, description="시작일"),
    end_date: Optional[date] = Form(None, description="종료일"),
    venue_id: Optional[int] = Form(None, description="전시 장소 ID"),
    cover_image: Optional[UploadFile] = File(None, description="새 커버 이미지"),
    artwork_ids: Optional[str] = Form(None, description="작품 ID 목록 (JSON 문자열)"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 정보 수정 (관리자)

    Args:
        exhibition_id: 전시 ID
        title: 전시 제목 (선택)
        description_text: 전시 설명 (선택)
        start_date: 시작일 (선택)
        end_date: 종료일 (선택)
        venue_id: 전시 장소 ID (선택)
        cover_image: 새 커버 이미지 (선택)
        artwork_ids: 작품 ID 목록 JSON 문자열 (선택)

    Returns:
        ExhibitionDetail: 수정된 전시 정보 (장소, 작품, 작가 포함)

    Raises:
        400: 날짜 검증 실패
        404: 전시, 장소 또는 작품을 찾을 수 없음
        500: S3 업로드 실패
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
        )

    # 날짜 검증
    start = start_date or exhibition.start_date
    end = end_date or exhibition.end_date
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작 날짜는 종료 날짜보다 이전이어야 합니다",
        )

    # Venue 존재 여부 확인
    if venue_id:
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 장소 ID {venue_id}를 찾을 수 없습니다",
            )

    # 기본 필드 수정
    if title is not None:
        exhibition.title = title  # type: ignore
    if description_text is not None:
        exhibition.description_text = description_text  # type: ignore
    if start_date is not None:
        exhibition.start_date = start_date  # type: ignore
    if end_date is not None:
        exhibition.end_date = end_date  # type: ignore
    if venue_id is not None:
        exhibition.venue_id = venue_id  # type: ignore

    # 커버 이미지 교체
    if cover_image is not None:
        # 기존 S3 이미지 삭제
        old_cover_url = exhibition.cover_image_url
        if old_cover_url:
            try:
                s3_client.delete_file(str(old_cover_url))
                logger.info(f"기존 커버 이미지 삭제 성공: {old_cover_url}")
            except Exception as e:
                logger.warning(f"기존 커버 이미지 삭제 실패 (계속 진행): {e}")

        # 새 이미지 업로드
        try:
            new_cover_url = await s3_client.upload_file(
                file=cover_image, folder="exhibitions"
            )
            exhibition.cover_image_url = new_cover_url  # type: ignore
            logger.info(f"새 커버 이미지 업로드 성공: {new_cover_url}")
        except Exception as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 실패: {str(e)}",
            )

    # Artwork 관계 수정
    if artwork_ids is not None:
        import json

        try:
            artwork_id_list = json.loads(artwork_ids)
            artworks = (
                db.query(Artwork).filter(Artwork.id.in_(artwork_id_list)).all()
            )

            found_ids = {artwork.id for artwork in artworks}
            missing_ids = set(artwork_id_list) - found_ids
            if missing_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"작품 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                )

            exhibition.artworks.clear()
            exhibition.artworks.extend(artworks)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="artwork_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    db.commit()
    db.refresh(exhibition)

    # 수정 후 상세 정보 조회하여 반환
    return get_exhibition(exhibition_id, db)


@router.delete(
    "/{exhibition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="전시 삭제",
    description="전시를 삭제합니다. S3 커버 이미지도 함께 삭제. (관리자 전용, API Key 필요)",
)
async def delete_exhibition(
    exhibition_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 삭제 (관리자)

    Args:
        exhibition_id: 전시 ID

    Raises:
        404: 전시를 찾을 수 없음

    Note:
        S3에 저장된 커버 이미지도 함께 삭제됩니다
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
        )

    # S3에서 커버 이미지 삭제
    if exhibition.cover_image_url:
        try:
            s3_client.delete_file(str(exhibition.cover_image_url))
            logger.info(f"S3 커버 이미지 삭제 성공: {exhibition.cover_image_url}")
        except Exception as e:
            logger.warning(f"S3 커버 이미지 삭제 실패 (계속 진행): {e}")

    # DB에서 전시 삭제
    db.delete(exhibition)
    db.commit()

    logger.info(f"Exhibition ID {exhibition_id} 삭제 완료")
    return None