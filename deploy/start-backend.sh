#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/srblogs}"
BACKEND_DIR="${BACKEND_DIR:-$APP_DIR/backend}"
ENV_FILE="${ENV_FILE:-/etc/srblogs/backend.env}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

cd "$BACKEND_DIR"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing backend virtualenv: $BACKEND_DIR/.venv"
  echo "Create it with: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

exec .venv/bin/python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
