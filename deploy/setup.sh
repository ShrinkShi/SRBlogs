#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/SRBlogs}
FRONTEND_DIR=/var/www/srblogs-frontend
ADMIN_DIR=/var/www/srblogs-admin
SERVICE_USER=${SERVICE_USER:-srblogs}

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 root 执行：sudo bash deploy/setup.sh"
  exit 1
fi

echo "[1/8] 安装系统依赖"
dnf install -y nginx git python3 python3-pip nodejs npm || yum install -y nginx git python3 python3-pip nodejs npm

echo "[2/8] 创建运行用户"
id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd -r -s /sbin/nologin "$SERVICE_USER"

echo "[3/8] 同步项目到 $APP_DIR"
mkdir -p "$APP_DIR"
rsync -a --delete ./ "$APP_DIR/"

echo "[4/8] 安装后端依赖"
cd "$APP_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
mkdir -p data/uploads
chown -R "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR/backend"

echo "[5/8] 构建前端"
cd "$APP_DIR/frontend"
npm install
npm run build
mkdir -p "$FRONTEND_DIR"
rsync -a --delete dist/ "$FRONTEND_DIR/"

echo "[6/8] 构建后台"
cd "$APP_DIR/admin"
npm install
npm run build
mkdir -p "$ADMIN_DIR"
rsync -a --delete dist/ "$ADMIN_DIR/"

echo "[7/8] 配置 Nginx 和 Systemd"
cp "$APP_DIR/deploy/nginx/srblogs.conf" /etc/nginx/conf.d/srblogs.conf
cp "$APP_DIR/deploy/systemd/srblogs.service" /etc/systemd/system/srblogs.service
systemctl daemon-reload
systemctl enable --now srblogs
systemctl enable --now nginx
nginx -t
systemctl reload nginx

echo "[8/8] 完成"
echo "请立刻修改：$APP_DIR/backend/.env 中的 ADMIN_PASSWORD 和 JWT_SECRET"
echo "前台： http://服务器IP/"
echo "后台： http://服务器IP/admin/"
