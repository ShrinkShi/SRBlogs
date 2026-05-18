# SRBlogs Production Checklist

## 1. Build Before Release

- [ ] `cd frontend && npm run build` passes.
- [ ] `cd admin && npm run build` passes.
- [ ] `python -m compileall backend\app` passes.
- [ ] `frontend/dist` and `admin/dist` are generated.
- [ ] Build artifacts do not contain secret values from `backend/.env`.

## 2. Environment Variables

- [ ] Production env is copied from `backend/.env.production.example`.
- [ ] `APP_ENV=production`.
- [ ] `DATA_DIR` points to persistent storage.
- [ ] `PUBLIC_BASE_URL` is the public HTTPS origin.
- [ ] `ADMIN_PASSWORD` is changed from the local development value.
- [ ] `JWT_SECRET` is changed to a long random value.
- [ ] `CORS_ORIGINS` does not use `*` and only includes trusted origins.
- [ ] AI, OSS, and GitHub OAuth secrets are empty or set only in server env.

## 3. Secret Check

- [ ] `GET /api/settings/public` does not return secret fields or values.
- [ ] `GET /api/admin/settings` only returns `xxxConfigured` booleans for secrets.
- [ ] `frontend/dist` does not contain `ADMIN_PASSWORD`, `JWT_SECRET`, AI Key, OSS Key, or OAuth Secret.
- [ ] `admin/dist` does not contain `ADMIN_PASSWORD`, `JWT_SECRET`, AI Key, OSS Key, or OAuth Secret.
- [ ] Backup zip files do not include `.env`.

## 4. CORS Check

- [ ] Frontend production origin is in `CORS_ORIGINS`.
- [ ] Admin production origin is in `CORS_ORIGINS`.
- [ ] Local dev origins are removed unless intentionally needed.
- [ ] Browser login and admin API calls work through the production origin.

## 5. Backend Health

- [ ] `GET /api/health` returns OK.
- [ ] `GET /api/admin/system/status` returns app name and data directory status after login.
- [ ] `backend/data` exists.
- [ ] `backend/data` is readable and writable by the backend service user.
- [ ] `backend/data/uploads` exists.

## 6. Nginx Check

- [ ] `deploy/nginx.srblogs.conf` is copied and domain is updated.
- [ ] `nginx -t` passes.
- [ ] `/` serves frontend SPA.
- [ ] `/admin/` serves admin SPA.
- [ ] `/api/` proxies to FastAPI.
- [ ] `/uploads/` resolves uploaded files.
- [ ] `client_max_body_size` matches the configured upload limit.
- [ ] HTTPS is enabled before public release.

## 7. systemd Check

- [ ] `deploy/srblogs-backend.service` is copied to systemd.
- [ ] `/etc/srblogs/backend.env` exists after `/install` or manual setup; systemd may start without it to enter install mode.
- [ ] `WorkingDirectory=/opt/srblogs/backend` exists.
- [ ] `systemctl enable --now srblogs-backend` succeeds.
- [ ] `journalctl -u srblogs-backend -f` shows no startup error.

## 8. Frontend Pages

- [ ] `/` opens.
- [ ] `/posts` opens.
- [ ] `/posts/:slug` opens for a published article.
- [ ] `/search`, `/tags`, `/archive` open.
- [ ] `/friends`, `/projects`, `/music`, `/photowall`, `/about`, `/timeline` open.
- [ ] 404 route is readable and not blank.
- [ ] Mobile 390px quick check has no serious horizontal overflow.

## 9. Admin Pages

- [ ] `/admin/` opens.
- [ ] Login succeeds with the production admin password.
- [ ] `/admin/editor`, `/admin/posts`, `/admin/comments`, `/admin/friends`, `/admin/projects`, `/admin/music`, `/admin/photos`, `/admin/settings` open.
- [ ] `/admin/audit` opens.
- [ ] `/admin/backups` opens.
- [ ] Login expiration or missing JWT has a clear redirect or prompt.

## 10. RSS, Sitemap, Robots

- [ ] `GET /api/rss.xml` opens in the browser.
- [ ] `GET /api/sitemap.xml` opens in the browser.
- [ ] `GET /robots.txt` includes `Disallow: /admin`.
- [ ] RSS and sitemap do not include draft posts.
- [ ] URLs use `PUBLIC_BASE_URL`.

## 11. Upload Check

- [ ] Allowed image type uploads succeed.
- [ ] Disallowed file extension is rejected.
- [ ] Disallowed MIME type is rejected.
- [ ] Oversized file is rejected.
- [ ] Uploaded URL works through `/uploads/`.

## 12. Audit Log Check

- [ ] Login success/failure is logged.
- [ ] Content create/edit/delete is logged.
- [ ] Comment delete is logged.
- [ ] Settings update is logged.
- [ ] Manual backup, restore, import, and export are logged.
- [ ] Audit logs do not contain secret values.

## 13. Backup Check

- [ ] `POST /api/admin/backups` creates a backup.
- [ ] `GET /api/admin/backups` lists backups.
- [ ] Backup download works and requires JWT.
- [ ] Backup zip does not contain `.env`, frontend source, `node_modules`, `dist`, or `.manual_backups`.
- [ ] Backup zip `settings.json` does not contain secret fields.

## 14. Restore Check

- [ ] Restore shows a clear risk warning in admin UI.
- [ ] Restore creates `pre-restore-*.zip` before replacing data.
- [ ] Restore rejects path traversal backup names.
- [ ] Restore rejects unsafe zip members.
- [ ] Data is readable after restore.

## 15. Rollback Plan

- [ ] Keep the previous deployment artifact or git tag.
- [ ] Keep the latest `backend/data/.manual_backups/*.zip`.
- [ ] To roll back code: restore previous release directory and restart `srblogs-backend`.
- [ ] To roll back data: restore the pre-restore backup from `/admin/backups`.
- [ ] Verify `/api/health`, frontend, admin, RSS, sitemap, and robots after rollback.

## 16. Known Deferred Items

- [ ] Real production server hands-on deployment with domain and HTTPS remains `部署实操待执行`.
- [ ] Real OSS/custom image hosting deep integration is not part of the current release candidate; local upload validation is covered.
- [ ] Real AI provider model integration is not part of the current release candidate; configuration boundary and key secrecy are covered.
- [ ] Real Gitalk/GitHub OAuth integration is not part of the current release candidate; Secret boundary is covered.
- [ ] P2 visual enhancements remain frozen.
