#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/srblogs}"
ENV_DIR="${ENV_DIR:-/etc/srblogs}"
SERVICE_USER="${SERVICE_USER:-srblogs}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash deploy/setup.sh"
  exit 1
fi

echo "[1/7] installing system packages"
if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y nginx rsync python3 python3-venv python3-pip nodejs npm
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y nginx rsync python3 python3-pip nodejs npm
else
  yum install -y nginx rsync python3 python3-pip nodejs npm
fi

echo "[2/7] creating service user"
id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd -r -s /usr/sbin/nologin "$SERVICE_USER" || useradd -r -s /sbin/nologin "$SERVICE_USER"

echo "[3/7] syncing project to $APP_DIR"
mkdir -p "$APP_DIR" "$ENV_DIR"
rsync -a --delete ./ "$APP_DIR/"

echo "[4/7] preparing backend"
cd "$APP_DIR/backend"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
mkdir -p data/uploads data/audit data/.manual_backups
if [ ! -f "$ENV_DIR/backend.env" ]; then
  cp "$APP_DIR/backend/.env.production.example" "$ENV_DIR/backend.env"
  echo "Created $ENV_DIR/backend.env. Edit it before exposing the service."
fi
chown -R "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR/backend"

echo "[5/7] building frontend and admin"
cd "$APP_DIR"
bash deploy/build-all.sh

echo "[6/7] installing systemd and nginx config"
cp "$APP_DIR/deploy/srblogs-backend.service" /etc/systemd/system/srblogs-backend.service
cp "$APP_DIR/deploy/nginx.srblogs.conf" /etc/nginx/conf.d/srblogs.conf
systemctl daemon-reload
systemctl enable --now srblogs-backend
systemctl enable --now nginx
nginx -t
systemctl reload nginx

echo "[7/7] done"
echo "Edit $ENV_DIR/backend.env: ADMIN_PASSWORD, JWT_SECRET, PUBLIC_BASE_URL, CORS_ORIGINS."
echo "Check backend logs: journalctl -u srblogs-backend -f"
