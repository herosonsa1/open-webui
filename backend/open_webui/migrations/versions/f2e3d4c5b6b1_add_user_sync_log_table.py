"""add user sync log table

Revision ID: f2e3d4c5b6b1
Revises: f2e3d4c5b6b0
Create Date: 2026-06-18 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# 리비전 식별자
revision = 'f2e3d4c5b6b1'
down_revision = 'f2e3d4c5b6b0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'user_sync_log' not in tables:
        op.create_table(
            'user_sync_log',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('sync_type', sa.String(length=20), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('appended_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('updated_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=False)
        )


def downgrade():
    op.drop_table('user_sync_log')
