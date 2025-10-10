from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """
    사용자 모델 (관람객 전용)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True, comment="iOS UUID")
    name = Column(String(100), nullable=True, comment="사용자 이름")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    visits = relationship("VisitHistory", back_populates="user")
    reactions = relationship("Reaction", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, uuid='{self.uuid}', name='{self.name}')>"