"""create artist_reaction_messages table

Revision ID: a55ffd0a7764
Revises: ca0b73974ad7
Create Date: 2025-11-13 23:30:26.000629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a55ffd0a7764'
down_revision: Union[str, None] = 'ca0b73974ad7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # artist_reaction_messages 테이블 생성
    op.create_table(
        'artist_reaction_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('reaction_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reaction_id'], ['reactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 인덱스 생성
    op.create_index('ix_artist_reaction_messages_id', 'artist_reaction_messages', ['id'])
    op.create_index('ix_artist_reaction_messages_reaction_id', 'artist_reaction_messages', ['reaction_id'])
    op.create_index('ix_artist_reaction_messages_artist_id', 'artist_reaction_messages', ['artist_id'])


def downgrade() -> None:
    op.drop_index('ix_artist_reaction_messages_artist_id', table_name='artist_reaction_messages')
    op.drop_index('ix_artist_reaction_messages_reaction_id', table_name='artist_reaction_messages')
    op.drop_index('ix_artist_reaction_messages_id', table_name='artist_reaction_messages')
    op.drop_table('artist_reaction_messages')
