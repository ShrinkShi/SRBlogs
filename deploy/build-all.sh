#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[frontend] installing dependencies and building"
cd "$ROOT_DIR/frontend"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
npm run build

echo "[admin] installing dependencies and building"
cd "$ROOT_DIR/admin"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
npm run build

echo "[backend] checking Python syntax"
cd "$ROOT_DIR"
python -m compileall backend/app

echo "Build complete:"
echo "- frontend/dist"
echo "- admin/dist"
