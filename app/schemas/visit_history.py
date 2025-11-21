"""
Visit History Schemas
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.exhibition import ExhibitionSummary

from app.schemas.reaction import ReactionSummary

# ============================================================================
# Nested Schemas
# ============================================================================


class VisitHistorySummary(BaseModel):
    """방문 기록 요약 정보"""

    id: int = Field(..., description="방문 기록 ID")
    exhibition_id: int = Field(..., description="전시 ID")
    exhibition_title: str = Field(..., description="전시 제목")
    visited_at: datetime = Field(..., description="방문 일시")

    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================


class VisitHistoryCreate(BaseModel):
    """전시 방문 기록 생성 요청"""

    visitor_id: int = Field(..., description="관람객 ID")
    exhibition_id: int = Field(..., description="전시 ID")


# ============================================================================
# Response Schemas
# ============================================================================


class VisitHistoryResponse(BaseModel):
    """방문 기록 기본 응답 (리스트용)"""

    id: int = Field(..., description="방문 기록 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    visitor_name: Optional[str] = Field(None, description="관람객 이름")
    exhibition_id: int = Field(..., description="전시 ID")
    exhibition_title: str = Field(..., description="전시 제목")
    visited_at: datetime = Field(..., description="방문 일시")
    reaction_count: int = Field(0, description="반응 개수")

    class Config:
        from_attributes = True


class VisitHistoryDetail(BaseModel):
    """방문 기록 상세 응답 (상세 조회용)"""

    id: int = Field(..., description="방문 기록 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    visitor_name: Optional[str] = Field(None, description="관람객 이름")
    exhibition_id: int = Field(..., description="전시 ID")
    exhibition: "ExhibitionSummary" = Field(..., description="전시 정보")
    visited_at: datetime = Field(..., description="방문 일시")
    reactions: List["ReactionSummary"] = Field([], description="반응 목록")

    class Config:
        from_attributes = True
