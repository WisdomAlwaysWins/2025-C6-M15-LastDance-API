from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class VisitHistory(Base):
    """관람 이력 모델 (관람객이 방문한 전시 기록)"""
    __tablename__ = "visit_histories"

    id = Column(Integer, primary_key=True, index=True)
    
    # 외래키
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="사용자 ID")
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"), nullable=False, comment="전시 ID")
    
    visited_at = Column(DateTime(timezone=True), server_default=func.now(), comment="방문 일시")

    # 관계
    user = relationship("User", back_populates="visit_histories")
    exhibition = relationship("Exhibition", back_populates="visit_histories")

    def __repr__(self):
        return f"<VisitHistory(id={self.id}, user_id={self.user_id}, exhibition_id={self.exhibition_id})>"