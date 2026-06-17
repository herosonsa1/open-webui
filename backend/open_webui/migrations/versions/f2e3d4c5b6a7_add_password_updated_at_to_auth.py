"""auth 테이블에 password_updated_at 컬럼 추가 및 기존 데이터 마이그레이션

Revision ID: f2e3d4c5b6a7
Revises: 461111b60977
Create Date: 2026-06-17 00:00:00.000000

"""

import time
import sqlalchemy as sa
from alembic import op

# 리비전 식별자
revision = 'f2e3d4c5b6a7'
down_revision = '461111b60977'
branch_labels = None
depends_on = None


def upgrade():
    # auth 테이블에 password_updated_at 컬럼 추가
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('auth')]
    
    if 'password_updated_at' not in columns:
        with op.batch_alter_table('auth', schema=None) as batch_op:
            batch_op.add_column(sa.Column('password_updated_at', sa.Integer(), nullable=True))
            
    # 기존에 비밀번호를 가지고 있지만 password_updated_at이 비어 있는 레코드에 현재 Unix timestamp를 주입하여 즉시 만기되는 현상을 예방함
    now = int(time.time())
    conn.execute(
        sa.text(
            "UPDATE auth SET password_updated_at = :now WHERE password_updated_at IS NULL AND password IS NOT NULL"
        ),
        {"now": now}
    )


def downgrade():
    with op.batch_alter_table('auth', schema=None) as batch_op:
        batch_op.drop_column('password_updated_at')
