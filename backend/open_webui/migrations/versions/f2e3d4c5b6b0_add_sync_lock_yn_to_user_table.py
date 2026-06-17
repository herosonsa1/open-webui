"""user 테이블에 sync_lock_yn 컬럼 추가

Revision ID: f2e3d4c5b6b0
Revises: f2e3d4c5b6a9
Create Date: 2026-06-18 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# 리비전 식별자
revision = 'f2e3d4c5b6b0'
down_revision = 'f2e3d4c5b6a9'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'sync_lock_yn' not in columns:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('sync_lock_yn', sa.String(length=1), nullable=True, server_default='N'))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('sync_lock_yn')
