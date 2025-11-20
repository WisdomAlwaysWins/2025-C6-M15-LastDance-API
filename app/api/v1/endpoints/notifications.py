"""
Notifications Router

알림 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.database import get_db
from app.models.notification import Notification
from app.models.visitor import Visitor
from app.models.artist import Artist
from app.schemas.notification import (
    NotificationResponse,
    NotificationDetail,
    NotificationReadUpdate,
    NotificationUnreadCount,
    NotificationBulkReadResponse,
    create_notification_response,
    create_notification_detail,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================

def get_user_notifications_query(db: Session, user_uuid: str):
    logger.info(f"🔍 알림 조회: UUID {user_uuid[:8]}...")
    
    # Visitor 확인
    visitor = db.query(Visitor).filter(Visitor.uuid == user_uuid).first()
    if visitor:
        logger.info(f"✅ Visitor 발견: ID {visitor.id}, 이름 '{visitor.name}'")
        query = db.query(Notification).filter(Notification.visitor_id == visitor.id)
        return query, True, visitor.id
    
    # Artist 확인
    artist = db.query(Artist).filter(Artist.uuid == user_uuid).first()
    if artist:
        logger.info(f"✅ Artist 발견: ID {artist.id}, 이름 '{artist.name}'")
        query = db.query(Notification).filter(Notification.artist_id == artist.id)
        return query, False, artist.id
    
    # 둘 다 아니면 에러
    logger.error(f"❌ User not found: UUID {user_uuid[:8]}...")
    raise HTTPException(status_code=404, detail="User not found")


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "",
    response_model=List[NotificationResponse],
    summary="알림 목록 조회",
    description="""
    사용자의 알림 목록을 조회합니다.
    
    - visitor 또는 artist UUID로 본인의 알림만 조회 가능
    - 최신순으로 정렬
    - 읽음/안읽음 필터링 가능
    - 딥링크 포함
    """
)
def get_notifications(
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
    is_read: Optional[bool] = Query(None, description="읽음 여부 필터 (없으면 전체)"),
    limit: int = Query(50, ge=1, le=100, description="조회할 알림 개수"),
    offset: int = Query(0, ge=0, description="건너뛸 알림 개수"),
):
    """알림 목록 조회"""
    logger.info(f"알림 목록 조회 시작: is_read={is_read}, limit={limit}, offset={offset}")
    
    # 사용자 확인 및 쿼리 생성
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 읽음 필터
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    # 정렬 및 페이징
    notifications = (
        query
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    user_type = "관람객" if is_visitor else "작가"
    logger.info(f"✅ 알림 {len(notifications)}개 조회 완료: {user_type} ID {user_id}")
    
    # 딥링크 포함하여 Response 생성
    return [create_notification_response(n) for n in notifications]


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCount,
    summary="읽지 않은 알림 개수",
    description="""
    사용자의 읽지 않은 알림 개수를 조회합니다.
    
    - iOS 앱 뱃지 표시용
    """
)
def get_unread_count(
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    """읽지 않은 알림 개수"""
    logger.info(f"읽지 않은 알림 개수 조회")
    
    # 사용자 확인 및 쿼리 생성
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 읽지 않은 알림 개수
    count = query.filter(Notification.is_read == False).count()
    
    user_type = "관람객" if is_visitor else "작가"
    logger.info(f"✅ 읽지 않은 알림 {count}개: {user_type} ID {user_id}")
    
    return NotificationUnreadCount(count=count)


@router.get(
    "/{notification_id}",
    response_model=NotificationDetail,
    summary="알림 상세 조회",
    description="""
    알림 상세 정보를 조회합니다.
    
    - reaction, exhibition, artwork 정보 포함
    - 본인의 알림만 조회 가능
    """
)
def get_notification_detail(
    notification_id: int,
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    """알림 상세 조회"""
    logger.info(f"알림 상세 조회 시작: ID {notification_id}")
    
    # 사용자 확인
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 알림 조회 (관계 포함)
    notification = (
        query
        .options(
            joinedload(Notification.reaction),
            joinedload(Notification.exhibition),
            joinedload(Notification.artwork),
        )
        .filter(Notification.id == notification_id)
        .first()
    )
    
    if not notification:
        logger.warning(f"알림 ID {notification_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Notification not found")
    
    logger.info(f"✅ 알림 조회 완료: ID {notification_id}, 타입 {notification.notification_type}")
    
    # 딥링크 포함하여 Detail 생성
    return create_notification_detail(notification)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="알림 읽음 처리",
    description="""
    특정 알림을 읽음 처리합니다.
    
    - read_at 타임스탬프 자동 기록
    - 본인의 알림만 처리 가능
    """
)
def mark_notification_as_read(
    notification_id: int,
    data: NotificationReadUpdate,
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    """알림 읽음 처리"""
    logger.info(f"알림 읽음 처리 시작: ID {notification_id}, is_read={data.is_read}")
    
    # 사용자 확인
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 알림 조회
    notification = query.filter(Notification.id == notification_id).first()
    
    if not notification:
        logger.warning(f"알림 ID {notification_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # 읽음 처리
    notification.is_read = data.is_read
    if data.is_read and notification.read_at is None:
        from datetime import datetime
        notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    
    logger.info(f"✅ 알림 읽음 처리 완료: ID {notification_id}, is_read={data.is_read}")
    
    return create_notification_response(notification)


@router.patch(
    "/read-all",
    response_model=NotificationBulkReadResponse,
    summary="모든 알림 읽음 처리",
    description="""
    사용자의 모든 읽지 않은 알림을 읽음 처리합니다.
    
    - 일괄 처리
    - 처리된 알림 개수 반환
    """
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    """모든 알림 읽음 처리"""
    from datetime import datetime
    
    logger.info(f"모든 알림 읽음 처리 시작")
    
    # 사용자 확인
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 읽지 않은 알림만 필터
    unread_notifications = query.filter(Notification.is_read == False).all()
    
    logger.info(f"읽지 않은 알림 {len(unread_notifications)}개 발견")
    
    # 일괄 읽음 처리
    count = 0
    for notification in unread_notifications:
        notification.is_read = True
        if notification.read_at is None:
            notification.read_at = datetime.utcnow()
        count += 1
    
    db.commit()
    
    user_type = "관람객" if is_visitor else "작가"
    logger.info(f"✅ 모든 알림 읽음 처리 완료: {count}개, {user_type} ID {user_id}")
    
    return NotificationBulkReadResponse(updated_count=count)


@router.delete(
    "/{notification_id}",
    status_code=204,
    summary="알림 삭제",
    description="""
    특정 알림을 삭제합니다.
    
    - 본인의 알림만 삭제 가능
    """
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    """알림 삭제"""
    logger.info(f"알림 삭제 시작: ID {notification_id}")
    
    # 사용자 확인
    query, is_visitor, user_id = get_user_notifications_query(db, user_uuid)
    
    # 알림 조회
    notification = query.filter(Notification.id == notification_id).first()
    
    if not notification:
        logger.warning(f"알림 ID {notification_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification_type = notification.notification_type
    
    # 삭제
    db.delete(notification)
    db.commit()
    
    logger.info(f"✅ 알림 삭제 완료: ID {notification_id}, 타입 {notification_type}")
    
    return None