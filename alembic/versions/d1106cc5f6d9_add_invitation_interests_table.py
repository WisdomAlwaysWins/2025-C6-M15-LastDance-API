"""add invitation interests table

Revision ID: d1106cc5f6d9
Revises: da8697bb2702
Create Date: 2025-11-17 20:46:02.333939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1106cc5f6d9'
down_revision: Union[str, None] = 'da8697bb2702'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
        # invitation_interests 테이블 생성
    op.create_table(
        'invitation_interests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invitation_id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['invitation_id'], ['invitations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('invitation_id', 'visitor_id', name='uq_interest_invitation_visitor')
    )
    
    # 인덱스 생성
    op.create_index(op.f('ix_invitation_interests_id'), 'invitation_interests', ['id'], unique=False)
    op.create_index(op.f('ix_invitation_interests_invitation_id'), 'invitation_interests', ['invitation_id'], unique=False)
    op.create_index(op.f('ix_invitation_interests_visitor_id'), 'invitation_interests', ['visitor_id'], unique=False)


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index(op.f('ix_invitation_interests_user_uuid'), table_name='invitation_interests')
    op.drop_index(op.f('ix_invitation_interests_invitation_id'), table_name='invitation_interests')
    op.drop_index(op.f('ix_invitation_interests_id'), table_name='invitation_interests')
    
    # 테이블 삭제
    op.drop_table('invitation_interests')
