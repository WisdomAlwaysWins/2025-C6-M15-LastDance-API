from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ExhibitionBase(BaseModel):
    """Exhibition 기본 스키마"""
    title: str = Field(..., max_length=255, description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="전시 시작일")
    end_date: date = Field(..., description="전시 종료일")
    venue_id: Optional[int] = Field(None, description="장소 ID")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="포스터 이미지 URL")


class ExhibitionCreate(ExhibitionBase):
    """Exhibition 생성 요청 스키마"""
    artist_ids: List[int] = Field(default=[], description="참여 작가 ID 리스트")


class ExhibitionUpdate(BaseModel):
    """Exhibition 수정 요청 스키마"""
    title: Optional[str] = Field(None, max_length=255, description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: Optional[date] = Field(None, description="전시 시작일")
    end_date: Optional[date] = Field(None, description="전시 종료일")
    venue_id: Optional[int] = Field(None, description="장소 ID")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="포스터 이미지 URL")
    artist_ids: Optional[List[int]] = Field(None, description="참여 작가 ID 리스트")


class ExhibitionResponse(ExhibitionBase):
    """Exhibition 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 중첩 객체 포함 버전 (선택적 사용)
class ExhibitionDetailResponse(ExhibitionResponse):
    """Exhibition 상세 응답 (venue, artists 포함)"""
    from app.schemas.venue import VenueResponse
    from app.schemas.artist import ArtistResponse
    
    venue: Optional[VenueResponse] = None
    artists: List[ArtistResponse] = []

    class Config:
        from_attributes = True