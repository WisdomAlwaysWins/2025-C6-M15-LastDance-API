from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ExhibitionBase(BaseModel):
    """Exhibition 기본 스키마"""
    title: str = Field(..., max_length=255, description="전시 제목")
    description: Optional[str] = Field(None, description="전시 설명")
    location: Optional[str] = Field(None, max_length=255, description="전시 장소")
    poster_url: Optional[str] = Field(None, max_length=500, description="전시 포스터 URL")
    artist_names: Optional[List[str]] = Field(None, description="참여 작가 리스트")
    start_date: date = Field(..., description="전시 시작일")
    end_date: date = Field(..., description="전시 종료일")


class ExhibitionCreate(ExhibitionBase):
    """Exhibition 생성 요청 스키마"""
    pass


class ExhibitionUpdate(BaseModel):
    """Exhibition 수정 요청 스키마"""
    title: Optional[str] = Field(None, max_length=255, description="전시 제목")
    description: Optional[str] = Field(None, description="전시 설명")
    location: Optional[str] = Field(None, max_length=255, description="전시 장소")
    poster_url: Optional[str] = Field(None, max_length=500, description="전시 포스터 URL")
    artist_names: Optional[List[str]] = Field(None, description="참여 작가 리스트")
    start_date: Optional[date] = Field(None, description="전시 시작일")
    end_date: Optional[date] = Field(None, description="전시 종료일")


class ExhibitionResponse(ExhibitionBase):
    """Exhibition 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True