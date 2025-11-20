from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Visitor(Base):
    """
    관람객 모델
    """

    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, nullable=False, index=True)  # iOS 생성
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    visits = relationship(
        "VisitHistory", back_populates="visitor", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "Reaction", back_populates="visitor", cascade="all, delete-orphan"
    )
    devices = relationship(
        "Device", back_populates="visitor", cascade="all, delete-orphan"
    )
    invitation_interests = relationship(
        "InvitationInterest", back_populates="visitor", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="visitor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Visitor(id={self.id}, uuid={self.uuid}, name={self.name})>"