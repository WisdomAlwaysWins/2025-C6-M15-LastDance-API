"""
Artwork Schemas
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.artist import ArtistResponse

from app.schemas.exhibition import ExhibitionSummary

# ============================================================================
# Request Schemas
# ============================================================================


class ArtworkCreate(BaseModel):
    """작품 생성 요청"""

    title: str = Field(..., description="작품 제목")
    artist_id: int = Field(..., description="작가 ID")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")


class ArtworkUpdate(BaseModel):
    """작품 정보 수정 요청"""

    title: Optional[str] = Field(None, description="작품 제목")
    artist_id: Optional[int] = Field(None, description="작가 ID")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")


class ArtworkMatchRequest(BaseModel):
    """작품 매칭 요청 (전체 작품 대상)"""

    image_base64: str = Field(..., description="Base64 인코딩된 이미지")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="유사도 임계값")


# ============================================================================
# Response Schemas
# ============================================================================


class ArtworkResponse(BaseModel):
    """작품 기본 응답 (리스트용)"""

    id: int = Field(..., description="작품 ID")
    title: str = Field(..., description="작품 제목")
    artist_id: int = Field(..., description="작가 ID")
    artist_name: str = Field(..., description="작가 이름")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    reaction_count: int = Field(0, description="반응 개수")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True


class ArtworkDetail(BaseModel):
    """작품 상세 응답 (상세 조회용)"""

    id: int = Field(..., description="작품 ID")
    title: str = Field(..., description="작품 제목")
    artist_id: int = Field(..., description="작가 ID")
    artist: "ArtistResponse" = Field(..., description="작가 정보")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    reaction_count: int = Field(0, description="반응 개수")
    exhibitions: List["ExhibitionSummary"] = Field([], description="전시 목록")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True


class ArtworkMatchResult(BaseModel):
    """작품 매칭 결과"""

    artwork_id: int = Field(..., description="작품 ID")
    title: str = Field(..., description="작품 제목")
    artist_id: int = Field(..., description="작가 ID")
    artist_name: str = Field(..., description="작가 이름")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    similarity: float = Field(..., description="유사도 점수")
    exhibitions: List["ExhibitionSummary"] = Field([], description="전시 목록")

    class Config:
        from_attributes = True


class ArtworkMatchResponse(BaseModel):
    """작품 매칭 응답"""

    matched: bool = Field(..., description="매칭 성공 여부")
    total_matches: int = Field(..., description="전체 매칭 개수")
    threshold: float = Field(..., description="사용된 임계값")
    results: List[ArtworkMatchResult] = Field(..., description="매칭 결과 목록")
