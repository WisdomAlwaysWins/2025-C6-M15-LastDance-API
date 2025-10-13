from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.artist import ArtistResponse
    from app.schemas.exhibition import ExhibitionResponse
    from app.schemas.reaction import ReactionResponse


class ArtworkCreate(BaseModel):
    """작품 생성"""
    exhibition_id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None


class ArtworkUpdate(BaseModel):
    """작품 수정"""
    exhibition_id: Optional[int] = None
    artist_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None


class ArtworkResponse(BaseModel):
    """작품 응답 (기본)"""
    id: int
    exhibition_id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArtworkDetailResponse(BaseModel):
    """작품 상세 (artist, exhibition, reactions 포함)"""
    id: int
    exhibition_id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    artist: Optional["ArtistResponse"] = None
    exhibition: Optional["ExhibitionResponse"] = None
    reactions: List["ReactionResponse"] = []

    model_config = {"from_attributes": True}