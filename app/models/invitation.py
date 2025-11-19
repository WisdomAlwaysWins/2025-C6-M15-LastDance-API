"""
Invitation Model

전시 초대장 모델
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Invitation(Base):
    """
    초대장 모델
    
    작가가 특정 전시에 대한 초대장을 생성하여 관객에게 공유
    
    Attributes:
        id: 초대장 ID
        code: 고유 UUID 코드 (링크용)
        artist_id: 작가 ID
        exhibition_id: 전시 ID
        message: 초대 메시지 (최대 20자)
        view_count: 실제 방문한 고유 관람객 수
        created_at: 생성일시
        updated_at: 수정일시
    """
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # UUID 코드 (딥링크용)
    code = Column(
        String, 
        unique=True, 
        nullable=False, 
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # 작가 & 전시
    artist_id = Column(
        Integer, 
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    exhibition_id = Column(
        Integer,
        ForeignKey("exhibitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 초대 메시지 (최대 20자)
    message = Column(String(20), nullable =True)
    
    # 통계 (실제 방문한 고유 관람객 수)
    view_count = Column(Integer, default=0, nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    artist = relationship("Artist", back_populates="invitations")
    exhibition = relationship("Exhibition", back_populates="invitations")
    interests = relationship("InvitationInterest", back_populates="invitation", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('exhibition_id', 'artist_id', name='uq_invitation_exhibition_artist'),
    )

    def __repr__(self):
        return f"<Invitation(id={self.id}, code={self.code[:8]}..., exhibition_id={self.exhibition_id})>"