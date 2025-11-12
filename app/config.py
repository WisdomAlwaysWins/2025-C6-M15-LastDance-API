from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Project
    PROJECT_NAME: str = "LastDance API"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-northeast-2"
    AWS_LAMBDA_REGION: str
    S3_BUCKET_NAME: str

    # HuggingFace
    HUGGINGFACE_TOKEN: str

    # Lambda
    LAMBDA_FUNCTION_NAME: str = "lastdance-embedding-generator"

    ENVIRONMENT: str = "local"

    # Admin API Key
    ADMIN_API_KEY: str

    # APNs (Apple Push Notification) 설정
    APNS_TEAM_ID: str
    APNS_BUNDLE_ID: str

    # Sandbox (개발용)
    APNS_SANDBOX_KEY_PATH: str
    APNS_SANDBOX_KEY_ID: str

    # Production (배포용)
    APNS_PRODUCTION_KEY_PATH: str
    APNS_PRODUCTION_KEY_ID: str

    # 현재 사용 환경
    APNS_USE_SANDBOX: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore


# 전역 설정 객체
settings = get_settings()