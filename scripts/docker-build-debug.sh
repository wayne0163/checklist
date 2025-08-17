#!/usr/bin/env bash
set -euo pipefail

# Build debug APK via Docker (no device needed).
# Auto-add --platform linux/amd64 on Apple Silicon (M1/M2).

# Use jedie/buildozer as alternative to kivy/buildozer
IMG=jedie/buildozer

PLATFORM_FLAG=""
ARCH=$(uname -m || true)
if [[ "${ARCH}" == "arm64" || "${ARCH}" == "aarch64" ]]; then
  PLATFORM_FLAG="--platform linux/amd64"
fi
# Allow override: DOCKER_PLATFORM_FLAG=""
PLATFORM_FLAG=${DOCKER_PLATFORM_FLAG:-$PLATFORM_FLAG}

# Ensure Docker is available
if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker not found.\n- Install Docker Desktop (macOS): brew install --cask docker, then start Docker.app\n- Or download from: https://www.docker.com/products/docker-desktop/" >&2
  exit 127
fi

echo "Using docker image: ${IMG} ${PLATFORM_FLAG}"

docker run --rm -it ${PLATFORM_FLAG} \
  -v "$PWD":/home/user/app \
  -w /home/user/app \
  -v "$HOME/.buildozer":/home/user/.buildozer \
  -v "$HOME/.gradle":/home/user/.gradle \
  "$IMG" buildozer android debug

echo
echo "If successful, your APK is under: bin/"
