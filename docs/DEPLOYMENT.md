# SRBlogs Deployment Guide

SRBlogs keeps the current stack: Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI.

This guide uses `/opt/srblogs` as the Linux deployment path and `/etc/srblogs/backend.env` as the production environment file. Replace `example.com` with your real domain.

## 1. Production Environment

SRBlogs supports a first-start web installer. After `deploy/setup.sh` and Nginx are installed, visit:

```text
https://example.com/install
```

The installer creates `backend/data/.install.lock`, writes required public site settings, writes `/etc/srblogs/backend.env`, and generates `JWT_SECRET` on the server. After finishing the installer, restart the backend:

```bash
sudo systemctl restart srblogs-backend
```

Manual environment setup is still supported. Start from the template:

```bash
sudo mkdir -p /etc/srblogs
sudo cp /opt/srblogs/backend/.env.production.example /etc/srblogs/backend.env
sudo editor /etc/srblogs/backend.env
```

Required production changes:

- `ADMIN_PASSWORD`: must not be the development default.
- `JWT_SECRET`: must be a long random value.
- `PUBLIC_BASE_URL`: must be the public site origin, for example `https://example.com`.
- `SITE_START_TIME`: optional ISO timestamp used for the site runtime counter. The installer writes this automatically when left blank.
- `CORS_ORIGINS`: must list trusted origins only. Do not use `*` in production.
- `DATA_DIR`: should point to the persistent data directory, usually `/opt/srblogs/backend/data`.

`PUBLIC_BASE_URL` is used by RSS, sitemap, robots, OpenGraph URLs, and upload URLs.

## 2. Build

Use the deploy helper:

```bash
cd /opt/srblogs
bash deploy/build-all.sh
```

Equivalent manual commands:

```bash
cd /opt/srblogs/frontend
npm install
npm run build

cd /opt/srblogs/admin
npm install
npm run build

cd /opt/srblogs
python -m compileall backend/app
```

## 3. Backend

```bash
cd /opt/srblogs/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p data/uploads data/audit data/.manual_backups
```

Reference startup script:

```bash
bash /opt/srblogs/deploy/start-backend.sh
```

The script loads `/etc/srblogs/backend.env` when present and starts uvicorn on `127.0.0.1:8000`. If the environment file is missing, the backend still starts in install mode so `/install` can finish initialization.

## 4. systemd

Reference unit: `deploy/srblogs-backend.service`

```bash
sudo cp /opt/srblogs/deploy/srblogs-backend.service /etc/systemd/system/srblogs-backend.service
sudo systemctl daemon-reload
sudo systemctl enable --now srblogs-backend
sudo systemctl status srblogs-backend
```

Logs:

```bash
journalctl -u srblogs-backend -f
```

## 5. Nginx

Reference config: `deploy/nginx.srblogs.conf`

The example includes:

- frontend static files from `/opt/srblogs/frontend/dist`
- admin static files from `/opt/srblogs/admin/dist`
- `/api` reverse proxy to `127.0.0.1:8000`
- `/uploads` reverse proxy to the backend upload service
- `/robots.txt` reverse proxy to the backend route
- gzip
- static cache headers
- `client_max_body_size 5m`

Install:

```bash
sudo cp /opt/srblogs/deploy/nginx.srblogs.conf /etc/nginx/conf.d/srblogs.conf
sudo nginx -t
sudo systemctl reload nginx
```

Use HTTPS in production, for example through Certbot or your platform's managed TLS.

## 6. Health Check

Backend endpoints:

- `GET /api/health`: public basic health check.
- `GET /api/install/status`: public install status check.
- `GET /api/admin/system/status`: admin JWT required; checks app name, environment, data directory, uploads directory, and read/write flags without returning secrets.

Deploy helper:

```bash
PUBLIC_BASE_URL=https://example.com API_BASE_URL=http://127.0.0.1:8000 bash deploy/healthcheck.sh
```

The script checks backend health, frontend homepage, admin entry, RSS, sitemap, and robots.

## 7. Data And Logs

Persistent directories:

- `backend/data`: Markdown, JSON, comments, uploads, audit logs, and manual backups.
- `backend/data/.manual_backups`: manual backups, exports, and pre-restore backups.
- `backend/data/audit/audit.log`: admin audit log in JSON Lines format.
- `backend/data/uploads`: uploaded files.
- `backend/data/.install.lock`: install completion marker. Remove it only for a deliberate reinstall.

Do not serve `.env`, `.manual_backups`, or `audit` directly through Nginx.

Before restore operations:

- confirm the backend service user owns or can write `backend/data`;
- create a fresh backup;
- confirm disk space is sufficient.

## 8. Production Preflight

- `/install` completed or `/etc/srblogs/backend.env` was configured manually.
- `ADMIN_PASSWORD` changed when using manual env setup.
- `JWT_SECRET` changed when using manual env setup.
- `CORS_ORIGINS` restricted to production origins.
- development ports `5173` and `5174` are not exposed.
- `frontend/dist` and `admin/dist` do not contain secret values.
- `/api/settings/public` does not return secret fields or values.
- `/api/admin/settings` only returns `xxxConfigured` booleans for secrets.
- `/api/rss.xml`, `/api/sitemap.xml`, and `/robots.txt` return public data only.
- `backend/data` has a backup.
- upload size/type/MIME limits are enabled.

See also [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md).
