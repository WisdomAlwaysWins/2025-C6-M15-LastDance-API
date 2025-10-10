from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ArtistBase(BaseModel):
    """Artist 기본 스키마"""
    name: str = Field(..., max_length=100, description="작가 이름")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[str] = Field(None, max_length=255, description="이메일")


class ArtistCreate(ArtistBase):
    """Artist 생성 요청 스키마"""
    pass


class ArtistUpdate(BaseModel):
    """Artist 수정 요청 스키마"""
    name: Optional[str] = Field(None, max_length=100, description="작가 이름")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[str] = Field(None, max_length=255, description="이메일")


class ArtistResponse(ArtistBase):
    """Artist 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True