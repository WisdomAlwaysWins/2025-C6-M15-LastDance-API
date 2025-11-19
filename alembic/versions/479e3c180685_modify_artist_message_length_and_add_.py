"""modify artist message length and add artist to invitation interest

Revision ID: 479e3c180685
Revises: d1106cc5f6d9
Create Date: 2025-11-19 16:08:26.001156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '479e3c180685'
down_revision: Union[str, None] = 'd1106cc5f6d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. artist_reaction_messages.message: String -> Text
    op.alter_column('artist_reaction_messages', 'message',
                    type_=sa.Text(),
                    existing_type=sa.String(),
                    existing_nullable=False)
    
    # 2. invitation_interests에 artist_id 추가
    op.add_column('invitation_interests', sa.Column('artist_id', sa.Integer(), nullable=True))
    
    # 3. artist_id FK 추가
    op.create_foreign_key(
        'fk_invitation_interests_artist_id',
        'invitation_interests', 'artists',
        ['artist_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # 4. artist_id 인덱스 추가
    op.create_index(
        'ix_invitation_interests_artist_id',
        'invitation_interests',
        ['artist_id']
    )
    
    # 5. visitor_id nullable로 변경
    op.alter_column('invitation_interests', 'visitor_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # 6. CheckConstraint 추가 (visitor_id, artist_id 중 하나만)
    op.create_check_constraint(
        'ck_interest_user_type',
        'invitation_interests',
        '(visitor_id IS NOT NULL AND artist_id IS NULL) OR (visitor_id IS NULL AND artist_id IS NOT NULL)'
    )
    
    # 7. 기존 UniqueConstraint 삭제
    op.drop_constraint('uq_interest_invitation_visitor', 'invitation_interests', type_='unique')
    
    # 8. 새로운 UniqueConstraint 추가 (visitor, artist 각각)
    op.create_unique_constraint(
        'uq_interest_invitation_visitor',
        'invitation_interests',
        ['invitation_id', 'visitor_id']
    )
    op.create_unique_constraint(
        'uq_interest_invitation_artist',
        'invitation_interests',
        ['invitation_id', 'artist_id']
    )


def downgrade() -> None:
    # 8. UniqueConstraint 삭제
    op.drop_constraint('uq_interest_invitation_artist', 'invitation_interests', type_='unique')
    op.drop_constraint('uq_interest_invitation_visitor', 'invitation_interests', type_='unique')
    
    # 7. 기존 UniqueConstraint 복원
    op.create_unique_constraint(
        'uq_interest_invitation_visitor',
        'invitation_interests',
        ['invitation_id', 'visitor_id']
    )
    
    # 6. CheckConstraint 삭제
    op.drop_constraint('ck_interest_user_type', 'invitation_interests', type_='check')
    
    # 5. visitor_id nullable=False로 복원
    op.alter_column('invitation_interests', 'visitor_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # 4. artist_id 인덱스 삭제
    op.drop_index('ix_invitation_interests_artist_id', 'invitation_interests')
    
    # 3. artist_id FK 삭제
    op.drop_constraint('fk_invitation_interests_artist_id', 'invitation_interests', type_='foreignkey')
    
    # 2. artist_id 컬럼 삭제
    op.drop_column('invitation_interests', 'artist_id')
    
    # 1. artist_reaction_messages.message: Text -> String
    op.alter_column('artist_reaction_messages', 'message',
                    type_=sa.String(),
                    existing_type=sa.Text(),
                    existing_nullable=False)