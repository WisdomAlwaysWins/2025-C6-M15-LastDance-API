"""
Venue Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============================================================================
# Request Schemas
# ============================================================================


class VenueCreate(BaseModel):
    """전시 장소 생성 요청"""

    name: str = Field(..., description="장소명")
    address: str = Field(..., description="주소")
    geo_lat: Optional[float] = Field(None, description="위도")
    geo_lon: Optional[float] = Field(None, description="경도")


class VenueUpdate(BaseModel):
    """전시 장소 수정 요청"""

    name: Optional[str] = Field(None, description="장소명")
    address: Optional[str] = Field(None, description="주소")
    geo_lat: Optional[float] = Field(None, description="위도")
    geo_lon: Optional[float] = Field(None, description="경도")


# ============================================================================
# Response Schemas
# ============================================================================


class VenueResponse(BaseModel):
    """전시 장소 응답"""

    id: int = Field(..., description="장소 ID")
    name: str = Field(..., description="장소명")
    address: str = Field(..., description="주소")
    geo_lat: Optional[float] = Field(None, description="위도")
    geo_lon: Optional[float] = Field(None, description="경도")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True
