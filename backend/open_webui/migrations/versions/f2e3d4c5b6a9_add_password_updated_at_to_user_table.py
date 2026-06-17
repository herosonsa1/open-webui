"""user 테이블에 password_updated_at 컬럼 추가 및 데이터 복사

Revision ID: f2e3d4c5b6a9
Revises: f2e3d4c5b6a8
Create Date: 2026-06-17 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# 리비전 식별자
revision = 'f2e3d4c5b6a9'
down_revision = 'f2e3d4c5b6a8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. user 테이블 컬럼 검사 및 password_updated_at 컬럼 추가
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'password_updated_at' not in columns:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('password_updated_at', sa.BigInteger(), nullable=True))
            
    # 2. auth 테이블의 기존 password_updated_at 데이터를 user 테이블로 복사
    conn.execute(
        sa.text(
            """
            UPDATE user 
            SET password_updated_at = (
                SELECT password_updated_at 
                FROM auth 
                WHERE auth.id = user.id
            )
            WHERE EXISTS (
                SELECT 1 
                FROM auth 
                WHERE auth.id = user.id AND auth.password_updated_at IS NOT NULL
            )
            """
        )
    )


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('password_updated_at')
