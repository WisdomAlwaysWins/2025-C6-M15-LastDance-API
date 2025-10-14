from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.venue import VenueResponse
    from app.schemas.artwork import ArtworkResponse

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
    전시 기본 응답
    
    Attributes:
        id: 전시 ID
        title: 전시 제목
        description_text: 전시 설명
        start_date: 시작일
        end_date: 종료일
        venue_id: 전시 장소 ID
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
    cover_image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExhibitionDetail(ExhibitionResponse):
    """
    전시 상세 응답 (장소, 작품 목록 포함)
    
    Attributes:
        venue: 전시 장소 정보
        artworks: 전시 작품 목록
    """
    venue: 'VenueResponse'  
    artworks: List['ArtworkResponse'] = []  

    class Config:
        from_attributes = True