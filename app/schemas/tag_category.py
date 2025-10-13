from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.tag import TagResponse


class TagCategoryCreate(BaseModel):
    """태그 카테고리 생성"""
    name: str
    color_hex: str
    display_order: int = 0

    @field_validator('color_hex')
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        """HEX 색상 코드 검증 (#RRGGBB)"""
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Must be valid hex color format (e.g., #FF5733)')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Invalid hex color format')
        return v.upper()


class TagCategoryUpdate(BaseModel):
    """태그 카테고리 수정"""
    name: Optional[str] = None
    color_hex: Optional[str] = None
    display_order: Optional[int] = None

    @field_validator('color_hex')
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Must be valid hex color format (e.g., #FF5733)')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Invalid hex color format')
        return v.upper()


class TagCategoryResponse(BaseModel):
    """태그 카테고리 응답 (기본)"""
    id: int
    name: str
    color_hex: str
    display_order: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TagCategoryDetailResponse(BaseModel):
    """태그 카테고리 상세 (태그 포함)"""
    id: int
    name: str
    color_hex: str
    display_order: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List["TagResponse"] = []

    model_config = {"from_attributes": True}