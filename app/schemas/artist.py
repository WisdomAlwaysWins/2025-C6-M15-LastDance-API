from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ArtistCreate(BaseModel):
    """
    작가 생성 요청

    Attributes:
        name: 작가명
        bio: 작가 소개 (선택)
        email: 이메일 (선택)

    Note:
        uuid는 서버에서 자동 생성
    """

    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    email: Optional[EmailStr] = Field(None, description="이메일")


class ArtistUpdate(BaseModel):
    """
    작가 정보 수정 요청

    Attributes:
        name: 작가명 (선택)
        bio: 작가 소개 (선택)
        email: 이메일 (선택)
    """

    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None


class ArtistResponse(BaseModel):
    """
    작가 기본 응답

    Attributes:
        id: 작가 ID (Integer)
        uuid: 작가 UUID (String)
        name: 작가명
        bio: 작가 소개
        email: 이메일
        login_code: 로그인 코드 (6자리) ✨ NEW
        login_code_created_at: 코드 생성일시 ✨ NEW
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    uuid: str
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None 
    login_code: Optional[str] = None
    login_code_created_at: Optional[datetime] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArtistLoginRequest(BaseModel):
    """
    작가 로그인 요청

    Attributes:
        login_code: 6자리 로그인 코드
    """
    login_code: str = Field(..., min_length=6, max_length=6, description="로그인 코드")

    class Config:
        json_schema_extra = {
            "example": {
                "login_code": "aB3!x9"
            }
        }


class ArtistLoginResponse(BaseModel):
    """
    작가 로그인 응답

    Attributes:
        id: 작가 ID
        uuid: 작가 UUID
        name: 작가명
        bio: 작가 소개
        email: 이메일
    """
    id: int
    uuid: str
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ArtistPublicResponse(BaseModel):
    """
    작가 공개 응답 (login_code 제외)
    
    Attributes:
        id: 작가 ID
        uuid: 작가 UUID
        name: 작가명
        bio: 작가 소개
        email: 이메일
        created_at: 생성일시
        updated_at: 수정일시
    """
    id: int
    uuid: str
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True