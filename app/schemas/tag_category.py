"""
Tag Category Schemas
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.tag import TagResponse


# ============================================================================
# Nested Schemas
# ============================================================================


class TagCategoryBase(BaseModel):
    """태그 카테고리 기본 정보"""

    id: int = Field(..., description="카테고리 ID")
    name: str = Field(..., description="카테고리명")
    color_hex: Optional[str] = Field(None, description="색상 코드 (#RRGGBB)")

    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas
# ============================================================================


class TagCategoryCreate(BaseModel):
    """태그 카테고리 생성 요청"""

    name: str = Field(..., description="카테고리명")
    color_hex: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드 (#RRGGBB)"
    )


class TagCategoryUpdate(BaseModel):
    """태그 카테고리 수정 요청"""

    name: Optional[str] = Field(None, description="카테고리명")
    color_hex: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드 (#RRGGBB)"
    )


# ============================================================================
# Response Schemas
# ============================================================================


class TagCategoryResponse(BaseModel):
    """태그 카테고리 기본 응답"""

    id: int = Field(..., description="카테고리 ID")
    name: str = Field(..., description="카테고리명")
    color_hex: Optional[str] = Field(None, description="색상 코드 (#RRGGBB)")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    tags: List["TagResponse"] = Field([], description="태그 목록")

    class Config:
        from_attributes = True


class TagCategoryDetail(TagCategoryResponse):
    """태그 카테고리 상세 응답"""

    class Config:
        from_attributes = True
