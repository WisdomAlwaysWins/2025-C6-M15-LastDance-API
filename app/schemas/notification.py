"""
Notification Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============================================================================
# Nested Schemas
# ============================================================================


class VisitorInNotification(BaseModel):
    """알림 내 관람객 정보"""

    id: int = Field(..., description="관람객 ID")
    uuid: str = Field(..., description="관람객 UUID")
    name: Optional[str] = Field(None, description="관람객 이름")

    class Config:
        from_attributes = True


class ArtistInNotification(BaseModel):
    """알림 내 작가 정보"""

    id: int = Field(..., description="작가 ID")
    uuid: str = Field(..., description="작가 UUID")
    name: str = Field(..., description="작가명")

    class Config:
        from_attributes = True


class ArtworkInNotification(BaseModel):
    """알림 내 작품 정보"""

    id: int = Field(..., description="작품 ID")
    title: str = Field(..., description="작품 제목")
    image_url: Optional[str] = Field(None, description="작품 이미지 URL")

    class Config:
        from_attributes = True


class ExhibitionInNotification(BaseModel):
    """알림 내 전시 정보"""

    id: int = Field(..., description="전시 ID")
    title: str = Field(..., description="전시 제목")
    cover_image_url: Optional[str] = Field(None, description="전시 포스터 이미지 URL")

    class Config:
        from_attributes = True


class ReactionInNotification(BaseModel):
    """알림 내 반응 정보"""

    id: int = Field(..., description="반응 ID")
    artwork_id: int = Field(..., description="작품 ID")
    visitor_id: int = Field(..., description="관람객 ID")
    comment: Optional[str] = Field(None, description="코멘트")
    image_url: Optional[str] = Field(None, description="반응 이미지 URL")

    class Config:
        from_attributes = True


# ============================================================================
# Response Schemas
# ============================================================================


class NotificationResponse(BaseModel):
    """알림 응답 (목록용)"""

    id: int = Field(..., description="알림 ID")
    notification_type: str = Field(..., description="알림 타입")
    title: str = Field(..., description="알림 제목")
    body: str = Field(..., description="알림 본문")
    reaction_id: int = Field(..., description="반응 ID")
    exhibition_id: Optional[int] = Field(None, description="전시 ID")
    artwork_id: Optional[int] = Field(None, description="작품 ID")
    visit_history_id: Optional[int] = Field(None, description="방문 기록 ID")
    deep_link: str = Field(..., description="딥링크 URL")
    is_read: bool = Field(..., description="읽음 여부")
    is_sent: bool = Field(..., description="전송 여부")
    created_at: datetime = Field(..., description="생성일시")
    read_at: Optional[datetime] = Field(None, description="알림 읽은 시각")

    class Config:
        from_attributes = True


def create_notification_response(notification) -> NotificationResponse:
    """ORM 객체에서 딥링크 생성하여 Response 생성"""
    if notification.notification_type == "reaction_to_artist":
        if notification.exhibition_id and notification.artwork_id:
            deep_link = f"lastdance://exhibition/{notification.exhibition_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
    elif notification.notification_type == "artist_reply":
        if notification.visit_history_id and notification.artwork_id:
            deep_link = f"lastdance://visit/{notification.visit_history_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
    else:
        deep_link = f"lastdance://notification/{notification.id}"

    return NotificationResponse(
        id=notification.id,
        notification_type=notification.notification_type,
        title=notification.title,
        body=notification.body,
        reaction_id=notification.reaction_id,
        exhibition_id=notification.exhibition_id,
        artwork_id=notification.artwork_id,
        visit_history_id=notification.visit_history_id,
        deep_link=deep_link,
        is_read=notification.is_read,
        is_sent=notification.is_sent,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


class NotificationDetail(BaseModel):
    """알림 상세 (관계 포함)"""

    id: int = Field(..., description="알림 ID")
    notification_type: str = Field(..., description="알림 타입")
    title: str = Field(..., description="알림 제목")
    body: str = Field(..., description="알림 본문")
    reaction: Optional[ReactionInNotification] = Field(None, description="반응 정보")
    exhibition: Optional[ExhibitionInNotification] = Field(
        None, description="전시 정보"
    )
    artwork: Optional[ArtworkInNotification] = Field(None, description="작품 정보")
    reaction_id: int = Field(..., description="반응 ID")
    exhibition_id: Optional[int] = Field(None, description="전시 ID")
    artwork_id: Optional[int] = Field(None, description="작품 ID")
    visit_history_id: Optional[int] = Field(None, description="방문 기록 ID")
    deep_link: str = Field(..., description="딥링크 URL")
    is_read: bool = Field(..., description="읽음 여부")
    is_sent: bool = Field(..., description="전송 여부")
    created_at: datetime = Field(..., description="생성일시")
    read_at: Optional[datetime] = Field(None, description="알림 읽은 시각")

    class Config:
        from_attributes = True


def create_notification_detail(notification) -> NotificationDetail:
    """ORM 객체에서 딥링크 생성하여 Detail 생성"""
    if notification.notification_type == "reaction_to_artist":
        if notification.exhibition_id and notification.artwork_id:
            deep_link = f"lastdance://exhibition/{notification.exhibition_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
    elif notification.notification_type == "artist_reply":
        if notification.visit_history_id and notification.artwork_id:
            deep_link = f"lastdance://visit/{notification.visit_history_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
    else:
        deep_link = f"lastdance://notification/{notification.id}"

    return NotificationDetail(
        id=notification.id,
        notification_type=notification.notification_type,
        title=notification.title,
        body=notification.body,
        reaction=notification.reaction if hasattr(notification, "reaction") else None,
        exhibition=(
            notification.exhibition if hasattr(notification, "exhibition") else None
        ),
        artwork=notification.artwork if hasattr(notification, "artwork") else None,
        reaction_id=notification.reaction_id,
        exhibition_id=notification.exhibition_id,
        artwork_id=notification.artwork_id,
        visit_history_id=notification.visit_history_id,
        deep_link=deep_link,
        is_read=notification.is_read,
        is_sent=notification.is_sent,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


# ============================================================================
# Request Schemas
# ============================================================================


class NotificationReadUpdate(BaseModel):
    """알림 읽음 처리 요청"""

    is_read: bool = Field(True, description="읽음 여부")


class NotificationUnreadCount(BaseModel):
    """읽지 않은 알림 개수 응답"""

    count: int = Field(..., description="읽지 않은 알림 개수")


class NotificationBulkReadResponse(BaseModel):
    """일괄 읽음 처리 응답"""

    updated_count: int = Field(..., description="읽음 처리된 알림 개수")
