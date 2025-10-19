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

    HUGGINGFACE_TOKEN: str

    # Lambda
    LAMBDA_FUNCTION_NAME: str = "lastdance-embedding-generator"

    ENVIRONMENT: str = "production"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환 (캐싱)"""
    return Settings()


# 전역 설정 객체
settings = get_settings()
