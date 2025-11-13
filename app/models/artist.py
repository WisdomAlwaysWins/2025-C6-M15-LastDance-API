import uuid as uuid_pkg

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Artist(Base):
    """
    작가 모델
    """

    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid_pkg.uuid4()),
    )
    name = Column(String, nullable=False, index=True)
    bio = Column(String, nullable=True)
    email = Column(String, nullable=True)

    login_code = Column(String(6), unique=True, nullable=True, index=True)
    login_code_created_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    artworks = relationship("Artwork", back_populates="artist")
    devices = relationship("Device", back_populates="artist", cascade="all, delete-orphan")
    reaction_emojis = relationship("ArtistReactionEmoji", back_populates="artist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artist(id={self.id}, uuid={self.uuid}, name={self.name})>"
