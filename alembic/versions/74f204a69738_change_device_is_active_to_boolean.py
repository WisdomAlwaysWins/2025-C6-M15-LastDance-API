"""change device is_active to boolean

Revision ID: 74f204a69738
Revises: 773d0ad39b50
Create Date: 2025-11-12 14:28:28.356940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f204a69738'
down_revision: Union[str, None] = '773d0ad39b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Integer(0,1) → Boolean(True/False) 변환
    op.alter_column(
        'devices',
        'is_active',
        type_=sa.Boolean(),
        postgresql_using='is_active::boolean',
        existing_nullable=True,
        server_default='true'
    )


def downgrade() -> None:
    # Boolean → Integer 변환
    op.alter_column(
        'devices',
        'is_active',
        type_=sa.Integer(),
        postgresql_using='is_active::integer',
        existing_nullable=True,
        server_default='1'
    )
