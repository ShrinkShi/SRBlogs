# SRBlogs Release Candidate Notes

## Scope

This release candidate packages SRBlogs as a deployable Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI blog system. It is an original Vue/FastAPI implementation that targets the experience level of XinghuisamaBlogs without copying its source, assets, text, or private material.

## Completed Capabilities

- Public blog pages: homepage, post list, post detail, moments, chatters, friends, projects, music, photowall, about, timeline.
- Content discovery: search, tags, tag detail, archive, homepage discovery entry.
- Writing workflow: Markdown editor, preview, drafts, publish, unpublish, edit, delete, and first-stage local pending operations.
- Comments: local comment read/write/delete, validation, XSS cleaning, admin comment index and management.
- Structured content: form-first admin management for friends, projects, music, and photos with advanced JSON fallback.
- SEO and subscription: dynamic meta, OpenGraph, Twitter Card, RSS, sitemap, robots, and share link copy.
- Stability: loading/empty/error states, mobile checks, image fallbacks, basic accessibility improvements.
- Data safety: atomic writes, per-file backups, audit logs, manual backup list/create/download/restore, export/import.
- Deployment readiness: production env template, Nginx example, systemd example, healthcheck script, production checklist.
- Final regression: content production demo flow, comment sync, audit logs, manual backup, backup download, pre-restore backup, restore, RSS/sitemap/robots, and Secret scans.
- Usability closure: clearer admin operation feedback, runtime artifact ignore rules, and `docs/USER_GUIDE.md` for daily use.

## Production Notes

- Prefer `deploy/install.sh` and complete `/install`; the installer writes `ADMIN_PASSWORD_HASH` and generates `JWT_SECRET`.
- For advanced manual setup, copy `backend/.env.production.example` to `/etc/srblogs/backend.env` and set a long random `JWT_SECRET`.
- Set `PUBLIC_BASE_URL` to the public HTTPS origin. RSS, sitemap, robots, OpenGraph URLs, and upload URLs depend on it.
- Restrict `CORS_ORIGINS` to trusted production origins.
- Keep `backend/data` persistent and backed up.
- Do not expose `.env`, `.manual_backups`, `audit`, frontend source, `node_modules`, or build internals through Nginx.

## Admin Account Reminder

Production administrator credentials are created by `/install`. If the password is lost, reset it with `backend/scripts/reset_admin.py`; legacy plain `ADMIN_PASSWORD` is only kept for old deployments.

## Backup And Recovery Reminder

- Create a manual backup before deployment, restore, import, or migration work.
- Restore automatically creates a `pre-restore-*.zip` backup, but operators should still verify disk space and data directory permissions first.
- Audit logs record high-risk operations, but logs must not be treated as a substitute for backups.

## Deferred Items

These remain outside the current P0/P1 closure scope and are not release blockers for this candidate:

- Real server deployment with a live domain and HTTPS certificate. Repository docs and scripts are ready; hands-on server execution is `部署实操待执行`.
- Image hosting provider deep OSS/custom integration beyond local upload validation.
- Real AI provider integration.
- Real Gitalk/GitHub OAuth integration.
- P2 visual enhancement work such as sakura, barrage, CyberCat, and dynamic-background upgrades.
