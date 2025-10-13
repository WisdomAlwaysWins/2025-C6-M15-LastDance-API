from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Artwork(Base):
    """
    작품 모델
    """
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)  # 🆕 추가
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)  # 🆕 추가
    year = Column(Integer, nullable=True)  # 🆕 추가
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    exhibition = relationship("Exhibition", back_populates="artworks")
    artist = relationship("Artist", back_populates="artworks")  # 🆕 추가
    reactions = relationship("Reaction", back_populates="artwork", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artwork(id={self.id}, title={self.title})>"