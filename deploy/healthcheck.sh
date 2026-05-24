#!/usr/bin/env bash
set -euo pipefail

PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://127.0.0.1}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"

check() {
  local name="$1"
  local url="$2"
  echo "[check] $name -> $url"
  curl --fail --silent --show-error --max-time 10 "$url" >/dev/null
}

check_backend_health() {
  local attempt url output last_error=""
  for attempt in $(seq 1 30); do
    for url in "$API_BASE_URL/api/health" "$API_BASE_URL/api/system/health"; do
      echo "[check] backend health -> $url"
      if output="$(curl --fail --silent --show-error --max-time 5 "$url" 2>&1)"; then
        echo "[ok] backend health endpoint: $url"
        return 0
      fi
      last_error="$url -> ${output:-curl failed}"
      echo "[warn] backend health failed: $last_error"
    done
    echo "[warn] backend health attempt $attempt/30 failed. Last error: ${last_error:-unknown}"
    sleep 2
  done
  echo "[fail] backend health failed after 30 attempts. Last error: ${last_error:-unknown}"
  return 1
}

check_backend_health
check "frontend homepage" "$PUBLIC_BASE_URL/"
check "admin entry" "$PUBLIC_BASE_URL/admin/"
check "rss" "$PUBLIC_BASE_URL/api/rss.xml"
check "sitemap" "$PUBLIC_BASE_URL/api/sitemap.xml"
check "robots" "$PUBLIC_BASE_URL/robots.txt"

echo "All health checks passed."
