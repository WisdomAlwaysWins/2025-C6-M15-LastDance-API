from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Exhibition(Base):
    """
    전시 모델
    """
    __tablename__ = "exhibitions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="전시 제목")
    description_text = Column(Text, nullable=True, comment="전시 설명")
    start_date = Column(Date, nullable=False, comment="전시 시작일")
    end_date = Column(Date, nullable=False, comment="전시 종료일")
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, comment="장소 ID")
    cover_image_url = Column(String(500), nullable=True, comment="포스터 이미지 URL")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    venue = relationship("Venue", back_populates="exhibitions")
    artists = relationship(
        "Artist",
        secondary="exhibition_artists",
        back_populates="exhibitions"
    )
    artworks = relationship("Artwork", back_populates="exhibition")
    visits = relationship("VisitHistory", back_populates="exhibition")

    def __repr__(self):
        return f"<Exhibition(id={self.id}, title='{self.title}')>"