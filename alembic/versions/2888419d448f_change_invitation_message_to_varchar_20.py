"""change invitation message to varchar 20

Revision ID: 2888419d448f
Revises: c98a94a8118d
Create Date: 2025-11-17 12:27:50.857063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2888419d448f'
down_revision: Union[str, None] = 'c98a94a8118d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    초대장 메시지 길이 제한 추가
    
    변경사항:
    - invitations.message: TEXT → VARCHAR(20)
    
    이유:
    - UI/UX 요구사항: 초대 메시지 최대 20자 제한
    - 데이터 무결성: DB 레벨에서 길이 제한 강제
    
    주의: 기존 20자 초과 메시지는 잘림 (현재 데이터 없음)
    """
    op.alter_column('invitations', 'message',
               existing_type=sa.TEXT(),
               type_=sa.String(length=20),
               existing_nullable=True)


def downgrade() -> None:
    """
    초대장 메시지 길이 제한 제거
    
    VARCHAR(20) → TEXT로 롤백
    """
    op.alter_column('invitations', 'message',
               existing_type=sa.String(length=20),
               type_=sa.TEXT(),
               existing_nullable=True)