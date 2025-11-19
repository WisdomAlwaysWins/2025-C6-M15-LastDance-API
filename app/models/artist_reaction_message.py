"""
ArtistReactionMessage Model
작가가 반응에 남긴 메시지
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ArtistReactionMessage(Base):
    """작가 반응 메시지"""
    __tablename__ = "artist_reaction_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    reaction_id = Column(Integer, ForeignKey("reactions.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    artist = relationship("Artist", back_populates="reaction_messages")
    reaction = relationship("Reaction", back_populates="artist_messages")
    
    # Indexes
    __table_args__ = (
        Index('ix_artist_reaction_messages_reaction_id', 'reaction_id'),
        Index('ix_artist_reaction_messages_artist_id', 'artist_id'),
    )