"""
Tag Schemas
"""
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.tag_category import TagCategoryBase


# ============================================================================
# Request Schemas
# ============================================================================

class TagCreate(BaseModel):
    """태그 생성 요청"""
    name: str = Field(..., description="태그명")
    category_id: int = Field(..., description="카테고리 ID")
    color_hex: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드 (#RRGGBB)"
    )


class TagUpdate(BaseModel):
    """태그 수정 요청"""
    name: Optional[str] = Field(None, description="태그명")
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    color_hex: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드 (#RRGGBB)")


# ============================================================================
# Response Schemas
# ============================================================================

class TagResponse(BaseModel):
    """태그 기본 응답"""
    id: int = Field(..., description="태그 ID")
    name: str = Field(..., description="태그명")
    category: TagCategoryBase = Field(..., description="카테고리 정보")
    color_hex: Optional[str] = Field(None, description="색상 코드 (#RRGGBB)")

    class Config:
        from_attributes = True


class TagDetail(TagResponse):
    """태그 상세 응답"""
    class Config:
        from_attributes = True