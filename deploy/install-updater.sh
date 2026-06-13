#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/srblogs"
SERVICE_USER="srblogs"
SERVICE_GROUP="srblogs"
MAIN_SERVICE="srblogs-backend.service"
UPDATER_BIN="/usr/local/sbin/srblogs-update"
UPDATER_SERVICE="/etc/systemd/system/srblogs-updater.service"
SUDOERS_FILE="/etc/sudoers.d/srblogs-updater"
STATE_DIR="/var/lib/srblogs/update"
REPO="ShrinkShi/SRBlogs"

usage() {
  cat <<'USAGE'
Usage: sudo bash deploy/install-updater.sh [options]

Options:
  --app-dir PATH       SRBlogs application root. Default: /opt/srblogs.
  --user NAME          SRBlogs service user. Default: srblogs.
  --group NAME         SRBlogs service group. Default: srblogs.
  --service NAME       Main backend service. Default: srblogs-backend.service.
  --repo OWNER/REPO    Fixed GitHub repository. Default: ShrinkShi/SRBlogs.
  --help              Show this help.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --app-dir) APP_DIR="${2:-}"; shift 2 ;;
    --user) SERVICE_USER="${2:-}"; shift 2 ;;
    --group) SERVICE_GROUP="${2:-}"; shift 2 ;;
    --service) MAIN_SERVICE="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash deploy/install-updater.sh"
  exit 1
fi

if [ "$REPO" != "ShrinkShi/SRBlogs" ]; then
  echo "For safety this installer only supports ShrinkShi/SRBlogs."
  exit 2
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home "$APP_DIR" --shell /sbin/nologin "$SERVICE_USER"
fi

install -d -m 0750 -o root -g "$SERVICE_GROUP" "$STATE_DIR"
install -d -m 0755 -o root -g root "$APP_DIR/releases"
install -d -m 0750 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$APP_DIR/shared"
install -d -m 0770 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$APP_DIR/shared/data"

if [ ! -f "$STATE_DIR/status.json" ]; then
  printf '%s\n' '{"status":"idle","currentStep":"idle","progress":0,"message":"updater installed"}' >"$STATE_DIR/status.json"
fi
if [ ! -f "$STATE_DIR/request.json" ]; then
  printf '%s\n' '{"repo":"ShrinkShi/SRBlogs","targetVersion":"","requestedAt":"","requestedBy":""}' >"$STATE_DIR/request.json"
fi
touch "$STATE_DIR/updater.log"
chown root:"$SERVICE_GROUP" "$STATE_DIR" "$STATE_DIR/status.json" "$STATE_DIR/request.json" "$STATE_DIR/updater.log"
chmod 0750 "$STATE_DIR"
chmod 0640 "$STATE_DIR/status.json" "$STATE_DIR/updater.log"
chmod 0660 "$STATE_DIR/request.json"

cat >"$UPDATER_BIN" <<'UPDATER'
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${SRBLOGS_APP_DIR:-/opt/srblogs}"
SERVICE_USER="${SRBLOGS_SERVICE_USER:-srblogs}"
SERVICE_GROUP="${SRBLOGS_SERVICE_GROUP:-srblogs}"
MAIN_SERVICE="${SRBLOGS_MAIN_SERVICE:-srblogs-backend.service}"
STATE_DIR="${SRBLOGS_UPDATE_STATE_DIR:-/var/lib/srblogs/update}"
REPO="${SRBLOGS_UPDATE_REPO:-ShrinkShi/SRBlogs}"
RELEASES_DIR="$APP_DIR/releases"
CURRENT_LINK="$APP_DIR/current"
SHARED_DIR="$APP_DIR/shared"
STATUS_FILE="$STATE_DIR/status.json"
REQUEST_FILE="$STATE_DIR/request.json"
LOG_FILE="$STATE_DIR/updater.log"
LOCK_FILE="$STATE_DIR/update.lock"
WORK_DIR=""
OLD_CURRENT=""
TARGET_VERSION=""

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])'
}

write_status() {
  local status="$1" step="$2" progress="$3" message="${4:-}" exit_code="${5:-null}" error_code="${6:-}" error_message="${7:-}"
  local now
  now="$(date -Is)"
  local escaped_message escaped_error
  escaped_message="$(printf '%s' "$message" | json_escape)"
  escaped_error="$(printf '%s' "$error_message" | json_escape)"
  cat >"$STATUS_FILE.tmp" <<JSON
{
  "taskId": "${TARGET_VERSION:-latest}",
  "status": "$status",
  "startedAt": "${STARTED_AT:-$now}",
  "finishedAt": "$([ "$status" = "running" ] && printf '' || printf '%s' "$now")",
  "updatedAt": "$now",
  "pid": $$,
  "exitCode": $exit_code,
  "currentStep": "$step",
  "progress": $progress,
  "logPath": "$LOG_FILE",
  "errorCode": "$error_code",
  "errorMessage": "$escaped_error",
  "message": "$escaped_message",
  "repo": "$REPO",
  "targetVersion": "$TARGET_VERSION",
  "previousVersion": "$OLD_CURRENT",
  "rollback": false
}
JSON
  mv "$STATUS_FILE.tmp" "$STATUS_FILE"
  chown root:"$SERVICE_GROUP" "$STATUS_FILE"
  chmod 0640 "$STATUS_FILE"
}

log() {
  local message="$*"
  printf '[%s] %s\n' "$(date -Is)" "$message" | tee -a "$LOG_FILE"
}

progress() {
  local percent="$1" step="$2" message="${3:-$2}"
  log "[$percent%] $step - $message"
  write_status "running" "$step" "$percent" "$message"
}

fail_status() {
  local step="$1" message="$2" code="${3:-update_failed}" exit_code="${4:-1}"
  log "failed: $message"
  write_status "failed" "$step" 0 "$message" "$exit_code" "$code" "$message"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    fail_status "preflight" "missing command: $1" "missing_dependency" 1
    exit 1
  }
}

run_as_app() {
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "$SERVICE_USER" -- "$@"
  else
    su -s /bin/bash "$SERVICE_USER" -c "$(printf '%q ' "$@")"
  fi
}

read_request_version() {
  python3 - "$REQUEST_FILE" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    data = {}
print(str(data.get("targetVersion") or "").strip())
PY
}

fetch_latest_release() {
  local release_json="$1"
  curl -fsSL \
    -H "Accept: application/vnd.github+json" \
    -H "User-Agent: SRBlogs-Restricted-Updater" \
    "https://api.github.com/repos/$REPO/releases/latest" \
    -o "$release_json"
}

parse_release_field() {
  local release_json="$1" field="$2"
  python3 - "$release_json" "$field" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(str(data.get(sys.argv[2]) or ""))
PY
}

version_key() {
  python3 - "$1" <<'PY'
import re, sys
parts = re.findall(r"\d+", sys.argv[1].lstrip("vV"))
print(".".join(parts[:3]) if parts else "0")
PY
}

normalize_source() {
  local unpack_dir="$1" normalized="$2"
  if [ -f "$unpack_dir/admin/package.json" ] && [ -f "$unpack_dir/frontend/package.json" ] && [ -d "$unpack_dir/backend/app" ]; then
    mv "$unpack_dir" "$normalized"
    return 0
  fi
  local child
  child="$(find "$unpack_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
  if [ -n "$child" ] && [ -f "$child/admin/package.json" ] && [ -f "$child/frontend/package.json" ] && [ -d "$child/backend/app" ]; then
    mv "$child" "$normalized"
    return 0
  fi
  return 1
}

prepare_shared_data() {
  install -d -m 0770 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$SHARED_DIR/data"
  install -d -m 0770 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$SHARED_DIR/data/uploads"
  install -d -m 0770 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$SHARED_DIR/data/update_logs"
  install -d -m 0770 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$SHARED_DIR/data/update_downloads"

  if [ ! -e "$SHARED_DIR/data/settings.json" ]; then
    if [ -n "$OLD_CURRENT" ] && [ -e "$OLD_CURRENT/backend/data" ]; then
      cp -a "$OLD_CURRENT/backend/data/." "$SHARED_DIR/data/" || true
    elif [ -e "$APP_DIR/backend/data" ]; then
      cp -a "$APP_DIR/backend/data/." "$SHARED_DIR/data/" || true
    fi
  fi
  chown -R "$SERVICE_USER:$SERVICE_GROUP" "$SHARED_DIR/data"
}

build_release() {
  local release_dir="$1"
  prepare_shared_data
  rm -rf "$release_dir/backend/data"
  ln -s "$SHARED_DIR/data" "$release_dir/backend/data"
  chown -R "$SERVICE_USER:$SERVICE_GROUP" "$release_dir"

  if command -v python3.11 >/dev/null 2>&1; then
    run_as_app python3.11 -m venv "$release_dir/backend/.venv"
  else
    run_as_app python3 -m venv "$release_dir/backend/.venv"
  fi
  run_as_app "$release_dir/backend/.venv/bin/python" -m pip install --upgrade pip
  run_as_app "$release_dir/backend/.venv/bin/pip" install -r "$release_dir/backend/requirements.txt"

  if [ -f "$release_dir/frontend/package-lock.json" ]; then
    run_as_app npm --prefix "$release_dir/frontend" ci
  else
    run_as_app npm --prefix "$release_dir/frontend" install
  fi
  run_as_app env NODE_OPTIONS=--max-old-space-size=1024 npm --prefix "$release_dir/frontend" run build

  if [ -f "$release_dir/admin/package-lock.json" ]; then
    run_as_app npm --prefix "$release_dir/admin" ci
  else
    run_as_app npm --prefix "$release_dir/admin" install
  fi
  run_as_app env NODE_OPTIONS=--max-old-space-size=1024 npm --prefix "$release_dir/admin" run build

  chown -R root:root "$release_dir"
  chmod -R a+rX,u+w,go-w "$release_dir"
  chown -h "$SERVICE_USER:$SERVICE_GROUP" "$release_dir/backend/data"
}

switch_current() {
  local release_dir="$1"
  local next_link="$APP_DIR/current.next"
  ln -sfn "$release_dir" "$next_link"
  mv -Tf "$next_link" "$CURRENT_LINK"
}

healthcheck() {
  local url="${SRBLOGS_HEALTH_URL:-http://127.0.0.1:8000/api/health}"
  local i
  for i in $(seq 1 30); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      log "healthcheck ok: $url"
      return 0
    fi
    sleep 2
  done
  log "healthcheck failed: $url"
  return 1
}

rollback() {
  if [ -n "$OLD_CURRENT" ] && [ -d "$OLD_CURRENT" ]; then
    log "rollback current to $OLD_CURRENT"
    switch_current "$OLD_CURRENT"
    systemctl restart "$MAIN_SERVICE" || true
  fi
}

main() {
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    fail_status "preflight" "another update is running" "update_locked" 1
    exit 1
  fi

  STARTED_AT="$(date -Is)"
  : >"$LOG_FILE"
  chown root:"$SERVICE_GROUP" "$LOG_FILE"
  chmod 0640 "$LOG_FILE"

  if [ "$REPO" != "ShrinkShi/SRBlogs" ]; then
    fail_status "preflight" "repository is not allowed: $REPO" "repo_not_allowed" 1
    exit 1
  fi

  require_command curl
  require_command unzip
  require_command python3
  require_command npm

  OLD_CURRENT="$(readlink -f "$CURRENT_LINK" 2>/dev/null || true)"
  progress 5 "preflight" "checking latest GitHub Release"

  WORK_DIR="$(mktemp -d /tmp/srblogs-updater.XXXXXX)"
  local release_json="$WORK_DIR/latest.json"
  fetch_latest_release "$release_json"
  local latest_tag zip_url requested
  latest_tag="$(parse_release_field "$release_json" tag_name)"
  zip_url="$(parse_release_field "$release_json" zipball_url)"
  requested="$(read_request_version)"
  TARGET_VERSION="${requested:-$latest_tag}"

  if [ -z "$latest_tag" ] || [ -z "$zip_url" ]; then
    fail_status "download" "GitHub latest release is missing tag or zipball_url" "github_release_invalid" 1
    exit 1
  fi
  if [ "$TARGET_VERSION" != "$latest_tag" ]; then
    fail_status "preflight" "requested version $TARGET_VERSION does not match latest release $latest_tag" "version_not_latest" 1
    exit 1
  fi
  case "$zip_url" in
    https://api.github.com/repos/ShrinkShi/SRBlogs/zipball/*|https://codeload.github.com/ShrinkShi/SRBlogs/zip/*) ;;
    *)
      fail_status "download" "release zip url is not allowed" "release_url_not_allowed" 1
      exit 1
      ;;
  esac

  local release_dir="$RELEASES_DIR/$TARGET_VERSION"
  if [ -d "$release_dir" ]; then
    fail_status "preflight" "release already exists: $release_dir" "release_exists" 1
    exit 1
  fi

  progress 12 "download" "downloading $TARGET_VERSION"
  curl -fL "$zip_url" -o "$WORK_DIR/release.zip"

  progress 25 "extract" "extracting release"
  unzip -q "$WORK_DIR/release.zip" -d "$WORK_DIR/unzip"
  normalize_source "$WORK_DIR/unzip" "$release_dir" || {
    fail_status "extract" "release archive does not contain SRBlogs project root" "archive_invalid" 1
    exit 1
  }

  progress 42 "build" "installing dependencies and building frontend/admin"
  build_release "$release_dir"

  progress 70 "backup" "backing up current pointer"
  mkdir -p "$APP_DIR/backups"
  if [ -n "$OLD_CURRENT" ]; then
    printf '%s\n' "$OLD_CURRENT" >"$APP_DIR/backups/current.$(date +%Y%m%d%H%M%S).txt"
  fi

  progress 82 "switch" "switching current symlink"
  switch_current "$release_dir"

  progress 88 "systemd" "restarting $MAIN_SERVICE"
  if ! systemctl restart "$MAIN_SERVICE"; then
    rollback
    fail_status "systemd" "failed to restart $MAIN_SERVICE" "service_restart_failed" 1
    exit 1
  fi

  progress 94 "healthcheck" "checking local API"
  if ! healthcheck; then
    rollback
    if healthcheck; then
      fail_status "rollback" "update failed; rollback completed" "rolled_back" 1
    else
      fail_status "rollback" "rollback attempted but healthcheck failed" "rollback_healthcheck_failed" 1
    fi
    exit 1
  fi

  progress 100 "completed" "update completed"
  write_status "success" "completed" 100 "update completed" 0 "" ""
}

trap 'code=$?; if [ $code -ne 0 ]; then log "updater exited with $code"; fi; [ -n "${WORK_DIR:-}" ] && rm -rf "$WORK_DIR"' EXIT
main "$@"
UPDATER

chown root:root "$UPDATER_BIN"
chmod 0750 "$UPDATER_BIN"

cat >"$UPDATER_SERVICE" <<SERVICE
[Unit]
Description=SRBlogs restricted updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
Group=root
Environment=SRBLOGS_APP_DIR=$APP_DIR
Environment=SRBLOGS_SERVICE_USER=$SERVICE_USER
Environment=SRBLOGS_SERVICE_GROUP=$SERVICE_GROUP
Environment=SRBLOGS_MAIN_SERVICE=$MAIN_SERVICE
Environment=SRBLOGS_UPDATE_REPO=$REPO
Environment=SRBLOGS_UPDATE_STATE_DIR=$STATE_DIR
ExecStart=$UPDATER_BIN
SERVICE

chown root:root "$UPDATER_SERVICE"
chmod 0644 "$UPDATER_SERVICE"

SYSTEMCTL_BIN="$(command -v systemctl || true)"
{
  echo "Defaults:$SERVICE_USER !requiretty"
  echo "$SERVICE_USER ALL=(root) NOPASSWD: /bin/systemctl start srblogs-updater.service, /bin/systemctl status srblogs-updater.service"
  echo "$SERVICE_USER ALL=(root) NOPASSWD: /usr/bin/systemctl start srblogs-updater.service, /usr/bin/systemctl status srblogs-updater.service"
  if [ -n "$SYSTEMCTL_BIN" ] && [ "$SYSTEMCTL_BIN" != "/bin/systemctl" ] && [ "$SYSTEMCTL_BIN" != "/usr/bin/systemctl" ]; then
    echo "$SERVICE_USER ALL=(root) NOPASSWD: $SYSTEMCTL_BIN start srblogs-updater.service, $SYSTEMCTL_BIN status srblogs-updater.service"
  fi
} >"$SUDOERS_FILE"
chown root:root "$SUDOERS_FILE"
chmod 0440 "$SUDOERS_FILE"

if command -v visudo >/dev/null 2>&1; then
  visudo -cf "$SUDOERS_FILE"
fi

systemctl daemon-reload

echo "SRBlogs updater installed."
echo "Service: srblogs-updater.service"
echo "Binary: $UPDATER_BIN"
echo "Status: $STATE_DIR/status.json"
echo "Request: $STATE_DIR/request.json"
