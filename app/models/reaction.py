from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Reaction(Base):
    """
    리액션 모델 (기존 Review)
    태그 또는 댓글 중 최소 1개 필수 (API 레벨에서 검증)
    """
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id", ondelete="CASCADE"), nullable=False, comment="작품 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="사용자 ID")
    visit_id = Column(Integer, ForeignKey("visit_histories.id", ondelete="SET NULL"), nullable=True, comment="방문 ID")
    photo_url = Column(String(500), nullable=True, comment="사용자가 찍은 사진 URL")
    comment = Column(Text, nullable=True, comment="텍스트 코멘트")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    artwork = relationship("Artwork", back_populates="reactions")
    user = relationship("User", back_populates="reactions")
    visit = relationship("VisitHistory", back_populates="reactions")
    tags = relationship("Tag", secondary="reaction_tags", back_populates="reactions")

    def __repr__(self):
        return f"<Reaction(id={self.id}, artwork_id={self.artwork_id}, user_id={self.user_id})>"