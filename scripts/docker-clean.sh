#!/usr/bin/env bash
set -euo pipefail

# Use jedie/buildozer as alternative to kivy/buildozer
IMG=jedie/buildozer

docker run --rm -it \
  -v "$PWD":/home/user/app \
  -w /home/user/app \
  -v "$HOME/.buildozer":/home/user/.buildozer \
  -v "$HOME/.gradle":/home/user/.gradle \
  "$IMG" buildozer android clean
