from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.visitor import VisitorResponse
    from app.schemas.exhibition import ExhibitionResponse
    from app.schemas.reaction import ReactionResponse

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
    방문 기록 기본 응답
    
    Attributes:
        id: 방문 기록 ID
        visitor_id: 관람객 ID
        exhibition_id: 전시 ID
        visited_at: 방문 일시
    """
    id: int
    visitor_id: int
    exhibition_id: int
    visited_at: datetime

    class Config:
        from_attributes = True


class VisitHistoryDetail(VisitHistoryResponse):
    """
    방문 기록 상세 응답 (관람객, 전시 정보 포함)
    
    Attributes:
        visitor: 관람객 정보
        exhibition: 전시 정보
        reactions: 해당 방문에서 작성한 반응 목록
    """
    visitor: 'VisitorResponse'  
    exhibition: 'ExhibitionResponse'  
    reactions: List['ReactionResponse'] = []  

    class Config:
        from_attributes = True