from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid as uuid_pkg

from app.database import Base


class Artist(Base):
    """
    작가 모델
    """
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, nullable=False, index=True, default=lambda: str(uuid_pkg.uuid4()))  # 🆕 추가
    name = Column(String, nullable=False, index=True)
    bio = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    artworks = relationship("Artwork", back_populates="artist")
    exhibitions = relationship("Exhibition", secondary="exhibition_artists", back_populates="artists")

    def __repr__(self):
        return f"<Artist(id={self.id}, uuid={self.uuid}, name={self.name})>"