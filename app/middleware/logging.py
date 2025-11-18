from datetime import datetime
import json
import logging
import time
from typing import Callable
from zoneinfo import ZoneInfo

from starlette.middleware.base import BaseHTTPMiddleware

from fastapi import Request, Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    모든 API 요청/응답을 자동으로 로깅하는 미들웨어
    """

    # 민감한 헤더 (완전 마스킹)
    SENSITIVE_HEADERS = {
        "authorization",
        "x-api-key",
        "cookie",
    }

    # 부분 마스킹할 헤더 (UUID 등)
    PARTIAL_MASK_HEADERS = {
        "x-artist-uuid",
        "x-user-uuid",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 한국 시간
        kst = ZoneInfo("Asia/Seoul")
        request_time = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")

        # 요청 시작
        start_time = time.time()

        # Request Body 읽기
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes.decode())

                # Body를 다시 읽을 수 있도록 설정
                async def receive():
                    return {"type": "http.request", "body": body_bytes}

                request._receive = receive
            except Exception as e:
                logger.warning(f"Request Body 읽기 실패: {e}")
                body = None

        # ✨ 요청 로깅 (줄바꿈으로 깔끔하게)
        headers = self._mask_sensitive_headers(dict(request.headers))
        
        logger.info("")  # 빈 줄
        logger.info("=" * 80)
        logger.info(f"📥 요청: {request.method} {request.url.path}")
        logger.info(f"   시간: {request_time}")
        logger.info(f"   IP: {request.client.host if request.client else 'unknown'}")
        
        # UUID 표시
        uuid = headers.get("x-user-uuid") or headers.get("x-artist-uuid")
        if uuid:
            logger.info(f"   UUID: {uuid}")
        
        # Query Parameters
        if request.query_params:
            query_params = dict(request.query_params)
            logger.info(f"   Query: {query_params}")

        # Body (간단하게)
        if body:
            safe_body = self._mask_body(body)
            if isinstance(safe_body, dict):
                # 중요 필드만 표시
                summary = {}
                for key in list(safe_body.keys())[:5]:  # 최대 5개
                    summary[key] = safe_body[key]
                logger.info(f"   Body: {json.dumps(summary, ensure_ascii=False)}")

        try:
            # 실제 엔드포인트 호출
            response = await call_next(request)

            # 응답 시간 계산
            process_time = time.time() - start_time

            # ✨ 응답 로깅
            status_emoji = "✅" if response.status_code < 400 else "❌"
            
            logger.info(f"{status_emoji} 응답: {response.status_code} ({process_time:.2f}초)")
            logger.info("=" * 80)
            logger.info("")  # 빈 줄

            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 에러 로깅
            process_time = time.time() - start_time
            logger.error(f"❌ 에러: {str(e)[:100]} ({process_time:.2f}초)")
            logger.error("=" * 80)
            logger.error("")  # 빈 줄
            logger.debug("상세 에러:", exc_info=True)
            raise

    def _mask_sensitive_headers(self, headers: dict) -> dict:
        """민감한 헤더 마스킹"""
        masked = {}
        for key, value in headers.items():
            key_lower = key.lower()
            
            # 완전 마스킹
            if key_lower in self.SENSITIVE_HEADERS:
                masked[key] = "***"
            # 부분 마스킹 (UUID 등 - 앞뒤만)
            elif key_lower in self.PARTIAL_MASK_HEADERS:
                if len(value) > 12:
                    masked[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    masked[key] = value
            # 일반 헤더
            else:
                masked[key] = value
        
        return masked

    def _mask_body(self, body) -> dict:
        """Body 민감 정보 마스킹"""
        if not isinstance(body, dict):
            return body
            
        safe_body = body.copy()
        
        # 민감 정보 마스킹
        if "password" in safe_body:
            safe_body["password"] = "***"
        if "token" in safe_body:
            safe_body["token"] = "***"
        
        # Base64 이미지는 길이만 표시
        if "image_base64" in safe_body:
            img_len = len(safe_body["image_base64"])
            safe_body["image_base64"] = f"<{img_len} bytes>"
        
        return safe_body