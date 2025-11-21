"""
Artist Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Request Schemas
# ============================================================================


class ArtistCreate(BaseModel):
    """작가 생성 요청"""

    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[EmailStr] = Field(None, description="이메일")


class ArtistUpdate(BaseModel):
    """작가 정보 수정 요청"""

    name: Optional[str] = Field(None, description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[EmailStr] = Field(None, description="이메일")


class ArtistLoginRequest(BaseModel):
    """작가 로그인 요청"""

    login_code: str = Field(
        ..., min_length=6, max_length=6, description="로그인 코드 (6자리)"
    )

    class Config:
        json_schema_extra = {"example": {"login_code": "aB3!x9"}}


# ============================================================================
# Response Schemas
# ============================================================================


class ArtistResponse(BaseModel):
    """작가 기본 응답 (Admin 전용 - login_code 포함)"""

    id: int = Field(..., description="작가 ID")
    uuid: str = Field(..., description="작가 UUID")
    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[str] = Field(None, description="이메일")
    login_code: Optional[str] = Field(None, description="로그인 코드 (6자리)")
    login_code_created_at: Optional[datetime] = Field(None, description="코드 생성일시")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True


class ArtistLoginResponse(BaseModel):
    """작가 로그인 응답 (uuid 포함)"""

    id: int = Field(..., description="작가 ID")
    uuid: str = Field(..., description="작가 UUID")
    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[str] = Field(None, description="이메일")

    class Config:
        from_attributes = True


class ArtistPublicResponse(BaseModel):
    """작가 공개 응답 (login_code, uuid 제외)"""

    id: int = Field(..., description="작가 ID")
    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[str] = Field(None, description="이메일")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True
