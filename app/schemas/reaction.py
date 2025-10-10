from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ReactionBase(BaseModel):
    """Reaction 기본 스키마"""
    artwork_id: int = Field(..., description="작품 ID")
    user_id: int = Field(..., description="사용자 ID")
    visit_id: Optional[int] = Field(None, description="방문 ID")
    photo_url: Optional[str] = Field(None, max_length=500, description="사용자가 찍은 사진 URL")
    comment: Optional[str] = Field(None, description="텍스트 코멘트")


class ReactionCreate(ReactionBase):
    """Reaction 생성 요청 스키마"""
    tag_ids: List[int] = Field(default=[], description="태그 ID 리스트")
    
    @validator('tag_ids', always=True)
    def validate_reaction_content(cls, tag_ids, values):
        """태그 또는 댓글 중 최소 1개 필수"""
        comment = values.get('comment')
        
        if not comment and not tag_ids:
            raise ValueError('태그 또는 댓글 중 최소 하나는 필수입니다')
        
        return tag_ids


class ReactionUpdate(BaseModel):
    """Reaction 수정 요청 스키마"""
    photo_url: Optional[str] = Field(None, max_length=500, description="사용자가 찍은 사진 URL")
    comment: Optional[str] = Field(None, description="텍스트 코멘트")
    tag_ids: Optional[List[int]] = Field(None, description="태그 ID 리스트")


class ReactionResponse(ReactionBase):
    """Reaction 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 중첩 객체 포함 버전 (선택적 사용)
class ReactionDetailResponse(ReactionResponse):
    """Reaction 상세 응답 (tags 포함)"""
    from app.schemas.tag import TagResponse
    
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


# 레거시 호환용 (기존 ReviewResponse와 호환)
class ReviewResponse(ReactionResponse):
    """Review 응답 스키마 (레거시 호환용)"""
    pass