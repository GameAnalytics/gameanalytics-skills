#!/usr/bin/env bash
# Builds dist/<skill>.zip for each skill, for upload to Claude (Settings > Capabilities > Skills) or other clients.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
bash scripts/sync-shared.sh >/dev/null
mkdir -p dist
for dir in skills/*/; do
  name="$(basename "$dir")"
  rm -f "dist/$name.zip"
  (cd skills && zip -qr "../dist/$name.zip" "$name" -x "*/__pycache__/*" "*.pyc" "*/.DS_Store")
  echo "dist/$name.zip"
done
