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
    """
    초대장 중복 생성 방지 제약 조건 추가
    
    제약 조건:
    - (exhibition_id, artist_id) 조합이 unique해야 함
    - 즉, 한 작가가 같은 전시에 대해 초대장을 1개만 생성 가능
    
    비즈니스 규칙:
    - 작가는 전시당 최대 1개의 초대장만 생성 가능
    - 중복 생성 시도 시 API에서 409 Conflict 에러 반환
    
    예외 케이스:
    - 작가 A가 전시 X에 초대장 생성: ✅ OK
    - 작가 A가 전시 Y에 초대장 생성: ✅ OK (다른 전시)
    - 작가 B가 전시 X에 초대장 생성: ✅ OK (다른 작가)
    - 작가 A가 전시 X에 초대장 재생성: ❌ DB Constraint 위반
    """
    op.create_unique_constraint(
        'uq_invitation_exhibition_artist',
        'invitations',
        ['exhibition_id', 'artist_id']
    )


def downgrade() -> None:
    """
    초대장 중복 방지 제약 조건 제거
    
    주의: 롤백 후 중복 초대장 생성 가능해짐
    """
    op.drop_constraint(
        'uq_invitation_exhibition_artist',
        'invitations',
        type_='unique'
    )