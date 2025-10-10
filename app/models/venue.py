from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Venue(Base):
    """
    장소 모델
    전시가 열리는 미술관, 갤러리 등
    """
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="장소 이름")
    address = Column(String(500), nullable=True, comment="주소")
    geo_lat = Column(Float, nullable=True, comment="위도")
    geo_lon = Column(Float, nullable=True, comment="경도")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 관계
    exhibitions = relationship("Exhibition", back_populates="venue")

    def __repr__(self):
        return f"<Venue(id={self.id}, name='{self.name}')>"