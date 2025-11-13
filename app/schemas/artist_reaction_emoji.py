"""
ArtistReactionEmoji Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants.emojis import ALLOWED_EMOJI_TYPES


class ArtistReactionEmojiCreate(BaseModel):
    """
    작가 이모지 생성 요청
    
    Attributes:
        emoji_type: 이모지 타입 (emoji_1 ~ emoji_5)
    """
    emoji_type: str = Field(..., description="이모지 타입")
    
    class Config:
        json_schema_extra = {
            "example": {
                "emoji_type": "emoji_1"
            }
        }


class ArtistSimple(BaseModel):
    """작가 간단 정보"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class ArtistReactionEmojiResponse(BaseModel):
    """
    작가 이모지 응답
    
    Attributes:
        id: 이모지 ID
        artist_id: 작가 ID
        artist: 작가 정보
        reaction_id: 반응 ID
        emoji_type: 이모지 타입
        created_at: 생성일시
    """
    id: int
    artist_id: int
    artist: Optional[ArtistSimple] = None
    reaction_id: int
    emoji_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True