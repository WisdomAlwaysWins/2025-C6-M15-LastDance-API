"""add artist login_code

Revision ID: 98dd0620d0c3
Revises: 74f204a69738
Create Date: 2025-11-13 22:24:37.002654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
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
    # 컬럼 존재 여부 확인 (멱등성 보장)
    connection = op.get_bind()
    inspector = inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('artists')]
    
    # login_code가 없으면 추가
    if 'login_code' not in columns:
        op.add_column('artists', sa.Column('login_code', sa.String(length=6), nullable=True))
        op.add_column('artists', sa.Column('login_code_created_at', sa.TIMESTAMP(timezone=True), nullable=True))
        op.create_index('ix_artists_login_code', 'artists', ['login_code'], unique=True)
        
        # 기존 작가들에게 코드 생성
        result = connection.execute(sa.text("SELECT id FROM artists"))
        artist_ids = [row[0] for row in result]
        
        used_codes = set()
        for artist_id in artist_ids:
            code = generate_login_code()
            
            while code in used_codes:
                code = generate_login_code()
            
            used_codes.add(code)
            
            connection.execute(
                sa.text(
                    "UPDATE artists SET login_code = :code, login_code_created_at = NOW() WHERE id = :id"
                ),
                {"code": code, "id": artist_id}
            )


def downgrade() -> None:
    # 인덱스/컬럼 존재 여부 확인 후 삭제 (멱등성 보장)
    connection = op.get_bind()
    inspector = inspect(connection)
    
    # 인덱스 확인
    indexes = [idx['name'] for idx in inspector.get_indexes('artists')]
    if 'ix_artists_login_code' in indexes:
        op.drop_index('ix_artists_login_code', table_name='artists')
    
    # 컬럼 확인
    columns = [col['name'] for col in inspector.get_columns('artists')]
    if 'login_code_created_at' in columns:
        op.drop_column('artists', 'login_code_created_at')
    if 'login_code' in columns:
        op.drop_column('artists', 'login_code')