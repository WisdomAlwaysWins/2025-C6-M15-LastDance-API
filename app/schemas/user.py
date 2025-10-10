from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """User 기본 스키마 (관람객 전용)"""
    uuid: str = Field(..., description="사용자 UUID (iOS 생성)")
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")


class UserCreate(UserBase):
    """User 생성 요청 스키마"""
    pass


class UserUpdate(BaseModel):
    """User 수정 요청 스키마"""
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")


class UserResponse(UserBase):
    """User 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True