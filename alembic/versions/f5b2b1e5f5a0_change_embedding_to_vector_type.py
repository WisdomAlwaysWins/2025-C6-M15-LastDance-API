"""change_embedding_to_vector_type

Revision ID: f5b2b1e5f5a0
Revises: 6de492bde999
Create Date: 2025-11-10 14:15:35.542016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'f5b2b1e5f5a0'
down_revision: Union[str, None] = '6de492bde999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
        # 1. pgvector extension 활성화 (이미 있지만 안전하게)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # 2. 기존 ARRAY(Float) 컬럼 삭제
    op.drop_column('artworks', 'embedding')
    
    # 3. Vector(384) 타입으로 새로 생성
    op.add_column('artworks',
        sa.Column('embedding', Vector(384), nullable=True)
    )
    
    # 4. ivfflat 인덱스 생성 (유사도 검색 최적화)
    op.execute("""
        CREATE INDEX artworks_embedding_idx 
        ON artworks 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    # 롤백: 원래대로 되돌리기
    op.drop_index('artworks_embedding_idx', table_name='artworks')
    op.drop_column('artworks', 'embedding')
    op.add_column('artworks',
        sa.Column('embedding', sa.ARRAY(sa.Float), nullable=True)
    )
