"""
푸시 알림 전송 헬퍼 함수
"""
from datetime import datetime
import logging

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.constants.notifications import NotificationMessages, NotificationType
from app.models.device import Device
from app.models.notification import Notification
from app.utils.apns_client import get_apns_client

logger = logging.getLogger(__name__)


async def notify_reaction_to_artist(
    db: Session,
    artist_id: int,
    exhibition_id: int,
    exhibition_title: str,
    artwork_id: int,
    artwork_title: str,
    reaction_id: int,
    created_at: datetime,
):
    """작품에 반응이 달렸을 때 작가에게 알림"""
    title = exhibition_title
    body = NotificationMessages.REACTION_TO_ARTIST_BODY.format(
        artwork_title=artwork_title
    )
    
    # 1. DB에 알림 기록 생성
    notification = Notification(
        artist_id=artist_id,
        notification_type=NotificationType.REACTION_TO_ARTIST,
        title=title,
        body=body,
        reaction_id=reaction_id,
        exhibition_id=exhibition_id,
        artwork_id=artwork_id,
        is_sent=False,  # 일단 False로, 전송 성공 시 True
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    logger.info(f"📝 알림 기록 생성 완료 (ID: {notification.id})")
    
    # 2. 푸시 알림 전송
    try:
        devices = (
            db.query(Device)
            .options(joinedload(Device.artist))
            .filter(Device.artist_id == artist_id, Device.is_active == True)
            .all()
        )

        if not devices:
            logger.info(f"작가 ID {artist_id}의 등록된 디바이스 없음")
            return

        artist = devices[0].artist
        logger.info(
            f"✅ 발견된 디바이스 {len(devices)}개 "
            f"(작가: {artist.name}, ID: {artist.id})"
        )

        logger.info(f"📤 푸시 내용 - 제목: {title}, 본문: {body}") 

        apns = get_apns_client(use_sandbox=settings.APNS_USE_SANDBOX)
        logger.info(f"🔧 APNs 모드: {'Sandbox' if settings.APNS_USE_SANDBOX else 'Production'}")

        device_tokens = [d.device_token for d in devices]
        result = await apns.send_batch_notification(
            device_tokens=device_tokens,
            title=title,
            body=body,
            data={
                "type": NotificationType.REACTION_TO_ARTIST,
                "exhibition_id": exhibition_id,
                "artwork_id": artwork_id,
                "reaction_id": reaction_id,
                "exhibition_title": exhibition_title,
                "artwork_title": artwork_title,
                "created_at": created_at.isoformat(),
            },
            badge=1,
        )

        logger.info(
            f"✅ 작가 '{artist.name}'(ID {artist_id})에게 "
            f"푸시 전송: 성공 {result['success']}개, 실패 {result['failed']}개"
        )

        if result['failed'] > 0:
            logger.error(f"❌ 푸시 전송 실패 상세: {result}")
        
        # 3. 전송 성공 시 is_sent 업데이트
        if result['success'] > 0:
            notification.is_sent = True
            db.commit()
            logger.info(f"✅ 알림 전송 상태 업데이트 완료 (ID: {notification.id})")

    except Exception as e:
        logger.error(f"❌ 작가 푸시 전송 실패 (Artist ID {artist_id}): {e}", exc_info=True)


async def notify_artist_reply_to_visitor(
    db: Session,
    visitor_id: int,
    exhibition_id: int,
    visit_history_id: int,
    exhibition_title: str,
    artwork_id: int,
    reaction_id: int,
    reply_created_at: datetime,
):
    """작가가 응답했을 때 관람객에게 알림"""
    title = exhibition_title
    body = NotificationMessages.ARTIST_REPLY_BODY
    
    # 1. DB에 알림 기록 생성
    notification = Notification(
        visitor_id=visitor_id,
        notification_type=NotificationType.ARTIST_REPLY,
        title=title,
        body=body,
        reaction_id=reaction_id,
        exhibition_id=exhibition_id,
        artwork_id=artwork_id,
        visit_history_id=visit_history_id,
        is_sent=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    logger.info(f"📝 알림 기록 생성 완료 (ID: {notification.id})")
    
    # 2. 푸시 알림 전송
    try:
        devices = (
            db.query(Device)
            .options(joinedload(Device.visitor))
            .filter(Device.visitor_id == visitor_id, Device.is_active == True)
            .all()
        )

        if not devices:
            logger.info(f"관람객 ID {visitor_id}의 등록된 디바이스 없음")
            return
        
        visitor = devices[0].visitor
        logger.info(
            f"✅ 발견된 디바이스 {len(devices)}개 "
            f"(관람객: {visitor.name or 'Anonymous'}, ID: {visitor.id})"
        )

        logger.info(f"📤 푸시 내용 - 제목: {title}, 본문: {body}")

        apns = get_apns_client(use_sandbox=settings.APNS_USE_SANDBOX)
        logger.info(f"🔧 APNs 모드: {'Sandbox' if settings.APNS_USE_SANDBOX else 'Production'}")

        device_tokens = [d.device_token for d in devices]
        result = await apns.send_batch_notification(
            device_tokens=device_tokens,
            title=title,
            body=body,
            data={
                "type": NotificationType.ARTIST_REPLY,
                "exhibition_id": exhibition_id,
                "visit_history_id": visit_history_id,
                "artwork_id": artwork_id,
                "reaction_id": reaction_id,
                "exhibition_title": exhibition_title,
                "created_at": reply_created_at.isoformat(),
            },
            badge=1,
        )

        if result['failed'] > 0:
            logger.error(f"❌ 푸시 전송 실패 상세: {result}")
        
        if result['success'] == 0:
            raise Exception(f"모든 디바이스 전송 실패: {result['failed_tokens']}")
        
        logger.info(
            f"✅ 관람객 '{visitor.name or 'Anonymous'}'(ID {visitor_id})에게 "
            f"푸시 전송: 성공 {result['success']}개, 실패 {result['failed']}개"
        )
        
        # 3. 전송 성공 시 is_sent 업데이트
        if result['success'] > 0:
            notification.is_sent = True
            db.commit()
            logger.info(f"✅ 알림 전송 상태 업데이트 완료 (ID: {notification.id})")

    except Exception as e:
        logger.error(f"❌ 관람객 푸시 전송 실패 (Visitor ID {visitor_id}): {e}", exc_info=True)
        raise