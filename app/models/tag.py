from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Tag(Base):
    """감정 태그 모델 (시원해요, 슬퍼요 등)"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="태그 이름")

    # 관계 (다대다 중간 테이블을 통해 Review와 연결)
    reviews = relationship("Review", secondary="review_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"