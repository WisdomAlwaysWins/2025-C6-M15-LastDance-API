"""create artist_reaction_emojis table

Revision ID: ec88694824bf
Revises: 98dd0620d0c3
Create Date: 2025-11-13 22:58:02.943139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'ec88694824bf'
down_revision: Union[str, None] = '98dd0620d0c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 테이블 존재 여부 확인 (멱등성 보장)
    connection = op.get_bind()
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    
    if 'artist_reaction_emojis' not in tables:
        # artist_reaction_emojis 테이블 생성
        op.create_table(
            'artist_reaction_emojis',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('artist_id', sa.Integer(), nullable=False),
            sa.Column('reaction_id', sa.Integer(), nullable=False),
            sa.Column('emoji_type', sa.String(length=20), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['reaction_id'], ['reactions.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('artist_id', 'reaction_id', name='uq_artist_reaction_emoji')
        )
        
        # 인덱스 생성
        op.create_index('ix_artist_reaction_emojis_id', 'artist_reaction_emojis', ['id'])
        op.create_index('ix_artist_reaction_emojis_reaction_id', 'artist_reaction_emojis', ['reaction_id'])
        op.create_index('ix_artist_reaction_emojis_artist_id', 'artist_reaction_emojis', ['artist_id'])


def downgrade() -> None:
    # 테이블 존재 여부 확인 후 삭제 (멱등성 보장)
    connection = op.get_bind()
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    
    if 'artist_reaction_emojis' in tables:
        op.drop_index('ix_artist_reaction_emojis_artist_id', table_name='artist_reaction_emojis')
        op.drop_index('ix_artist_reaction_emojis_reaction_id', table_name='artist_reaction_emojis')
        op.drop_index('ix_artist_reaction_emojis_id', table_name='artist_reaction_emojis')
        op.drop_table('artist_reaction_emojis')