from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Tag 기본 스키마"""
    name: str = Field(..., max_length=50, description="태그 이름")


class TagCreate(TagBase):
    """Tag 생성 요청 스키마"""
    pass


class TagResponse(TagBase):
    """Tag 응답 스키마"""
    id: int

    class Config:
        from_attributes = True