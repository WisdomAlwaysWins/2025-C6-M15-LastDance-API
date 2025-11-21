"""
ArtistReactionMessage Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Request Schemas
# ============================================================================


class ArtistReactionMessageCreate(BaseModel):
    """작가 메시지 생성 요청"""

    message: str = Field(..., min_length=1, description="메시지")

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        """메시지 길이 검증"""
        if not v.strip():
            raise ValueError("메시지는 공백만으로 구성될 수 없습니다")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "message": "작품에 대한 관심 감사합니다! 이 작품은 제가 2023년 여름에 완성한 작품으로..."
            }
        }


# ============================================================================
# Nested Schemas
# ============================================================================


class ArtistSimpleForMessage(BaseModel):
    """작가 간단 정보"""

    id: int = Field(..., description="작가 ID")
    uuid: str = Field(..., description="작가 UUID")
    name: str = Field(..., description="작가명")

    class Config:
        from_attributes = True


# ============================================================================
# Response Schemas
# ============================================================================


class ArtistReactionMessageResponse(BaseModel):
    """작가 메시지 응답"""

    id: int = Field(..., description="메시지 ID")
    artist_id: int = Field(..., description="작가 ID")
    artist: Optional[ArtistSimpleForMessage] = Field(None, description="작가 정보")
    reaction_id: int = Field(..., description="반응 ID")
    message: str = Field(..., description="메시지 내용")
    created_at: datetime = Field(..., description="생성일시")

    class Config:
        from_attributes = True
