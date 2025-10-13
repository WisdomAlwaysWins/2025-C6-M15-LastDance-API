from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.tag import TagResponse
    from app.schemas.visitor import VisitorResponse
    from app.schemas.artwork import ArtworkResponse
    from app.schemas.visit_history import VisitHistoryResponse


class ReactionCreate(BaseModel):
    """리액션 생성"""
    artwork_id: int
    visitor_id: int
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    tag_ids: Optional[List[int]] = None

    @model_validator(mode='after')
    def check_tags_or_comment(self):
        """tag_ids 또는 comment 중 최소 하나 필수"""
        if not self.tag_ids and not self.comment:
            raise ValueError('Either tag_ids or comment must be provided')
        return self


class ReactionUpdate(BaseModel):
    """리액션 수정"""
    comment: Optional[str] = None
    tag_ids: Optional[List[int]] = None

    @model_validator(mode='after')
    def check_tags_or_comment(self):
        """tag_ids 또는 comment 중 최소 하나 필수"""
        if not self.tag_ids and not self.comment:
            raise ValueError('Either tag_ids or comment must be provided')
        return self


class ReactionResponse(BaseModel):
    """리액션 응답 (기본)"""
    id: int
    artwork_id: int
    visitor_id: int
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReactionDetailResponse(BaseModel):
    """리액션 상세 (visitor, artwork, visit, tags 포함)"""
    id: int
    artwork_id: int
    visitor_id: int
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    visitor: Optional["VisitorResponse"] = None
    artwork: Optional["ArtworkResponse"] = None
    visit: Optional["VisitHistoryResponse"] = None
    tags: List["TagResponse"] = []

    model_config = {"from_attributes": True}