"""
ArtistReactionEmoji Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants.emojis import ALLOWED_EMOJI_TYPES

# ============================================================================
# Request Schemas
# ============================================================================


class ArtistReactionEmojiCreate(BaseModel):
    """작가 이모지 생성 요청"""

    emoji_type: str = Field(..., description="이모지 타입")

    class Config:
        json_schema_extra = {"example": {"emoji_type": "emoji_like"}}


# ============================================================================
# Nested Schemas
# ============================================================================


class ArtistSimple(BaseModel):
    """작가 간단 정보"""

    id: int = Field(..., description="작가 ID")
    name: str = Field(..., description="작가명")

    class Config:
        from_attributes = True


# ============================================================================
# Response Schemas
# ============================================================================


class ArtistReactionEmojiResponse(BaseModel):
    """작가 이모지 응답"""

    id: int = Field(..., description="이모지 ID")
    artist_id: int = Field(..., description="작가 ID")
    artist: Optional[ArtistSimple] = Field(None, description="작가 정보")
    reaction_id: int = Field(..., description="반응 ID")
    emoji_type: str = Field(..., description="이모지 타입")
    created_at: datetime = Field(..., description="생성일시")

    class Config:
        from_attributes = True
