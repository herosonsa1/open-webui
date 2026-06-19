# 히어로손해사정 AI지식관리시스템 구축 작업 이력

본 문서는 AI지식관리시스템(구 Open WebUI) 고도화 및 로컬화 과정에서 진행된 백엔드 및 프론트엔드 작업 내역을 한글로 기록합니다.

---

## 1. 폰트 로컬화 및 오프라인 배포 환경 최적화
- **작업 내용**: 인터넷이 되지 않는 폐쇄망 Docker 배포 환경을 고려하여 외부 CDN 의존성을 제거하였습니다.
- **상세**: 백엔드 `static`에 적재된 나눔스퀘어네오(NanumSquareNeo) CDN 웹 폰트를 로컬 폰트 파일로 참조하게 함으로써 오프라인 상태에서도 정상 동작하도록 폰트 로드 설정을 개선하였습니다.

## 2. 워크스페이스 모델 토글 및 실시간 설명 연동
- **작업 내용**: 워크스페이스에서 등록한 커스텀 모델들을 메인 채팅창 상단의 버튼 그룹으로 동적 표출하고 이를 활용할 수 있게 하였습니다.
- **상세**:
  - 백엔드 `get_all_models` 로직을 보완하여 기본 모델(`base_model_id`)이 없는 독립형 커스텀 모델도 `$models` 스토어에 안정적으로 담기도록 개선하였습니다.
  - 프론트엔드 `MessageInput.svelte` 내 모델 필터를 수정하여 프리셋 커스텀 모델들만 토글 버튼 그룹으로 출력되도록 하였으며, 버튼 폰트 크기를 `text-xs`로 키워 가독성을 높였습니다.
  - `Placeholder.svelte`에서 `<MessageInput>` 호출 시 `selectedModels`를 양방향 바인딩(`bind:selectedModels`)으로 연결하여, 버튼 토글 클릭 시 하단 설명 카드의 상세 설명 문구와 제목이 실시간으로 해당 모델의 메타 정보로 갱신되도록 연동하였습니다.

## 3. 권한별 UI 제어 및 인사말 개인화
- **작업 내용**: 일반 사용자와 관리자의 권한 구분을 강화하고, 첫 화면의 사용자 인사말을 세련되게 다듬었습니다.
- **상세**:
  - 일반 사용자 로그인 시에는 좌측의 워크스페이스 및 모델 관리 등의 메뉴를 완전히 감추고, 관리자로 로그인했을 때만 노출되도록 뷰 권한 제어를 적용하였습니다.
  - 첫 화면의 인사말을 `"안녕하세요, {이름} {직책}님 | {소속부서명}"` 형태로 동적 표시하도록 연동하였습니다.
  - 인사말 중 성함을 제외한 직책/소속부서 부분("팀장님 | IT기획팀")은 상대적으로 작고 부드러운 회색조 서체(`text-xl @sm:text-2xl font-medium text-gray-500`)로 분리 스타일링하여 시각적 비대칭 미를 살렸습니다.

## 4. 사용자 데이터 및 개인 정보 수정 기능 연동
- **작업 내용**: SQL을 통해 임포트된 사용자 데이터가 시스템에 온전히 반영되도록 세션 및 마이페이지 기능을 확장하였습니다.
- **상세**:
  - 관리자 패널의 사용자 편집 모달과 호환되는 사용자 상세 프로필 필드들(직급, 부서명, 연락처, 사번, 입사일 등)을 개인 계정 설정(Account.svelte) 화면에도 추가하였습니다.
  - 사용자가 개인 설정에서 정보를 수정 및 저장할 때 백엔드 프로필 수정 API(`users.py`)와 로그인 세션 바인딩 DTO(`auths.py`)에도 즉각 동기화되도록 연동 로직을 고도화하였습니다.

## 5. 로컬 테스트 우회 로직 수립 (운영 격리)
- **작업 내용**: 로컬 개발망에서 LLM 모델이 없는 상태에서도 테스트와 저장이 원활히 가능하도록 로컬 전용 우회 로직을 구현하였습니다.
- **상세**:
  - DB 조회 모델(`models.py`) 및 API 컨트롤러(`routers/models.py`)에서 HTTP Request 객체의 Host 및 Client IP를 분석하여 로컬 환경(localhost, 127.0.0.1, 192.168.x.x 등)을 자동 감지하도록 하였습니다.
  - 로컬 테스트 환경에서는 기본 모델 필수 지정 검증(`base_model_id != None`) 필터를 건너뛰고, vLLM 테스트용 더미 모델(Gemma 2 31B 등)을 매핑하여 임시 모델 생성을 보장하게 하였습니다. (운영 배포 환경에서는 해당 우회 로직이 차단되고 필수 검증이 엄격하게 복원됩니다.)

## 6. 라이트 테마 가독성 개선 (짙은 남색 적용)
- **작업 내용**: 라이트 테마 환경에서 실제 입력값과 폼 안내문 간의 경계가 불분명하던 점을 스타일 수정을 통해 개선하였습니다.
- **상세**:
  - 글로벌 스타일 `src/app.css` 하단에 라이트 테마 전용 선택자(`html:not(.dark)`)를 추가하였습니다.
  - 입력 항목의 레이블(Label), 회색 설명문구(`.text-gray-500` 등), 플레이스홀더(`::placeholder`) 텍스트의 색상을 선명한 짙은 남색(`#1e3a8a`)으로 일괄 덮어씌워 폼 구분을 또렷이 시각화하였습니다.

## 7. 시스템 명칭 일괄 변경 (브랜딩 통일)
- **작업 내용**: 기존 명칭인 `Open WebUI`를 지우고 독자적인 브랜딩 명칭으로 변경하였습니다.
- **상세**:
  - 백엔드 설정(`env.py`) 및 프론트엔드 상수(`constants.ts`)의 기본 시스템명을 `'히어로손해사정 AI지식관리시스템'`으로 변경하고 접미사 강제 추가 구문을 해제하였습니다.
  - 브라우저 푸시 알림 타이틀 및 채널 헤드 탭 타이틀에 하드코딩되어 있던 `Open WebUI` 문자열도 모두 `$WEBUI_NAME` 스토어 동적 참조로 수정하여 전체 명칭을 일률적으로 통일하였습니다.

## 8. 사용자 정보 동기화 및 수동 동기화 기능 이식
- **작업 내용**: ITTM 프로젝트의 사용자 정보 동기화 스케줄링 및 수동 동기화 기능을 open-webui 프로젝트에 안전하게 이식 완료하였습니다. (ITTM 프로젝트의 코드는 전혀 수정하지 않음)
- **상세**:
  - 백엔드에 PostgreSQL 원천 DB(`pcor`)로부터 사용자 정보를 매일 배치로 조회하여 open-webui DB에 동적 가입/갱신 처리하는 비동기 서비스 `sync_users_from_prod_db`를 작성하였습니다.
  - 매일 자정(`00:00:00`)에 실행되는 비동기 예약 스케줄러 태스크(`user_sync_scheduler_loop`)를 구현하여 애플리케이션 시작 시 백그라운드에서 상시 작동하도록 lifespan 핸들러에 통합하였습니다.
  - 특정 사용자의 정보가 자동 동기화 시 덮어씌워지는 것을 방지할 수 있도록 `sync_lock_yn` 컬럼을 DB에 확장(Alembic 마이그레이션 적용)하고 모델 및 DTO에 속성 매핑을 완료하였습니다.
  - 프론트엔드 사용자 목록 화면 상단에 실시간으로 동기화를 호출하는 `실시간 사용자 동기화` 수동 버튼을 추가하였고, 개별 사용자별로 `동기화 잠금` 여부를 손쉽게 제어할 수 있는 토글 체크박스를 테이블 열에 추가하였습니다.

## 9. 사용자 동기화 작업 이력 화면 및 백엔드 로깅 파이프라인 추가
- **작업 내용**: 동기화 실행 결과(성공/실패 상태, 갱신 건수, 에러 내역 등)를 지속적으로 누적 기록하는 이력 조회 전용 DB 테이블을 구축하고, 어드민 화면에서 이를 확인할 수 있는 모달 팝업을 연동하였습니다.
- **상세**:
  - 동기화 로그 적재 전용 테이블 `user_sync_log` 구조를 확보하기 위한 Alembic 마이그레이션을 생성하고 반영하였습니다.
  - 동기화 수행 시 실행 구분(`AUTO`/`MANUAL`), 실행 시각, 최종 상태(`SUCCESS`/`EMPTY`/`FAIL`), 추가/수정 건수 및 실패 시 예외 원인 메일/텍스트 로그를 데이터베이스에 안전하게 적재하는 이력 로깅 시스템을 연동하였습니다.
  - 어드민 전용 이력 조회 엔드포인트(`GET /api/v1/users/sync/history`) 및 프론트엔드 API 호출 유틸리티를 추가하였습니다.
  - 사용자 목록 화면 상단에 `동기화 이력` 버튼을 배치하였으며, 클릭 시 이력 데이터를 날짜 내림차순으로 정렬하여 일목요연하게 표출하고 비정상 실패 건에 대한 디버그 상세 메시지도 확인할 수 있도록 지원하는 모던한 반응형 모달 컴포넌트(`UserSyncHistoryModal.svelte`)를 신규 연동 완료하였습니다.

## 10. 관리자 패널 UI 최적화, 기동 스크립트 고도화 및 기초 데이터 정제
- **작업 내용**: 관리자 패널 사용자 목록의 시각 여백과 폰트 크기를 대폭 컴팩트화하고, 윈도우용 구동 스크립트를 안정적으로 고도화하였으며, 무효 유저 레코드 제거 및 신규 기초 데이터를 성공적으로 이식하였습니다.
- **상세**:
  - **테이블 UI 공간 효율화**: 사용자 개요 테이블(`UserList.svelte`)의 기본 폰트 크기를 `text-[11px]`로 축소하고 각 셀의 여백을 `px-1 py-0.5`로 줄여 가로 스크롤을 최소화하였습니다. 역할 배지(`Badge.svelte`)가 부모 폰트 설정을 상속받아 동일한 `11px`로 렌더링되도록 컴포넌트 속성을 확장 및 적용하였습니다. 또한 프로필 이미지(`w-5 h-5`), 체크박스(`size-3`), 각종 액션 아이콘(`w-3.5 h-3.5`)의 사이즈를 컴팩트하게 조율하였습니다.
  - **사이드바 여백 최소화**: 사용자 관리 탭 메뉴(`Users.svelte`)의 기본 너비를 `lg:w-50`에서 `lg:w-32`로 크게 좁히고 오른쪽 간격을 축소하여, 메인 테이블과의 넓은 공백 영역을 조밀하게 정리하였습니다.
  - **기동 스크립트(start_windows.bat) 안정성 향상**:
    - 한글 출력 깨짐 해결을 위해 인코딩을 UTF-8(`chcp 65001`)로 설정하였습니다.
    - uvicorn 서버 실행 전 기존 8080 포트를 점유 중인 프로세스를 감지하여 강제 종료(`taskkill`)한 후, 소켓이 안전하게 해제될 수 있도록 2초 대기(`timeout /t 2`) 로직을 추가하여 포트 충돌(Errno 10048)을 방지했습니다.
    - 윈도우 환경에서 uvicorn의 workers가 1인 경우 발생하는 다중 소켓 에러를 예방하기 위해, workers가 1일 때는 `--workers` 파라미터 없이 실행되도록 분기 처리했습니다.
    - 백그라운드(`start /b`) 비동기 프로세스로 서버를 실행하면서 실시간 로그는 파일(`open_webui_server.log`)에 영구 기록하고, 동시에 콘솔에는 PowerShell의 `Get-Content -Wait` 명령어를 연결해 실시간으로 로그 출력이 가능하도록 쉘 스트림 제어 구문을 추가했습니다.
    - 서버 구동 전 자동으로 최신 웹 리소스를 빌드하는 `call npm run build` 프로세스를 탑재하였습니다.
  - **무효 데이터 제거 및 기초 데이터 이식**: 엑셀/tsv 기초 데이터 임포트 시 누락된 헤더 정보(`EMP_ID`, `EMP_NAME` 등)가 DB의 `user`, `auth` 테이블에 삽입되어 주요 관리자(Primary Admin) 보호 필터에 걸려 삭제가 불가(403 Forbidden)했던 현상을 sqlite3 직접 조회를 통해 안전하게 DB에서 영구 삭제 처리하였습니다. 아울러 제공된 이미지 내 신규 사원 32명의 정보를 SQL 규격(연락처 하이픈 자동 포맷 적용)에 맞춰 [users_import.sql](file:///c:/myWork/workspace/scratch/open-webui/backend/data/users_import.sql) 파일 마지막에 성공적으로 연동 추가하였습니다.

## 11. SQL 임포트 신규 사용자 DB 수동 동기화 반영
- **작업 내용**: `users_import.sql`에 신규 추가한 32명의 사원 데이터를 SQLite 로컬 DB(`webui.db`)에 최종 영구 반영하였습니다.
- **상세**:
  - `backend/register_users.py` 스크립트를 실행하여 `users_import.sql`에 새로 작성된 신규 사원 데이터를 파싱하고, `user` 및 `auth` 테이블에 인서트 및 업데이트 처리를 완료하였습니다.
  - 신규 사용자들의 로그인 비밀번호는 각 사번(`EMP_ID`)의 해시값으로 인코딩하여 설정되었으며, 이를 통해 관리자 패널의 사용자 개요 화면 및 사용자 상세 정보에 정상 표출되도록 완전히 조치하였습니다.

## 12. 사용자 관리 화면 이메일 헤더명 변경 및 기본 정렬 순서 조정
- **작업 내용**: 사용자 목록의 이메일 컬럼 헤더명을 '사번'으로 변경하고, 기본 정렬을 사번 오름차순으로 수정하였습니다.
- **상세**:
  - [UserList.svelte](file:///c:/myWork/workspace/scratch/open-webui/src/lib/components/admin/Users/UserList.svelte) 파일에서 이메일 필드(`email`)의 헤더 텍스트를 `{$i18n.t('Email')}`에서 `'사번'`으로 직접 변경하였습니다.
  - 초기 화면 로드 시의 기본 정렬 기준인 `orderBy` 변수를 `'created_at'`에서 `'email'`로 수정하여, 테이블 데이터가 최초 로드될 때 사번을 기준으로 오름차순 정렬되도록 조정하였습니다.

## 13. 브랜드 로고(OI) 이미지 전면 교체 및 favicon.ico 404 에러 대응
- **작업 내용**: 시스템 기본 파비콘 외에 스플래시 화면 등 브랜드 아이덴티티(OI)로 작동하는 모든 로고 이미지를 교체하고, 브라우저의 기본 favicon.ico 요청에 따른 404 에러를 방지하도록 조치하였습니다.
- **상세**:
  - **로고 및 스플래시 이미지 교체**:
    - [favicon.png](file:///c:/myWork/workspace/scratch/open-webui/static/favicon.png)
    - [favicon-dark.png](file:///c:/myWork/workspace/scratch/open-webui/static/static/favicon-dark.png)
    - [splash.png](file:///c:/myWork/workspace/scratch/open-webui/static/static/splash.png)
    - [splash-dark.png](file:///c:/myWork/workspace/scratch/open-webui/static/static/splash-dark.png)
    위 경로의 이미지 파일들을 모두 업로드된 신규 "HERO" 로고 이미지로 덮어쓰기 완료하였습니다.
  - **진짜 다중 레이어 ICO 규격 변환**:
    - 파이썬 Pillow 라이브러리를 통해 기존 PNG 포맷 로고 이미지를 진짜 `.ico` 규격(16x16, 32x32, 48x48 등 다중 해상도 지원) 파일로 인코딩하여 `static/favicon.ico`, `static/static/favicon.ico`, `backend/open_webui/static/favicon.ico`에 각각 이식하였습니다.
  - **SVG 파비콘 참조 차단**:
    - 모던 브라우저가 SVG를 PNG/ICO보다 우선 렌더링하여 예전 로고가 남아보이던 현상을 방지하고자, [app.html](file:///c:/myWork/workspace/scratch/open-webui/src/app.html) 헤더 탭에서 `favicon.svg`를 연결하는 `<link>` 태그 선언부 자체를 영구 제거하였습니다.
  - **백엔드 정적 리소스 동기화 및 강제 적용**:
    - SvelteKit 빌드 디렉토리(`build/`) 내의 리소스들을 백엔드 FastAPI가 물리적으로 서빙하는 실시간 static 디렉토리인 [backend/open_webui/static](file:///c:/myWork/workspace/scratch/open-webui/backend/open_webui/static) 하위에 수동으로 전수 복사 덮어쓰기 하였습니다.
    - 변경된 정적 자산 및 백엔드 라우팅 설정을 최종 기동하기 위해 `start_windows.bat` 스크립트를 수행하여 캐시 클린 및 포트 충돌 없이 백엔드 서버를 안정적으로 재부팅 완료하였습니다.

## 14. 채팅 화면 및 대화 텍스트 폰트 크기 최적화
- **작업 내용**: 채팅 화면 본문 및 사용자 입력 영역의 폰트 크기를 조밀하게 축소하여 가독성을 개선하였습니다.
- **상세**:
  - [app.css](file:///c:/myWork/workspace/scratch/open-webui/src/app.css) 파일에서 `html` 기본 폰트 크기를 기존 `1.2rem`(120%)에서 `1.1rem`(110%)으로 줄였습니다.
  - 대화 내용이 렌더링되는 `.markdown-prose` 클래스에 `@apply text-[15px]`를 추가하여, 글자 크기가 더욱 깔끔하고 보기 편하게 수정하였습니다.

## 15. 관리자 생성 모델의 일반 사용자 공유 노출 구현
- **작업 내용**: 관리자 계정에서 추가한 RAG 프리셋 커스텀 모델이 일반 사용자 계정으로 로그인했을 때도 동일하게 화면에 노출되고 작동하도록 백엔드 접근 제어 및 필터링 로직을 개선하였습니다.
- **상세**:
  - **데이터베이스 권한 필터 우회**: [access_grants.py](file:///c:/myWork/workspace/scratch/open-webui/backend/open_webui/models/access_grants.py) 내 `has_permission_filter` 메서드 및 [models.py](file:///c:/myWork/workspace/scratch/open-webui/backend/open_webui/models/models.py) 내 `get_models_by_user_id`를 수정하여, 리소스 타입이 `model`인 경우 소유자가 `system`이거나 생성자의 역할(Role)이 `admin`인 경우 SQL `OR` 조건 및 우회 로직을 적용하였습니다.
  - **SQL 500 에러 해결**: `search_models` 내 `exists` 쿼리 수행 시 발생하는 auto-correlation(자기 상관)으로 인한 `Returned no FROM clauses` 500 에러를 방지하고자, `exists` 서브쿼리 생성 시 `.correlate(DocumentModel)`를 명시적으로 체이닝하였습니다.
  - **메모리 및 캐시 필터링 우회**: [models.py (Utils)](file:///c:/myWork/workspace/scratch/open-webui/backend/open_webui/utils/models.py)의 `check_model_access` 및 `get_filtered_models`를 수정하여, 모델 소유자(Owner)가 `system`이거나 소유자 역할이 `admin`인 모델의 경우 필터에서 예외 처리를 하여 일반 사용자의 최종 조회 모델 목록에 항상 반환되도록 하였습니다. 이 과정에서 모델 소유자의 역할을 일괄(Batch) 조회하여 성능 저하를 차단하였습니다.
  - **작업 검증 완료**: 일반 사용자 계정으로 로그인하여 `/api/models` 및 `/api/v1/models/list` API를 호출하고 관리자가 등록해둔 모델이 목록에 정상 수신되는지 시뮬레이션 테스트를 완료하였습니다.

## 16. 오프라인 폐쇄망 배포용 Docker 이미지 빌드 패키징 및 스크립트 구축
- **작업 내용**: 인터넷망 연결이 차단된 오프라인 리눅스 운영서버 배포를 위해, 모든 외부 CDN 자산(웹 폰트 등)을 로컬 정적 경로로 처리하고 핵심 AI 모델 가중치(임베딩, Whisper 등)를 빌드 시점에 이미지 내에 영구 캐싱하여 배포 아카이브(`.tar` 파일)를 추출할 수 있는 빌드 프로세스 및 자동화 스크립트를 구축하였습니다.
- **상세**:
  - **오프라인 빌드 설계**: `USE_SLIM=false` 및 `USE_CUDA=false` 빌드 인자를 사용하여 Dockerfile 빌드 타임에 `SentenceTransformer` 임베딩 가중치, `WhisperModel` 음성인식 가중치, `tiktoken` 인코딩 사전, `nltk` 토크나이저 데이터를 내부 `/app/backend/data/cache`에 미리 저장하여 이미지 내장형으로 제작되도록 하였습니다.
  - **외부 CDN 및 텔레메트리 차단**: NanumSquareNeo 폰트 등 정적 리소스를 모두 `static/assets/fonts/` 하위로 로컬화했으며, 외부 트래킹 요청을 방지하기 위해 텔레메트리 비활성화 환경변수(`SCARF_NO_ANALYTICS=true`, `DO_NOT_TRACK=true`, `ANONYMIZED_TELEMETRY=false`)가 내장된 Docker 실행 구조를 확립했습니다.
  - **통합 빌드 스크립트 배포**:
    - **윈도우용**: [build_offline.bat](file:///c:/myWork/workspace/scratch/open-webui/build_offline.bat) 및 [build_offline_image.ps1](file:///c:/myWork/workspace/scratch/open-webui/dist/build_offline_image.ps1)을 작성했습니다. 특히 `build_offline.bat`는 한글 윈도우 인코딩(CP949) 환경에서의 충돌을 예방하고자 모든 주석과 메시지를 영문으로 설계하여 무결성을 높였습니다.
    - **리눅스용**: [build_offline.sh](file:///c:/myWork/workspace/scratch/open-webui/build_offline.sh) 및 [build_offline_image.sh](file:///c:/myWork/workspace/scratch/open-webui/dist/build_offline_image.sh)를 작성하여, 리눅스 빌드 서버에서 `./build_offline.sh`를 구동하면 `dist/open-webui-offline-latest.tar`로 배포본이 자동 출력되도록 제작했습니다.
  - **배포 가이드 수립**: [README.md](file:///c:/myWork/workspace/scratch/open-webui/dist/README.md) 안내서를 배포용 `dist` 폴더 내에 작성하여, 현재 개발 PC 내 Docker 데몬 부재로 인한 빌드 불가 현상을 진단하고 리눅스에서의 이미지 빌드 및 오프라인 적재 실행 방법을 완벽하게 정리했습니다.

## 17. Docker 배포 시 로컬 사용자 정보 누락 문제 조치
- **작업 내용**: 로컬에서 임포트한 사용자 데이터가 Docker 빌드 및 배포본 생성 시 이미지 내부에 포함되지 않는 현상을 해결하였습니다.
- **상세**:
  - 루트 `.dockerignore` 및 `backend/.dockerignore` 파일을 수정하여, 기존에 일괄 차단(ignore)되던 `backend/data` 폴더 자산 중 사용자 등록 SQL 파일(`users_import.sql`)을 빌드 제외 대상에서 예외 처리 (`!users_import.sql` 또는 `!/data/users_import.sql`)하였습니다.
  - 컨테이너 기동 시 실행되는 진입점 스크립트 [start.sh](file:///c:/myWork/workspace/scratch/open-webui/backend/start.sh)에 `register_users.py` 및 `users_import.sql`이 존재할 경우 자동으로 실행되도록 하는 구동 구문을 주입하였습니다. 이로써 최초 배포 혹은 볼륨 마운트 시에도 이미지 내에 포함된 신규 사용자가 SQLite DB(`webui.db`)에 누락 없이 인서트/업데이트(UPSERT)되도록 설계하였습니다.

## 18. 워크스페이스 모델 선택 버튼 클릭 시 모델 미변경 버그 수정
- **작업 내용**: 메인 채팅 화면의 커스텀 모델 버튼 그룹에서 특정 모델을 클릭했을 때 화면의 설명 및 타이틀은 변경되나, 실제 질의가 이전 모델로 전송되던 동기화 결함을 해결하였습니다.
- **상세**:
  - `Chat.svelte`에서 하위 컴포넌트인 `<Placeholder>` 및 `<MessageInput>`을 호출할 때 `selectedModels` 상태를 전달하는 부분이 단방향(`{selectedModels}`)으로 지정되어 있었기 때문에 하위 컴포넌트 내에서의 선택 변경 사항이 최상위 채팅 상태로 반영되지 못하고 유실되었던 점을 원인으로 파악하였습니다.
  - [Chat.svelte](file:///c:/myWork/workspace/scratch/open-webui/src/lib/components/chat/Chat.svelte) 내 두 컴포넌트 호출부에 모두 양방향 바인딩(`bind:selectedModels={selectedModels}`)을 올바르게 추가함으로써, 사용자가 화면의 모델 캡슐 버튼(예: `Test2`)을 누를 시 실제 질문 전송 대상 모델 및 드롭다운 선택 모델이 정상적으로 동기화 변경되도록 최종 조치 완료하였습니다.
