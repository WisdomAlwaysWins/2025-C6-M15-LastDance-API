from pydantic import BaseModel, Field
from typing import Optional


class ArtworkBase(BaseModel):
    """Artwork 기본 스키마"""
    title: str = Field(..., max_length=255, description="작품 제목")
    artist_name: str = Field(..., max_length=100, description="작가 이름")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    image_url: str = Field(..., max_length=500, description="작품 원본 이미지 URL")
    exhibition_id: int = Field(..., description="전시 ID")


class ArtworkCreate(ArtworkBase):
    """Artwork 생성 요청 스키마"""
    pass


class ArtworkUpdate(BaseModel):
    """Artwork 수정 요청 스키마"""
    title: Optional[str] = Field(None, max_length=255, description="작품 제목")
    artist_name: Optional[str] = Field(None, max_length=100, description="작가 이름")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    image_url: Optional[str] = Field(None, max_length=500, description="작품 원본 이미지 URL")


class ArtworkResponse(ArtworkBase):
    """Artwork 응답 스키마"""
    id: int

    class Config:
        from_attributes = True