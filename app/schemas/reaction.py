from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.tag import TagResponse

if TYPE_CHECKING:
    from app.schemas.artwork import ArtworkResponse
    from app.schemas.visit_history import VisitHistorySummary
    from app.schemas.visitor import VisitorResponse


class ReactionBase(BaseModel):
    """
    작품 반응 기본 속성

    Attributes:
        artwork_id: 작품 ID
        visitor_id: 관람객 ID
        visit_id: 방문 기록 ID (선택)
        comment: 코멘트 (선택)
        image_url: 촬영한 작품 사진 URL (선택)
    """

    artwork_id: int
    visitor_id: int
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None


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
    작품 반응 기본 응답 (리스트용)

    GET /reactions 리스트 조회 시 사용

    Attributes:
        id: 반응 ID
        artwork_id: 작품 ID
        artwork_title: 작품 제목
        visitor_id: 관람객 ID
        visitor_name: 관람객 이름
        visit_id: 방문 기록 ID
        comment: 코멘트
        image_url: 촬영한 작품 사진 URL
        tags: 선택한 태그 목록
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    artwork_id: int
    artwork_title: str
    visitor_id: int
    visitor_name: Optional[str] = None
    visit_id: Optional[int] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReactionSummary(BaseModel):
    """
    반응 요약 정보 (순환 참조 방지용)

    VisitHistory에서 사용

    Attributes:
        id: 반응 ID
        artwork_id: 작품 ID
        artwork_title: 작품 제목
        comment: 코멘트
        created_at: 생성일시
    """

    id: int
    artwork_id: int
    artwork_title: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionDetail(BaseModel):
    """
    작품 반응 상세 응답 (상세 조회용)

    GET /reactions/{id} 상세 조회 시 사용

    Attributes:
        id: 반응 ID
        artwork_id: 작품 ID
        artwork: 작품 전체 정보
        visitor_id: 관람객 ID
        visitor: 관람객 전체 정보
        visit_id: 방문 기록 ID
        visit: 방문 기록 요약 정보
        comment: 코멘트
        image_url: 촬영한 작품 사진 URL
        tags: 선택한 태그 목록
        created_at: 생성일시
        updated_at: 수정일시
    """

    id: int
    artwork_id: int
    artwork: "ArtworkResponse"
    visitor_id: int
    visitor: "VisitorResponse"
    visit_id: Optional[int] = None
    visit: Optional["VisitHistorySummary"] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
