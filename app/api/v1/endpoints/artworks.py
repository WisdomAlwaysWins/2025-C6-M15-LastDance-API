from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
from app.schemas.artwork import ArtworkResponse

router = APIRouter()


@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    작품 상세 조회
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork


@router.get("/exhibition/{exhibition_id}/artworks", response_model=List[ArtworkResponse])
async def list_artworks_by_exhibition(
    exhibition_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 전시의 작품 목록 조회
    """
    # 전시 존재 확인
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    artworks = db.query(Artwork).filter(Artwork.exhibition_id == exhibition_id).all()
    return artworks