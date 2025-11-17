"""create invitations table

Revision ID: c98a94a8118d
Revises: a55ffd0a7764
Create Date: 2025-11-17 12:06:31.137681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c98a94a8118d'
down_revision: Union[str, None] = 'a55ffd0a7764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    초대장 테이블 생성 및 visit_histories 연관 추가
    
    초대장(Invitation):
    - 작가가 전시에 대한 초대장 생성
    - UUID 기반 딥링크 지원 (lastdance://invitation/{code})
    - 관객 방문 통계 추적 (view_count)
    
    변경사항:
    1. invitations 테이블 생성
    2. visit_histories에 invitation_id 외래키 추가 (nullable)
       - 초대장 없이도 전시 방문 가능
    """
    # 1. invitations 테이블 생성
    op.create_table('invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('exhibition_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exhibition_id'], ['exhibitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. 인덱스 생성
    op.create_index(op.f('ix_invitations_id'), 'invitations', ['id'], unique=False)
    op.create_index(op.f('ix_invitations_code'), 'invitations', ['code'], unique=True)
    op.create_index(op.f('ix_invitations_artist_id'), 'invitations', ['artist_id'], unique=False)
    op.create_index(op.f('ix_invitations_exhibition_id'), 'invitations', ['exhibition_id'], unique=False)
    
    # 3. visit_histories에 invitation_id 추가
    op.add_column('visit_histories', sa.Column('invitation_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'visit_histories', 'invitations', ['invitation_id'], ['id'])


def downgrade() -> None:
    """
    초대장 테이블 및 관련 변경사항 롤백
    
    주의: 초대장 데이터 및 visit_histories의 invitation 연관 정보 삭제됨
    """
    # 1. visit_histories 변경 롤백
    op.drop_constraint(None, 'visit_histories', type_='foreignkey')
    op.drop_column('visit_histories', 'invitation_id')
    
    # 2. invitations 테이블 삭제
    op.drop_index(op.f('ix_invitations_exhibition_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_artist_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_code'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_id'), table_name='invitations')
    op.drop_table('invitations')