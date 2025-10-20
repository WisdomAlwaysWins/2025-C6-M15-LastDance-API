import logging

from app.api.v1 import api_router
from app.config import settings
from app.middleware.logging import LoggingMiddleware
from app.utils.cloudwatch import setup_cloudwatch_logging, setup_console_logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# 로깅 설정
if settings.ENVIRONMENT in ["production", "test"]:
    setup_cloudwatch_logging()
else:
    setup_console_logging() # 로컬 개발

# 로깅 기본 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(message)s"
)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="LastDance - 전시 관람 경험 플랫폼 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정 (iOS 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)


# 헬스체크 엔드포인트
@app.get("/health", tags=["Health"])
async def health_check():
    """
    서버 상태 확인용 헬스체크 API
    """
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": "1.0.0"}


# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    """
    API 루트 - 간단한 환영 메시지
    """
    return {"message": "LastDance API", "docs": "/docs", "health": "/health"}


# API v1 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드: 코드 변경 시 자동 재시작
    )
