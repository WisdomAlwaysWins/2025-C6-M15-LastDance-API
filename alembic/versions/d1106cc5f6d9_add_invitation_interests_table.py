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
    """
    초대장 관심 표현 (갈게요) 테이블 생성
    
    기능:
    - 관객이 초대장을 보고 "갈게요" 버튼 클릭 시 기록
    - invitation.view_count 자동 증가에 사용
    - 실제 전시 방문(visit_histories)과는 별개
    
    비즈니스 로직:
    1. 관객이 "갈게요" 클릭
    2. invitation_interests 레코드 생성
    3. invitation.view_count += 1
    4. 작가에게 푸시 알림 (향후 구현)
    
    제약 조건:
    - (invitation_id, visitor_id) unique
    - 한 관객은 한 초대장에 한 번만 "갈게요" 가능
    - 중복 시도 시 409 Conflict
    
    CASCADE 삭제:
    - invitation 삭제 시 관련 interests 자동 삭제
    - visitor 삭제 시 관련 interests 자동 삭제
    """
    # 1. invitation_interests 테이블 생성
    op.create_table(
        'invitation_interests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invitation_id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['invitation_id'], ['invitations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invitation_id', 'visitor_id', name='uq_interest_invitation_visitor')
    )
    
    # 2. 인덱스 생성
    op.create_index(op.f('ix_invitation_interests_id'), 'invitation_interests', ['id'], unique=False)
    op.create_index(op.f('ix_invitation_interests_invitation_id'), 'invitation_interests', ['invitation_id'], unique=False)
    op.create_index(op.f('ix_invitation_interests_visitor_id'), 'invitation_interests', ['visitor_id'], unique=False)


def downgrade() -> None:
    """
    초대장 관심 표현 테이블 삭제
    
    주의:
    - 모든 "갈게요" 기록 삭제됨
    - invitation.view_count는 유지됨 (별도 필드)
    """
    # 1. 인덱스 삭제
    op.drop_index(op.f('ix_invitation_interests_visitor_id'), table_name='invitation_interests')
    op.drop_index(op.f('ix_invitation_interests_invitation_id'), table_name='invitation_interests')
    op.drop_index(op.f('ix_invitation_interests_id'), table_name='invitation_interests')
    
    # 2. 테이블 삭제
    op.drop_table('invitation_interests')