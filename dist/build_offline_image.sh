#!/bin/bash
# 이 스크립트는 리눅스 빌드 서버에서 오프라인 폐쇄망 배포용 Docker 이미지를 빌드하고 tar 파일로 추출하는 스크립트입니다.
set -e

# 스크립트가 위치한 dist 폴더의 상위 폴더(프로젝트 루트)로 이동
cd "$(dirname "$0")/.."

echo "=================================================="
echo "오프라인 폐쇄망 배포용 Docker 이미지 빌드를 시작합니다."
echo "빌드 설정: USE_CUDA=false, USE_OLLAMA=false, USE_SLIM=true"
echo "=================================================="

# 1. dist 디렉토리 존재 확인
mkdir -p dist

# 2. Docker 이미지 빌드 (가중치 캐싱을 위해 빌드 환경은 인터넷 연결 필수)
echo "[1/2] Docker 이미지를 빌드 중입니다... (USE_SLIM=true: AI 가중치 제외)"
docker build \
  --build-arg="USE_CUDA=false" \
  --build-arg="USE_OLLAMA=false" \
  --build-arg="USE_SLIM=true" \
  -t open-webui:offline-latest .

# 3. Docker 이미지를 tar 파일로 추출 및 저장
echo "[2/2] 빌드 완료된 이미지를 dist/open-webui-offline-latest.tar 파일로 아카이브 저장 중입니다..."
docker save -o dist/open-webui-offline-latest.tar open-webui:offline-latest

echo "=================================================="
echo "배포 이미지 생성 완료!"
echo "경로: dist/open-webui-offline-latest.tar"
echo "--------------------------------------------------"
echo "폐쇄망 운영 서버에서 다음 명령어로 이미지를 로드하여 기동하십시오:"
echo "  1) 이미지 로드: docker load -i open-webui-offline-latest.tar"
echo "  2) 컨테이너 기동 예시:"
echo "     docker run -d -p 8080:8080 --name open-webui \\"
echo "       -e SCARF_NO_ANALYTICS=true \\"
echo "       -e DO_NOT_TRACK=true \\"
echo "       -e ANONYMIZED_TELEMETRY=false \\"
echo "       -v open-webui:/app/backend/data \\"
echo "       open-webui:offline-latest"
echo "=================================================="
