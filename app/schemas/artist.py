from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ArtistCreate(BaseModel):
    """작가 생성"""
    uuid: Optional[str] = None
    name: str  # 필수
    bio: Optional[str] = None
    email: Optional[str] = None


class ArtistUpdate(BaseModel):
    """작가 수정"""
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None


class ArtistResponse(BaseModel):
    """작가 응답"""
    id: int
    uuid: str  # 🆕 추가
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}