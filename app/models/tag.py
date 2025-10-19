from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Tag(Base):
    """
    감정 태그 모델
    """

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("tag_categories.id"), nullable=False)
    name = Column(String, unique=True, nullable=False, index=True)
    color_hex = Column(String, nullable=True)

    # Relationships
    category = relationship("TagCategory", back_populates="tags")
    reactions = relationship(
        "Reaction", secondary="reaction_tags", back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, color_hex={self.color_hex})>"
