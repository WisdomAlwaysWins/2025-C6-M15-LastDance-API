# app/api/v1/endpoints/artists.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import (
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse
)

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("", response_model=List[ArtistResponse])
def get_artists(
    db: Session = Depends(get_db)
):
    """
    작가 전체 조회
    
    Returns:
        List[ArtistResponse]: 작가 목록
    """
    artists = db.query(Artist).order_by(Artist.name).all()
    return artists


@router.get("/{artist_id}", response_model=ArtistResponse)
def get_artist(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    작가 상세 조회
    
    Args:
        artist_id: 작가 ID
        
    Returns:
        ArtistResponse: 작가 정보
        
    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found"
        )
    return artist


@router.get("/uuid/{uuid}", response_model=ArtistResponse)
def get_artist_by_uuid(
    uuid: str,
    db: Session = Depends(get_db)
):
    """
    작가 UUID로 조회
    
    Args:
        uuid: 작가 UUID
        
    Returns:
        ArtistResponse: 작가 정보
        
    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.uuid == uuid).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with uuid {uuid} not found"
        )
    return artist


@router.post("", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED)
def create_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db)
):
    """
    작가 생성 (관리자)
    
    Args:
        artist_data: 작가 생성 데이터
        
    Returns:
        ArtistResponse: 생성된 작가 정보
        
    Note:
        UUID는 서버에서 자동 생성
    """
    new_artist = Artist(**artist_data.model_dump())
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist


@router.put("/{artist_id}", response_model=ArtistResponse)
def update_artist(
    artist_id: int,
    artist_data: ArtistUpdate,
    db: Session = Depends(get_db)
):
    """
    작가 정보 수정 (관리자)
    
    Args:
        artist_id: 작가 ID
        artist_data: 수정 데이터
        
    Returns:
        ArtistResponse: 수정된 작가 정보
        
    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found"
        )
    
    update_data = artist_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artist, key, value)
    
    db.commit()
    db.refresh(artist)
    return artist


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    작가 삭제 (관리자)
    
    Args:
        artist_id: 작가 ID
        
    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found"
        )
    
    db.delete(artist)
    db.commit()
    return None