from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base
from app.models.exhibition import exhibition_artworks

class Artwork(Base):
    """
    작품 모델
    """
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False) 
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)  
    year = Column(Integer, nullable=True)  
    thumbnail_url = Column(String, nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    artist = relationship("Artist", back_populates="artworks")
    exhibitions = relationship(
        "Exhibition",
        secondary="exhibition_artworks",
        back_populates="artworks"
    )
    reactions = relationship("Reaction", back_populates="artwork", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artwork(id={self.id}, title={self.title})>"