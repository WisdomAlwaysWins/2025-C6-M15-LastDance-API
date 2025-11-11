from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.tag_category import TagCategoryBase


class TagCreate(BaseModel):
    """
    태그 생성 요청

    Attributes:
        name: 태그명 (예: 마음이 깊게 울려요)
        category_id: 소속 카테고리 ID
        color_hex: 색상 코드 (선택, #RRGGBB 형식)
    """

    name: str = Field(..., description="태그명")
    category_id: int = Field(..., description="카테고리 ID")
    color_hex: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드"
    )


class TagUpdate(BaseModel):
    """
    태그 수정 요청

    Attributes:
        name: 태그명 (선택)
        category_id: 카테고리 ID (선택)
        color_hex: 색상 코드 (선택)
    """

    name: Optional[str] = None
    category_id: Optional[int] = None
    color_hex: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagResponse(BaseModel):
    """
    태그 기본 응답

    Attributes:
        id: 태그 ID
        name: 태그명
        category: 소속 카테고리 기본 정보
        color_hex: 색상 코드
    """

    id: int
    name: str
    category: TagCategoryBase
    color_hex: Optional[str] = None

    class Config:
        from_attributes = True


class TagDetail(TagResponse):
    """
    태그 상세 응답 (카테고리 정보 포함)

    Attributes:
        category: 소속 카테고리 정보

    Note: 부모 클래스에서 상속
    """

    class Config:
        from_attributes = True
