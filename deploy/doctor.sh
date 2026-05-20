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
INSTALL_LOCK="$APP_DIR/backend/data/.install.lock"

command_exists() {
  command -v "$1" >/dev/null 2>&1
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
  if command_exists ss && ss -ltn | grep -q ':8000 '; then
    pass "port 8000 is listening."
  elif command_exists netstat && netstat -ltn | grep -q ':8000 '; then
    pass "port 8000 is listening."
  else
    fail "port 8000 is not listening."
  fi
}

check_http() {
  if curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    pass "/api/health is reachable."
  else
    fail "/api/health is not reachable."
  fi
  local status_file="/tmp/srblogs-doctor-install-status.$$"
  if curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/install/status >"$status_file" 2>/dev/null; then
    pass "/api/install/status is reachable."
    if grep -q '"installed"[[:space:]]*:[[:space:]]*true' "$status_file"; then
      if curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/settings/public >/dev/null 2>&1; then
        pass "/api/settings/public is reachable."
      else
        fail "/api/settings/public is not reachable after installation."
      fi
    else
      warn "system is not installed yet; /api/settings/public may return INSTALL_REQUIRED."
    fi
  else
    fail "/api/install/status is not reachable."
  fi
}

check_files() {
  [ -d "$APP_DIR" ] && pass "$APP_DIR exists." || fail "$APP_DIR is missing."
  [ -d "$APP_DIR/backend/data" ] && pass "backend/data exists." || fail "backend/data is missing."
  [ -d "$APP_DIR/backend/.venv" ] && pass "backend virtualenv exists." || fail "backend virtualenv is missing."
  [ -f "$APP_DIR/frontend/dist/index.html" ] && pass "frontend dist exists." || fail "frontend dist is missing."
  [ -f "$APP_DIR/admin/dist/index.html" ] && pass "admin dist exists." || fail "admin dist is missing."
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
  if [ -f "$INSTALL_LOCK" ] && [[ "$mode" =~ ^[0-7]{3,4}$ ]]; then
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
  if grep -Eq '^(ADMIN_PASSWORD|JWT_SECRET)=change-me' "$ENV_FILE" 2>/dev/null; then
    warn "$ENV_FILE still contains a default placeholder secret."
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
    log_line "Would check Python, Node/npm, services, port 8000, HTTP endpoints, permissions, dist files, nginx defaults, and swap."
    log_line "Summary: PASS=0 WARN=0 FAIL=0"
    return 0
  fi
  check_python
  check_node
  check_services
  check_http
  check_files
  check_env_permissions
  check_nginx_defaults
  check_swap
  log_line "Summary: PASS=$PASS_COUNT WARN=$WARN_COUNT FAIL=$FAIL_COUNT"
  if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
  fi
}

main "$@"
