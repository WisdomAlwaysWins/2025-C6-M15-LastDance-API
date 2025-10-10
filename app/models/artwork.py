from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Artwork(Base):
    """
    작품 모델
    """
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"), nullable=False, comment="전시 ID")
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="SET NULL"), nullable=True, comment="작가 ID")
    title = Column(String(255), nullable=False, comment="작품 제목")
    description = Column(Text, nullable=True, comment="작품 설명")
    year = Column(Integer, nullable=True, comment="제작 연도")
    thumbnail_url = Column(String(500), nullable=False, comment="작품 이미지 URL")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    exhibition = relationship("Exhibition", back_populates="artworks")
    artist = relationship("Artist", back_populates="artworks")
    reactions = relationship("Reaction", back_populates="artwork")

    def __repr__(self):
        return f"<Artwork(id={self.id}, title='{self.title}')>"