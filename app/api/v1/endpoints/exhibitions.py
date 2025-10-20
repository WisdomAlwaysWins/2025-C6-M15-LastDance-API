# app/api/v1/endpoints/exhibitions.py
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

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


@router.get("", response_model=List[ExhibitionResponse])
def get_exhibitions(
    status: Optional[str] = Query(None, description="ongoing/upcoming/past"),
    venue_id: Optional[int] = Query(None, description="전시 장소 ID"),
    db: Session = Depends(get_db),
):
    """
    전시 전체 조회

    Args:
        status: 전시 상태 (ongoing/upcoming/past)
        venue_id: 전시 장소 ID

    Returns:
        List[ExhibitionResponse]: 전시 목록

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

    query = db.query(Exhibition)

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

    exhibitions = query.order_by(Exhibition.start_date.desc()).all()
    return exhibitions


@router.get("/{exhibition_id}", response_model=ExhibitionDetail)
def get_exhibition(exhibition_id: int, db: Session = Depends(get_db)):
    """
    전시 상세 조회 (장소, 작품 목록 포함)
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID를 {exhibition_id}를 찾을 수 없습니다",
        )
    return exhibition


@router.post("", response_model=ExhibitionDetail, status_code=status.HTTP_201_CREATED)
def create_exhibition(
    exhibition_data: ExhibitionCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 생성 (관리자)

    Returns:
        ExhibitionDetail: 생성된 전시 정보 (장소, 작품 포함)

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

    return new_exhibition


@router.put("/{exhibition_id}", response_model=ExhibitionDetail)
def update_exhibition(
    exhibition_id: int,
    exhibition_data: ExhibitionUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 정보 수정 (관리자)

    Returns:
        ExhibitionDetail: 수정된 전시 정보 (장소, 작품 포함)
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID를 {exhibition_id}를 찾을 수 없습니다",
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
    return exhibition


@router.delete("/{exhibition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exhibition(
    exhibition_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    전시 삭제 (관리자)
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID를 {exhibition_id}를 찾을 수 없습니다",
        )

    db.delete(exhibition)
    db.commit()
    return None
