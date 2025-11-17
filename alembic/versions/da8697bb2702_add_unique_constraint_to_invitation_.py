"""add unique constraint to invitation exhibition artist

Revision ID: da8697bb2702
Revises: 2888419d448f
Create Date: 2025-11-17 20:15:56.984010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da8697bb2702'
down_revision: Union[str, None] = '2888419d448f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_invitation_exhibition_artist',
        'invitations',
        ['exhibition_id', 'artist_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_invitation_exhibition_artist',
        'invitations',
        type_='unique'
    )
