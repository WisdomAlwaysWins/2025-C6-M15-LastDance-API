"""
ArtistReactionMessage Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ArtistReactionMessageCreate(BaseModel):
    """
    작가 메시지 생성 요청
    
    Attributes:
        message: 메시지 (10자 이내)
    """
    message: str = Field(..., min_length=1, max_length=10, description="메시지 (10자 이내)")
    
    @field_validator('message')
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        """메시지 길이 검증"""
        if len(v) > 10:
            raise ValueError('메시지는 10자 이내여야 합니다')
        if not v.strip():
            raise ValueError('메시지는 공백만으로 구성될 수 없습니다')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "감사합니다!"
            }
        }


class ArtistSimpleForMessage(BaseModel):
    """작가 간단 정보"""
    id: int
    uuid: str
    name: str
    
    class Config:
        from_attributes = True


class ArtistReactionMessageResponse(BaseModel):
    """
    작가 메시지 응답
    
    Attributes:
        id: 메시지 ID
        artist_id: 작가 ID
        artist: 작가 정보 (선택)
        reaction_id: 반응 ID
        message: 메시지 내용
        created_at: 생성일시
    """
    id: int
    artist_id: int
    artist: Optional[ArtistSimpleForMessage] = None
    reaction_id: int
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True