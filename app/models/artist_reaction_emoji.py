"""
ArtistReactionEmoji Model
작가가 반응에 남긴 이모지
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ArtistReactionEmoji(Base):
    """작가 반응 이모지"""

    __tablename__ = "artist_reaction_emojis"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    reaction_id = Column(
        Integer, ForeignKey("reactions.id", ondelete="CASCADE"), nullable=False
    )
    emoji_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    artist = relationship("Artist", back_populates="reaction_emojis")
    reaction = relationship("Reaction", back_populates="artist_emojis")

    # 제약: 작가당 반응당 1개 이모지만
    __table_args__ = (
        UniqueConstraint("artist_id", "reaction_id", name="uq_artist_reaction_emoji"),
    )
