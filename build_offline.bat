@echo off
REM Offline build script for Open-WebUI Docker Image
setlocal enabledelayedexpansion

echo ==================================================
echo Starting Offline WebUI Docker Build
echo Args: USE_CUDA=false, USE_OLLAMA=false, USE_SLIM=true
echo ==================================================

REM 1. Create dist directory if not exists
if not exist dist (
    mkdir dist
)

REM 2. Run docker build
echo [1/2] Building Docker image... (USE_SLIM=true: AI weights excluded)
docker build ^
  --build-arg="USE_CUDA=false" ^
  --build-arg="USE_OLLAMA=false" ^
  --build-arg="USE_SLIM=true" ^
  -t open-webui:offline-latest .

if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed with code %errorlevel%
    exit /b %errorlevel%
)

REM 3. Save to tar archive
echo [2/2] Saving image to dist/open-webui-offline-latest.tar...
docker save -o dist\open-webui-offline-latest.tar open-webui:offline-latest

if %errorlevel% neq 0 (
    echo [ERROR] Failed to save Docker image tar.
    exit /b %errorlevel%
)

echo ==================================================
echo Build and save completed successfully!
echo Target: dist\open-webui-offline-latest.tar
echo ==================================================
pause
