# SRBlogs Production Deploy Assets

These files are reference assets for a Linux deployment. They use `/opt/srblogs` and `/etc/srblogs/backend.env` as placeholders; adjust paths and domain names for the target server.

## Files

- `build-all.sh`: builds `frontend/dist` and `admin/dist`, then runs backend Python syntax checks.
- `start-backend.sh`: starts FastAPI with the project virtualenv and optional environment file.
- `srblogs-backend.service`: systemd unit for the backend.
- `nginx.srblogs.conf`: Nginx example serving frontend/admin static files and proxying `/api`, `/uploads`, and `/robots.txt`.
- `healthcheck.sh`: checks backend health, frontend, admin, RSS, sitemap, and robots.

## Basic Flow

Recommended first install:

```bash
sudo bash deploy/setup.sh
```

Then visit `http://your-domain/install` to complete the web installer. The installer writes `/etc/srblogs/backend.env`, initializes `backend/data/settings.json`, creates `backend/data/.install.lock`, and generates `JWT_SECRET` server-side. Restart the backend after installation:

```bash
sudo systemctl restart srblogs-backend
```

Manual setup is still supported:

```bash
sudo mkdir -p /opt/srblogs /etc/srblogs
sudo rsync -a --delete ./ /opt/srblogs/
sudo cp /opt/srblogs/backend/.env.production.example /etc/srblogs/backend.env
sudo editor /etc/srblogs/backend.env
```

Production must set `ADMIN_PASSWORD`, `JWT_SECRET`, `PUBLIC_BASE_URL`, `CORS_ORIGINS`, and optionally `SITE_START_TIME` when using manual setup.

```bash
cd /opt/srblogs/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

cd /opt/srblogs
bash deploy/build-all.sh
sudo cp deploy/srblogs-backend.service /etc/systemd/system/srblogs-backend.service
sudo systemctl daemon-reload
sudo systemctl enable --now srblogs-backend

sudo cp deploy/nginx.srblogs.conf /etc/nginx/conf.d/srblogs.conf
sudo nginx -t
sudo systemctl reload nginx
```

## Logs And Data

- Persistent data: `/opt/srblogs/backend/data`
- Manual backups: `/opt/srblogs/backend/data/.manual_backups`
- Audit logs: `/opt/srblogs/backend/data/audit/audit.log`
- Uploads: `/opt/srblogs/backend/data/uploads`
- Install lock: `/opt/srblogs/backend/data/.install.lock`
- Backend logs: `journalctl -u srblogs-backend -f`
- Nginx logs: usually `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

Before restore operations, confirm the backend service user can read and write the data directory.
