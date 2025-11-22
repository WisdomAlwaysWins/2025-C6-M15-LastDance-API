"""
Visitor Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============================================================================
# Request Schemas
# ============================================================================


class VisitorCreate(BaseModel):
    """관람객 생성 요청"""

    uuid: str = Field(..., description="iOS 생성 UUID")
    name: Optional[str] = Field(None, description="관람객 이름")


class VisitorUpdate(BaseModel):
    """관람객 정보 수정 요청"""

    name: Optional[str] = Field(None, description="관람객 이름")


# ============================================================================
# Response Schemas
# ============================================================================


class VisitorResponse(BaseModel):
    """관람객 기본 응답"""

    id: int = Field(..., description="관람객 ID")
    uuid: str = Field(..., description="관람객 UUID")
    name: Optional[str] = Field(None, description="관람객 이름")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")

    class Config:
        from_attributes = True
