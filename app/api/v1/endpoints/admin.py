# app/api/v1/endpoints/admin.py
"""
관리자 API 엔드포인트
- Lambda가 생성한 임베딩 업데이트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.session import get_db
from app.models import Artwork

router = APIRouter()


class EmbeddingUpdate(BaseModel):
    """임베딩 업데이트 요청 스키마"""
    embedding: List[float]


@router.put("/artworks/{artwork_id}/embedding")
def update_artwork_embedding(
    artwork_id: int,
    data: EmbeddingUpdate,
    db: Session = Depends(get_db)
):
    """
    작품 임베딩 업데이트 (Lambda 전용)
    
    Lambda 함수가 DINOv2로 생성한 임베딩을 DB에 저장
    """
    
    # 임베딩 차원 검증 (DINOv2-small: 384차원)
    if len(data.embedding) != 384:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid embedding dimension: expected 384, got {len(data.embedding)}"
        )
    
    # 작품 조회
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=404,
            detail=f"Artwork with id {artwork_id} not found"
        )
    
    # 임베딩 저장
    artwork.embedding = data.embedding
    db.commit()
    db.refresh(artwork)
    
    return {
        "success": True,
        "message": "Embedding updated successfully",
        "artwork_id": artwork_id,
        "embedding_dim": len(data.embedding)
    }