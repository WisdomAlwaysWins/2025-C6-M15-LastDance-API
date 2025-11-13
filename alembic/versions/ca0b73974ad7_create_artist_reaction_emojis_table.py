"""create artist_reaction_emojis table

Revision ID: ca0b73974ad7
Revises: ec88694824bf
Create Date: 2025-11-13 23:19:07.161121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca0b73974ad7'
down_revision: Union[str, None] = 'ec88694824bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
