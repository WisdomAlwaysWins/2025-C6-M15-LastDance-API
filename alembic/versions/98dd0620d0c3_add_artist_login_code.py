"""add artist login_code

Revision ID: 98dd0620d0c3
Revises: 74f204a69738
Create Date: 2025-11-13 22:24:37.002654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import random
import string


# revision identifiers, used by Alembic.
revision: str = '98dd0620d0c3'
down_revision: Union[str, None] = '74f204a69738'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generate_login_code():
    """6자리 로그인 코드 생성"""
    digits = string.digits
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    special = "!@#$%^&*"
    
    all_chars = digits + lowercase + uppercase + special
    
    code = [
        random.choice(digits),
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(special),
    ]
    
    for _ in range(2):
        code.append(random.choice(all_chars))
    
    random.shuffle(code)
    return ''.join(code)


def upgrade() -> None:
    # login_code 컬럼 추가
    op.add_column('artists', sa.Column('login_code', sa.String(length=6), nullable=True))
    op.add_column('artists', sa.Column('login_code_created_at', sa.TIMESTAMP(timezone=True), nullable=True))
    
    # 인덱스 추가
    op.create_index('ix_artists_login_code', 'artists', ['login_code'], unique=True)

    connection = op.get_bind()

        # 기존 작가 조회
    result = connection.execute(sa.text("SELECT id FROM artists"))
    artist_ids = [row[0] for row in result]
    
    # 각 작가에게 유니크한 코드 생성
    used_codes = set()
    for artist_id in artist_ids:
        code = generate_login_code()
        
        # 중복 방지
        while code in used_codes:
            code = generate_login_code()
        
        used_codes.add(code)
        
        # 코드 업데이트
        connection.execute(
            sa.text(
                "UPDATE artists SET login_code = :code, login_code_created_at = NOW() WHERE id = :id"
            ),
            {"code": code, "id": artist_id}
        )
    
    connection.commit()


def downgrade() -> None:
    op.drop_index('ix_artists_login_code', table_name='artists')
    op.drop_column('artists', 'login_code_created_at')
    op.drop_column('artists', 'login_code')
