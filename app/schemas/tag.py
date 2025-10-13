from pydantic import BaseModel
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.tag_category import TagCategoryResponse


class TagCreate(BaseModel):
    """태그 생성"""
    category_id: int
    name: str
    display_order: int = 0


class TagUpdate(BaseModel):
    """태그 수정"""
    category_id: Optional[int] = None
    name: Optional[str] = None
    display_order: Optional[int] = None


class TagResponse(BaseModel):
    """태그 응답 (기본)"""
    id: int
    category_id: int
    name: str
    display_order: int

    model_config = {"from_attributes": True}


class TagDetailResponse(BaseModel):
    """태그 상세 (카테고리 포함)"""
    id: int
    category_id: int
    name: str
    display_order: int
    category: Optional["TagCategoryResponse"] = None

    model_config = {"from_attributes": True}