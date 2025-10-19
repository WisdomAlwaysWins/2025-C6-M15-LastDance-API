from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from app.schemas.artwork import ArtworkResponse
    from app.schemas.tag import TagResponse
    from app.schemas.visitor import VisitorResponse


class ReactionCreate(BaseModel):
    """
    작품 반응 생성 요청

    Attributes:
        artwork_id: 작품 ID
        visitor_id: 관람객 ID
        visit_id: 방문 기록 ID (선택)
        comment: 코멘트 (선택)
        image_url: 촬영한 작품 사진 URL (선택)
        tag_ids: 선택한 태그 ID 목록 (선택)

    Validation:
        comment와 tag_ids 중 최소 하나는 필수
    """

    artwork_id: int = Field(..., description="작품 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    visit_id: Optional[int] = Field(None, description="방문 기록 ID")
    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="촬영한 작품 사진 URL")
    tag_ids: Optional[List[int]] = Field(None, description="태그 ID 목록")

    @validator("tag_ids")
    def validate_reaction_content(cls, tag_ids, values):
        """comment 또는 tag_ids 중 하나는 필수"""
        comment = values.get("comment")
        if not comment and not tag_ids:
            raise ValueError("comment 또는 tag_ids 중 하나는 필수입니다")
        return tag_ids


class ReactionUpdate(BaseModel):
    """
    작품 반응 수정 요청

    Attributes:
        comment: 코멘트 (선택)
        image_url: 촬영한 작품 사진 URL (선택)
        tag_ids: 태그 ID 목록 (선택)

    Validation:
        수정 시에도 comment와 tag_ids 중 최소 하나는 필수
    """

    comment: Optional[str] = None
    image_url: Optional[str] = None
    tag_ids: Optional[List[int]] = None

    @validator("tag_ids")
    def validate_reaction_content(cls, tag_ids, values):
        """comment 또는 tag_ids 중 하나는 필수"""
        comment = values.get("comment")
        if comment is None and not tag_ids:
            raise ValueError("comment 또는 tag_ids 중 하나는 필수입니다")
        return tag_ids


class ReactionResponse(BaseModel):
    """
    작품 반응 기본 응답

    Attributes:
        id: 반응 ID
        artwork_id: 작품 ID
        visitor_id: 관람객 ID
        visit_id: 방문 기록 ID
        comment: 코멘트
        image_url: 촬영한 작품 사진 URL
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    artwork_id: int
    visitor_id: int
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReactionDetail(ReactionResponse):
    """
    작품 반응 상세 응답 (작품, 관람객, 태그 정보 포함)

    Attributes:
        artwork: 작품 정보
        visitor: 관람객 정보
        tags: 선택한 태그 목록
    """

    artwork: "ArtworkResponse"
    visitor: "VisitorResponse"
    tags: List["TagResponse"] = []

    class Config:
        from_attributes = True
