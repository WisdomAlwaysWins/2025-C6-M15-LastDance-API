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

    # 로그에서 제외하거나 마스킹할 민감한 헤더
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

        # ✨ Request Headers 로깅
        headers = self._mask_sensitive_headers(dict(request.headers))
        
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

        # 요청 정보
        log_msg = (
            f"[{request_time}] 📥 요청 시작 - {request.method} {request.url.path} "
            f"- IP: {request.client.host if request.client else 'unknown'}"
        )

        # ✨ 헤더 로깅
        if headers:
            # 중요 헤더만 INFO 레벨에 표시
            important_headers = {
                k: v for k, v in headers.items() 
                if k.lower() in ['content-type', 'user-agent', 'x-artist-uuid', 'x-user-uuid']
            }
            if important_headers:
                log_msg += f" | Headers: {json.dumps(important_headers, ensure_ascii=False)}"
            
            # 전체 헤더는 DEBUG 레벨에만
            logger.debug(f"Full Headers: {json.dumps(headers, ensure_ascii=False)}")

        # Query Parameters 로깅
        if request.query_params:
            query_params = dict(request.query_params)
            log_msg += f" | Query: {json.dumps(query_params, ensure_ascii=False)}"

        if body:
            # 민감한 정보 마스킹
            safe_body = body.copy() if isinstance(body, dict) else body
            if isinstance(safe_body, dict):
                if "password" in safe_body:
                    safe_body["password"] = "***"
                if "token" in safe_body:
                    safe_body["token"] = "***"
                # Base64 이미지는 길이만 표시
                if "image_base64" in safe_body:
                    img_len = len(safe_body["image_base64"])
                    safe_body["image_base64"] = f"<base64_image: {img_len} bytes>"

            body_str = json.dumps(safe_body, ensure_ascii=False)
            if len(body_str) > 500:
                body_str = body_str[:500] + "..."
            log_msg += f" | Body: {body_str}"

        logger.info(log_msg)

        try:
            # 실제 엔드포인트 호출
            response = await call_next(request)

            # 응답 시간 계산
            process_time = time.time() - start_time

            # ✨ 상태 코드별 이모지
            status_emoji = "✅" if response.status_code < 400 else "❌"

            # 응답 정보 로깅
            logger.info(
                f"[{request_time}] {status_emoji} 요청 완료 - {request.method} {request.url.path} "
                f"- 상태: {response.status_code} "
                f"- 소요시간: {process_time:.2f}초"
            )

            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 에러 로깅
            process_time = time.time() - start_time
            logger.error(
                f"[{request_time}] ❌ 요청 실패 - {request.method} {request.url.path} "
                f"- 에러: {str(e)} "
                f"- 소요시간: {process_time:.2f}초",
                exc_info=True  # ✨ 스택 트레이스 포함
            )
            raise

    def _mask_sensitive_headers(self, headers: dict) -> dict:
        """민감한 헤더 마스킹"""
        masked = {}
        for key, value in headers.items():
            key_lower = key.lower()
            
            # 완전 마스킹
            if key_lower in self.SENSITIVE_HEADERS:
                masked[key] = "***MASKED***"
            # 부분 마스킹 (UUID 등)
            elif key_lower in self.PARTIAL_MASK_HEADERS:
                if len(value) > 8:
                    masked[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    masked[key] = value
            # 일반 헤더
            else:
                masked[key] = value
        
        return masked