from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Engine 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 검사
    echo=False,  # SQL 쿼리 로깅 (개발 시 True로 변경 가능)
)

# Session 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모든 모델의 부모 클래스)
Base = declarative_base()


# Dependency: DB 세션 주입
def get_db():
    """
    FastAPI 의존성으로 사용할 DB 세션 생성기
    요청마다 새로운 세션을 만들고, 요청 종료 시 자동으로 닫음
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()