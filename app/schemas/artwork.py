from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.artist import ArtistResponse
    from app.schemas.exhibition import ExhibitionResponse

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
    작품 기본 응답
    
    Attributes:
        id: 작품 ID
        title: 작품 제목
        artist_id: 작가 ID
        description: 작품 설명
        year: 제작 연도
        thumbnail_url: 썸네일 URL
        created_at: 생성일시
        updated_at: 수정일시
    """
    id: int
    title: str
    artist_id: int
    description: Optional[str] = None
    year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArtworkDetail(ArtworkResponse):
    """
    작품 상세 응답 (작가, 전시 정보 포함)
    
    Attributes:
        artist: 작가 정보
        exhibitions: 작품이 전시된 전시 목록
    """
    artist: 'ArtistResponse'  
    exhibitions: List['ExhibitionResponse'] = []  

    class Config:
        from_attributes = True


class ArtworkMatchRequest(BaseModel):
    """작품 매칭 요청"""
    image_base64: str = Field(..., description="Base64 인코딩된 이미지")
    exhibition_id: int = Field(..., description="전시 ID")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="유사도 임계값")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "iVBORw0KGgoAAAANS...",
                "exhibition_id": 1,
                "threshold": 0.7
            }
        }


class ArtworkMatchResult(BaseModel):
    """작품 매칭 결과"""
    artwork_id: int
    title: str
    artist_id: int
    thumbnail_url: Optional[str]
    similarity: float


class ArtworkMatchResponse(BaseModel):
    """작품 매칭 응답"""
    matched: bool
    total_matches: int
    threshold: float
    results: List[ArtworkMatchResult]