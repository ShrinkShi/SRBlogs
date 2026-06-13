#!/usr/bin/env bash
set -Eeuo pipefail

REPO="ShrinkShi/SRBlogs"
SERVICE_USER="srblogs"
SERVICE_GROUP="srblogs"
BACKEND_SERVICE="srblogs-backend.service"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
LOG_DIR="/var/log/srblogs"
LOG_FILE="$LOG_DIR/install.$TIMESTAMP.log"
TMP_ROOT="/tmp/srblogs-online.$TIMESTAMP"

APP_DIR="/opt/srblogs"
ENV_DIR="/etc/srblogs"
PUBLIC_PORT="80"
BACKEND_PORT="8000"
SITE_DOMAIN=""
ADMIN_USERNAME="admin"
ADMIN_PASSWORD=""
INSTALL_UPDATER="yes"
CONFIGURE_UFW="ask"
ENV_WRITE_MODE="write"

redact() {
  sed -E \
    -e 's/((ADMIN_PASSWORD|JWT_SECRET|TOKEN|API_KEY|[A-Z0-9_]*SECRET)=)[^[:space:]]+/\1***REDACTED***/g' \
    -e 's/(password[[:space:]]*[:=][[:space:]]*)[^[:space:]]+/\1***REDACTED***/Ig' \
    -e 's/(secret[[:space:]]*[:=][[:space:]]*)[^[:space:]]+/\1***REDACTED***/Ig'
}

log_line() {
  local message="$*"
  printf '%s\n' "$message" | redact | tee -a "$LOG_FILE"
}

on_error() {
  local exit_code="$?" line_no="${BASH_LINENO[0]:-unknown}" command_text="${BASH_COMMAND:-unknown}"
  if [ -n "${LOG_FILE:-}" ] && [ -f "$LOG_FILE" ]; then
    log_line "[失败] 安装在第 $line_no 行中断：$command_text (exit $exit_code)"
    log_line "安装日志：$LOG_FILE"
  else
    printf '安装失败：第 %s 行，exit %s\n' "$line_no" "$exit_code" >&2
  fi
  exit "$exit_code"
}

trap on_error ERR

run_cmd() {
  log_line "+ $*"
  "$@" > >(redact >>"$LOG_FILE") 2> >(redact >>"$LOG_FILE" >&2)
}

fail() {
  log_line "[失败] $*"
  log_line "安装日志：$LOG_FILE"
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "请使用 root 权限运行：sudo bash /tmp/srblogs-install.sh"
    exit 1
  fi
}

init_runtime_dirs() {
  mkdir -p "$LOG_DIR" "$TMP_ROOT"
  chmod 0750 "$LOG_DIR"
  touch "$LOG_FILE"
  chmod 0640 "$LOG_FILE"
}

has_whiptail() {
  command_exists whiptail
}

tui_msg() {
  local title="$1" message="$2"
  if has_whiptail; then
    whiptail --title "$title" --msgbox "$message" 12 72
  else
    printf '\n[%s]\n%s\n\n' "$title" "$message"
  fi
}

tui_input() {
  local title="$1" prompt="$2" default_value="$3" result
  if has_whiptail; then
    result="$(whiptail --title "$title" --inputbox "$prompt" 10 72 "$default_value" 3>&1 1>&2 2>&3)" || return 1
    printf '%s' "$result"
  else
    printf '%s [%s]: ' "$prompt" "$default_value" >&2
    read -r result
    printf '%s' "${result:-$default_value}"
  fi
}

tui_password() {
  local title="$1" prompt="$2" result
  if has_whiptail; then
    result="$(whiptail --title "$title" --passwordbox "$prompt" 10 72 3>&1 1>&2 2>&3)" || return 1
    printf '%s' "$result"
  else
    printf '%s: ' "$prompt" >&2
    read -rs result
    printf '\n' >&2
    printf '%s' "$result"
  fi
}

tui_yesno() {
  local title="$1" prompt="$2" default_answer="$3"
  if has_whiptail; then
    if [ "$default_answer" = "yes" ]; then
      whiptail --title "$title" --yesno "$prompt" 12 72
    else
      whiptail --title "$title" --yesno "$prompt" 12 72 --defaultno
    fi
  else
    local suffix answer
    suffix="[y/N]"
    [ "$default_answer" = "yes" ] && suffix="[Y/n]"
    printf '%s %s ' "$prompt" "$suffix" >&2
    read -r answer
    answer="${answer:-$default_answer}"
    [ "$answer" = "yes" ] || [ "$answer" = "y" ] || [ "$answer" = "Y" ]
  fi
}

tui_menu() {
  local title="$1" prompt="$2"
  shift 2
  if has_whiptail; then
    whiptail --title "$title" --menu "$prompt" 16 76 6 "$@" 3>&1 1>&2 2>&3
  else
    local count=1 choice tags=()
    printf '\n[%s]\n%s\n' "$title" "$prompt" >&2
    while [ "$#" -gt 0 ]; do
      tags+=("$1")
      printf '  %s) %s - %s\n' "$count" "$1" "$2" >&2
      shift 2
      count=$((count + 1))
    done
    printf '请选择序号: ' >&2
    read -r choice
    choice="${choice:-1}"
    printf '%s' "${tags[$((choice - 1))]}"
  fi
}

validate_port() {
  local value="$1" name="$2"
  if ! printf '%s' "$value" | grep -Eq '^[0-9]+$'; then
    fail "$name 必须是数字端口。"
  fi
  if [ "$value" -lt 1 ] || [ "$value" -gt 65535 ]; then
    fail "$name 必须在 1-65535 之间。"
  fi
}

collect_config() {
  tui_msg "SRBlogs 在线安装" "欢迎使用 SRBlogs 在线安装器。\n\n本脚本会从 GitHub Releases 下载最新版本，不会静默拉取 main 分支。\n后端服务将以普通用户 srblogs 运行，不会以 root 运行 Web 后端。"

  APP_DIR="$(tui_input "安装目录" "请输入安装目录" "$APP_DIR")"
  ENV_DIR="$(tui_input "配置目录" "请输入生产配置目录" "$ENV_DIR")"
  PUBLIC_PORT="$(tui_input "访问端口" "请输入 Nginx 对外访问端口，不使用随机端口" "$PUBLIC_PORT")"
  BACKEND_PORT="$(tui_input "后端端口" "请输入 FastAPI 内部端口，默认绑定 127.0.0.1" "$BACKEND_PORT")"
  SITE_DOMAIN="$(tui_input "站点域名" "请输入站点域名，可留空" "$SITE_DOMAIN")"
  ADMIN_USERNAME="$(tui_input "管理员账号" "请输入管理员用户名" "$ADMIN_USERNAME")"

  validate_port "$PUBLIC_PORT" "对外访问端口"
  validate_port "$BACKEND_PORT" "后端内部端口"
  if [ "$PUBLIC_PORT" = "$BACKEND_PORT" ]; then
    fail "对外访问端口不能与后端内部端口相同，否则 Nginx 与后端会抢占端口。"
  fi
  if [ -z "$ADMIN_USERNAME" ]; then
    fail "管理员用户名不能为空。"
  fi

  local pass1 pass2
  while true; do
    pass1="$(tui_password "管理员密码" "请输入管理员密码（不能为空）")"
    pass2="$(tui_password "确认密码" "请再次输入管理员密码")"
    if [ -z "$pass1" ]; then
      tui_msg "密码无效" "管理员密码不能为空。"
      continue
    fi
    if [ "$pass1" != "$pass2" ]; then
      tui_msg "密码不一致" "两次输入的管理员密码不一致，请重新输入。"
      continue
    fi
    ADMIN_PASSWORD="$pass1"
    break
  done

  if tui_yesno "一键更新器" "是否安装受限一键更新器？\n\n推荐安装。Web 后端只会触发固定 systemd service，不会以 root 执行任意命令。" "yes"; then
    INSTALL_UPDATER="yes"
  else
    INSTALL_UPDATER="no"
  fi

  if tui_yesno "UFW 防火墙" "是否尝试配置 UFW 放行 TCP $PUBLIC_PORT 端口？\n\n云服务器仍需要在安全组中放行该端口。" "no"; then
    CONFIGURE_UFW="yes"
  else
    CONFIGURE_UFW="no"
  fi
}

detect_package_manager() {
  if command_exists apt-get; then
    printf 'apt'
  elif command_exists dnf; then
    printf 'dnf'
  elif command_exists yum; then
    printf 'yum'
  else
    fail "未检测到 apt、dnf 或 yum，当前系统暂不支持自动安装。"
  fi
}

install_system_dependencies() {
  local pm="$1"
  log_line "[步骤] 安装系统依赖（包管理器：$pm）"
  if [ "$pm" = "apt" ]; then
    export DEBIAN_FRONTEND=noninteractive
    run_cmd apt-get update
    run_cmd apt-get install -y nginx curl wget unzip rsync python3 python3-venv python3-pip ca-certificates gnupg lsb-release openssl
    if [ "$CONFIGURE_UFW" = "yes" ]; then
      run_cmd apt-get install -y ufw
    fi
  else
    run_cmd "$pm" install -y nginx curl wget unzip rsync python3 python3-pip ca-certificates openssl tar gzip
  fi
}

node_major() {
  if ! command_exists node; then
    printf '0'
    return
  fi
  node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || printf '0'
}

install_node20_if_needed() {
  local pm="$1" major
  major="$(node_major)"
  if [ "$major" -ge 20 ] 2>/dev/null; then
    log_line "[ok] Node.js 已满足要求：$(node -v)"
    return
  fi

  log_line "[步骤] 安装 Node.js 20 LTS"
  if [ "$pm" = "apt" ]; then
    run_cmd curl -fsSL -o "$TMP_ROOT/nodesource_setup.sh" https://deb.nodesource.com/setup_20.x
    run_cmd bash "$TMP_ROOT/nodesource_setup.sh"
    run_cmd apt-get install -y nodejs
  else
    run_cmd curl -fsSL -o "$TMP_ROOT/nodesource_setup.sh" https://rpm.nodesource.com/setup_20.x
    run_cmd bash "$TMP_ROOT/nodesource_setup.sh"
    run_cmd "$pm" install -y nodejs
  fi

  major="$(node_major)"
  if [ "$major" -lt 20 ] 2>/dev/null; then
    fail "Node.js 安装后仍低于 20，请手动检查 NodeSource 安装。"
  fi
}

detect_public_ipv4() {
  local ip
  for url in https://api.ipify.org https://ifconfig.me https://ip.sb; do
    ip="$(curl -4 -fsS --max-time 5 "$url" 2>/dev/null || true)"
    if printf '%s' "$ip" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
      printf '%s' "$ip"
      return
    fi
  done
  printf ''
}

detect_private_ipv4() {
  hostname -I 2>/dev/null | awk '{print $1}' || true
}

url_for() {
  local host="$1" port="$2"
  if [ -z "$host" ]; then
    return
  fi
  if [ "$port" = "80" ]; then
    printf 'http://%s' "$host"
  else
    printf 'http://%s:%s' "$host" "$port"
  fi
}

append_unique_csv() {
  local current="$1" value="$2"
  if [ -z "$value" ]; then
    printf '%s' "$current"
  elif printf ',%s,' "$current" | grep -Fq ",$value,"; then
    printf '%s' "$current"
  elif [ -z "$current" ]; then
    printf '%s' "$value"
  else
    printf '%s,%s' "$current" "$value"
  fi
}

fetch_latest_release() {
  local api_url release_file code tag zip_url
  api_url="https://api.github.com/repos/$REPO/releases/latest"
  release_file="$TMP_ROOT/latest-release.json"
  log_line "[步骤] 查询 GitHub latest release：$api_url"
  code="$(curl -sS -L -H 'Accept: application/vnd.github+json' -w '%{http_code}' -o "$release_file" "$api_url" || true)"
  if [ "$code" = "404" ]; then
    fail "未找到 GitHub Release。请先在 GitHub 仓库 $REPO 创建 release，安装器不会静默拉取 main。"
  fi
  if [ "$code" != "200" ]; then
    fail "GitHub Release 查询失败，HTTP 状态码：${code:-unknown}。"
  fi

  tag="$(python3 - "$release_file" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("tag_name") or "")
PY
)"
  zip_url="$(python3 - "$release_file" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("zipball_url") or "")
PY
)"
  if [ -z "$tag" ] || [ -z "$zip_url" ]; then
    fail "GitHub Release 响应缺少 tag_name 或 zipball_url。"
  fi
  printf '%s\n%s\n' "$tag" "$zip_url" >"$TMP_ROOT/release-info.txt"
  log_line "[ok] 最新版本：$tag"
}

download_and_extract_release() {
  local tag zip_url zip_file extract_dir root child
  tag="$(sed -n '1p' "$TMP_ROOT/release-info.txt")"
  zip_url="$(sed -n '2p' "$TMP_ROOT/release-info.txt")"
  zip_file="$TMP_ROOT/SRBlogs-$tag.zip"
  extract_dir="$TMP_ROOT/extract"
  log_line "[步骤] 下载 Release 包：$tag"
  run_cmd curl -fL -o "$zip_file" "$zip_url"
  mkdir -p "$extract_dir"
  run_cmd unzip -q "$zip_file" -d "$extract_dir"

  if [ -f "$extract_dir/frontend/package.json" ] &&
     [ -f "$extract_dir/admin/package.json" ] &&
     [ -d "$extract_dir/backend/app" ] &&
     [ -f "$extract_dir/backend/requirements.txt" ]; then
    root="$extract_dir"
  else
    child="$(find "$extract_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
    if [ -n "$child" ] &&
       [ -f "$child/frontend/package.json" ] &&
       [ -f "$child/admin/package.json" ] &&
       [ -d "$child/backend/app" ] &&
       [ -f "$child/backend/requirements.txt" ]; then
      root="$child"
    else
      fail "Release 包结构校验失败，必须包含 frontend/package.json、admin/package.json、backend/app、backend/requirements.txt。"
    fi
  fi
  printf '%s' "$root" >"$TMP_ROOT/source-root.txt"
}

ask_existing_policy() {
  local target="$1" kind="$2" choice
  if [ ! -e "$target" ]; then
    printf 'write'
    return
  fi
  choice="$(tui_menu "$kind 已存在" "$target 已存在，请选择处理方式：" \
    keep "保留现有配置/目录，跳过写入" \
    backup "备份后重建" \
    exit "退出安装")"
  case "$choice" in
    keep) printf 'keep' ;;
    backup) printf 'backup' ;;
    exit) exit 0 ;;
    *) fail "未知选择：$choice" ;;
  esac
}

ask_existing_app_policy() {
  local choice
  choice="$(tui_menu "安装目录已存在" "$APP_DIR 已存在，请选择处理方式：" \
    "overwrite" "覆盖安装（会先自动备份现有目录）" \
    "backup" "备份后覆盖安装" \
    "exit" "退出安装")"
  case "$choice" in
    overwrite|backup) printf 'backup' ;;
    exit) exit 0 ;;
    *) fail "未知选择：$choice" ;;
  esac
}

prepare_app_directory() {
  local source_root backup policy
  source_root="$(cat "$TMP_ROOT/source-root.txt")"
  if [ -e "$APP_DIR" ]; then
    policy="$(ask_existing_app_policy)"
    backup="$APP_DIR.backup.$TIMESTAMP"
    log_line "[步骤] 备份现有应用目录到 $backup"
    run_cmd mv "$APP_DIR" "$backup"
  fi
  run_cmd mkdir -p "$(dirname "$APP_DIR")"
  log_line "[步骤] 同步 Release 到 $APP_DIR"
  run_cmd rsync -a "$source_root/" "$APP_DIR/"
}

ensure_service_user() {
  if ! getent group "$SERVICE_GROUP" >/dev/null 2>&1; then
    log_line "[步骤] 创建系统用户组：$SERVICE_GROUP"
    run_cmd groupadd --system "$SERVICE_GROUP"
  fi
  if id "$SERVICE_USER" >/dev/null 2>&1; then
    log_line "[ok] 系统用户已存在：$SERVICE_USER"
    return
  fi
  log_line "[步骤] 创建系统用户：$SERVICE_USER"
  if command_exists useradd; then
    local shell_path
    shell_path="/usr/sbin/nologin"
    [ -x "$shell_path" ] || shell_path="/sbin/nologin"
    run_cmd useradd --system --gid "$SERVICE_GROUP" --home-dir "$APP_DIR" --shell "$shell_path" "$SERVICE_USER"
  else
    fail "系统缺少 useradd，无法创建服务用户。"
  fi
}

run_as_service() {
  if command_exists runuser; then
    run_cmd runuser -u "$SERVICE_USER" -- "$@"
  else
    local rendered=""
    local item
    for item in "$@"; do
      rendered="$rendered $(printf '%q' "$item")"
    done
    run_cmd su -s /bin/sh "$SERVICE_USER" -c "$rendered"
  fi
}

prepare_build_permissions() {
  run_cmd chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
}

harden_app_permissions() {
  run_cmd chown -R root:root "$APP_DIR"
  run_cmd chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR/backend/data"
  run_cmd chmod -R u+rwX,g+rwX "$APP_DIR/backend/data"
}

generate_jwt_secret() {
  openssl rand -hex 32
}

write_backend_env() {
  local env_file example tmp public_ip private_ip host public_base cors jwt site_start
  env_file="$ENV_DIR/backend.env"
  if [ -f "$env_file" ]; then
    ENV_WRITE_MODE="$(ask_existing_policy "$env_file" "生产配置文件")"
    if [ "$ENV_WRITE_MODE" = "keep" ]; then
      log_line "[ok] 保留现有 $env_file"
      return
    fi
    run_cmd cp -a "$env_file" "$env_file.backup.$TIMESTAMP"
  fi

  run_cmd mkdir -p "$ENV_DIR"
  example="$APP_DIR/backend/.env.production.example"
  tmp="$TMP_ROOT/backend.env"
  if [ -f "$example" ]; then
    cp "$example" "$tmp"
  else
    : >"$tmp"
  fi
  sed -i -E '/^(APP_ENV|DATA_DIR|PUBLIC_BASE_URL|SITE_START_TIME|ADMIN_USERNAME|ADMIN_PASSWORD|ADMIN_PASSWORD_HASH|JWT_SECRET|CORS_ORIGINS|HOST|PORT)=/d' "$tmp"

  public_ip="$(detect_public_ipv4)"
  private_ip="$(detect_private_ipv4)"
  host="${SITE_DOMAIN:-$public_ip}"
  [ -z "$host" ] && host="$private_ip"
  [ -z "$host" ] && host="127.0.0.1"
  public_base="$(url_for "$host" "$PUBLIC_PORT")"
  jwt="$(generate_jwt_secret)"
  site_start="$(date -Is)"

  cors=""
  cors="$(append_unique_csv "$cors" "$public_base")"
  cors="$(append_unique_csv "$cors" "$(url_for "$SITE_DOMAIN" "$PUBLIC_PORT")")"
  cors="$(append_unique_csv "$cors" "$(url_for "$public_ip" "$PUBLIC_PORT")")"
  cors="$(append_unique_csv "$cors" "$(url_for "$private_ip" "$PUBLIC_PORT")")"
  cors="$(append_unique_csv "$cors" "$(url_for "127.0.0.1" "$PUBLIC_PORT")")"

  cat >>"$tmp" <<EOF
APP_ENV=production
DATA_DIR=$APP_DIR/backend/data
PUBLIC_BASE_URL=$public_base
SITE_START_TIME=$site_start
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
JWT_SECRET=$jwt
CORS_ORIGINS=$cors
HOST=127.0.0.1
PORT=$BACKEND_PORT
EOF
  run_cmd install -m 0640 -o root -g "$SERVICE_GROUP" "$tmp" "$env_file"
  log_line "[ok] 已写入 $env_file"
}

prepare_data_directory() {
  local data_dir lock_file settings_file tag
  data_dir="$APP_DIR/backend/data"
  tag="$(sed -n '1p' "$TMP_ROOT/release-info.txt" 2>/dev/null || printf 'latest')"
  run_cmd mkdir -p "$data_dir/uploads" "$data_dir/audit" "$data_dir/update_logs" "$data_dir/update_downloads" "$data_dir/.backups" "$data_dir/.manual_backups"

  settings_file="$data_dir/settings.json"
  if [ ! -f "$settings_file" ]; then
    cat >"$settings_file" <<EOF
{
  "siteTitle": "SRBlogs",
  "title": "SRBlogs",
  "subtitle": "",
  "author": "$ADMIN_USERNAME",
  "siteStartTime": "$(date -Is)"
}
EOF
  fi

  lock_file="$data_dir/.install.lock"
  if [ ! -f "$lock_file" ]; then
    cat >"$lock_file" <<EOF
{
  "installedAt": "$(date -Is)",
  "version": "$tag",
  "siteStartTime": "$(date -Is)"
}
EOF
  fi
  run_cmd chown -R "$SERVICE_USER:$SERVICE_GROUP" "$data_dir"
  run_cmd chmod -R u+rwX,g+rwX "$data_dir"
}

install_backend() {
  log_line "[步骤] 创建后端虚拟环境并安装依赖"
  run_as_service python3 -m venv "$APP_DIR/backend/.venv"
  run_as_service "$APP_DIR/backend/.venv/bin/python" -m pip install --upgrade pip
  run_as_service "$APP_DIR/backend/.venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt"
}

npm_install_and_build() {
  local dir="$1"
  if [ -f "$dir/package-lock.json" ]; then
    run_as_service bash -c "cd '$dir' && npm ci"
  else
    run_as_service bash -c "cd '$dir' && npm install"
  fi
  run_as_service bash -c "cd '$dir' && NODE_OPTIONS=--max-old-space-size=1024 npm run build"
}

build_frontends() {
  log_line "[步骤] 构建前台"
  npm_install_and_build "$APP_DIR/frontend"
  log_line "[步骤] 构建后台"
  npm_install_and_build "$APP_DIR/admin"
}

disable_default_nginx_sites() {
  local file
  for file in /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/welcome.conf /etc/nginx/sites-enabled/default; do
    if [ -f "$file" ] || [ -L "$file" ]; then
      run_cmd mv "$file" "$file.disabled.$TIMESTAMP"
    fi
  done
}

write_nginx_config() {
  local server_name conf
  server_name="${SITE_DOMAIN:-_}"
  conf="/etc/nginx/conf.d/srblogs.conf"
  if [ -f "$conf" ]; then
    run_cmd cp -a "$conf" "$conf.backup.$TIMESTAMP"
  fi
  run_cmd mkdir -p /etc/nginx/conf.d
  disable_default_nginx_sites
  cat >"$conf" <<EOF
server {
    listen $PUBLIC_PORT;
    server_name $server_name;
    root $APP_DIR/frontend/dist;
    index index.html;
    client_max_body_size 20m;

    location = /admin {
        return 301 /admin/;
    }

    location ^~ /admin/ {
        alias $APP_DIR/admin/dist/;
        try_files \$uri \$uri/ /admin/index.html;
    }

    location ^~ /api/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/uploads/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|webp|svg|ico|woff2?)$ {
        add_header Cache-Control "public, max-age=604800, immutable";
        try_files \$uri =404;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF
  run_cmd nginx -t
}

write_systemd_service() {
  local service_file
  service_file="/etc/systemd/system/$BACKEND_SERVICE"
  if [ -f "$service_file" ]; then
    run_cmd cp -a "$service_file" "$service_file.backup.$TIMESTAMP"
  fi
  cat >"$service_file" <<EOF
[Unit]
Description=SRBlogs FastAPI backend
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=-$ENV_DIR/backend.env
ExecStart=$APP_DIR/backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT
Restart=always
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
EOF
  run_cmd systemctl daemon-reload
  run_cmd systemctl enable "$BACKEND_SERVICE"
}

configure_ufw_if_requested() {
  if [ "$CONFIGURE_UFW" != "yes" ]; then
    return
  fi
  if ! command_exists ufw; then
    log_line "[警告] 未找到 ufw，跳过防火墙配置。"
    return
  fi
  run_cmd ufw allow "$PUBLIC_PORT/tcp"
  log_line "[ok] 已添加 UFW 放行规则：$PUBLIC_PORT/tcp。若 UFW 未启用，本脚本不会自动启用。"
}

install_restricted_updater() {
  if [ "$INSTALL_UPDATER" != "yes" ]; then
    return
  fi
  if [ ! -f "$APP_DIR/deploy/install-updater.sh" ]; then
    log_line "[警告] Release 中没有 deploy/install-updater.sh，跳过受限 updater 安装。"
    return
  fi
  log_line "[步骤] 安装受限一键更新器"
  run_cmd bash "$APP_DIR/deploy/install-updater.sh" --app-dir "$APP_DIR" --user "$SERVICE_USER" --group "$SERVICE_GROUP" --service "$BACKEND_SERVICE"
}

start_services() {
  log_line "[步骤] 启动服务"
  run_cmd systemctl restart "$BACKEND_SERVICE"
  run_cmd systemctl enable nginx
  run_cmd systemctl restart nginx
}

healthcheck_url() {
  local url="$1" label="$2" i
  for i in $(seq 1 30); do
    if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
      log_line "[ok] 健康检查通过：$label $url"
      return 0
    fi
    sleep 2
  done
  fail "健康检查失败：$label $url"
}

run_healthchecks() {
  healthcheck_url "http://127.0.0.1:$BACKEND_PORT/api/health" "后端 API"
  healthcheck_url "http://127.0.0.1:$PUBLIC_PORT/" "前台"
  healthcheck_url "http://127.0.0.1:$PUBLIC_PORT/admin/" "后台"
}

print_summary() {
  local public_ip private_ip public_host private_host public_home public_admin private_home private_admin api_url
  public_ip="$(detect_public_ipv4)"
  private_ip="$(detect_private_ipv4)"
  public_host="${SITE_DOMAIN:-$public_ip}"
  [ -z "$public_host" ] && public_host="<your-server-ip>"
  private_host="${private_ip:-127.0.0.1}"
  public_home="$(url_for "$public_host" "$PUBLIC_PORT")"
  public_admin="$public_home/admin/login"
  private_home="$(url_for "$private_host" "$PUBLIC_PORT")"
  private_admin="$private_home/admin/login"
  api_url="$(url_for "127.0.0.1" "$BACKEND_PORT")/api/health"

  printf '\n'
  printf 'SRBlogs 安装完成。\n'
  printf '外网前台：%s\n' "$public_home"
  printf '外网后台：%s\n' "$public_admin"
  printf '内网前台：%s\n' "$private_home"
  printf '内网后台：%s\n' "$private_admin"
  printf 'API 地址：%s\n' "$api_url"
  printf '管理员 username：%s\n' "$ADMIN_USERNAME"
  if [ "$ENV_WRITE_MODE" = "keep" ]; then
    printf '管理员 password：已保留现有 %s/backend.env 配置\n' "$ENV_DIR"
  else
    printf '管理员 password：%s\n' "$ADMIN_PASSWORD"
  fi
  printf '\n'
  printf '查看服务状态：systemctl status %s --no-pager\n' "$BACKEND_SERVICE"
  printf '查看后端日志：journalctl -u %s -n 100 --no-pager\n' "$BACKEND_SERVICE"
  printf '安装日志：%s\n' "$LOG_FILE"
  printf '\n'
  printf '如果使用云服务器，请在安全组中放行 TCP %s 端口。\n' "$PUBLIC_PORT"
  if [ "$public_host" = "<your-server-ip>" ]; then
    printf '未能自动检测公网 IPv4，请将 <your-server-ip> 替换为服务器公网地址。\n'
  fi
}

main() {
  require_root
  init_runtime_dirs
  log_line "SRBlogs 在线安装开始：$TIMESTAMP"
  collect_config
  local pm
  pm="$(detect_package_manager)"
  install_system_dependencies "$pm"
  install_node20_if_needed "$pm"
  fetch_latest_release
  download_and_extract_release
  ensure_service_user
  prepare_app_directory
  prepare_build_permissions
  write_backend_env
  prepare_data_directory
  install_backend
  build_frontends
  harden_app_permissions
  write_systemd_service
  write_nginx_config
  configure_ufw_if_requested
  install_restricted_updater
  start_services
  run_healthchecks
  log_line "SRBlogs 在线安装完成。"
  print_summary
}

main "$@"
