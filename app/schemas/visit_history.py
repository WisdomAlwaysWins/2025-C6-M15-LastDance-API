from pydantic import BaseModel, Field
from datetime import datetime


class VisitHistoryBase(BaseModel):
    """VisitHistory 기본 스키마"""
    user_id: int = Field(..., description="사용자 ID")
    exhibition_id: int = Field(..., description="전시 ID")


class VisitHistoryCreate(VisitHistoryBase):
    """VisitHistory 생성 요청 스키마"""
    pass


class VisitHistoryResponse(VisitHistoryBase):
    """VisitHistory 응답 스키마"""
    id: int
    visited_at: datetime

    class Config:
        from_attributes = True