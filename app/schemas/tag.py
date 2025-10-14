from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.tag_category import TagCategoryResponse

class TagCreate(BaseModel):
    """
    태그 생성 요청
    
    Attributes:
        name: 태그명 (예: 마음이 깊게 울려요)
        category_id: 소속 카테고리 ID
        display_order: 카테고리 내 표시 순서
    """
    name: str = Field(..., description="태그명")
    category_id: int = Field(..., description="카테고리 ID")
    display_order: int = Field(0, description="표시 순서")


class TagUpdate(BaseModel):
    """
    태그 수정 요청
    
    Attributes:
        name: 태그명 (선택)
        category_id: 카테고리 ID (선택)
        display_order: 표시 순서 (선택)
    """
    name: Optional[str] = None
    category_id: Optional[int] = None
    display_order: Optional[int] = None


class TagResponse(BaseModel):
    """
    태그 기본 응답
    
    Attributes:
        id: 태그 ID
        name: 태그명
        category_id: 소속 카테고리 ID
        display_order: 표시 순서
    """
    id: int
    name: str
    category_id: int
    display_order: int

    class Config:
        from_attributes = True


class TagDetail(TagResponse):
    """
    태그 상세 응답 (카테고리 정보 포함)
    
    Attributes:
        category: 소속 카테고리 정보
    """
    category: 'TagCategoryResponse' 

    class Config:
        from_attributes = True