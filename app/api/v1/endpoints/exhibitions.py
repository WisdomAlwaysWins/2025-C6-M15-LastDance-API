# app/api/v1/endpoints/exhibitions.py
from datetime import date
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
from fastapi import APIRouter, Depends, HTTPException, Query, status

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
        joinedload(Exhibition.artworks).joinedload(Artwork.artist)
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
        
        results.append({
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
        })
    
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
            joinedload(Exhibition.artworks).joinedload(Artwork.artist)
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
    description="새 전시를 생성합니다. (관리자 전용, API Key 필요)",
)
def create_exhibition(
    exhibition_data: ExhibitionCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 생성 (관리자)

    Args:
        exhibition_data: 전시 생성 데이터
        
    Returns:
        ExhibitionDetail: 생성된 전시 정보 (장소, 작품, 작가 포함)

    Raises:
        400: 날짜 검증 실패
        404: 존재하지 않는 venue_id 또는 artwork_ids
    """
    # 날짜 검증
    if exhibition_data.start_date > exhibition_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작 날짜는 종료 날짜보다 이전이어야 합니다",
        )

    # Venue 존재 여부 확인
    venue = db.query(Venue).filter(Venue.id == exhibition_data.venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 장소 ID {exhibition_data.venue_id}를 찾을 수 없습니다",
        )

    # Exhibition 생성
    exhibition_dict = exhibition_data.model_dump(exclude={"artwork_ids"})
    new_exhibition = Exhibition(**exhibition_dict)
    db.add(new_exhibition)
    db.commit()
    db.refresh(new_exhibition)

    # Artwork 연결
    if exhibition_data.artwork_ids:
        artworks = (
            db.query(Artwork).filter(Artwork.id.in_(exhibition_data.artwork_ids)).all()
        )

        found_ids = {artwork.id for artwork in artworks}
        missing_ids = set(exhibition_data.artwork_ids) - found_ids
        if missing_ids:
            db.delete(new_exhibition)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {sorted(missing_ids)}를 찾을 수 없습니다",
            )

        new_exhibition.artworks.extend(artworks)
        db.commit()
        db.refresh(new_exhibition)

    # 생성 후 상세 정보 조회하여 반환
    return get_exhibition(new_exhibition.id, db)


@router.put(
    "/{exhibition_id}",
    response_model=ExhibitionDetail,
    summary="전시 수정",
    description="전시 정보를 수정합니다. (관리자 전용, API Key 필요)",
)
def update_exhibition(
    exhibition_id: int,
    exhibition_data: ExhibitionUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 정보 수정 (관리자)

    Args:
        exhibition_id: 전시 ID
        exhibition_data: 수정 데이터
        
    Returns:
        ExhibitionDetail: 수정된 전시 정보 (장소, 작품, 작가 포함)
        
    Raises:
        400: 날짜 검증 실패
        404: 전시, 장소 또는 작품을 찾을 수 없음
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
        )

    # 날짜 검증
    start = exhibition_data.start_date or exhibition.start_date
    end = exhibition_data.end_date or exhibition.end_date
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작 날짜는 종료 날짜보다 이전이어야 합니다",
        )

    # Venue 존재 여부 확인
    if exhibition_data.venue_id:
        venue = db.query(Venue).filter(Venue.id == exhibition_data.venue_id).first()
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 장소 ID {exhibition_data.venue_id}를 찾을 수 없습니다",
            )

    # 기본 필드 수정
    update_dict = exhibition_data.model_dump(
        exclude={"artwork_ids"}, exclude_unset=True
    )
    for key, value in update_dict.items():
        setattr(exhibition, key, value)

    # Artwork 관계 수정
    if exhibition_data.artwork_ids is not None:
        artworks = (
            db.query(Artwork).filter(Artwork.id.in_(exhibition_data.artwork_ids)).all()
        )

        found_ids = {artwork.id for artwork in artworks}
        missing_ids = set(exhibition_data.artwork_ids) - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {sorted(missing_ids)}를 찾을 수 없습니다",
            )

        exhibition.artworks.clear()
        exhibition.artworks.extend(artworks)

    db.commit()
    db.refresh(exhibition)
    
    # 수정 후 상세 정보 조회하여 반환
    return get_exhibition(exhibition_id, db)


@router.delete(
    "/{exhibition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="전시 삭제",
    description="전시를 삭제합니다. (관리자 전용, API Key 필요)",
)
def delete_exhibition(
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
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
        )

    db.delete(exhibition)
    db.commit()
    return None