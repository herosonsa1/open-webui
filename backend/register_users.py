import asyncio
import os
import re
import sys
import time
from sqlalchemy import text

# open_webui 경로 추가
sys.path.append(os.path.abspath('.'))

# WEBUI_SECRET_KEY 환경 변수 로드
key_file = os.path.join(os.path.dirname(__file__), ".webui_secret_key")
if not os.environ.get("WEBUI_SECRET_KEY") and os.path.exists(key_file):
    with open(key_file, "r", encoding="utf-8") as f:
        os.environ["WEBUI_SECRET_KEY"] = f.read().strip()

# Python 3.14 chromadb 호환성을 위한 환경 변수 주입
if not os.environ.get("VECTOR_DB"):
    os.environ["VECTOR_DB"] = "s3vector"
if not os.environ.get("RAG_EMBEDDING_ENGINE"):
    os.environ["RAG_EMBEDDING_ENGINE"] = "openai"

from open_webui.internal.db import get_async_db
from open_webui.utils.auth import get_password_hash

async def main():
    # 1. users_import.sql 파일 읽기
    sql_path = os.path.join(os.path.dirname(__file__), "data", "users_import.sql")
    if not os.path.exists(sql_path):
        print(f"Error: SQL file not found at {sql_path}")
        return

    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. TB_IT_USER 인서트문 찾기
    pattern = re.compile(r"INSERT INTO TB_IT_USER.*?;", re.DOTALL)
    matches = pattern.findall(content)
    if not matches:
        print("TB_IT_USER insert statement not found.")
        return

    # 3. 데이터 파싱
    users = []
    values_pattern = re.compile(r"\(([^)]+)\)")
    for match in matches:
        val_matches = values_pattern.findall(match)
        for val_str in val_matches:
            # 콤마로 분할하되 따옴표 안의 콤마 무시하도록 파싱
            tokens = [t.strip().strip("'") for t in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", val_str)]
            if len(tokens) >= 12:
                emp_id = tokens[0]
                emp_name = tokens[1]
                org_nm = tokens[2] if tokens[2] != 'NULL' else None
                org_cd = tokens[3] if tokens[3] != 'NULL' else None
                parent_org_nm = tokens[4] if tokens[4] != 'NULL' else None
                position_name = tokens[5] if tokens[5] != 'NULL' else None
                phone_number = tokens[6] if tokens[6] != 'NULL' else None
                role = tokens[7]
                ip_address = tokens[10] if tokens[10] != 'NULL' else None
                join_date = tokens[11] if tokens[11] != 'NULL' else None
                
                resign_date = None
                if len(tokens) > 12:
                    resign_date = tokens[12] if tokens[12] != 'NULL' else None
                
                # admin 사용자는 이미 기본 생성되어 있으므로 건너뜀
                if emp_id == 'admin':
                    continue
                    
                admin_ids = {'9000414', '9000241', '9000423'}
                if emp_id in admin_ids:
                    mapped_role = 'admin'
                else:
                    mapped_role = 'admin' if role == 'ADMIN' else 'user'
                users.append({
                    'id': emp_id,
                    'name': emp_name,
                    'email': emp_id,
                    'role': mapped_role,
                    'org_nm': org_nm,
                    'org_cd': org_cd,
                    'parent_org_nm': parent_org_nm,
                    'position_name': position_name,
                    'phone_number': phone_number,
                    'ip_address': ip_address,
                    'join_date': join_date,
                    'resign_date': resign_date
                })

    print(f"Parsed {len(users)} users.")

    # 4. DB에 인서트 또는 업데이트
    now = int(time.time())

    async with get_async_db() as session:
        for u in users:
            try:
                # 비밀번호 해시는 각 사용자의 사번(id)으로 설정
                user_password_hash = get_password_hash(u['id'])
                
                # 이미 존재하는 유저인지 확인
                result = await session.execute(
                    text("SELECT id FROM user WHERE id = :id"), {'id': u['id']}
                )
                if result.fetchone():
                    # 기존 유저 업데이트 (이메일=사번, 비밀번호=사번, 역할, 이름 및 추가 필드들 갱신)
                    await session.execute(
                        text("""
                            UPDATE auth 
                            SET email = :email, password = :password, password_updated_at = :password_updated_at 
                            WHERE id = :id
                        """),
                        {
                            'id': u['id'],
                            'email': u['email'],
                            'password': user_password_hash,
                            'password_updated_at': now
                        }
                    )
                    await session.execute(
                        text("""
                            UPDATE user 
                            SET email = :email, role = :role, name = :name,
                                position_name = :position_name, org_nm = :org_nm, org_cd = :org_cd,
                                parent_org_nm = :parent_org_nm, phone_number = :phone_number,
                                ip_address = :ip_address, join_date = :join_date, resign_date = :resign_date,
                                password_updated_at = :password_updated_at
                            WHERE id = :id
                        """),
                        {
                            'id': u['id'],
                            'email': u['email'],
                            'role': u['role'],
                            'name': u['name'],
                            'position_name': u['position_name'],
                            'org_nm': u['org_nm'],
                            'org_cd': u['org_cd'],
                            'parent_org_nm': u['parent_org_nm'],
                            'phone_number': u['phone_number'],
                            'ip_address': u['ip_address'],
                            'join_date': u['join_date'],
                            'resign_date': u['resign_date'],
                            'password_updated_at': now
                        }
                    )
                    print(f"Updated user: {u['id']} ({u['name']}) as {u['role']}")
                    continue

                # auth 테이블에 인서트
                await session.execute(
                    text("""
                        INSERT INTO auth (id, email, password, active, password_updated_at) 
                        VALUES (:id, :email, :password, :active, :password_updated_at)
                    """),
                    {
                        'id': u['id'],
                        'email': u['email'],
                        'password': user_password_hash,
                        'active': True,
                        'password_updated_at': now
                    }
                )

                # user 테이블에 인서트
                await session.execute(
                    text("""
                        INSERT INTO user (id, email, role, name, profile_image_url, last_active_at, created_at, updated_at,
                                          position_name, org_nm, org_cd, parent_org_nm, phone_number, ip_address, join_date, resign_date,
                                          password_updated_at) 
                        VALUES (:id, :email, :role, :name, :profile_image_url, :last_active_at, :created_at, :updated_at,
                                :position_name, :org_nm, :org_cd, :parent_org_nm, :phone_number, :ip_address, :join_date, :resign_date,
                                :password_updated_at)
                    """),
                    {
                        'id': u['id'],
                        'email': u['email'],
                        'role': u['role'],
                        'name': u['name'],
                        'profile_image_url': '/user.png',
                        'last_active_at': now,
                        'created_at': now,
                        'updated_at': now,
                        'position_name': u['position_name'],
                        'org_nm': u['org_nm'],
                        'org_cd': u['org_cd'],
                        'parent_org_nm': u['parent_org_nm'],
                        'phone_number': u['phone_number'],
                        'ip_address': u['ip_address'],
                        'join_date': u['join_date'],
                        'resign_date': u['resign_date'],
                        'password_updated_at': now
                    }
                )
                print(f"Registered user: {u['id']} ({u['name']}) as {u['role']}")
            except Exception as e:
                print(f"Error registering/updating user {u['id']}: {e}")
                
        await session.commit()
    print("User registration completed.")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
