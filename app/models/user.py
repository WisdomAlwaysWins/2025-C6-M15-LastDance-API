from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserType(str, enum.Enum):
    """사용자 타입"""
    VISITOR = "visitor"  # 관람객
    ARTIST = "artist"    # 작가


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # UUID: 모든 사용자의 고유 식별자
    uuid = Column(String(36), unique=True, nullable=False, index=True, comment="사용자 고유 식별자 (UUID)")
    
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.VISITOR, comment="사용자 타입 (관람객/작가)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 일시")

    # 선택 정보 (나중에 입력 가능)
    name = Column(String(100), nullable=True, comment="사용자 이름 (선택)")
    email = Column(String(255), unique=True, index=True, nullable=True, comment="이메일 (선택)")

    # 관계 (Relationships)
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    visit_histories = relationship("VisitHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, uuid='{self.uuid}', type={self.user_type})>"