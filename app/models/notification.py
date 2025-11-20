"""
Notification Model
푸시 알림 기록 모델
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Notification(Base):
    """
    푸시 알림 기록
    
    작가와 관람객 간의 모든 푸시 알림을 기록하고 관리
    iOS 앱에서 알림 목록을 조회하고 읽음 처리할 수 있음
    
    Attributes:
        id: 알림 ID
        visitor_id: 관람객 ID (nullable, artist_id와 배타적)
        artist_id: 작가 ID (nullable, visitor_id와 배타적)
        notification_type: 알림 타입 ("reaction_to_artist", "artist_reply")
        title: 알림 제목
        body: 알림 본문
        reaction_id: 관련 반응 ID (필수)
        exhibition_id: 관련 전시 ID (선택)
        artwork_id: 관련 작품 ID (선택)
        visit_history_id: 관련 방문기록 ID (선택, 관람객용)
        is_read: 읽음 여부
        is_sent: 전송 여부
        created_at: 생성일시
        read_at: 읽은 일시
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 수신자 정보 (visitor 또는 artist 중 정확히 하나)
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
    
    # 알림 타입
    notification_type = Column(String(50), nullable=False, index=True)
    # "reaction_to_artist" - 작가에게: 관람객이 새 반응을 남김
    # "artist_reply" - 관람객에게: 작가가 반응에 응답함
    
    # 알림 내용
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    
    # 관련 엔티티 (어떤 반응에 대한 알림인지)
    reaction_id = Column(
        Integer, 
        ForeignKey("reactions.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # 선택적 관련 엔티티 (딥링크용 추가 정보)
    exhibition_id = Column(
        Integer, 
        ForeignKey("exhibitions.id", ondelete="CASCADE"), 
        nullable=True
    )
    artwork_id = Column(
        Integer, 
        ForeignKey("artworks.id", ondelete="CASCADE"), 
        nullable=True
    )
    visit_history_id = Column(
        Integer, 
        ForeignKey("visit_histories.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # 읽음 여부
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # 전송 여부 (APNs 전송 성공/실패)
    is_sent = Column(Boolean, default=False, nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    visitor = relationship("Visitor", back_populates="notifications")
    artist = relationship("Artist", back_populates="notifications")
    reaction = relationship("Reaction", back_populates="notifications")
    exhibition = relationship("Exhibition", back_populates="notifications")
    artwork = relationship("Artwork", back_populates="notifications")
    visits = relationship("VisitHistory", back_populates="notifications")
    
    # Constraints
    __table_args__ = (
        # visitor 또는 artist 둘 중 정확히 하나만 있어야 함
        CheckConstraint(
            '(visitor_id IS NOT NULL AND artist_id IS NULL) OR (visitor_id IS NULL AND artist_id IS NOT NULL)',
            name='ck_notification_user_type'
        ),
        # 복합 인덱스: 사용자별 읽지 않은 알림 조회 최적화
        Index('ix_notifications_user_unread', 'visitor_id', 'artist_id', 'is_read'),
        # 복합 인덱스: 사용자별 최신 알림 조회 최적화
        Index('ix_notifications_user_created', 'visitor_id', 'artist_id', 'created_at'),
    )
    
    def __repr__(self):
        user_info = f"visitor_id={self.visitor_id}" if self.visitor_id else f"artist_id={self.artist_id}"
        return f"<Notification(id={self.id}, type={self.notification_type}, {user_info}, is_read={self.is_read})>"