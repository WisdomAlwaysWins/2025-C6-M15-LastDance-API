"""add notification model

Revision ID: 93eba08617ec
Revises: 479e3c180685
Create Date: 2025-11-20 16:05:53.920263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93eba08617ec'
down_revision: Union[str, None] = '479e3c180685'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # notifications 테이블 생성
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=True),
        sa.Column('artist_id', sa.Integer(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('reaction_id', sa.Integer(), nullable=False),
        sa.Column('exhibition_id', sa.Integer(), nullable=True),
        sa.Column('artwork_id', sa.Integer(), nullable=True),
        sa.Column('visit_history_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 인덱스 생성
    op.create_index('ix_notifications_id', 'notifications', ['id'])
    op.create_index('ix_notifications_visitor_id', 'notifications', ['visitor_id'])
    op.create_index('ix_notifications_artist_id', 'notifications', ['artist_id'])
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'])
    op.create_index('ix_notifications_reaction_id', 'notifications', ['reaction_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    
    # 복합 인덱스 (사용자별 읽지 않은 알림 조회 최적화)
    op.create_index('ix_notifications_user_unread', 'notifications', ['visitor_id', 'artist_id', 'is_read'])
    
    # 복합 인덱스 (사용자별 최신 알림 조회 최적화)
    op.create_index('ix_notifications_user_created', 'notifications', ['visitor_id', 'artist_id', 'created_at'])
    
    # Foreign Key 제약 조건
    op.create_foreign_key(
        'fk_notifications_visitor_id',
        'notifications', 'visitors',
        ['visitor_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_notifications_artist_id',
        'notifications', 'artists',
        ['artist_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_notifications_reaction_id',
        'notifications', 'reactions',
        ['reaction_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_notifications_exhibition_id',
        'notifications', 'exhibitions',
        ['exhibition_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_notifications_artwork_id',
        'notifications', 'artworks',
        ['artwork_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_notifications_visit_history_id',
        'notifications', 'visit_histories',
        ['visit_history_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # CheckConstraint (visitor_id 또는 artist_id 중 정확히 하나만)
    op.create_check_constraint(
        'ck_notification_user_type',
        'notifications',
        '(visitor_id IS NOT NULL AND artist_id IS NULL) OR (visitor_id IS NULL AND artist_id IS NOT NULL)'
    )


def downgrade() -> None:
    # CheckConstraint 삭제
    op.drop_constraint('ck_notification_user_type', 'notifications', type_='check')
    
    # Foreign Key 제약 조건 삭제
    op.drop_constraint('fk_notifications_visit_history_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_artwork_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_exhibition_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_reaction_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_artist_id', 'notifications', type_='foreignkey')
    op.drop_constraint('fk_notifications_visitor_id', 'notifications', type_='foreignkey')
    
    # 인덱스 삭제
    op.drop_index('ix_notifications_user_created', 'notifications')
    op.drop_index('ix_notifications_user_unread', 'notifications')
    op.drop_index('ix_notifications_is_read', 'notifications')
    op.drop_index('ix_notifications_reaction_id', 'notifications')
    op.drop_index('ix_notifications_notification_type', 'notifications')
    op.drop_index('ix_notifications_artist_id', 'notifications')
    op.drop_index('ix_notifications_visitor_id', 'notifications')
    op.drop_index('ix_notifications_id', 'notifications')
    
    # 테이블 삭제
    op.drop_table('notifications')