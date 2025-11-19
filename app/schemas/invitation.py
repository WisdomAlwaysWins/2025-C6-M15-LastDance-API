"""
Invitation Schemas

초대장 Request/Response 스키마
"""
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime, date


# ============================================================================
# Nested Schemas
# ============================================================================

class ArtistInInvitation(BaseModel):
    """초대장 내 작가 정보"""
    id: int
    name: str
    bio: Optional[str]
    
    class Config:
        from_attributes = True


class VenueInInvitation(BaseModel):
    """초대장 내 장소 정보"""
    name: str
    address: str
    geo_lat: Optional[float]
    geo_lon: Optional[float]
    
    class Config:
        from_attributes = True


class ExhibitionInInvitation(BaseModel):
    """초대장 내 전시 정보"""
    id: int
    title: str
    description_text: Optional[str]
    start_date: date
    end_date: date
    cover_image_url: Optional[str]
    venue: VenueInInvitation
    
    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================

class InvitationCreate(BaseModel):
    """
    초대장 생성 요청
    
    Attributes:
        exhibition_id: 전시 ID
        message: 초대 메시지 (최대 20자)
    """
    exhibition_id: int
    message: Optional[str] = Field(None, max_length=20, description="초대 메시지 (최대 20자)")


class InvitationInterestCreate(BaseModel):
    """
    초대장 관심 표현 (갈게요)
    
    Attributes:
        invitation_id: 초대장 ID
    """
    invitation_id: int


# ============================================================================
# Response Schemas
# ============================================================================

class InvitationResponse(BaseModel):
    """
    초대장 응답 (작가용)
    
    작가가 자신의 초대장 목록 조회 시 사용
    view_count, 링크 정보 포함
    """
    id: int
    code: str
    artist: ArtistInInvitation
    exhibition: ExhibitionInInvitation
    message: Optional[str]
    view_count: int  # 실제 방문자 수
    created_at: datetime
    updated_at: Optional[datetime]
    
    @computed_field
    @property
    def deep_link(self) -> str:
        """딥링크 URL 생성"""
        return f"lastdance://invitation/{self.code}"
    
    @computed_field
    @property
    def app_store_link(self) -> str:
        """앱스토어 링크"""
        return "https://apps.apple.com/kr/app/%EC%97%AC%EC%9A%B4/id6754415794"
    
    class Config:
        from_attributes = True


class InvitationPublicResponse(BaseModel):
    """
    초대장 공개 응답 (관객용)
    
    관객이 초대장 코드로 조회 시 사용
    view_count 제외 (보안)
    """
    id: int
    code: str
    artist: ArtistInInvitation
    exhibition: ExhibitionInInvitation
    message: Optional[str]
    created_at: datetime
    
    @computed_field
    @property
    def deep_link(self) -> str:
        """딥링크 URL 생성"""
        return f"lastdance://invitation/{self.code}"
    
    class Config:
        from_attributes = True


class InvitationInterestResponse(BaseModel):
    """
    초대장 관심 표현 응답
    
    "갈게요" 클릭 시 응답
    visitor_id 또는 artist_id 중 하나만 존재
    """
    id: int
    invitation_id: int
    visitor_id: Optional[int] = None
    artist_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True