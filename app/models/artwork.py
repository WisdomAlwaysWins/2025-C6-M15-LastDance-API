from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Artwork(Base):
    """작품 모델"""
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="작품 제목")
    artist_name = Column(String(100), nullable=False, comment="작가 이름")
    description = Column(Text, nullable=True, comment="작품 설명")
    year = Column(Integer, nullable=True, comment="제작 연도")
    
    # S3에 저장된 원본 이미지 URL
    image_url = Column(String(500), nullable=False, comment="작품 원본 이미지 URL (S3)")
    
    # 외래키
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id", ondelete="CASCADE"), nullable=False, comment="전시 ID")

    # 관계
    exhibition = relationship("Exhibition", back_populates="artworks")
    reviews = relationship("Review", back_populates="artwork", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artwork(id={self.id}, title='{self.title}', artist='{self.artist_name}')>"