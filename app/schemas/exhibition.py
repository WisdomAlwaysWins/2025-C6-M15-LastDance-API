from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.venue import VenueResponse
    from app.schemas.artist import ArtistResponse
    from app.schemas.artwork import ArtworkResponse


class ExhibitionCreate(BaseModel):
    """전시 생성"""
    title: str
    description_text: Optional[str] = None
    start_date: date
    end_date: date
    venue_id: int
    artist_ids: List[int] = []
    cover_image_url: Optional[str] = None


class ExhibitionUpdate(BaseModel):
    """전시 수정"""
    title: Optional[str] = None
    description_text: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    venue_id: Optional[int] = None
    artist_ids: Optional[List[int]] = None
    cover_image_url: Optional[str] = None


class ExhibitionResponse(BaseModel):
    """전시 응답 (기본)"""
    id: int
    title: str
    description_text: Optional[str] = None
    start_date: date
    end_date: date
    venue_id: int
    cover_image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExhibitionDetailResponse(BaseModel):
    """전시 상세 (venue, artists, artworks 포함)"""
    id: int
    title: str
    description_text: Optional[str] = None
    start_date: date
    end_date: date
    venue_id: int
    cover_image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    venue: Optional["VenueResponse"] = None
    artists: List["ArtistResponse"] = []
    artworks: List["ArtworkResponse"] = []  # 선택

    model_config = {"from_attributes": True}