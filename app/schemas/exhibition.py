from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.venue import VenueResponse


class ArtworkSummary(BaseModel):
    """
    작품 요약 정보 (순환 참조 방지용)

    Exhibition에서 사용

    Attributes:
        id: 작품 ID
        title: 작품 제목
        artist_name: 작가 이름
        year: 제작 연도
        thumbnail_url: 썸네일 URL
    """

    id: int
    title: str
    artist_name: str
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


class ArtistSummary(BaseModel):
    """작가 요약 정보 (Exhibition에서 사용)"""

    id: int
    name: str

    class Config:
        from_attributes = True


class ExhibitionCreate(BaseModel):
    """
    전시 생성 요청

    Attributes:
        title: 전시 제목
        description_text: 전시 설명
        start_date: 시작일
        end_date: 종료일
        venue_id: 전시 장소 ID
        cover_image_url: 포스터 이미지 URL (선택)
        artwork_ids: 전시할 작품 ID 목록 (선택)
    """

    title: str = Field(..., description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    venue_id: int = Field(..., description="전시 장소 ID")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    artwork_ids: Optional[List[int]] = Field(None, description="전시 작품 ID 목록")


class ExhibitionUpdate(BaseModel):
    """
    전시 정보 수정 요청

    Attributes:
        title: 전시 제목 (선택)
        description_text: 전시 설명 (선택)
        start_date: 시작일 (선택)
        end_date: 종료일 (선택)
        venue_id: 전시 장소 ID (선택)
        cover_image_url: 포스터 이미지 URL (선택)
        artwork_ids: 전시 작품 ID 목록 (선택)
    """

    title: Optional[str] = None
    description_text: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    venue_id: Optional[int] = None
    cover_image_url: Optional[str] = None
    artwork_ids: Optional[List[int]] = None


class ExhibitionResponse(BaseModel):
    """
    전시 기본 응답 (리스트용)

    GET /exhibitions 리스트 조회 시 사용

    Attributes:
        id: 전시 ID
        title: 전시 제목
        description_text: 전시 설명
        start_date: 시작일
        end_date: 종료일
        venue_id: 전시 장소 ID
        venue_name: 전시 장소 이름
        cover_image_url: 포스터 이미지 URL
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    title: str
    description_text: Optional[str] = None
    start_date: date
    end_date: date
    venue_id: int
    venue_name: str
    cover_image_url: Optional[str] = None
    artists: List["ArtistSummary"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExhibitionSummary(BaseModel):
    """
    전시 요약 정보 (순환 참조 방지용)

    다른 스키마에서 사용 (Artwork, VisitHistory 등)

    Attributes:
        id: 전시 ID
        title: 전시 제목
        venue_name: 전시 장소 이름
        start_date: 시작일
        end_date: 종료일
        cover_image_url: 포스터 이미지 URL
    """

    id: int
    title: str
    venue_name: str
    start_date: date
    end_date: date
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ExhibitionDetail(BaseModel):
    """
    전시 상세 응답 (상세 조회용)

    GET /exhibitions/{id} 상세 조회 시 사용

    Attributes:
        id: 전시 ID
        title: 전시 제목
        description_text: 전시 설명
        start_date: 시작일
        end_date: 종료일
        venue_id: 전시 장소 ID
        venue: 전시 장소 전체 정보
        cover_image_url: 포스터 이미지 URL
        artworks: 전시 작품 목록 (요약 정보)
        artists: 참여 작가 목록 (요약 정보)
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    title: str
    description_text: Optional[str] = None
    start_date: date
    end_date: date
    venue_id: int
    venue: "VenueResponse"
    cover_image_url: Optional[str] = None
    artworks: List["ArtworkSummary"] = []
    artists: List["ArtistSummary"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
