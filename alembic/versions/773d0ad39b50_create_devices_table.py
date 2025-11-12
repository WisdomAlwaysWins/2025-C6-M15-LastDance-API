"""create devices table

Revision ID: 773d0ad39b50
Revises: f5b2b1e5f5a0
Create Date: 2025-11-12 01:41:03.946796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '773d0ad39b50'
down_revision: Union[str, None] = 'f5b2b1e5f5a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=True),
        sa.Column('artist_id', sa.Integer(), nullable=True),
        sa.Column('device_token', sa.String(255), nullable=False),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('app_version', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_token')
    )
    
    op.create_index('idx_devices_visitor_id', 'devices', ['visitor_id'])
    op.create_index('idx_devices_artist_id', 'devices', ['artist_id'])
    op.create_index('idx_devices_is_active', 'devices', ['is_active'])


def downgrade() -> None:
    op.drop_index('idx_devices_is_active', table_name='devices')
    op.drop_index('idx_devices_artist_id', table_name='devices')
    op.drop_index('idx_devices_visitor_id', table_name='devices')
    op.drop_table('devices')
