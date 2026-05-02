# SRBlogs Deployment Guide

This project keeps the current stack: Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI.

## Build

Frontend:

```powershell
cd frontend
npm install
npm run build
```

Admin:

```powershell
cd admin
npm install
npm run build
```

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Production `.env`

Set these on the server, not in frontend/admin source:

```env
APP_ENV=production
PUBLIC_BASE_URL=https://example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-strong-password
JWT_SECRET=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://example.com
UPLOAD_DRIVER=local
AI_A_API_KEY=
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
```

## Data Directory

- `backend/data` stores Markdown, JSON, comments, uploads, and backups.
- The backend process user must have read/write permission to `backend/data`.
- Back up `backend/data` before deployment and before migrations.
- Do not serve `.env` or backup files directly through Nginx.

## Nginx Example

```nginx
server {
    listen 80;
    server_name example.com;

    root /srv/srblogs/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /admin/ {
        alias /srv/srblogs/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
    }
}
```

Use HTTPS in production, for example with Certbot or the platform's managed TLS.

## systemd Example

```ini
[Unit]
Description=SRBlogs FastAPI
After=network.target

[Service]
WorkingDirectory=/srv/srblogs/backend
EnvironmentFile=/srv/srblogs/backend/.env
ExecStart=/srv/srblogs/backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
User=srblogs
Group=srblogs

[Install]
WantedBy=multi-user.target
```

Commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable srblogs
sudo systemctl start srblogs
sudo systemctl status srblogs
```

## Preflight Checklist

- `ADMIN_PASSWORD` is changed from the default.
- `JWT_SECRET` is changed to a long random value.
- `CORS_ORIGINS` only includes production domains.
- Development ports 5173/5174 are not exposed.
- `frontend/dist` and `admin/dist` do not contain Secret values.
- `backend/data` has a backup.
- Upload size/type/MIME limits are enabled.
- `/api/health` returns OK.
- `/api/settings/public` does not return Secret fields or values.
- `/api/admin/settings` only returns configured booleans for Secrets.
