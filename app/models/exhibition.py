from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Exhibition(Base):
    """전시 모델"""
    __tablename__ = "exhibitions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 전시 기본 정보
    title = Column(String(255), nullable=False, comment="전시 제목")
    description = Column(Text, nullable=True, comment="전시 설명")
    location = Column(String(255), nullable=True, comment="전시 장소")
    
    # 전시 포스터 (S3 URL)
    poster_url = Column(String(500), nullable=True, comment="전시 포스터 이미지 URL (S3)")
    
    # 참여 작가 리스트 (배열로 저장)
    artist_names = Column(ARRAY(String), nullable=True, comment="참여 작가 이름 리스트")
    
    # 전시 기간
    start_date = Column(Date, nullable=False, comment="전시 시작일")
    end_date = Column(Date, nullable=False, comment="전시 종료일")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 일시")

    # 관계
    artworks = relationship("Artwork", back_populates="exhibition", cascade="all, delete-orphan")
    visit_histories = relationship("VisitHistory", back_populates="exhibition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exhibition(id={self.id}, title='{self.title}')>"