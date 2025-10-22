from datetime import datetime
import logging
import time
import json
from typing import Callable
from zoneinfo import ZoneInfo

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    모든 API 요청/응답을 자동으로 로깅하는 미들웨어
    """

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
                    body = json.loads(body_bytes.decode())  # ← 이거 추가!
                
                # Body를 다시 읽을 수 있도록 설정
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
            except Exception as e:
                logger.warning(f"Request Body 읽기 실패: {e}")
                body = None

        # 요청 정보 
        log_msg = (
            f"[{request_time}] 요청 시작 - {request.method} {request.url.path} "
            f"- IP: {request.client.host if request.client else 'unknown'}"
        )

        if body:
            # 민감한 정보 마스킹
            safe_body = body.copy() if isinstance(body, dict) else body
            if isinstance(safe_body, dict):
                if 'password' in safe_body:
                    safe_body['password'] = '***'
                if 'token' in safe_body:
                    safe_body['token'] = '***'
            
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

            # 응답 정보 로깅
            logger.info(
                f"[{request_time}] 요청 완료 - {request.method} {request.url.path} "
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
                f"[{request_time}] 요청 실패 - {request.method} {request.url.path} "
                f"- 에러: {str(e)} "
                f"- 소요시간: {process_time:.2f}초"
            )
            raise