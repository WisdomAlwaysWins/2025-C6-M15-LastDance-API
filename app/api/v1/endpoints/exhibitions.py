from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.exhibition import Exhibition
from app.schemas.exhibition import ExhibitionResponse

router = APIRouter()


@router.get("/", response_model=List[ExhibitionResponse])
async def list_exhibitions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    전시 목록 조회
    """
    exhibitions = db.query(Exhibition).offset(skip).limit(limit).all()
    return exhibitions


@router.get("/{exhibition_id}", response_model=ExhibitionResponse)
async def get_exhibition(
    exhibition_id: int,
    db: Session = Depends(get_db)
):
    """
    전시 상세 조회
    """
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return exhibition