from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# M:N 중간 테이블
exhibition_artists = Table(
    'exhibition_artists',
    Base.metadata,
    Column('exhibition_id', Integer, ForeignKey('exhibitions.id'), primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
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
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)  # 🆕 추가
    cover_image_url = Column(String, nullable=True)  # 포스터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    venue = relationship("Venue", back_populates="exhibitions")  # 🆕 추가
    artists = relationship("Artist", secondary=exhibition_artists, back_populates="exhibitions")  # 🆕 추가
    artworks = relationship("Artwork", back_populates="exhibition", cascade="all, delete-orphan")
    visits = relationship("VisitHistory", back_populates="exhibition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exhibition(id={self.id}, title={self.title})>"