from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from datetime import datetime
from app.database import Base


# M:N 중간 테이블
exhibition_artists = Table(
    'exhibition_artists',
    Base.metadata,
    Column('exhibition_id', Integer, ForeignKey('exhibitions.id', ondelete='CASCADE'), primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False)
)