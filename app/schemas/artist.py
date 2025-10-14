from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

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