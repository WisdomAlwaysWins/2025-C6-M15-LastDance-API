from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base


# M:N 중간 테이블
reaction_tags = Table(
    'reaction_tags',
    Base.metadata,
    Column('reaction_id', Integer, ForeignKey('reactions.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)