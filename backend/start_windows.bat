:: This method is not recommended, and we recommend you use the `start.sh` file with WSL instead.
@echo off
chcp 65001 >nul
SETLOCAL ENABLEDELAYEDEXPANSION

:: Get the directory of the current script
SET "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || exit /b

:: Add conditional Playwright browser installation
IF /I "%WEB_LOADER_ENGINE%" == "playwright" (
    IF "%PLAYWRIGHT_WS_URL%" == "" (
        echo Installing Playwright browsers...
        playwright install chromium
        playwright install-deps chromium
    )

    python -c "import nltk; nltk.download('punkt_tab')"
)

SET "KEY_FILE=.webui_secret_key"
IF NOT "%WEBUI_SECRET_KEY_FILE%" == "" (
    SET "KEY_FILE=%WEBUI_SECRET_KEY_FILE%"
)

IF "%VECTOR_DB%"=="" SET "VECTOR_DB=s3vector"
IF "%RAG_EMBEDDING_ENGINE%"=="" SET "RAG_EMBEDDING_ENGINE=openai"

IF "%PORT%"=="" SET PORT=8080
IF "%HOST%"=="" SET HOST=0.0.0.0
IF "%FORWARDED_ALLOW_IPS%"=="" SET "FORWARDED_ALLOW_IPS='*'"
SET "WEBUI_SECRET_KEY=%WEBUI_SECRET_KEY%"
SET "WEBUI_JWT_SECRET_KEY=%WEBUI_JWT_SECRET_KEY%"

:: Check if WEBUI_SECRET_KEY and WEBUI_JWT_SECRET_KEY are not set
IF "%WEBUI_SECRET_KEY% %WEBUI_JWT_SECRET_KEY%" == " " (
    echo Loading WEBUI_SECRET_KEY from file, not provided as an environment variable.

    IF NOT EXIST "%KEY_FILE%" (
        echo Generating WEBUI_SECRET_KEY
        :: Generate a random value to use as a WEBUI_SECRET_KEY in case the user didn't provide one
        SET /p WEBUI_SECRET_KEY=<nul
        FOR /L %%i IN (1,1,12) DO SET /p WEBUI_SECRET_KEY=<!random!>>%KEY_FILE%
        echo WEBUI_SECRET_KEY generated
    )

    echo Loading WEBUI_SECRET_KEY from %KEY_FILE%
    SET /p WEBUI_SECRET_KEY=<%KEY_FILE%
)

:: 기존에 포트를 사용 중인 프로세스가 있다면 강제 종료
echo 포트 %PORT%번을 사용 중인 기존 프로세스가 있는지 확인 중...
set "PORT_FOUND=N"
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r /c:":%PORT% .*LISTENING"') do (
    echo 포트 %PORT%번을 점유 중인 프로세스 %%a 종료 중...
    taskkill /f /pid %%a 2>nul
    set "PORT_FOUND=Y"
)
if "!PORT_FOUND!"=="Y" (
    echo 프로세스 종료 후 소켓 릴리즈를 위해 2초 대기 중...
    timeout /t 2 /nobreak >nul
)

:: 프론트엔드 빌드 실행
echo 프론트엔드 빌드를 시작합니다...
cd /d "%SCRIPT_DIR%.."
call npm run build
cd /d "%SCRIPT_DIR%"

:: Execute uvicorn
SET "WEBUI_SECRET_KEY=%WEBUI_SECRET_KEY%"
IF "%UVICORN_WORKERS%"=="" SET UVICORN_WORKERS=1
echo 서버를 백그라운드에서 구동하고 로그 파일에 기록합니다...
if "%UVICORN_WORKERS%"=="1" (
    start /b uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips %FORWARDED_ALLOW_IPS% --ws auto > "%SCRIPT_DIR%open_webui_server.log" 2>&1
) else (
    start /b uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips %FORWARDED_ALLOW_IPS% --workers %UVICORN_WORKERS% --ws auto > "%SCRIPT_DIR%open_webui_server.log" 2>&1
)

:: 로그 파일이 생성되도록 2초 대기
timeout /t 2 /nobreak >nul

:: 실시간 로그 모니터링 (PowerShell의 Get-Content -Wait 활용)
echo 실시간 로그 출력을 시작합니다 (로그 모니터링 종료: Ctrl+C)...
powershell -Command "Get-Content '%SCRIPT_DIR%open_webui_server.log' -Wait -Tail 20"
:: For ssl user uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips '*' --ssl-keyfile "key.pem" --ssl-certfile "cert.pem" --ws auto
