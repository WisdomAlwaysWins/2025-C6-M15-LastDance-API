"""
Exhibition Schemas
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.venue import VenueResponse


# ============================================================================
# Nested Schemas
# ============================================================================


class ArtworkSummary(BaseModel):
    """작품 요약 정보"""

    id: int = Field(..., description="작품 ID")
    title: str = Field(..., description="작품 제목")
    artist_name: str = Field(..., description="작가 이름")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")

    class Config:
        from_attributes = True


class ArtistSummary(BaseModel):
    """작가 요약 정보"""

    id: int = Field(..., description="작가 ID")
    name: str = Field(..., description="작가명")

    class Config:
        from_attributes = True


class ExhibitionSummary(BaseModel):
    """전시 요약 정보"""

    id: int = Field(..., description="전시 ID")
    title: str = Field(..., description="전시 제목")
    venue_name: str = Field(..., description="전시 장소 이름")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")

    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================


class ExhibitionCreate(BaseModel):
    """전시 생성 요청"""

    title: str = Field(..., description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    venue_id: int = Field(..., description="전시 장소 ID")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    artwork_ids: Optional[List[int]] = Field(None, description="전시 작품 ID 목록")


class ExhibitionUpdate(BaseModel):
    """전시 정보 수정 요청"""

    title: Optional[str] = Field(None, description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: Optional[date] = Field(None, description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    venue_id: Optional[int] = Field(None, description="전시 장소 ID")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    artwork_ids: Optional[List[int]] = Field(None, description="전시 작품 ID 목록")


# ============================================================================
# Response Schemas
# ============================================================================


class ExhibitionResponse(BaseModel):
    """전시 기본 응답 (리스트용)"""

    id: int = Field(..., description="전시 ID")
    title: str = Field(..., description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    venue_id: int = Field(..., description="전시 장소 ID")
    venue_name: str = Field(..., description="전시 장소 이름")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    artists: List["ArtistSummary"] = Field([], description="참여 작가 목록")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True


class ExhibitionDetail(BaseModel):
    """전시 상세 응답 (상세 조회용)"""

    id: int = Field(..., description="전시 ID")
    title: str = Field(..., description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    venue_id: int = Field(..., description="전시 장소 ID")
    venue: "VenueResponse" = Field(..., description="전시 장소 정보")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    artworks: List["ArtworkSummary"] = Field([], description="전시 작품 목록")
    artists: List["ArtistSummary"] = Field([], description="참여 작가 목록")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True
