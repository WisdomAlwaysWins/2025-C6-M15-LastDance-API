from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# 다대다 관계를 위한 중간 테이블
review_tags = Table(
    'review_tags',
    Base.metadata,
    Column('review_id', Integer, ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Review(Base):
    """작품 평가 모델"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # 관람객이 찍은 사진 URL (S3)
    photo_url = Column(String(500), nullable=False, comment="관람객이 촬영한 작품 사진 URL (S3)")
    
    # 텍스트 평가 (선택)
    text_review = Column(Text, nullable=True, comment="텍스트 평가 (선택)")
    
    # 외래키
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="사용자 ID")
    artwork_id = Column(Integer, ForeignKey("artworks.id", ondelete="CASCADE"), nullable=False, comment="작품 ID")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 일시")

    # 관계
    user = relationship("User", back_populates="reviews")
    artwork = relationship("Artwork", back_populates="reviews")
    tags = relationship("Tag", secondary=review_tags, back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, artwork_id={self.artwork_id})>"