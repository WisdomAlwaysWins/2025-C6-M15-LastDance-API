from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Venue(Base):
    """
    전시 장소 모델
    """

    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    geo_lat = Column(Float, nullable=True)  # 위도
    geo_lon = Column(Float, nullable=True)  # 경도
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    exhibitions = relationship("Exhibition", back_populates="venue")

    def __repr__(self):
        return f"<Venue(id={self.id}, name={self.name})>"
