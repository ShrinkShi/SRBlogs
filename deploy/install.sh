#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/srblogs"
ENV_DIR="/etc/srblogs"
SERVICE_USER="srblogs"
DOMAIN="_"
ZIP_PATH=""
SOURCE_PATH=""
DRY_RUN=0
COMPILE_PYTHON=0
FORCE_NGINX_MAIN=0
PYTHON_VERSION="3.11.9"
NODE_MAJOR="20"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
LOG_DIR="/var/log/srblogs"
LOG_FILE="$LOG_DIR/install.$TIMESTAMP.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAGING_DIR="/tmp/srblogs-install.$TIMESTAMP"
NORMALIZED_SOURCE="$STAGING_DIR/source"
RAW_ARGS=("$@")

usage() {
  cat <<'USAGE'
Usage: sudo bash deploy/install.sh [options]

Options:
  --dry-run                 Print planned changes without executing them.
  --zip PATH                Deploy from a zip archive.
  --source PATH             Deploy from a local source directory.
  --app-dir PATH            Application directory. Default: /opt/srblogs.
  --domain NAME             Nginx server_name. Default: _.
  --compile-python          Allow source compiling Python 3.11 with make altinstall.
  --force-nginx-main        Allow backing up and rewriting /etc/nginx/nginx.conf.
  --help                    Show this help.
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
  log_line "[error] install.sh failed at line $line: $command"
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
    --compile-python) COMPILE_PYTHON=1; shift ;;
    --force-nginx-main) FORCE_NGINX_MAIN=1; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

ENV_FILE="$ENV_DIR/backend.env"

require_root() {
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  if [ "$(id -u)" -ne 0 ]; then
    echo "Run as root: sudo bash deploy/install.sh"
    exit 1
  fi
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_pkg_manager() {
  if command_exists dnf; then
    echo "dnf"
  elif command_exists yum; then
    echo "yum"
  else
    echo "Unsupported system: this installer currently expects dnf or yum." >&2
    exit 1
  fi
}

validate_inputs() {
  if [ -n "$ZIP_PATH" ] && [ -n "$SOURCE_PATH" ]; then
    echo "Use only one of --zip or --source."
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
    local source="${SOURCE_PATH:-$REPO_ROOT}"
    if validate_project_root "$source"; then
      run_cmd mkdir -p "$NORMALIZED_SOURCE"
      run_cmd rsync -a --exclude node_modules --exclude dist --exclude .venv --exclude __pycache__ "$source/" "$NORMALIZED_SOURCE/"
      return 0
    fi
  fi
  echo "Cannot normalize source. Expected admin/, backend/, frontend/ at archive root or one nested root directory."
  exit 1
}

install_system_packages() {
  local pm="$1"
  run_cmd "$pm" install -y nginx unzip wget make gcc openssl-devel bzip2-devel libffi-devel zlib-devel tar xz rsync curl
}

ensure_python311() {
  if command_exists python3.11; then
    log_line "[ok] python3.11 found: $(python3.11 --version 2>&1)"
    return 0
  fi
  local pm="$1"
  if run_cmd "$pm" install -y python3.11 python3.11-devel python3.11-pip; then
    if command_exists python3.11; then
      return 0
    fi
  fi
  if [ "$COMPILE_PYTHON" -ne 1 ]; then
    echo "python3.11 is not available from $pm. Install Python 3.11 manually or rerun with --compile-python."
    exit 1
  fi
  local build_dir="/tmp/srblogs-python-$PYTHON_VERSION"
  run_cmd mkdir -p "$build_dir"
  run_cmd wget -O "$build_dir/Python-$PYTHON_VERSION.tgz" "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
  run_cmd tar -xzf "$build_dir/Python-$PYTHON_VERSION.tgz" -C "$build_dir"
  run_cmd bash -c "cd '$build_dir/Python-$PYTHON_VERSION' && ./configure --enable-optimizations"
  run_cmd bash -c "cd '$build_dir/Python-$PYTHON_VERSION' && make -j\$(nproc)"
  run_cmd bash -c "cd '$build_dir/Python-$PYTHON_VERSION' && make altinstall"
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
    if [ "$current" -gt 22 ]; then
      log_line "[warn] Node $current detected. Node 20 LTS is recommended for production builds."
    else
      log_line "[ok] Node $(node -v) found."
    fi
    return 0
  fi
  local setup="/tmp/nodesource-node$NODE_MAJOR.sh"
  run_cmd curl -fsSL "https://rpm.nodesource.com/setup_${NODE_MAJOR}.x" -o "$setup"
  run_cmd bash "$setup"
  local pm="$1"
  run_cmd "$pm" install -y nodejs
}

ensure_user() {
  if id -u "$SERVICE_USER" >/dev/null 2>&1; then
    return 0
  fi
  run_cmd useradd -r -s /usr/sbin/nologin "$SERVICE_USER" || run_cmd useradd -r -s /sbin/nologin "$SERVICE_USER"
}

ensure_swap() {
  if swapon --show | grep -q .; then
    log_line "[ok] swap already exists."
    return 0
  fi
  local available_kb
  available_kb="$(df --output=avail / | tail -n 1 | tr -d ' ')"
  if [ "${available_kb:-0}" -le 4194304 ]; then
    log_line "[warn] skip swap creation: available disk space is not greater than 4G."
    return 0
  fi
  if ! run_cmd fallocate -l 2G /swapfile-srblogs; then
    log_line "[warn] failed to allocate /swapfile-srblogs; continue without swap."
    return 0
  fi
  safe_chmod 600 /swapfile-srblogs || true
  run_cmd mkswap /swapfile-srblogs || { log_line "[warn] mkswap failed; continue without swap."; return 0; }
  run_cmd swapon /swapfile-srblogs || { log_line "[warn] swapon failed; continue without swap."; return 0; }
}

sync_project() {
  run_cmd mkdir -p "$APP_DIR"
  run_cmd rsync -a --delete \
    --exclude backend/data \
    --exclude backend/.venv \
    --exclude node_modules \
    --exclude dist \
    "$NORMALIZED_SOURCE/" "$APP_DIR/"
}

prepare_env_and_data() {
  run_cmd mkdir -p "$ENV_DIR" "$APP_DIR/backend/data/uploads" "$APP_DIR/backend/data/audit" "$APP_DIR/backend/data/.manual_backups"
  if [ ! -f "$ENV_FILE" ]; then
    safe_cp "$APP_DIR/backend/.env.production.example" "$ENV_FILE"
  fi
  safe_chown "$SERVICE_USER:$SERVICE_USER" "$ENV_DIR" "$ENV_FILE"
  safe_chmod 700 "$ENV_DIR"
  safe_chmod 600 "$ENV_FILE"
  safe_chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR/backend"
}

install_backend() {
  run_cmd bash -c "cd '$APP_DIR/backend' && python3.11 -m venv .venv"
  run_cmd "$APP_DIR/backend/.venv/bin/python" -m pip install --upgrade pip
  run_cmd "$APP_DIR/backend/.venv/bin/python" -m pip install -r "$APP_DIR/backend/requirements.txt"
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

build_project() {
  npm_install_and_build "$APP_DIR/frontend"
  npm_install_and_build "$APP_DIR/admin"
  run_cmd bash -c "cd '$APP_DIR' && '$APP_DIR/backend/.venv/bin/python' -m compileall backend/app"
}

nginx_config_content() {
  cat <<NGINX
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 5m;

    gzip on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/javascript application/json application/xml image/svg+xml;

    root $APP_DIR/frontend/dist;
    index index.html;

    location = /admin {
        return 301 /admin/;
    }

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

minimal_nginx_main() {
  cat <<'NGINX'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    access_log /var/log/nginx/access.log;
    sendfile on;
    keepalive_timeout 65;
    include /etc/nginx/conf.d/*.conf;
}
NGINX
}

disable_default_nginx_sites() {
  local file
  for file in /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/welcome.conf; do
    if [ -f "$file" ]; then
      safe_mv "$file" "$file.disabled.$TIMESTAMP"
    fi
  done
}

install_nginx_config() {
  run_cmd mkdir -p /etc/nginx/conf.d
  disable_default_nginx_sites
  if [ "$FORCE_NGINX_MAIN" -eq 1 ] && [ -f /etc/nginx/nginx.conf ]; then
    safe_cp /etc/nginx/nginx.conf "/etc/nginx/nginx.conf.backup.$TIMESTAMP"
    write_file /etc/nginx/nginx.conf "$(minimal_nginx_main)"
  fi
  write_file /etc/nginx/conf.d/srblogs.conf "$(nginx_config_content)"
}

systemd_unit_content() {
  cat <<UNIT
[Unit]
Description=SRBlogs FastAPI backend
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
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

install_systemd() {
  write_file /etc/systemd/system/srblogs-backend.service "$(systemd_unit_content)"
  if ! grep -q 'EnvironmentFile=-/etc/srblogs/backend.env' /etc/systemd/system/srblogs-backend.service 2>/dev/null; then
    echo "systemd unit must use EnvironmentFile=-/etc/srblogs/backend.env for the default env file."
    exit 1
  fi
  safe_systemctl daemon-reload
  safe_systemctl enable srblogs-backend
  safe_systemctl enable nginx
}

valid_ipv4() {
  local value="$1"
  [[ "$value" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
}

detect_public_ip() {
  local candidate=""
  if command_exists curl; then
    candidate="$(curl -4 --silent --show-error --max-time 5 https://ifconfig.me 2>/dev/null | tr -d '[:space:]' || true)"
    if valid_ipv4 "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
    candidate="$(curl -4 --silent --show-error --max-time 5 https://ip.sb 2>/dev/null | tr -d '[:space:]' || true)"
    if valid_ipv4 "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi
  if command_exists hostname; then
    candidate="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
    if valid_ipv4 "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi
  return 1
}

print_access_info() {
  local access_host="" print_ip_hint=0
  if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "_" ]; then
    access_host="$DOMAIN"
  else
    access_host="$(detect_public_ip || true)"
  fi
  if [ -z "$access_host" ]; then
    access_host="<your-server-ip>"
    print_ip_hint=1
  fi
  log_line "Install complete."
  log_line "Visit: http://$access_host/install"
  log_line "Admin: http://$access_host/admin/login"
  log_line "Home: http://$access_host/"
  if [ "$print_ip_hint" -eq 1 ]; then
    log_line "Could not detect public IP automatically. Replace <your-server-ip> with your server public IPv4 address."
  fi
  log_line "Service: srblogs-backend"
  log_line "Check service:"
  log_line "  systemctl status srblogs-backend --no-pager"
  log_line "View logs:"
  log_line "  journalctl -u srblogs-backend -n 100 --no-pager"
}

print_plan() {
  log_line "SRBlogs install plan:"
  log_line "- app dir: $APP_DIR"
  log_line "- env file: $ENV_FILE"
  log_line "- domain: $DOMAIN"
  log_line "- source: ${ZIP_PATH:-${SOURCE_PATH:-$REPO_ROOT}}"
  log_line "- compile python: $COMPILE_PYTHON"
  log_line "- force nginx main: $FORCE_NGINX_MAIN"
  log_line "- dry-run: $DRY_RUN"
}

main() {
  validate_inputs
  require_root
  print_plan
  if [ "$DRY_RUN" -eq 1 ]; then
    normalize_source
    log_line "[dry-run] no system changes were made."
    return 0
  fi
  local pm
  pm="$(detect_pkg_manager)"
  install_system_packages "$pm"
  ensure_python311 "$pm"
  ensure_node "$pm"
  ensure_user
  ensure_swap
  normalize_source
  sync_project
  prepare_env_and_data
  install_backend
  build_project
  install_systemd
  install_nginx_config
  safe_nginx_test
  safe_systemctl restart srblogs-backend
  safe_systemctl restart nginx
  print_access_info
}

main "$@"
