from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ArtworkBase(BaseModel):
    """Artwork 기본 스키마"""
    title: str = Field(..., max_length=255, description="작품 제목")
    exhibition_id: int = Field(..., description="전시 ID")
    artist_id: Optional[int] = Field(None, description="작가 ID")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: str = Field(..., max_length=500, description="작품 이미지 URL")


class ArtworkCreate(ArtworkBase):
    """Artwork 생성 요청 스키마"""
    pass


class ArtworkUpdate(BaseModel):
    """Artwork 수정 요청 스키마"""
    title: Optional[str] = Field(None, max_length=255, description="작품 제목")
    exhibition_id: Optional[int] = Field(None, description="전시 ID")
    artist_id: Optional[int] = Field(None, description="작가 ID")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="작품 이미지 URL")


class ArtworkResponse(ArtworkBase):
    """Artwork 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 중첩 객체 포함 버전 (선택적 사용)
class ArtworkDetailResponse(ArtworkResponse):
    """Artwork 상세 응답 (artist, exhibition 포함)"""
    from app.schemas.artist import ArtistResponse
    from app.schemas.exhibition import ExhibitionResponse
    
    artist: Optional[ArtistResponse] = None
    exhibition: Optional[ExhibitionResponse] = None

    class Config:
        from_attributes = True