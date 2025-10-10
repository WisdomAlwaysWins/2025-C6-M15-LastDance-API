from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class VisitHistory(Base):
    """
    방문 기록 모델
    같은 날 같은 전시 중복 방문 가능
    """
    __tablename__ = "visit_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="사용자 ID")
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"), nullable=False, comment="전시 ID")
    visited_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="방문 시각")

    # 관계
    user = relationship("User", back_populates="visits")
    exhibition = relationship("Exhibition", back_populates="visits")
    reactions = relationship("Reaction", back_populates="visit")

    def __repr__(self):
        return f"<VisitHistory(id={self.id}, user_id={self.user_id}, exhibition_id={self.exhibition_id})>"