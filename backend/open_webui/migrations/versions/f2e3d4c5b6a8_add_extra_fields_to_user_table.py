"""user 테이블에 직급, 부서명, 연락처, 입사일 등 추가 정보 컬럼 확장

Revision ID: f2e3d4c5b6a8
Revises: f2e3d4c5b6a7
Create Date: 2026-06-17 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# 리비전 식별자
revision = 'f2e3d4c5b6a8'
down_revision = 'f2e3d4c5b6a7'
branch_labels = None
depends_on = None


def upgrade():
    # user 테이블 컬럼 검사 후 추가 관리할 컬럼 8개 생성
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    extra_cols = [
        ('position_name', sa.String()),  # 직급
        ('org_nm', sa.String()),         # 부서명
        ('org_cd', sa.String()),         # 부서 코드
        ('parent_org_nm', sa.String()),  # 상위부서명
        ('phone_number', sa.String()),   # 연락처
        ('ip_address', sa.String()),     # 고정 IP주소
        ('join_date', sa.String()),      # 입사일
        ('resign_date', sa.String())     # 퇴사일
    ]
    
    with op.batch_alter_table('user', schema=None) as batch_op:
        for col_name, col_type in extra_cols:
            if col_name not in columns:
                batch_op.add_column(sa.Column(col_name, col_type, nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        for col_name in ['position_name', 'org_nm', 'org_cd', 'parent_org_nm', 'phone_number', 'ip_address', 'join_date', 'resign_date']:
            batch_op.drop_column(col_name)
