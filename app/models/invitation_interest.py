"""
InvitationInterest Model

초대장 관심 표현 모델 (갈게요)
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InvitationInterest(Base):
    """
    초대장 관심 표현 (갈게요)
    
    관람객 또는 작가가 초대장을 보고 '갈게요' 버튼을 눌렀을 때 기록
    (본인 전시는 제외)
    visitor_id와 artist_id 중 정확히 하나만 값이 있어야 함
    
    Attributes:
        id: 관심 표현 ID
        invitation_id: 초대장 ID
        visitor_id: 관람객 ID (FK, nullable)
        artist_id: 작가 ID (FK, nullable)
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
        nullable=True,
        index=True
    )
    
    artist_id = Column(
        Integer,
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=True,
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
    artist = relationship("Artist", back_populates="invitation_interests")
    
    # Constraints
    __table_args__ = (
        # visitor 또는 artist 둘 중 정확히 하나만 있어야 함
        CheckConstraint(
            '(visitor_id IS NOT NULL AND artist_id IS NULL) OR (visitor_id IS NULL AND artist_id IS NOT NULL)',
            name='ck_interest_user_type'
        ),
        # visitor 기준 unique
        UniqueConstraint('invitation_id', 'visitor_id', name='uq_interest_invitation_visitor'),
        # artist 기준 unique  
        UniqueConstraint('invitation_id', 'artist_id', name='uq_interest_invitation_artist'),
    )
    
    def __repr__(self):
        user_info = f"visitor_id={self.visitor_id}" if self.visitor_id else f"artist_id={self.artist_id}"
        return f"<InvitationInterest(id={self.id}, invitation_id={self.invitation_id}, {user_info})>"
    
    @property
    def user_uuid(self) -> str:
        """관람객 또는 작가의 user_uuid 반환"""
        if self.visitor_id:
            return self.visitor.user_uuid
        elif self.artist_id:
            return self.artist.user_uuid
        return ""