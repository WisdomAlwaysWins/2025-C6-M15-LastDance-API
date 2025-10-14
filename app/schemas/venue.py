from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VenueCreate(BaseModel):
    """
    전시 장소 생성 요청
    
    Attributes:
        name: 장소명 (예: 루미나 갤러리)
        address: 주소
        geo_lat: 위도 (선택)
        geo_lon: 경도 (선택)
    """
    name: str = Field(..., description="장소명")
    address: str = Field(..., description="주소")
    geo_lat: Optional[float] = Field(None, description="위도")
    geo_lon: Optional[float] = Field(None, description="경도")


class VenueUpdate(BaseModel):
    """
    전시 장소 수정 요청
    
    Attributes:
        name: 장소명 (선택)
        address: 주소 (선택)
        geo_lat: 위도 (선택)
        geo_lon: 경도 (선택)
    """
    name: Optional[str] = None
    address: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None


class VenueResponse(BaseModel):
    """
    전시 장소 응답
    
    Attributes:
        id: 장소 ID
        name: 장소명
        address: 주소
        geo_lat: 위도
        geo_lon: 경도
        created_at: 생성일시
        updated_at: 수정일시
    """
    id: int
    name: str
    address: str
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True