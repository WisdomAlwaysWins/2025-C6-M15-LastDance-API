# app/utils/apns_client.py
import logging
from typing import Optional
from pathlib import Path

from aioapns import APNs, NotificationRequest

logger = logging.getLogger(__name__)


class APNsClient:
    def __init__(
        self,
        key_path: str,
        key_id: str,
        team_id: str,
        bundle_id: str,
        use_sandbox: bool = True,
    ):
        self.bundle_id = bundle_id
        self.use_sandbox = use_sandbox

        key_content = Path(key_path).read_text().strip()
        
        # 🔍 초기화 정보 로깅
        logger.info(f"🔧 APNs 초기화 - Sandbox: {use_sandbox}")
        logger.info(f"   Key ID: {key_id}")
        logger.info(f"   Team ID: {team_id}")
        logger.info(f"   Bundle ID: {bundle_id}")
        logger.info(f"   Key 길이: {len(key_content)} bytes")
        
        self.apns = APNs(
            key=key_content,
            key_id=key_id,
            team_id=team_id,
            topic=bundle_id,
            use_sandbox=use_sandbox,
        )
        
        logger.info("✅ APNs 클라이언트 초기화 완료")

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        badge: Optional[int] = None,
        sound: str = "default",
    ):
        try:
            logger.info(f"📤 푸시 전송 시도 - Token: {device_token[:20]}...")
            logger.info(f"   Title: {title}")
            logger.info(f"   Body: {body}")
            
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
                    **(data or {}),
                },
            )

            result = await self.apns.send_notification(request)
            
            env = "Sandbox" if self.use_sandbox else "Production"
            logger.info(f"✅ [{env}] 푸시 알림 전송 성공: {device_token[:10]}...")
            logger.info(f"   Result: {result}")

        except Exception as e:
            env = "Sandbox" if self.use_sandbox else "Production"
            logger.error(f"❌ [{env}] 푸시 알림 전송 실패")
            logger.error(f"   Exception Type: {type(e).__name__}")
            logger.error(f"   Exception Message: {str(e)}")
            logger.error(f"   Device Token: {device_token[:20]}...")
            
            # 🔍 상세 에러 정보
            import traceback
            logger.error(f"   Traceback:\n{traceback.format_exc()}")
            raise

    async def send_batch_notification(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        badge: Optional[int] = None,
    ):
        success_count = 0
        failed_count = 0
        failed_tokens = []

        for token in device_tokens:
            try:
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


_apns_sandbox: Optional[APNsClient] = None
_apns_production: Optional[APNsClient] = None


def get_apns_client(use_sandbox: bool = True) -> APNsClient:
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