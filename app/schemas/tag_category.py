from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.tag import TagResponse


class TagCategoryCreate(BaseModel):
    """
    태그 카테고리 생성 요청

    Attributes:
        name: 카테고리명 (예: 감동이에요, 아름다워요)
        color_hex: 색상 코드 (선택, #RRGGBB 형식)
    """

    name: str = Field(..., description="카테고리명")
    color_hex: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드"
    )


class TagCategoryUpdate(BaseModel):
    """
    태그 카테고리 수정 요청

    Attributes:
        name: 카테고리명 (선택)
        color_hex: 색상 코드 (선택)
    """

    name: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagCategoryResponse(BaseModel):
    """
    태그 카테고리 기본 응답

    Attributes:
        id: 카테고리 ID
        name: 카테고리명
        color_hex: 색상 코드
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    name: str
    color_hex: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TagCategoryDetail(TagCategoryResponse):
    """
    태그 카테고리 상세 응답 (태그 목록 포함)

    Attributes:
        tags: 해당 카테고리의 태그 목록
    """

    tags: List["TagResponse"] = []

    class Config:
        from_attributes = True
