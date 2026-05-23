#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/srblogs"
ENV_DIR="/etc/srblogs"
DOMAIN="_"
ZIP_PATH=""
SOURCE_PATH=""
DRY_RUN=0
CLEANUP=0
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
LOG_DIR="/var/log/srblogs"
LOG_FILE="$LOG_DIR/update.$TIMESTAMP.log"
RUNNER_DIR="/tmp/srblogs-runner.$TIMESTAMP"
STAGING_DIR="/tmp/srblogs-update.$TIMESTAMP"
NORMALIZED_SOURCE="$STAGING_DIR/source"
BACKUP_DIR="/opt/srblogs.backup.$TIMESTAMP"
PREVIOUS_DIR="/opt/srblogs.previous.$TIMESTAMP"
FAILED_DIR="/opt/srblogs.failed.$TIMESTAMP"
ENV_FILE="$ENV_DIR/backend.env"
NGINX_CONF="/etc/nginx/conf.d/srblogs.conf"
SYSTEMD_UNIT="/etc/systemd/system/srblogs-backend.service"
SWITCHED=0
RAW_ARGS=("$@")

usage() {
  cat <<'USAGE'
Usage: sudo bash deploy/update.sh --zip PATH [options]
       sudo bash deploy/update.sh --source PATH [options]

Options:
  --dry-run          Print planned changes without executing them.
  --zip PATH         Update from a zip archive.
  --source PATH      Update from a local source directory.
  --app-dir PATH     Application directory. Default: /opt/srblogs.
  --domain NAME      Nginx server_name. Default: _.
  --cleanup          Also remove old /opt/srblogs.previous.* and /opt/srblogs.failed.* entries.
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
    printf '%s\n' "$message" >>"$LOG_FILE"
  fi
}

ensure_log_dir() {
  if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$LOG_DIR"
  fi
}

render_cmd() {
  local rendered="" arg
  for arg in "$@"; do
    rendered+="$(printf '%q' "$arg") "
  done
  printf '%s' "$rendered" | sanitize
}

run_cmd() {
  log_line "[run] $(render_cmd "$@")"
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  "$@"
}

safe_mv() { run_cmd mv "$@"; }
safe_cp() { run_cmd cp "$@"; }
safe_chown() { run_cmd chown "$@"; }
safe_chmod() { run_cmd chmod "$@"; }
safe_systemctl() { run_cmd systemctl "$@"; }
safe_nginx_test() { run_cmd nginx -t; }

write_file() {
  local path="$1"
  local content="$2"
  log_line "[write] $path"
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  printf '%s\n' "$content" >"$path"
}

on_error() {
  local line="$1"
  local command="$2"
  log_line "[error] update.sh failed at line $line: $command"
  log_line "[error] log: $LOG_FILE"
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --zip) ZIP_PATH="${2:-}"; shift 2 ;;
    --source) SOURCE_PATH="${2:-}"; shift 2 ;;
    --app-dir) APP_DIR="${2:-}"; shift 2 ;;
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    --cleanup) CLEANUP=1; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

ENV_FILE="$ENV_DIR/backend.env"
NGINX_CONF="/etc/nginx/conf.d/srblogs.conf"
SYSTEMD_UNIT="/etc/systemd/system/srblogs-backend.service"

start_runner_if_needed() {
  if [ "$DRY_RUN" -eq 1 ] || [ "${SRBLOGS_RUNNER:-0}" = "1" ]; then
    return 0
  fi
  run_cmd mkdir -p "$RUNNER_DIR"
  safe_cp "$0" "$RUNNER_DIR/update.sh"
  exec env SRBLOGS_RUNNER=1 bash "$RUNNER_DIR/update.sh" "$@"
}

require_root() {
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  if [ "$(id -u)" -ne 0 ]; then
    echo "Run as root: sudo bash deploy/update.sh"
    exit 1
  fi
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

validate_inputs() {
  if [ -n "$ZIP_PATH" ] && [ -n "$SOURCE_PATH" ]; then
    echo "Use only one of --zip or --source."
    exit 2
  fi
  if [ -z "$ZIP_PATH" ] && [ -z "$SOURCE_PATH" ]; then
    echo "Use --zip PATH or --source PATH for updates."
    exit 2
  fi
  if [ -n "$ZIP_PATH" ] && [ ! -f "$ZIP_PATH" ]; then
    echo "Zip file does not exist: $ZIP_PATH"
    exit 2
  fi
  if [ -n "$SOURCE_PATH" ] && [ ! -d "$SOURCE_PATH" ]; then
    echo "Source directory does not exist: $SOURCE_PATH"
    exit 2
  fi
  if [ "$DRY_RUN" -eq 0 ] && [ ! -d "$APP_DIR" ]; then
    echo "Application directory does not exist: $APP_DIR"
    exit 1
  fi
}

validate_project_root() {
  local root="$1"
  if [ -f "$root/admin/package.json" ] &&
     [ -f "$root/frontend/package.json" ] &&
     [ -d "$root/backend/app" ] &&
     [ -f "$root/backend/requirements.txt" ]; then
    return 0
  fi
  return 1
}

normalize_source() {
  if [ "$DRY_RUN" -eq 1 ]; then
    log_line "[dry-run] would normalize source into $NORMALIZED_SOURCE"
    return 0
  fi
  run_cmd mkdir -p "$STAGING_DIR"
  if [ -n "$ZIP_PATH" ]; then
    run_cmd mkdir -p "$STAGING_DIR/unzip"
    run_cmd unzip -q "$ZIP_PATH" -d "$STAGING_DIR/unzip"
    if validate_project_root "$STAGING_DIR/unzip"; then
      safe_mv "$STAGING_DIR/unzip" "$NORMALIZED_SOURCE"
      return 0
    fi
    local child=""
    child="$(find "$STAGING_DIR/unzip" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
    if [ -n "$child" ] && validate_project_root "$child"; then
      safe_mv "$child" "$NORMALIZED_SOURCE"
      return 0
    fi
  else
    if validate_project_root "$SOURCE_PATH"; then
      run_cmd mkdir -p "$NORMALIZED_SOURCE"
      run_cmd rsync -a --exclude node_modules --exclude dist --exclude .venv --exclude __pycache__ "$SOURCE_PATH/" "$NORMALIZED_SOURCE/"
      return 0
    fi
  fi
  echo "Cannot normalize source. Expected admin/, backend/, frontend/ at archive root or one nested root directory."
  exit 1
}

ensure_python311() {
  if command_exists python3.11; then
    return 0
  fi
  echo "python3.11 is required before update. Install it first, then rerun update.sh."
  return 1
}

node_major() {
  node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/'
}

ensure_node() {
  local current=""
  if command_exists node; then
    current="$(node_major)"
  fi
  if [ -n "$current" ] && [ "$current" -ge 20 ]; then
    return 0
  fi
  echo "Node.js >= 20 is required before update."
  return 1
}

backup_current() {
  run_cmd mkdir -p "$BACKUP_DIR"
  safe_cp -a "$APP_DIR" "$BACKUP_DIR/app"
  if [ -f "$ENV_FILE" ]; then safe_cp -a "$ENV_FILE" "$BACKUP_DIR/backend.env"; fi
  if [ -f "$NGINX_CONF" ]; then safe_cp -a "$NGINX_CONF" "$BACKUP_DIR/srblogs.conf"; fi
  if [ -f "$SYSTEMD_UNIT" ]; then safe_cp -a "$SYSTEMD_UNIT" "$BACKUP_DIR/srblogs-backend.service"; fi
}

cleanup_backups() {
  if [ "$DRY_RUN" -eq 1 ]; then
    log_line "[dry-run] would keep latest 3 /opt/srblogs.backup.* directories"
    return 0
  fi
  find /opt -maxdepth 1 -type d -name 'srblogs.backup.*' | sort -r | tail -n +4 | while read -r old; do
    run_cmd rm -rf "$old"
  done
  if [ "$CLEANUP" -eq 1 ]; then
    find /opt -maxdepth 1 -type d \( -name 'srblogs.previous.*' -o -name 'srblogs.failed.*' \) | while read -r old; do
      run_cmd rm -rf "$old"
    done
  fi
}

migrate_data() {
  if [ -d "$APP_DIR/backend/data" ]; then
    run_cmd mkdir -p "$NORMALIZED_SOURCE/backend"
    safe_cp -a "$APP_DIR/backend/data" "$NORMALIZED_SOURCE/backend/data"
  fi
}

npm_install_and_build() {
  local dir="$1"
  if [ -f "$dir/package-lock.json" ]; then
    run_cmd bash -c "cd '$dir' && npm ci"
  else
    run_cmd bash -c "cd '$dir' && npm install"
  fi
  run_cmd bash -c "cd '$dir' && NODE_OPTIONS=--max-old-space-size=1024 npm run build"
}

build_staging() {
  run_cmd bash -c "cd '$NORMALIZED_SOURCE/backend' && python3.11 -m venv .venv"
  run_cmd "$NORMALIZED_SOURCE/backend/.venv/bin/python" -m pip install --upgrade pip
  run_cmd "$NORMALIZED_SOURCE/backend/.venv/bin/python" -m pip install -r "$NORMALIZED_SOURCE/backend/requirements.txt"
  npm_install_and_build "$NORMALIZED_SOURCE/frontend"
  npm_install_and_build "$NORMALIZED_SOURCE/admin"
  run_cmd bash -c "cd '$NORMALIZED_SOURCE' && '$NORMALIZED_SOURCE/backend/.venv/bin/python' -m compileall backend/app"
}

nginx_config_content() {
  cat <<NGINX
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 5m;
    root $APP_DIR/frontend/dist;
    index index.html;

    location = /admin { return 301 /admin/; }
    location ^~ /admin/ {
        alias $APP_DIR/admin/dist/;
        try_files \$uri \$uri/ /admin/index.html;
    }
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    location = /robots.txt {
        proxy_pass http://127.0.0.1:8000/robots.txt;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
        add_header Cache-Control "public, max-age=604800";
    }
    location ~* \.(?:js|css|png|jpg|jpeg|gif|webp|svg|ico|woff2?)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800, immutable";
        try_files \$uri =404;
    }
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NGINX
}

systemd_unit_content() {
  cat <<UNIT
[Unit]
Description=SRBlogs FastAPI backend
After=network.target

[Service]
Type=simple
User=srblogs
Group=srblogs
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=-$ENV_FILE
Environment=APP_DIR=$APP_DIR
Environment=BACKEND_DIR=$APP_DIR/backend
ExecStart=/usr/bin/env bash $APP_DIR/deploy/start-backend.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
}

install_configs() {
  write_file "$SYSTEMD_UNIT" "$(systemd_unit_content)"
  write_file "$NGINX_CONF" "$(nginx_config_content)"
  safe_systemctl daemon-reload
}

api_health() {
  curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/health >/dev/null
}

api_install_status() {
  curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/install/status >/tmp/srblogs-install-status.$$ 2>/dev/null
}

api_public_settings_if_installed() {
  local status_file="/tmp/srblogs-install-status.$$"
  if [ -f "$status_file" ] && grep -q '"installed"[[:space:]]*:[[:space:]]*true' "$status_file"; then
    curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8000/api/settings/public >/dev/null
  fi
}

run_healthchecks() {
  api_health && api_install_status && api_public_settings_if_installed
}

rollback() {
  local reason="$1"
  set +e
  log_line "[rollback] reason: $reason"
  if [ "$SWITCHED" -eq 1 ]; then
    if [ -d "$APP_DIR" ]; then safe_mv "$APP_DIR" "$FAILED_DIR"; fi
    if [ -d "$PREVIOUS_DIR" ]; then safe_mv "$PREVIOUS_DIR" "$APP_DIR"; fi
    if [ -f "$BACKUP_DIR/backend.env" ]; then safe_cp -a "$BACKUP_DIR/backend.env" "$ENV_FILE"; fi
    if [ -f "$BACKUP_DIR/srblogs.conf" ]; then safe_cp -a "$BACKUP_DIR/srblogs.conf" "$NGINX_CONF"; fi
    if [ -f "$BACKUP_DIR/srblogs-backend.service" ]; then safe_cp -a "$BACKUP_DIR/srblogs-backend.service" "$SYSTEMD_UNIT"; fi
    safe_systemctl daemon-reload
    safe_systemctl restart srblogs-backend
    safe_systemctl reload nginx
  fi
  if api_health; then
    log_line "[rollback] old version healthcheck passed."
  else
    log_line "rollback attempted but healthcheck failed"
  fi
  set -e
}

fail_update() {
  local reason="$1"
  rollback "$reason"
  exit 1
}

switch_release() {
  if ! safe_mv "$APP_DIR" "$PREVIOUS_DIR"; then
    fail_update "failed to move current release to previous"
  fi
  SWITCHED=1
  if ! safe_mv "$NORMALIZED_SOURCE" "$APP_DIR"; then
    fail_update "failed to move staging release to current"
  fi
}

print_plan() {
  log_line "SRBlogs update plan:"
  log_line "- app dir: $APP_DIR"
  log_line "- env file: $ENV_FILE"
  log_line "- source: ${ZIP_PATH:-$SOURCE_PATH}"
  log_line "- backup dir: $BACKUP_DIR"
  log_line "- dry-run: $DRY_RUN"
  log_line "- cleanup previous/failed: $CLEANUP"
}

main() {
  validate_inputs
  require_root
  start_runner_if_needed "${RAW_ARGS[@]}"
  print_plan
  if [ "$DRY_RUN" -eq 1 ]; then
    normalize_source
    log_line "[dry-run] would backup app/env/nginx/systemd, build staging, switch release, run healthchecks."
    return 0
  fi
  ensure_python311 || fail_update "python3.11 check failed"
  ensure_node || fail_update "node check failed"
  backup_current || fail_update "backup failed"
  cleanup_backups
  normalize_source || fail_update "source normalization failed"
  migrate_data || fail_update "data migration failed"
  build_staging || fail_update "dependency install or build failed"
  switch_release
  install_configs || fail_update "config installation failed"
  safe_nginx_test || fail_update "nginx -t failed"
  safe_systemctl restart srblogs-backend || fail_update "systemd restart failed"
  safe_systemctl reload nginx || fail_update "nginx reload failed"
  run_healthchecks || fail_update "API healthcheck failed"
  log_line "Update complete."
  log_line "Backup: $BACKUP_DIR"
}

main "$@"
