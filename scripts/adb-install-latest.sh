#!/usr/bin/env bash
set -euo pipefail

# Install the latest debug APK using adb on the host.

if ! command -v adb >/dev/null 2>&1; then
  echo "adb not found. Please install Android platform-tools and ensure 'adb' is in PATH." >&2
  exit 1
fi

APK=$(ls -t bin/*-debug.apk 2>/dev/null | head -n 1 || true)
if [[ -z "${APK}" ]]; then
  echo "No debug APK found under bin/. Build one first." >&2
  exit 1
fi

echo "Installing: ${APK}"
adb devices
adb install -r "${APK}"
echo "Done. If install failed, enable USB debugging and allow installation from unknown sources on device."
