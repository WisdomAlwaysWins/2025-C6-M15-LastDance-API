from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class VisitHistory(Base):
    """
    전시 방문 기록 모델
    """

    __tablename__ = "visit_histories"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False)
    visited_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    visitor = relationship("Visitor", back_populates="visits")
    exhibition = relationship("Exhibition", back_populates="visits")
    reactions = relationship(
        "Reaction", back_populates="visit", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<VisitHistory(id={self.id}, visitor_id={self.visitor_id}, exhibition_id={self.exhibition_id})>"
