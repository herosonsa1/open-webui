# 이 스크립트는 윈도우 빌드 서버(Docker Desktop 설치 환경)에서 오프라인 폐쇄망 배포용 Docker 이미지를 빌드하고 tar 파일로 추출하는 스크립트입니다.
$ErrorActionPreference = "Stop"

# 스크립트 디렉토리 기준으로 프로젝트 루트 경로 설정
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "오프라인 폐쇄망 배포용 Docker 이미지 빌드를 시작합니다." -ForegroundColor Cyan
Write-Host "빌드 설정: USE_CUDA=false, USE_OLLAMA=false, USE_SLIM=false" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. dist 디렉토리 존재 확인
if (-not (Test-Path dist)) {
    New-Item -ItemType Directory -Path dist -Force | Out-Null
}

# 2. Docker 이미지 빌드 (가중치 캐싱을 위해 빌드 환경은 인터넷 연결 필수)
Write-Host "[1/2] Docker 이미지를 빌드 중입니다... (모델 다운로드로 인해 대략 10~20분 소요 가능)" -ForegroundColor Yellow
docker build `
  --build-arg="USE_CUDA=false" `
  --build-arg="USE_OLLAMA=false" `
  --build-arg="USE_SLIM=false" `
  -t open-webui:offline-latest .

# 3. Docker 이미지를 tar 파일로 추출 및 저장
Write-Host "[2/2] 빌드 완료된 이미지를 dist\open-webui-offline-latest.tar 파일로 아카이브 저장 중입니다..." -ForegroundColor Yellow
docker save -o dist\open-webui-offline-latest.tar open-webui:offline-latest

Write-Host "==================================================" -ForegroundColor Green
Write-Host "배포 이미지 생성 완료!" -ForegroundColor Green
Write-Host "경로: dist\open-webui-offline-latest.tar" -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Green
Write-Host "폐쇄망 운영 서버(리눅스)에서 다음 명령어로 이미지를 로드하여 기동하십시오:" -ForegroundColor Green
Write-Host "  1) 이미지 로드: docker load -i open-webui-offline-latest.tar" -ForegroundColor Green
Write-Host "  2) 컨테이너 기동 예시:" -ForegroundColor Green
Write-Host "     docker run -d -p 8080:8080 --name open-webui \`" -ForegroundColor Green
Write-Host "       -e SCARF_NO_ANALYTICS=true \`" -ForegroundColor Green
Write-Host "       -e DO_NOT_TRACK=true \`" -ForegroundColor Green
Write-Host "       -e ANONYMIZED_TELEMETRY=false \`" -ForegroundColor Green
Write-Host "       -v open-webui:/app/backend/data \`" -ForegroundColor Green
Write-Host "       open-webui:offline-latest" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
