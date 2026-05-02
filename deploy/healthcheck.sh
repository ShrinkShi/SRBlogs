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

check "backend health" "$API_BASE_URL/api/health"
check "frontend homepage" "$PUBLIC_BASE_URL/"
check "admin entry" "$PUBLIC_BASE_URL/admin/"
check "rss" "$PUBLIC_BASE_URL/api/rss.xml"
check "sitemap" "$PUBLIC_BASE_URL/api/sitemap.xml"
check "robots" "$PUBLIC_BASE_URL/robots.txt"

echo "All health checks passed."
