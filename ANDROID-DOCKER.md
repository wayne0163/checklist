Android Debug build using Docker

Prerequisites
- Docker installed and running.
  - macOS: brew install --cask docker, then launch Docker.app once
  - Or download: https://www.docker.com/products/docker-desktop/
- This repo checked out locally.

Build a debug APK
- Run: bash scripts/docker-build-debug.sh (auto-detects Apple Silicon and adds --platform linux/amd64)
- First run downloads SDK/NDK inside the container (can take a while).
- Artifact: bin/<name>-<version>-<arch>-debug.apk
  - Note: Spec builds for arm64-v8a and armeabi-v7a by default. This increases build time and APK size but improves install success across devices.

Clean and retry
- Run: bash scripts/docker-clean.sh, then build again.

Install on a device (optional)
- You don’t need a device to build. To install, use Android platform tools on host:
  - bash scripts/adb-install-latest.sh
  - or: adb install -r bin/*-debug.apk
- Enable Developer Options + USB debugging on the phone before installing.

Notes
- If using Apple Silicon, you may need: add --platform linux/amd64 to docker run in scripts.
- APKs produced by "android debug" are debug-signed (sufficient for personal sharing/testing).
