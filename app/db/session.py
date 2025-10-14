# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 환경변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://lastdance:2025-c6-m15-lastdance-kbejyj@db:5432/lastdance"
)

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()