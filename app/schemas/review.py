from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewBase(BaseModel):
    """Review 기본 스키마"""
    photo_url: str = Field(..., max_length=500, description="관람객이 촬영한 사진 URL")
    text_review: Optional[str] = Field(None, description="텍스트 평가")
    artwork_id: int = Field(..., description="작품 ID")
    user_id: int = Field(..., description="사용자 ID")


class ReviewPrepareResponse(BaseModel):
    """Review 준비 응답 스키마 (작품 리스트 반환)"""
    uploaded_image_url: str = Field(..., description="업로드된 이미지 URL")
    artworks: List[dict] = Field(..., description="해당 전시의 작품 리스트")


class ReviewCreate(BaseModel):
    """Review 생성 요청 스키마"""
    photo_url: str = Field(..., max_length=500, description="관람객이 촬영한 사진 URL")
    text_review: Optional[str] = Field(None, description="텍스트 평가")
    artwork_id: int = Field(..., description="선택한 작품 ID")
    user_id: int = Field(..., description="사용자 ID")
    tag_ids: Optional[List[int]] = Field(default=[], description="선택한 태그 ID 리스트")


class ReviewResponse(BaseModel):
    """Review 응답 스키마"""
    id: int
    photo_url: str
    text_review: Optional[str]
    artwork_id: int
    user_id: int
    tags: List[dict] = Field(default=[], description="선택된 태그 리스트")
    created_at: datetime

    class Config:
        from_attributes = True