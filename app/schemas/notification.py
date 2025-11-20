"""
Notification Schemas

푸시 알림 Request/Response 스키마
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ============================================================================
# Nested Schemas (알림 내 관련 엔티티 정보)
# ============================================================================

class VisitorInNotification(BaseModel):
    """알림 내 관람객 정보"""
    id: int
    uuid: str
    name: Optional[str]
    
    class Config:
        from_attributes = True


class ArtistInNotification(BaseModel):
    """알림 내 작가 정보"""
    id: int
    uuid: str
    name: str
    
    class Config:
        from_attributes = True


class ArtworkInNotification(BaseModel):
    """알림 내 작품 정보"""
    id: int
    title: str
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class ExhibitionInNotification(BaseModel):
    """알림 내 전시 정보"""
    id: int
    title: str
    cover_image_url: Optional[str]
    
    class Config:
        from_attributes = True


class ReactionInNotification(BaseModel):
    """알림 내 반응 정보"""
    id: int
    artwork_id: int
    visitor_id: int
    comment: Optional[str]
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# Response Schemas
# ============================================================================

class NotificationResponse(BaseModel):
    """
    알림 응답 (목록용)
    
    알림 목록 조회 시 사용
    관계 정보 제외, 기본 데이터만 포함
    """
    id: int
    notification_type: str
    title: str
    body: str
    
    # 관련 엔티티 ID
    reaction_id: int
    exhibition_id: Optional[int]
    artwork_id: Optional[int]
    visit_history_id: Optional[int]
    
    # 딥링크
    deep_link: str
    
    # 상태
    is_read: bool
    is_sent: bool
    
    # 타임스탬프
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


def create_notification_response(notification) -> NotificationResponse:
    """ORM 객체에서 딥링크 생성하여 Response 생성"""
    # 딥링크 생성
    if notification.notification_type == "reaction_to_artist":
        # 작가용: exhibition/{exhibition_id}/artwork/{artwork_id}/reaction/{reaction_id}
        if notification.exhibition_id and notification.artwork_id:
            deep_link = f"lastdance://exhibition/{notification.exhibition_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
            
    elif notification.notification_type == "artist_reply":
        # 관람객용: visit/{visit_history_id}/artwork/{artwork_id}/reaction/{reaction_id}
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
    """
    알림 상세 (관계 포함)
    
    알림 상세 조회 시 사용
    관련 엔티티의 상세 정보 포함
    """
    id: int
    notification_type: str
    title: str
    body: str
    
    # 관련 엔티티 (전체 정보)
    reaction: Optional[ReactionInNotification]
    exhibition: Optional[ExhibitionInNotification]
    artwork: Optional[ArtworkInNotification]
    
    # 관련 엔티티 ID (딥링크용)
    reaction_id: int
    exhibition_id: Optional[int]
    artwork_id: Optional[int]
    visit_history_id: Optional[int]
    
    # 딥링크
    deep_link: str
    
    # 상태
    is_read: bool
    is_sent: bool
    
    # 타임스탬프
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


def create_notification_detail(notification) -> NotificationDetail:
    """ORM 객체에서 딥링크 생성하여 Detail 생성"""
    # 딥링크 생성
    if notification.notification_type == "reaction_to_artist":
        # 작가용: exhibition/{exhibition_id}/artwork/{artwork_id}/reaction/{reaction_id}
        if notification.exhibition_id and notification.artwork_id:
            deep_link = f"lastdance://exhibition/{notification.exhibition_id}/artwork/{notification.artwork_id}/reaction/{notification.reaction_id}"
        else:
            deep_link = f"lastdance://reaction/{notification.reaction_id}"
            
    elif notification.notification_type == "artist_reply":
        # 관람객용: visit/{visit_history_id}/artwork/{artwork_id}/reaction/{reaction_id}
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
        reaction=notification.reaction if hasattr(notification, 'reaction') else None,
        exhibition=notification.exhibition if hasattr(notification, 'exhibition') else None,
        artwork=notification.artwork if hasattr(notification, 'artwork') else None,
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
    """
    알림 읽음 처리 요청
    
    Attributes:
        is_read: 읽음 여부 (기본값: True)
    """
    is_read: bool = True


class NotificationUnreadCount(BaseModel):
    """
    읽지 않은 알림 개수 응답
    
    Attributes:
        count: 읽지 않은 알림 개수
    """
    count: int


# ============================================================================
# Bulk Operation Schemas
# ============================================================================

class NotificationBulkReadResponse(BaseModel):
    """
    일괄 읽음 처리 응답
    
    Attributes:
        updated_count: 읽음 처리된 알림 개수
    """
    updated_count: int