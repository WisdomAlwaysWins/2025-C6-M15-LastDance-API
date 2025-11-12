# app/utils/apns_client.py
import logging
from typing import Optional
from aioapns import APNs, NotificationRequest

logger = logging.getLogger(__name__)


class APNsClient:
    def __init__(
        self,
        key_path: str,  # .p8 파일 경로
        key_id: str,  # Key ID
        team_id: str,  # Team ID
        bundle_id: str,  # Bundle ID
        use_sandbox: bool = True,  # Test/Prod 구분
    ):
        self.bundle_id = bundle_id
        self.use_sandbox = use_sandbox
        self.apns = APNs(
            key=key_path,
            key_id=key_id,
            team_id=team_id,
            topic=bundle_id,
            use_sandbox=use_sandbox,
        )

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        badge: Optional[int] = None,
        sound: str = "default",
    ):
        """
        푸시 알림 전송

        Args:
            device_token: iOS 기기 토큰
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (딕셔너리)
            badge: 뱃지 숫자
            sound: 알림 소리

        Raises:
            Exception: 푸시 전송 실패 시
        """
        try:
            request = NotificationRequest(
                device_token=device_token,
                message={
                    "aps": {
                        "alert": {
                            "title": title,
                            "body": body,
                        },
                        "badge": badge,
                        "sound": sound,
                    },
                    **(data or {}),  # 커스텀 데이터
                },
            )

            await self.apns.send_notification(request)
            env = "Sandbox" if self.use_sandbox else "Production"
            logger.info(f"[{env}] 푸시 알림 전송 성공: {device_token[:10]}...")

        except Exception as e:
            env = "Sandbox" if self.use_sandbox else "Production"
            logger.error(f"[{env}] 푸시 알림 전송 실패: {e}")
            raise

    async def send_batch_notification(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        badge: Optional[int] = None,
    ):
        """
        여러 디바이스에 푸시 일괄 전송

        Args:
            device_tokens: iOS 기기 토큰 리스트
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터
            badge: 뱃지 숫자

        Returns:
            dict: {"success": 성공 수, "failed": 실패 수, "failed_tokens": 실패 상세}
        """
        success_count = 0
        failed_count = 0
        failed_tokens = []

        for token in device_tokens:
            try:
                # ✅ send_notification 메서드 직접 호출
                await self.send_notification(
                    device_token=token,
                    title=title,
                    body=body,
                    data=data,
                    badge=badge,
                )
                
                logger.info(f"✅ 토큰 {token[:20]}... 전송 성공")
                success_count += 1
                
            except Exception as e:
                logger.error(
                    f"❌ 토큰 {token[:20]}... 전송 실패: "
                    f"{type(e).__name__} - {str(e)}"
                )
                failed_count += 1
                failed_tokens.append({
                    "token": token[:20],
                    "error": str(e)
                })

        logger.info(
            f"일괄 전송 완료: 성공 {success_count}개, 실패 {failed_count}개"
        )
        
        return {
            "success": success_count,
            "failed": failed_count,
            "failed_tokens": failed_tokens
        }


# 싱글톤 인스턴스 (환경별)
_apns_sandbox: Optional[APNsClient] = None
_apns_production: Optional[APNsClient] = None


def get_apns_client(use_sandbox: bool = True) -> APNsClient:
    """
    APNs 클라이언트 싱글톤 인스턴스 반환

    Args:
        use_sandbox: True면 Sandbox, False면 Production

    Returns:
        APNsClient 인스턴스
    """
    global _apns_sandbox, _apns_production

    from app.config import settings

    if use_sandbox:
        if _apns_sandbox is None:
            _apns_sandbox = APNsClient(
                key_path=settings.APNS_SANDBOX_KEY_PATH,
                key_id=settings.APNS_SANDBOX_KEY_ID,
                team_id=settings.APNS_TEAM_ID,
                bundle_id=settings.APNS_BUNDLE_ID,
                use_sandbox=True,
            )
        return _apns_sandbox
    else:
        if _apns_production is None:
            _apns_production = APNsClient(
                key_path=settings.APNS_PRODUCTION_KEY_PATH,
                key_id=settings.APNS_PRODUCTION_KEY_ID,
                team_id=settings.APNS_TEAM_ID,
                bundle_id=settings.APNS_BUNDLE_ID,
                use_sandbox=False,
            )
        return _apns_production