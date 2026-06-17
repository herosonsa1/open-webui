import time
import logging
import asyncio
import datetime
import random
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import select
from open_webui.internal.db import get_async_db_context
from open_webui.models.users import Users, User, UserModel, UserSyncLogs
from open_webui.models.auths import Auths, Auth
from open_webui.utils.auth import get_password_hash

log = logging.getLogger(__name__)

# DB 접속 설정 정보 (Prod DB 정보 이식)
DB_HOST = "pg-gru16.vpc-cdb-fkr.fin-ntruss.com"
DB_PORT = 15433
DB_NAME = "pcor"
DB_USER = "adm_pcor"
DB_PASSWORD = "Qwe12#pcor"

def fetch_users_from_prod():
    """운영 PostgreSQL DB에서 사용자 목록을 조회해오는 동기 함수"""
    query = """
    select distinct 
        dept.dept_name, 
        dept.POSITION_NAME, 
        emp.login_id, 
        emp.emp_name_kr, 
        emp.mobile_tel_num || emp.mobile_tel_tltno || emp.mobile_tel_tlsno as tel_no, 
        (select max(ppr_orgcd) from com.com_org where orgnm = dept.dept_name) as parent_org_cd, 
        (select max(orgnm) from com.com_org where orgcd = (select max(ppr_orgcd) from com.com_org where orgnm = dept.dept_name)) as parent_org_nm, 
        (select max(orgcd) from com.com_org where orgnm = dept.dept_name) as org_cd, 
        dept.dept_name as org_nm, 
        emp.join_day, 
        emp.resign_day 
    from 
        com.com_emp_list as emp, 
        com.COM_EMP_DEPT_LIST as dept 
    where 
        emp.emp_seq = dept.emp_seq 
        AND emp.BASE_DATE = TO_CHAR(CURRENT_DATE-1,'YYYYMMDD') 
        AND dept.base_date = TO_CHAR(CURRENT_DATE-1,'YYYYMMDD') 
        AND emp.resign_day is NULL 
        and emp.use_yn = 'Y' 
        and emp.login_id <> 'admin' 
    order by login_id
    """
    
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return rows
    except Exception as e:
        log.error(f"[SYNC] 운영 DB 연결 및 조회 실패: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close()

async def sync_users_from_prod_db(sync_type: str = 'MANUAL', db=None) -> tuple[int, int]:
    """사용자 데이터 동기화 비동기 함수.
    sync_type: 'AUTO' 또는 'MANUAL'
    db: AsyncSession 객체 (전달되지 않으면 신규 획득)
    반환값: (appended_count, updated_count)
    """
    log.info(f"[SYNC] 사용자 데이터(TB_IT_USER -> user) 동기화 시작 (유형: {sync_type})...")
    
    try:
        # 1. 운영 DB에서 데이터 조회 (블로킹 I/O를 비동기 스레드 풀에서 실행)
        rows = await asyncio.to_thread(fetch_users_from_prod)
    except Exception as e:
        log.error(f"[SYNC] 사용자 동기화 실패 (운영 DB 조회 오류): {str(e)}")
        # 실패 이력 로그 기록
        try:
            await UserSyncLogs.insert_new_log(
                sync_type=sync_type,
                status='FAIL',
                error_message=f"운영 DB 조회 실패: {str(e)}",
                db=db
            )
        except Exception as log_err:
            log.error(f"[SYNC] 실패 로그 기록 오류: {str(log_err)}")
        raise e

    if not rows:
        log.warn("[SYNC] 원천 테이블(com.com_emp_list)에서 사용자 데이터를 찾을 수 없거나 대상이 없습니다.")
        try:
            await UserSyncLogs.insert_new_log(
                sync_type=sync_type,
                status='EMPTY',
                appended_count=0,
                updated_count=0,
                db=db
            )
        except Exception as log_err:
            log.error(f"[SYNC] 빈 결과 로그 기록 오류: {str(log_err)}")
        return 0, 0

    appended_count = 0
    updated_count = 0

    try:
        async with get_async_db_context(db) as session:
            for row in rows:
                login_id = row.get("login_id")
                emp_name = row.get("emp_name_kr")
                dept_name = row.get("dept_name")
                position_name = row.get("position_name")
                tel_no_raw = row.get("tel_no")
                org_cd = row.get("org_cd")
                org_nm = row.get("org_nm")
                parent_org_cd = row.get("parent_org_cd")
                parent_org_nm = row.get("parent_org_nm")
                join_day = row.get("join_day")
                resign_day = row.get("resign_day")

                # 방어 로직 (Null 필터링)
                if not login_id or login_id == "None" or login_id == "null":
                    continue

                dept_name = "" if dept_name is None or dept_name == "None" or dept_name == "null" else str(dept_name)
                position_name = "" if position_name is None or position_name == "None" or position_name == "null" else str(position_name)
                emp_name = "" if emp_name is None or emp_name == "None" or emp_name == "null" else str(emp_name)
                org_cd = "" if org_cd is None or org_cd == "None" or org_cd == "null" else str(org_cd)
                org_nm = "" if org_nm is None or org_nm == "None" or org_nm == "null" else str(org_nm)
                parent_org_cd = "" if parent_org_cd is None or parent_org_cd == "None" or parent_org_cd == "null" else str(parent_org_cd)
                parent_org_nm = "" if parent_org_nm is None or parent_org_nm == "None" or parent_org_nm == "null" or not str(parent_org_nm).strip() else str(parent_org_nm)
                join_day = "" if join_day is None or join_day == "None" or join_day == "null" else str(join_day)
                resign_day = "" if resign_day is None or resign_day == "None" or resign_day == "null" else str(resign_day)

                # 최상위 상위부서 Fallback 로직 적용 (부모코드가 없는경우 200000/히어로손해사정 지정)
                if not parent_org_cd and org_cd != "200000":
                    parent_org_cd = "200000"
                    parent_org_nm = "히어로손해사정"

                tel_no = "" if tel_no_raw is None or tel_no_raw == "None" or tel_no_raw == "null" else str(tel_no_raw).replace("-", "")

                # 기존 사용자 조회
                existing_user = await session.get(User, login_id)
                email = f"{login_id}@herosonsa.co.kr"

                if existing_user:
                    # 동기화 잠금 상태인지 체크
                    if getattr(existing_user, "sync_lock_yn", "N") == "Y":
                        log.info(f"[SYNC] 사용자 {existing_user.name} (사번: {existing_user.id})는 동기화 잠금 상태이므로 스킵합니다.")
                        continue

                    changed = False

                    # 데이터 수정 비교
                    if emp_name != existing_user.name:
                        existing_user.name = emp_name
                        changed = True
                    if position_name != getattr(existing_user, 'position_name', None):
                        existing_user.position_name = position_name
                        changed = True
                    if org_nm != getattr(existing_user, 'org_nm', None):
                        existing_user.org_nm = org_nm
                        changed = True
                    if org_cd != getattr(existing_user, 'org_cd', None):
                        existing_user.org_cd = org_cd
                        changed = True
                    if parent_org_nm != getattr(existing_user, 'parent_org_nm', None):
                        existing_user.parent_org_nm = parent_org_nm
                        changed = True
                    if tel_no != getattr(existing_user, 'phone_number', None):
                        existing_user.phone_number = tel_no
                        changed = True
                    if join_day != getattr(existing_user, 'join_date', None):
                        existing_user.join_date = join_day
                        changed = True
                    if resign_day != getattr(existing_user, 'resign_date', None):
                        existing_user.resign_date = resign_day
                        changed = True

                    if changed:
                        existing_user.updated_at = int(time.time())
                        updated_count += 1
                else:
                    # 신규 사용자 가입 등록 처리
                    hashed_pw = get_password_hash(login_id)

                    # 1. Auth 테이블 추가
                    new_auth = Auth(
                        id=login_id,
                        email=email,
                        password=hashed_pw,
                        active=True,
                        password_updated_at=0
                    )
                    session.add(new_auth)

                    # 2. User 테이블 추가
                    role = 'user'
                    new_user = User(
                        id=login_id,
                        email=email,
                        name=emp_name,
                        role=role,
                        profile_image_url='/user.png',
                        last_active_at=int(time.time()),
                        created_at=int(time.time()),
                        updated_at=int(time.time()),
                        position_name=position_name,
                        org_nm=org_nm,
                        org_cd=org_cd,
                        parent_org_nm=parent_org_nm,
                        phone_number=tel_no,
                        join_date=join_day,
                        resign_date=resign_day,
                        password_updated_at=0,
                        sync_lock_yn='N'
                    )
                    session.add(new_user)
                    appended_count += 1

            # 모든 처리가 끝난 후 커밋
            await session.commit()

            # 작업 완료 이력 로그 저장
            status_log = 'SUCCESS'
            if appended_count == 0 and updated_count == 0:
                status_log = 'EMPTY'

            await UserSyncLogs.insert_new_log(
                sync_type=sync_type,
                status=status_log,
                appended_count=appended_count,
                updated_count=updated_count,
                db=session
            )
            
    except Exception as e:
        log.error(f"[SYNC] 사용자 데이터 동기화 루프 처리 실패: {str(e)}")
        try:
            await UserSyncLogs.insert_new_log(
                sync_type=sync_type,
                status='FAIL',
                error_message=f"데이터 처리 실패: {str(e)}",
                db=db
            )
        except Exception as log_err:
            log.error(f"[SYNC] 실패 로그 기록 오류: {str(log_err)}")
        raise e

    log.info(f"[SYNC] 사용자 데이터 동기화 완료: 신규 추가 {appended_count}건, 수정 {updated_count}건")
    return appended_count, updated_count

async def user_sync_scheduler_loop(app) -> None:
    """매일 자정 00:00:00에 사용자 정보를 정기적으로 동기화하는 백그라운드 스케줄러"""
    log.info("사용자 동기화 스케줄러 루프가 시작되었습니다.")
    while True:
        try:
            now = datetime.datetime.now()
            # 다음 날 00:00:00 계산
            tomorrow = now + datetime.timedelta(days=1)
            next_run = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
            sleep_sec = (next_run - now).total_seconds()
            
            log.info(f"[SYNC] 다음 정기 사용자 동기화 예정 시각: {next_run} (대기 시간: {sleep_sec:.1f}초)")
            # 대기
            await asyncio.sleep(sleep_sec)
            
            # 동기화 시작 (AUTO 타입으로 로그 설정)
            appended, updated = await sync_users_from_prod_db(sync_type='AUTO')
            log.info(f"[SYNC] 정기 사용자 동기화 완료: 신규 추가 {appended}건, 수정 {updated}건")
            
        except asyncio.CancelledError:
            log.info("사용자 동기화 스케줄러 루프가 정지되었습니다.")
            break
        except Exception as e:
            log.exception(f"[SYNC] 사용자 동기화 스케줄러 루프에서 예외가 발생했습니다: {str(e)}")
            # 에러 발생 시 60초 대기 후 루프 재개
            await asyncio.sleep(60)
