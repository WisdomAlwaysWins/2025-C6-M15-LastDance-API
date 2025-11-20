from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# M:N 중간 테이블
reaction_tags = Table(
    "reaction_tags",
    Base.metadata,
    Column("reaction_id", Integer, ForeignKey("reactions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Reaction(Base):
    """
    작품에 대한 반응/평가 모델 (기존 Review에서 변경)
    """

    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("visit_histories.id"), nullable=True)
    image_url = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    artwork = relationship("Artwork", back_populates="reactions")
    visitor = relationship("Visitor", back_populates="reactions")
    visit = relationship("VisitHistory", back_populates="reactions")
    tags = relationship("Tag", secondary=reaction_tags, back_populates="reactions")
    artist_emojis = relationship("ArtistReactionEmoji", back_populates="reaction", cascade="all, delete-orphan") 
    artist_messages = relationship("ArtistReactionMessage", back_populates="reaction", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="reaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reaction(id={self.id}, artwork_id={self.artwork_id}, visitor_id={self.visitor_id})>"