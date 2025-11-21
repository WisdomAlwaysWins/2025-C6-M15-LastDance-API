"""
Invitation Schemas
"""
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime, date


# ============================================================================
# Nested Schemas
# ============================================================================

class ArtistInInvitation(BaseModel):
    """초대장 내 작가 정보"""
    id: int = Field(..., description="작가 ID")
    name: str = Field(..., description="작가명")
    bio: Optional[str] = Field(None, description="작가 소개")
    
    class Config:
        from_attributes = True


class VenueInInvitation(BaseModel):
    """초대장 내 장소 정보"""
    name: str = Field(..., description="장소명")
    address: str = Field(..., description="주소")
    geo_lat: Optional[float] = Field(None, description="위도")
    geo_lon: Optional[float] = Field(None, description="경도")
    
    class Config:
        from_attributes = True


class ExhibitionInInvitation(BaseModel):
    """초대장 내 전시 정보"""
    id: int = Field(..., description="전시 ID")
    title: str = Field(..., description="전시 제목")
    description_text: Optional[str] = Field(None, description="전시 설명")
    start_date: date = Field(..., description="시작일")
    end_date: date = Field(..., description="종료일")
    cover_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    venue: VenueInInvitation = Field(..., description="장소 정보")
    
    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================

class InvitationCreate(BaseModel):
    """초대장 생성 요청"""
    exhibition_id: int = Field(..., description="전시 ID")
    message: Optional[str] = Field(None, max_length=20, description="초대 메시지 (최대 20자)")


class InvitationInterestCreate(BaseModel):
    """초대장 관심 표현 (갈게요)"""
    invitation_id: int = Field(..., description="초대장 ID")


# ============================================================================
# Response Schemas
# ============================================================================

class InvitationResponse(BaseModel):
    """초대장 응답 (작가용)"""
    id: int = Field(..., description="초대장 ID")
    code: str = Field(..., description="초대 코드")
    artist: ArtistInInvitation = Field(..., description="작가 정보")
    exhibition: ExhibitionInInvitation = Field(..., description="전시 정보")
    message: Optional[str] = Field(None, description="초대 메시지")
    view_count: int = Field(..., description="조회수")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
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
    """초대장 공개 응답 (관객용)"""
    id: int = Field(..., description="초대장 ID")
    code: str = Field(..., description="초대 코드")
    artist: ArtistInInvitation = Field(..., description="작가 정보")
    exhibition: ExhibitionInInvitation = Field(..., description="전시 정보")
    message: Optional[str] = Field(None, description="초대 메시지")
    created_at: datetime = Field(..., description="생성일시")
    
    @computed_field
    @property
    def deep_link(self) -> str:
        """딥링크 URL 생성"""
        return f"lastdance://invitation/{self.code}"
    
    class Config:
        from_attributes = True


class InvitationInterestResponse(BaseModel):
    """초대장 관심 표현 응답"""
    id: int = Field(..., description="관심 표현 ID")
    invitation_id: int = Field(..., description="초대장 ID")
    visitor_id: Optional[int] = Field(None, description="관람객 ID")
    artist_id: Optional[int] = Field(None, description="작가 ID")
    created_at: datetime = Field(..., description="생성일시")
    
    class Config:
        from_attributes = True