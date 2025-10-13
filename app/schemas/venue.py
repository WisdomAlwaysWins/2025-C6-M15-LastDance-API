from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VenueBase(BaseModel):
    """Venue 기본 스키마"""
    name: str = Field(..., max_length=255, description="장소 이름")
    address: Optional[str] = Field(None, max_length=500, description="주소")
    geo_lat: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    geo_lon: Optional[float] = Field(None, ge=-180, le=180, description="경도")


class VenueCreate(VenueBase):
    """Venue 생성 요청 스키마"""
    pass


class VenueUpdate(BaseModel):
    """Venue 수정 요청 스키마"""
    name: Optional[str] = Field(None, max_length=255, description="장소 이름")
    address: Optional[str] = Field(None, max_length=500, description="주소")
    geo_lat: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    geo_lon: Optional[float] = Field(None, ge=-180, le=180, description="경도")


class VenueResponse(VenueBase):
    """Venue 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True