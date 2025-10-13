from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Tag(Base):
    """
    감정 태그 모델 (시원해요, 슬퍼요 등)
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("tag_categories.id"), nullable=False) 
    name = Column(String, unique=True, nullable=False, index=True)
    display_order = Column(Integer, nullable=False, default=0)  

    # Relationships
    category = relationship("TagCategory", back_populates="tags")
    reactions = relationship("Reaction", secondary="reaction_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, category_id={self.category_id})>"