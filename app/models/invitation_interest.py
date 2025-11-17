"""
InvitationInterest Model

초대장 관심 표현 모델 (갈게요)
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InvitationInterest(Base):
    """
    초대장 관심 표현 (갈게요)
    
    관객이 초대장을 보고 '갈게요' 버튼을 눌렀을 때 기록
    실제 방문과 별개로, 방문 의사만 표현
    
    Attributes:
        id: 관심 표현 ID
        invitation_id: 초대장 ID
        visitor_id: 관람객 ID (FK)
        created_at: 생성일시 (갈게요 누른 시간)
    """
    __tablename__ = "invitation_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    invitation_id = Column(
        Integer,
        ForeignKey("invitations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    visitor_id = Column(
        Integer,
        ForeignKey("visitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    invitation = relationship("Invitation", back_populates="interests")
    visitor = relationship("Visitor", back_populates="invitation_interests")
    
    # Unique constraint: 한 관객은 한 초대장에 한 번만 갈게요 가능
    __table_args__ = (
        UniqueConstraint(
            'invitation_id',
            'visitor_id',
            name='uq_interest_invitation_visitor'
        ),
    )
    
    def __repr__(self):
        return f"<InvitationInterest(id={self.id}, invitation_id={self.invitation_id}, visitor_id={self.visitor_id})>"