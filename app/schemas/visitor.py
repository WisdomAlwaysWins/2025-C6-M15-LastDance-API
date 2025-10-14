from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VisitorCreate(BaseModel):
    """
    관람객 생성 요청
    
    Attributes:
        uuid: iOS에서 생성한 UUID (디바이스 식별용)
        name: 관람객 이름 (선택)
    """
    uuid: str = Field(..., description="iOS 생성 UUID")
    name: Optional[str] = Field(None, description="관람객 이름")


class VisitorUpdate(BaseModel):
    """
    관람객 정보 수정 요청
    
    Attributes:
        name: 관람객 이름
    """
    name: Optional[str] = None


class VisitorResponse(BaseModel):
    """
    관람객 기본 응답
    
    Attributes:
        id: 관람객 ID (Integer)
        uuid: 관람객 UUID (String)
        name: 관람객 이름
        created_at: 생성일시
        updated_at: 수정일시
    """
    id: int
    uuid: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True