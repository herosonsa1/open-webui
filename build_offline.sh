#!/bin/bash
# Offline build script for Open-WebUI Docker Image
set -e

# Change directory to the script folder
cd "$(dirname "$0")"

echo "=================================================="
echo "Starting Offline WebUI Docker Build"
echo "Args: USE_CUDA=false, USE_OLLAMA=false, USE_SLIM=false"
echo "=================================================="

# 1. Create dist directory
mkdir -p dist

# 2. Run docker build
echo "[1/2] Building Docker image... (This may take 10-20 mins)"
docker build \
  --build-arg="USE_CUDA=false" \
  --build-arg="USE_OLLAMA=false" \
  --build-arg="USE_SLIM=false" \
  -t open-webui:offline-latest .

# 3. Save to tar archive
echo "[2/2] Saving image to dist/open-webui-offline-latest.tar..."
docker save -o dist/open-webui-offline-latest.tar open-webui:offline-latest

echo "=================================================="
echo "Build and save completed successfully!"
echo "Target: dist/open-webui-offline-latest.tar"
echo "=================================================="
