# app/api/v1/endpoints/venues.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.venue import Venue
from app.schemas.venue import (
    VenueCreate,
    VenueUpdate,
    VenueResponse
)

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.get("", response_model=List[VenueResponse])
def get_venues(
    db: Session = Depends(get_db)
):
    """
    전시 장소 전체 조회
    
    Returns:
        List[VenueResponse]: 전시 장소 목록
    """
    venues = db.query(Venue).order_by(Venue.name).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """
    전시 장소 상세 조회
    
    Args:
        venue_id: 장소 ID
        
    Returns:
        VenueResponse: 장소 정보
        
    Raises:
        404: 장소를 찾을 수 없음
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    return venue


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db)
):
    """
    전시 장소 생성 (관리자)
    
    Args:
        venue_data: 장소 생성 데이터
        
    Returns:
        VenueResponse: 생성된 장소 정보
    """
    new_venue = Venue(**venue_data.model_dump())
    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)
    return new_venue


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    venue_data: VenueUpdate,
    db: Session = Depends(get_db)
):
    """
    전시 장소 수정 (관리자)
    
    Args:
        venue_id: 장소 ID
        venue_data: 수정 데이터
        
    Returns:
        VenueResponse: 수정된 장소 정보
        
    Raises:
        404: 장소를 찾을 수 없음
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    
    update_data = venue_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(venue, key, value)
    
    db.commit()
    db.refresh(venue)
    return venue


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """
    전시 장소 삭제 (관리자)
    
    Args:
        venue_id: 장소 ID
        
    Raises:
        404: 장소를 찾을 수 없음
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    
    db.delete(venue)
    db.commit()
    return None