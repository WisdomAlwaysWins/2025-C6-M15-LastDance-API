from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.artist import ArtistResponse

from app.schemas.exhibition import ExhibitionSummary


class ArtworkCreate(BaseModel):
    """
    작품 생성 요청

    Attributes:
        title: 작품 제목
        artist_id: 작가 ID
        description: 작품 설명 (선택)
        year: 제작 연도 (선택)
        thumbnail_url: 썸네일 이미지 URL (선택)
    """

    title: str = Field(..., description="작품 제목")
    artist_id: int = Field(..., description="작가 ID")
    description: Optional[str] = Field(None, description="작품 설명")
    year: Optional[int] = Field(None, description="제작 연도")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")


class ArtworkUpdate(BaseModel):
    """
    작품 정보 수정 요청

    Attributes:
        title: 작품 제목 (선택)
        artist_id: 작가 ID (선택)
        description: 작품 설명 (선택)
        year: 제작 연도 (선택)
        thumbnail_url: 썸네일 이미지 URL (선택)
    """

    title: Optional[str] = None
    artist_id: Optional[int] = None
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None


class ArtworkResponse(BaseModel):
    """
    작품 기본 응답 (리스트용)

    GET /artworks 리스트 조회 시 사용

    Attributes:
        id: 작품 ID
        title: 작품 제목
        artist_id: 작가 ID
        artist_name: 작가 이름
        description: 작품 설명
        year: 제작 연도
        thumbnail_url: 썸네일 URL
        reaction_count: 해당 작품의 반응 개수
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    title: str
    artist_id: int
    artist_name: str
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    reaction_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArtworkDetail(BaseModel):
    """
    작품 상세 응답 (상세 조회용)

    GET /artworks/{id} 상세 조회 시 사용

    Attributes:
        id: 작품 ID
        title: 작품 제목
        artist_id: 작가 ID
        artist: 작가 전체 정보
        description: 작품 설명
        year: 제작 연도
        thumbnail_url: 썸네일 URL
        reaction_count: 해당 작품의 반응 개수
        exhibitions: 작품이 전시된 전시 목록 (요약 정보)
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    title: str
    artist_id: int
    artist: "ArtistResponse"
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    reaction_count: int = 0
    exhibitions: List["ExhibitionSummary"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArtworkMatchRequest(BaseModel):
    """
    작품 매칭 요청 (전체 작품 대상)

    Attributes:
        image_base64: Base64 인코딩된 이미지
        threshold: 유사도 임계값 (0.0 ~ 1.0, 기본값 0.7)

    Note:
        전시 필터링 없이 전체 작품에서 매칭합니다.
    """

    image_base64: str = Field(..., description="Base64 인코딩된 이미지")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="유사도 임계값")


class ArtworkMatchResult(BaseModel):
    """
    작품 매칭 결과

    Attributes:
        artwork_id: 작품 ID
        title: 작품 제목
        artist_id: 작가 ID
        artist_name: 작가 이름
        thumbnail_url: 썸네일 URL
        similarity: 유사도 점수 (0.0 ~ 1.0)
        exhibitions: 해당 작품이 전시된 전시 목록
    """

    artwork_id: int
    title: str
    artist_id: int
    artist_name: str
    thumbnail_url: Optional[str]
    similarity: float
    exhibitions: List["ExhibitionSummary"] = []

    class Config:
        from_attributes = True


class ArtworkMatchResponse(BaseModel):
    """
    작품 매칭 응답

    Attributes:
        matched: 매칭 성공 여부
        total_matches: 전체 매칭된 작품 수
        threshold: 사용된 임계값
        results: 매칭 결과 목록 (유사도 높은 순)
    """

    matched: bool
    total_matches: int
    threshold: float
    results: List[ArtworkMatchResult]
