# app/api/v1/endpoints/artworks.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.artwork import Artwork
from app.models.artist import Artist
from app.models.exhibition import Exhibition
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkUpdate,
    ArtworkResponse,
    ArtworkDetail
)

router = APIRouter(prefix="/artworks", tags=["Artworks"])


@router.get("", response_model=List[ArtworkResponse])
def get_artworks(
    artist_id: Optional[int] = Query(None, description="작가 ID"),
    exhibition_id: Optional[int] = Query(None, description="전시 ID"),
    db: Session = Depends(get_db)
):
    """
    작품 전체 조회
    
    Args:
        artist_id: 작가 ID로 필터링
        exhibition_id: 전시 ID로 필터링
        
    Returns:
        List[ArtworkResponse]: 작품 목록
        
    Raises:
        404: 존재하지 않는 artist_id 또는 exhibition_id
    """
    # Artist 존재 여부 확인
    if artist_id:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {artist_id} not found"
            )
    
    # Exhibition 존재 여부 확인
    if exhibition_id:
        exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exhibition with id {exhibition_id} not found"
            )
    
    query = db.query(Artwork)
    
    if artist_id:
        query = query.filter(Artwork.artist_id == artist_id)
    
    if exhibition_id:
        query = query.join(Artwork.exhibitions).filter(Exhibition.id == exhibition_id)
    
    artworks = query.order_by(Artwork.id).all()
    return artworks


@router.get("/{artwork_id}", response_model=ArtworkDetail)
def get_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    작품 상세 조회 (작가, 전시 정보 포함)
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {artwork_id} not found"
        )
    return artwork


@router.post("", response_model=ArtworkDetail, status_code=status.HTTP_201_CREATED)
def create_artwork(
    artwork_data: ArtworkCreate,
    db: Session = Depends(get_db)
):
    """
    작품 생성 (관리자)
    
    Returns:
        ArtworkDetail: 생성된 작품 정보 (작가, 전시 포함)
        
    Raises:
        404: 존재하지 않는 artist_id
    """
    # Artist 존재 여부 확인
    artist = db.query(Artist).filter(Artist.id == artwork_data.artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artwork_data.artist_id} not found"
        )
    
    new_artwork = Artwork(**artwork_data.model_dump())
    db.add(new_artwork)
    db.commit()
    db.refresh(new_artwork)
    return new_artwork


@router.put("/{artwork_id}", response_model=ArtworkDetail)
def update_artwork(
    artwork_id: int,
    artwork_data: ArtworkUpdate,
    db: Session = Depends(get_db)
):
    """
    작품 정보 수정 (관리자)
    
    Returns:
        ArtworkDetail: 수정된 작품 정보 (작가, 전시 포함)
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {artwork_id} not found"
        )
    
    # Artist 존재 여부 확인
    if artwork_data.artist_id:
        artist = db.query(Artist).filter(Artist.id == artwork_data.artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {artwork_data.artist_id} not found"
            )
    
    update_data = artwork_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artwork, key, value)
    
    db.commit()
    db.refresh(artwork)
    return artwork


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    작품 삭제 (관리자)
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {artwork_id} not found"
        )
    
    db.delete(artwork)
    db.commit()
    return None