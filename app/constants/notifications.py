# app/constants/notifications.py
"""
푸시 알림 메시지 템플릿
"""


class NotificationMessages:
    """알림 메시지 템플릿"""

    # ========================================
    # 작가에게 보내는 알림
    # ========================================

    # 반응 관련
    # 제목: 전시 이름 (동적)
    # 내용: '{작품 이름}'에 새로운 메시지가 있어요.
    REACTION_TO_ARTIST_BODY = "'{artwork_title}'에 새로운 메시지가 있어요."

    # ========================================
    # 관람객에게 보내는 알림 (작가 응답)
    # ========================================

    # 작가 응답 알림
    # 제목: 전시 이름 (동적)
    # 내용: 내가 남긴 메시지에 대한 반응이 있어요.
    ARTIST_REPLY_BODY = "내가 남긴 메시지에 대한 반응이 있어요."


class NotificationType:
    """알림 타입 상수"""

    REACTION_TO_ARTIST = "reaction_to_artist"  # 작가에게: 새 반응
    ARTIST_REPLY = "artist_reply"  # 관람객에게: 작가 응답