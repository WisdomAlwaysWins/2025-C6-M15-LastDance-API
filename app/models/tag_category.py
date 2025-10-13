from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TagCategory(Base):
    """
    태그 카테고리 모델
    """
    __tablename__ = "tag_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    color_hex = Column(String, nullable=False)  # #RRGGBB 형식
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tags = relationship("Tag", back_populates="category")

    def __repr__(self):
        return f"<TagCategory(id={self.id}, name={self.name}, color_hex={self.color_hex})>"