from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.exhibition import ExhibitionSummary


class VisitHistoryCreate(BaseModel):
    """
    전시 방문 기록 생성 요청

    Attributes:
        visitor_id: 관람객 ID
        exhibition_id: 전시 ID

    Note:
        visited_at은 서버에서 자동 생성 (현재 시각)
    """
    visitor_id: int = Field(..., description="관람객 ID")
    exhibition_id: int = Field(..., description="전시 ID")


class VisitHistoryResponse(BaseModel):
    """
    방문 기록 기본 응답 (리스트용)
    
    GET /visit-histories 리스트 조회 시 사용

    Attributes:
        id: 방문 기록 ID
        visitor_id: 관람객 ID
        visitor_name: 관람객 이름
        exhibition_id: 전시 ID
        exhibition_title: 전시 제목
        visited_at: 방문 일시
        reaction_count: 해당 방문에서 작성한 반응 개수
    """
    id: int
    visitor_id: int
    visitor_name: Optional[str] = None
    exhibition_id: int
    exhibition_title: str
    visited_at: datetime
    reaction_count: int = 0

    class Config:
        from_attributes = True


class VisitHistorySummary(BaseModel):
    """
    방문 기록 요약 정보 (순환 참조 방지용)
    
    Reaction에서 사용

    Attributes:
        id: 방문 기록 ID
        exhibition_id: 전시 ID
        exhibition_title: 전시 제목
        visited_at: 방문 일시
    """
    id: int
    exhibition_id: int
    exhibition_title: str
    visited_at: datetime

    class Config:
        from_attributes = True


class VisitHistoryDetail(BaseModel):
    """
    방문 기록 상세 응답 (상세 조회용)
    
    GET /visit-histories/{id} 상세 조회 시 사용

    Attributes:
        id: 방문 기록 ID
        visitor_id: 관람객 ID
        visitor_name: 관람객 이름
        exhibition_id: 전시 ID
        exhibition: 전시 요약 정보
        visited_at: 방문 일시
        reactions: 해당 방문에서 작성한 반응 목록 (요약 정보)
    """
    id: int
    visitor_id: int
    visitor_name: Optional[str] = None
    exhibition_id: int
    exhibition: "ExhibitionSummary"
    visited_at: datetime
    reactions: List["ReactionSummary"] = []

    class Config:
        from_attributes = True