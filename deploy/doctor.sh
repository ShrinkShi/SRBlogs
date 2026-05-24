#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/srblogs"
ENV_DIR="/etc/srblogs"
DOMAIN="_"
DRY_RUN=0
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
LOG_DIR="/var/log/srblogs"
LOG_FILE="$LOG_DIR/doctor.$TIMESTAMP.log"

usage() {
  cat <<'USAGE'
Usage: sudo bash deploy/doctor.sh [options]

Options:
  --dry-run          Print diagnostic plan without probing services.
  --app-dir PATH     Application directory. Default: /opt/srblogs.
  --domain NAME      Public domain used for notes. Default: _.
  --help             Show this help.
USAGE
}

sanitize() {
  sed -E 's/((ADMIN_PASSWORD|JWT_SECRET|[A-Z0-9_]*SECRET|OAUTH_[A-Z0-9_]*|TOKEN|API_KEY)=)[^[:space:]]+/\1***REDACTED***/g'
}

log_line() {
  local message
  message="$(printf '%s' "$*" | sanitize)"
  echo "$message"
  if [ "$DRY_RUN" -eq 0 ]; then
    ensure_log_dir
    printf '%s\n' "$message" >>"$LOG_FILE" 2>/dev/null || true
  fi
}

ensure_log_dir() {
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$LOG_DIR" 2>/dev/null || true
  fi
}

pass() { PASS_COUNT=$((PASS_COUNT + 1)); log_line "[PASS] $*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); log_line "[WARN] $*"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); log_line "[FAIL] $*"; }

on_error() {
  local line="$1"
  local command="$2"
  log_line "[error] doctor.sh failed at line $line: $command"
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --app-dir) APP_DIR="${2:-}"; shift 2 ;;
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

ENV_FILE="$ENV_DIR/backend.env"
HEALTH_LAST_ERROR=""
HEALTH_OK_URL=""

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

settings_data_dir() {
  local value=""
  if [ -f "$ENV_FILE" ]; then
    value="$(grep -E '^DATA_DIR=' "$ENV_FILE" 2>/dev/null | tail -n 1 || true)"
    value="${value#DATA_DIR=}"
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
  fi
  if [ -z "$value" ]; then
    printf '%s\n' "$APP_DIR/backend/data"
  elif [[ "$value" = /* ]]; then
    printf '%s\n' "$value"
  elif [[ "$value" = data || "$value" = data/* ]]; then
    printf '%s\n' "$APP_DIR/backend/$value"
  else
    printf '%s\n' "$APP_DIR/$value"
  fi
}

node_major() {
  node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/'
}

check_python() {
  if command_exists python3.11; then
    pass "python3.11 found: $(python3.11 --version 2>&1)"
  else
    fail "python3.11 is missing."
  fi
}

check_node() {
  if ! command_exists node; then
    fail "node is missing."
    return
  fi
  local major
  major="$(node_major)"
  if [ -z "$major" ] || [ "$major" -lt 20 ]; then
    fail "Node $(node -v) is below required version 20."
  elif [ "$major" -eq 20 ]; then
    pass "Node $(node -v) found. Node 20 LTS is recommended."
  elif [ "$major" -le 22 ]; then
    warn "Node $(node -v) found. Node 20 LTS is recommended for production."
  else
    warn "Node $(node -v) is newer than validated range. Node 20 LTS is recommended."
  fi
  if command_exists npm; then
    pass "npm found: $(npm -v)"
  else
    fail "npm is missing."
  fi
}

check_services() {
  if command_exists systemctl && systemctl is-active --quiet nginx; then
    pass "nginx is running."
  else
    fail "nginx is not running."
  fi
  if command_exists systemctl && systemctl is-active --quiet srblogs-backend; then
    pass "srblogs-backend is running."
    pass "service check command: systemctl status srblogs-backend --no-pager"
    pass "log command: journalctl -u srblogs-backend -n 100 --no-pager"
  else
    fail "srblogs-backend is not running. Check with: systemctl status srblogs-backend --no-pager"
  fi
  if command_exists systemctl && systemctl list-unit-files srblogs.service --no-legend 2>/dev/null | grep -q '^srblogs\.service'; then
    warn "legacy systemd unit srblogs.service exists; use srblogs-backend.service only."
  else
    pass "no legacy srblogs.service unit found."
  fi
  if [ -f /etc/systemd/system/srblogs-backend.service ]; then
    if grep -q '^KillMode=process' /etc/systemd/system/srblogs-backend.service 2>/dev/null; then
      pass "srblogs-backend.service keeps update runner alive during backend restart."
    else
      warn "srblogs-backend.service is missing KillMode=process; WebUI-triggered update may be interrupted during restart."
    fi
  fi
  if command_exists ss && ss -ltn | grep -q ':8000 '; then
    pass "port 8000 is listening."
  elif command_exists netstat && netstat -ltn | grep -q ':8000 '; then
    pass "port 8000 is listening."
  else
    fail "port 8000 is not listening."
  fi
}

check_sudo_nopasswd() {
  if ! command_exists sudo; then
    warn "sudo is missing; WebUI update cannot escalate to run deploy/update.sh."
    return
  fi
  if [ "$(id -u)" -eq 0 ]; then
    local service_user="srblogs"
    if [ -f /etc/systemd/system/srblogs-backend.service ]; then
      service_user="$(grep -E '^User=' /etc/systemd/system/srblogs-backend.service 2>/dev/null | tail -n 1 | cut -d= -f2- || echo srblogs)"
      service_user="${service_user:-srblogs}"
    fi
    if ! id "$service_user" >/dev/null 2>&1; then
      warn "service user $service_user does not exist; cannot verify WebUI update sudo permission."
      return
    fi
    local output
    if output="$(sudo -u "$service_user" sudo -n true 2>&1)"; then
      pass "sudo -n true succeeded for service user $service_user; WebUI update can run deploy/update.sh."
    else
      warn "sudo -n true failed for service user $service_user; WebUI update will fail unless NOPASSWD sudo is configured. Reason: ${output:-unknown}"
    fi
    return
  fi
  local output
  if output="$(sudo -n true 2>&1)"; then
    pass "sudo -n true succeeded; WebUI update can run deploy/update.sh without password prompt."
  else
    warn "sudo -n true failed; WebUI update will fail unless NOPASSWD sudo is configured. Reason: ${output:-unknown}"
  fi
}

api_health_once() {
  local url output
  for url in http://127.0.0.1:8000/api/health http://127.0.0.1:8000/api/system/health; do
    log_line "[health] checking $url"
    if output="$(curl --fail --silent --show-error --max-time 5 "$url" 2>&1)"; then
      HEALTH_OK_URL="$url"
      log_line "[health] ok: $url"
      return 0
    fi
    HEALTH_LAST_ERROR="$url -> ${output:-curl failed}"
    log_line "[health] failed: $HEALTH_LAST_ERROR"
  done
  return 1
}

wait_for_api_health() {
  local attempt
  HEALTH_LAST_ERROR=""
  HEALTH_OK_URL=""
  for attempt in $(seq 1 30); do
    if api_health_once; then
      return 0
    fi
    log_line "[health] attempt $attempt/30 failed. Last error: ${HEALTH_LAST_ERROR:-unknown}"
    sleep 2
  done
  return 1
}

check_http() {
  local status_file="/tmp/srblogs-doctor-install-status.$$"
  local admin_html="/tmp/srblogs-doctor-admin-login.$$"
  if wait_for_api_health; then
    pass "backend health is reachable. Endpoint: $HEALTH_OK_URL"
  else
    fail "backend health is not reachable after 30 attempts. Last error: ${HEALTH_LAST_ERROR:-unknown}"
  fi
  if curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/install/status >"$status_file" 2>/dev/null; then
    pass "/api/install/status is reachable."
    if grep -q '"installed"[[:space:]]*:[[:space:]]*true' "$status_file"; then
      check_settings_chain
    else
      warn "system is not installed yet; /api/settings/public may return INSTALL_REQUIRED."
    fi
  else
    fail "/api/install/status is not reachable."
  fi
  if curl --fail --silent --show-error --max-time 10 http://127.0.0.1/admin/login >"$admin_html" 2>/dev/null; then
    pass "/admin/login returns HTTP 200."
    if grep -Eq 'id="app"|/admin/assets/|<script' "$admin_html"; then
      pass "/admin/login contains admin SPA entry markup."
    else
      fail "/admin/login does not look like the admin SPA HTML."
    fi
    check_admin_assets "$admin_html"
  else
    fail "/admin/login is not reachable through Nginx."
  fi
}

settings_summary() {
  local body_file="$1"
  local version="-"
  if [ -f "$APP_DIR/VERSION" ]; then
    version="$(tr -d '\r\n' <"$APP_DIR/VERSION" 2>/dev/null || echo "-")"
  fi
  if command_exists python3.11; then
    local summary
    summary="$(python3.11 - "$body_file" "$version" <<'PY' 2>/dev/null || true
import json
import sys

path = sys.argv[1]
version = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)
title = data.get("siteTitle") or data.get("title") or ""
subtitle = data.get("subtitle") or data.get("description") or ""
print(f"settings summary: siteTitle={title!r}, subtitle={subtitle!r}, version={version or '-'}")
PY
)"
    if [ -n "$summary" ]; then
      log_line "$summary"
    else
      warn "could not parse /api/settings/public response body."
    fi
  else
    log_line "settings summary: python3.11 unavailable; raw settings body stored at $body_file, version=$version"
  fi
}

check_cache_header() {
  local label="$1"
  local headers_file="$2"
  if grep -iq '^cache-control:.*no-store' "$headers_file"; then
    pass "$label Cache-Control contains no-store."
  else
    warn "$label Cache-Control does not contain no-store; /api/settings/public may be cached by browser or proxy."
  fi
}

check_settings_chain() {
  local data_dir
  data_dir="$(settings_data_dir)"
  local data_file="$data_dir/settings.json"
  local backend_headers="/tmp/srblogs-doctor-settings-backend-headers.$$"
  local backend_body="/tmp/srblogs-doctor-settings-backend-body.$$"
  local nginx_headers="/tmp/srblogs-doctor-settings-nginx-headers.$$"
  local nginx_body="/tmp/srblogs-doctor-settings-nginx-body.$$"

  if [ -f "$data_file" ]; then
    pass "production settings file exists: $data_file"
  else
    fail "production settings file is missing: $data_file"
  fi

  if curl --fail --silent --show-error --max-time 10 -D "$backend_headers" -o "$backend_body" http://127.0.0.1:8000/api/settings/public 2>/dev/null; then
    pass "/api/settings/public is reachable from backend."
    settings_summary "$backend_body"
    check_cache_header "backend /api/settings/public" "$backend_headers"
  else
    fail "/api/settings/public is not reachable from backend after installation."
  fi

  if curl --fail --silent --show-error --max-time 10 -D "$nginx_headers" -o "$nginx_body" http://127.0.0.1/api/settings/public 2>/dev/null; then
    pass "/api/settings/public is reachable through Nginx."
    check_cache_header "Nginx /api/settings/public" "$nginx_headers"
  else
    fail "/api/settings/public is not reachable through Nginx."
  fi
}

check_admin_assets() {
  local html_file="$1"
  local asset path
  asset="$(grep -Eo '/admin/assets/[^"]+\.(js|css)' "$html_file" | head -n 1 || true)"
  if [ -z "$asset" ]; then
    fail "admin HTML does not reference /admin/assets JS/CSS."
    return
  fi
  path="http://127.0.0.1$asset"
  if curl --fail --silent --show-error --head --max-time 10 "$path" >/dev/null 2>&1; then
    pass "admin asset is reachable: $asset"
  else
    fail "admin asset is not reachable: $asset"
  fi
}

check_files() {
  [ -d "$APP_DIR" ] && pass "$APP_DIR exists." || fail "$APP_DIR is missing."
  local data_dir
  data_dir="$(settings_data_dir)"
  [ -d "$data_dir" ] && pass "data directory exists: $data_dir" || fail "data directory is missing: $data_dir"
  [ -d "$APP_DIR/backend/.venv" ] && pass "backend virtualenv exists." || fail "backend virtualenv is missing."
  [ -f "$APP_DIR/frontend/dist/index.html" ] && pass "frontend dist exists." || fail "frontend dist is missing."
  [ -f "$APP_DIR/admin/dist/index.html" ] && pass "admin dist exists." || fail "admin dist is missing."
}

check_update_task() {
  local data_dir update_dir task_file info status pid log_path exit_code
  data_dir="$(settings_data_dir)"
  update_dir="$data_dir/update_logs"
  task_file="$update_dir/update-task.json"

  if [ -d "$update_dir" ]; then
    pass "update_logs directory exists: $update_dir"
  else
    warn "update_logs directory is missing: $update_dir"
    return
  fi

  if [ ! -f "$task_file" ]; then
    warn "no update task record found yet: $task_file"
    return
  fi

  if ! command_exists python3.11; then
    warn "python3.11 unavailable; cannot parse update task record."
    return
  fi

  info="$(python3.11 - "$task_file" <<'PY' 2>/dev/null || true
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)
for key in ("taskId", "status", "pid", "exitCode", "currentStep", "progress", "logPath", "startedAt", "finishedAt", "errorMessage"):
    value = data.get(key)
    if value is None:
        value = ""
    print(f"{key}={value}")
PY
)"
  if [ -z "$info" ]; then
    warn "could not parse update task record: $task_file"
    return
  fi

  status="$(printf '%s\n' "$info" | sed -n 's/^status=//p' | tail -n 1)"
  pid="$(printf '%s\n' "$info" | sed -n 's/^pid=//p' | tail -n 1)"
  log_path="$(printf '%s\n' "$info" | sed -n 's/^logPath=//p' | tail -n 1)"
  exit_code="$(printf '%s\n' "$info" | sed -n 's/^exitCode=//p' | tail -n 1)"
  log_line "update task: $(printf '%s' "$info" | tr '\n' ' ')"

  if [ "$status" = "running" ]; then
    if [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1; then
      pass "latest update task is running with pid $pid."
    else
      warn "latest update task is running but pid is not alive; stale task may need review."
    fi
  elif [ "$status" = "success" ]; then
    pass "latest update task completed successfully."
  elif [ "$status" = "failed" ]; then
    warn "latest update task failed with exitCode=${exit_code:-unknown}; review logs."
  elif [ "$status" = "idle" ] || [ -z "$status" ]; then
    pass "no update task is running."
  else
    warn "latest update task has unknown status: $status"
  fi

  if [ -n "$log_path" ] && [ -f "$log_path" ]; then
    pass "latest update log exists: $log_path"
  elif [ -n "$log_path" ]; then
    warn "latest update log path is recorded but missing: $log_path"
  else
    warn "latest update task has no logPath."
  fi
}

check_env_permissions() {
  if [ ! -f "$ENV_FILE" ]; then
    fail "$ENV_FILE is missing."
    return
  fi
  pass "$ENV_FILE exists."
  local mode owner group
  mode="$(stat -c '%a' "$ENV_FILE" 2>/dev/null || echo unknown)"
  owner="$(stat -c '%U' "$ENV_FILE" 2>/dev/null || echo unknown)"
  group="$(stat -c '%G' "$ENV_FILE" 2>/dev/null || echo unknown)"
  case "$mode" in
    600|640) pass "$ENV_FILE mode is $mode." ;;
    *) warn "$ENV_FILE mode is $mode; 600 or 640 is recommended." ;;
  esac
  local install_lock
  install_lock="$(settings_data_dir)/.install.lock"
  if [ -f "$install_lock" ] && [[ "$mode" =~ ^[0-7]{3,4}$ ]]; then
    local perm owner_digit group_digit other_digit srblogs_writable=0
    perm="${mode: -3}"
    owner_digit="${perm:0:1}"
    group_digit="${perm:1:1}"
    other_digit="${perm:2:1}"
    if [ "$owner" = "srblogs" ] && (( owner_digit & 2 )); then srblogs_writable=1; fi
    if [ "$group" = "srblogs" ] && (( group_digit & 2 )); then srblogs_writable=1; fi
    if (( other_digit & 2 )); then srblogs_writable=1; fi
    if [ "$srblogs_writable" -eq 1 ]; then
      warn "installed system still leaves backend.env writable by srblogs or others; tighten permissions."
    fi
  fi
  if grep -Eq '^ADMIN_PASSWORD=' "$ENV_FILE" 2>/dev/null; then
    warn "$ENV_FILE contains legacy ADMIN_PASSWORD; prefer ADMIN_PASSWORD_HASH and rotate with backend/scripts/reset_admin.py."
  fi
  if grep -Eq "^ADMIN_PASSWORD=['\"]?(change-me|admin|123456|password|admin123)['\"]?$" "$ENV_FILE" 2>/dev/null ||
     grep -Eq "^JWT_SECRET=['\"]?(please-change-this-secret|change-me)['\"]?$" "$ENV_FILE" 2>/dev/null; then
    warn "$ENV_FILE still contains a weak default credential or secret placeholder."
  fi
  if [ -f "$install_lock" ]; then
    if grep -Eq '^ADMIN_USERNAME=' "$ENV_FILE" 2>/dev/null; then
      pass "installed system has ADMIN_USERNAME configured."
    else
      fail "installed system is missing ADMIN_USERNAME in $ENV_FILE."
    fi
    if grep -Eq '^ADMIN_PASSWORD_HASH=' "$ENV_FILE" 2>/dev/null; then
      pass "installed system uses ADMIN_PASSWORD_HASH."
    elif grep -Eq '^ADMIN_PASSWORD=' "$ENV_FILE" 2>/dev/null; then
      warn "installed system still uses legacy ADMIN_PASSWORD; rotate with backend/scripts/reset_admin.py."
    else
      fail "installed system has no admin credential in $ENV_FILE."
    fi
  fi
}

check_nginx_defaults() {
  local found=0 file
  for file in /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/welcome.conf; do
    if [ -f "$file" ]; then
      warn "default nginx site may conflict: $file"
      found=1
    fi
  done
  [ "$found" -eq 0 ] && pass "no known default nginx site conflicts found."
  local conf="/etc/nginx/conf.d/srblogs.conf"
  if [ -f "$conf" ]; then
    if grep -Eq 'location[[:space:]]+\^~[[:space:]]+/admin/' "$conf" 2>/dev/null &&
       grep -Eq 'alias[[:space:]]+.*/admin/dist/' "$conf" 2>/dev/null; then
      pass "srblogs nginx admin SPA fallback uses the current template."
    else
      warn "srblogs nginx config may use an old admin SPA template; rerun install.sh/update.sh or review /etc/nginx/conf.d/srblogs.conf."
    fi
  else
    fail "srblogs nginx config is missing: $conf"
  fi
}

check_swap() {
  if swapon --show | grep -q .; then
    pass "swap is enabled."
  else
    warn "swap is not enabled; 2C2G builds may fail under memory pressure."
  fi
}

main() {
  if [ "$DRY_RUN" -eq 1 ]; then
    log_line "SRBlogs doctor dry-run plan for $APP_DIR on domain $DOMAIN."
    log_line "Would check Python, Node/npm, services, sudo -n true, port 8000, HTTP endpoints, settings cache, update task logs, permissions, dist files, nginx defaults, and swap."
    log_line "Summary: PASS=0 WARN=0 FAIL=0"
    return 0
  fi
  check_python
  check_node
  check_services
  check_sudo_nopasswd
  check_http
  check_files
  check_update_task
  check_env_permissions
  check_nginx_defaults
  check_swap
  log_line "Summary: PASS=$PASS_COUNT WARN=$WARN_COUNT FAIL=$FAIL_COUNT"
  if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
  fi
}

main "$@"
