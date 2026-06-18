# 오프라인 폐쇄망 배포용 Docker 이미지 빌드 패키지 안내

이 디렉토리는 인터넷이 제한된 오프라인(폐쇄망) 리눅스 운영서버에 `open-webui`를 Docker 이미지로 배포하기 위한 패키지 및 빌드 스크립트를 포함하고 있습니다.

## 포함된 빌드 스크립트
1. [build_offline_image.sh](file:///c:/myWork/workspace/scratch/open-webui/dist/build_offline_image.sh) : 리눅스 서버 환경에서 이미지를 빌드하고 tar 아카이브로 추출하는 쉘 스크립트입니다.
2. [build_offline_image.ps1](file:///c:/myWork/workspace/scratch/open-webui/dist/build_offline_image.ps1) : Windows 환경(Docker Desktop 설치됨)에서 이미지를 빌드하고 tar 아카이브로 추출하는 PowerShell 스크립트입니다.

## 중요한 참고사항
- **빌드 환경의 인터넷 연결 필수**: 빌드 타임에 RAG 임베딩 가중치(`sentence-transformers/all-MiniLM-L6-v2`), 보조 가중치(`TaylorAI/bge-micro-v2`), 음성 인식 가중치(`Whisper base`), `tiktoken` 사전, `nltk` 데이터를 자동으로 인터넷에서 다운로드하여 이미지 내부에 캐싱합니다 (`USE_SLIM=false` 설정). 따라서, **이 이미지를 빌드하는 머신(Windows 또는 Linux 빌드 장비)은 인터넷에 정상적으로 연결되어 있어야 합니다.**
- **호스트 환경 진단 결과**: 현재 이 Windows 개발 환경에는 Docker 데몬(Docker Desktop 등)이 설치되어 있지 않아 로컬 빌드가 불가능합니다.
  따라서 본 빌드 패키지 소스를 빌드 가능한 운영 서버(리눅스)로 가져가 `dist/build_offline_image.sh`를 실행하거나, 이 PC에 Docker Desktop을 설치한 뒤 `dist/build_offline_image.ps1`을 실행하여 이미지를 추출해야 합니다.

## 리눅스 서버 빌드 방법 (인터넷 가능 서버 기준)
1. 이 프로젝트 소스 코드 전체를 리눅스 빌드 서버로 복사합니다.
2. `dist` 폴더 내 빌드 스크립트에 실행 권한을 부여하고 실행합니다:
   ```bash
   chmod +x dist/build_offline_image.sh
   ./dist/build_offline_image.sh
   ```
3. 완료되면 `dist/open-webui-offline-latest.tar` 파일이 생성됩니다.

## 오프라인 폐쇄망 서버 배포 및 실행 방법
1. 빌드 완료된 `dist/open-webui-offline-latest.tar` 파일을 오프라인 리눅스 운영 서버로 이동시킵니다.
2. 리눅스 운영 서버에서 다음 명령으로 Docker 이미지를 로드합니다:
   ```bash
   docker load -i open-webui-offline-latest.tar
   ```
3. 외부 CDN 접속 시도 및 텔레메트리 전송을 완전히 차단하기 위해 아래 환경변수를 지정하여 컨테이너를 구동합니다:
   ```bash
   docker run -d -p 8080:8080 --name open-webui \
     -e SCARF_NO_ANALYTICS=true \
     -e DO_NOT_TRACK=true \
     -e ANONYMIZED_TELEMETRY=false \
     -v open-webui:/app/backend/data \
     open-webui:offline-latest
   ```
