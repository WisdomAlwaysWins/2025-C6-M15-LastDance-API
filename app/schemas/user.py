from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserType


class UserBase(BaseModel):
    """User 기본 스키마"""
    uuid: str = Field(..., description="사용자 UUID")
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    email: Optional[EmailStr] = Field(None, description="이메일")
    user_type: UserType = Field(default=UserType.VISITOR, description="사용자 타입")


class UserCreate(BaseModel):
    """User 생성 요청 스키마"""
    uuid: str = Field(..., description="사용자 UUID")
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    email: Optional[EmailStr] = Field(None, description="이메일")
    user_type: UserType = Field(default=UserType.VISITOR, description="사용자 타입")


class UserUpdate(BaseModel):
    """User 수정 요청 스키마"""
    name: Optional[str] = Field(None, max_length=100, description="사용자 이름")
    email: Optional[EmailStr] = Field(None, description="이메일")


class UserResponse(UserBase):
    """User 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2에서 orm_mode 대신 사용