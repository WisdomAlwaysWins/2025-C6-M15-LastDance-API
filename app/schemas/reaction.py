"""
Reaction Schemas
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.tag import TagResponse

if TYPE_CHECKING:
    from app.schemas.artwork import ArtworkResponse
    from app.schemas.visit_history import VisitHistorySummary
    from app.schemas.visitor import VisitorResponse


# ============================================================================
# Nested Schemas
# ============================================================================


class ReactionSummary(BaseModel):
    """반응 요약 정보"""

    id: int = Field(..., description="반응 ID")
    artwork_id: int = Field(..., description="작품 ID")
    artwork_title: str = Field(..., description="작품 제목")
    comment: Optional[str] = Field(None, description="코멘트")
    created_at: datetime = Field(..., description="생성일시")

    class Config:
        from_attributes = True


class ArtistReactionEmojiInReaction(BaseModel):
    """반응에 포함되는 작가 이모지 정보"""

    id: int = Field(..., description="이모지 ID")
    artist_id: int = Field(..., description="작가 ID")
    artist_name: str = Field(..., description="작가명")
    emoji_type: str = Field(..., description="이모지 타입")
    created_at: datetime = Field(..., description="생성일시")

    class Config:
        from_attributes = True


class ArtistReactionMessageInReaction(BaseModel):
    """반응에 포함되는 작가 메시지 정보"""

    id: int = Field(..., description="메시지 ID")
    artist_id: int = Field(..., description="작가 ID")
    artist_name: str = Field(..., description="작가명")
    message: str = Field(..., description="메시지 내용")
    created_at: datetime = Field(..., description="생성일시")

    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================


class ReactionBase(BaseModel):
    """작품 반응 기본 속성"""

    artwork_id: int = Field(..., description="작품 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    visit_id: Optional[int] = Field(None, description="방문 기록 ID")
    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")


class ReactionCreate(BaseModel):
    """작품 반응 생성 요청"""

    artwork_id: int = Field(..., description="작품 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    visit_id: Optional[int] = Field(None, description="방문 기록 ID")
    comment: str = Field(..., description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")
    tag_ids: Optional[List[int]] = Field(None, description="태그 ID 목록")


class ReactionUpdate(BaseModel):
    """작품 반응 수정 요청"""

    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")
    tag_ids: Optional[List[int]] = Field(None, description="태그 ID 목록")

    @validator("tag_ids")
    def validate_reaction_content(cls, tag_ids, values):
        """comment 또는 tag_ids 중 하나는 필수"""
        comment = values.get("comment")
        if comment is None and not tag_ids:
            raise ValueError("comment 또는 tag_ids 중 하나는 필수입니다")
        return tag_ids


# ============================================================================
# Response Schemas
# ============================================================================


class ReactionResponse(BaseModel):
    """작품 반응 기본 응답 (리스트용)"""

    id: int = Field(..., description="반응 ID")
    artwork_id: int = Field(..., description="작품 ID")
    artwork_title: str = Field(..., description="작품 제목")
    visitor_id: int = Field(..., description="관람객 ID")
    visitor_name: Optional[str] = Field(None, description="관람객 이름")
    visit_id: Optional[int] = Field(None, description="방문 기록 ID")
    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")
    tags: List[TagResponse] = Field([], description="태그 목록")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True


class ReactionDetail(BaseModel):
    """작품 반응 상세 응답 (상세 조회용)"""

    id: int = Field(..., description="반응 ID")
    artwork_id: int = Field(..., description="작품 ID")
    artwork: "ArtworkResponse" = Field(..., description="작품 정보")
    visitor_id: int = Field(..., description="관람객 ID")
    visitor: "VisitorResponse" = Field(..., description="관람객 정보")
    visit_id: Optional[int] = Field(None, description="방문 기록 ID")
    visit: Optional["VisitHistorySummary"] = Field(None, description="방문 기록 정보")
    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")
    tags: List[TagResponse] = Field([], description="태그 목록")
    artist_emojis: List[ArtistReactionEmojiInReaction] = Field(
        [], description="작가 이모지 목록"
    )
    artist_messages: List[ArtistReactionMessageInReaction] = Field(
        [], description="작가 메시지 목록"
    )
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True
