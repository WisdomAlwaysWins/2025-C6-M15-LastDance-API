from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VisitorCreate(BaseModel):
    """관람객 생성"""
    uuid: str
    name: Optional[str] = None


class VisitorUpdate(BaseModel):
    """관람객 수정"""
    name: Optional[str] = None


class VisitorResponse(BaseModel):
    """관람객 응답"""
    id: int
    uuid: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}