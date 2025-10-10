from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Artist(Base):
    """
    작가 모델 (User와 완전 분리)
    """
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True, comment="작가 이름")
    bio = Column(Text, nullable=True, comment="작가 소개")
    email = Column(String(255), nullable=True, comment="이메일")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    artworks = relationship("Artwork", back_populates="artist")
    exhibitions = relationship(
        "Exhibition",
        secondary="exhibition_artists",
        back_populates="artists"
    )

    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"