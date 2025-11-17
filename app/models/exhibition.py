from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# M:N 중간 테이블
exhibition_artworks = Table(
    "exhibition_artworks",
    Base.metadata,
    Column("exhibition_id", Integer, ForeignKey("exhibitions.id"), primary_key=True),
    Column("artwork_id", Integer, ForeignKey("artworks.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


class Exhibition(Base):
    """
    전시 모델
    """

    __tablename__ = "exhibitions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description_text = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    cover_image_url = Column(String, nullable=True)  # 포스터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    venue = relationship("Venue", back_populates="exhibitions")
    artworks = relationship(
        "Artwork", secondary=exhibition_artworks, back_populates="exhibitions"
    )
    visits = relationship(
        "VisitHistory", back_populates="exhibition", cascade="all, delete-orphan"
    )
    invitations = relationship("Invitation", back_populates="exhibition", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<Exhibition(id={self.id}, title={self.title})>"
