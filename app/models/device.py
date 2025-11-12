# app/models/device.py
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Device(Base):
    """
    디바이스 토큰 모델

    관람객(Visitor) 또는 작가(Artist)의 iOS 기기 정보 저장

    Attributes:
        id: 디바이스 ID
        visitor_id: 관람객 ID (선택)
        artist_id: 작가 ID (선택)
        device_token: APNs 디바이스 토큰 (고유값)
        is_active: 활성 상태
        created_at: 등록 일시
        updated_at: 수정 일시

    Note:
        visitor_id와 artist_id 중 하나는 필수
    """

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=True)

    device_token = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    visitor = relationship("Visitor", back_populates="devices")
    artist = relationship("Artist", back_populates="devices")