# SRBlogs Release Candidate Notes

## Scope

This release candidate packages SRBlogs as a deployable Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI blog system. It is an original Vue/FastAPI implementation that targets the experience level of XinghuisamaBlogs without copying its source, assets, text, or private material.

## Completed Capabilities

- Public blog pages: homepage, post list, post detail, moments, chatters, friends, projects, music, photowall, about, timeline.
- Content discovery: search, tags, tag detail, archive, homepage discovery entry.
- Writing workflow: Markdown editor, preview, drafts, publish, edit, delete, and first-stage local pending operations.
- Comments: local comment read/write/delete, validation, XSS cleaning, admin comment index and management.
- Structured content: form-first admin management for friends, projects, music, and photos with advanced JSON fallback.
- SEO and subscription: dynamic meta, OpenGraph, Twitter Card, RSS, sitemap, robots, and share link copy.
- Stability: loading/empty/error states, mobile checks, image fallbacks, basic accessibility improvements.
- Data safety: atomic writes, per-file backups, audit logs, manual backup list/create/download/restore, export/import.
- Deployment readiness: production env template, Nginx example, systemd example, healthcheck script, production checklist.

## Production Notes

- Copy `backend/.env.production.example` to `/etc/srblogs/backend.env` or another server-only environment file.
- Change `ADMIN_PASSWORD` and `JWT_SECRET` before first production start.
- Set `PUBLIC_BASE_URL` to the public HTTPS origin. RSS, sitemap, robots, OpenGraph URLs, and upload URLs depend on it.
- Restrict `CORS_ORIGINS` to trusted production origins.
- Keep `backend/data` persistent and backed up.
- Do not expose `.env`, `.manual_backups`, `audit`, frontend source, `node_modules`, or build internals through Nginx.

## Default Account Reminder

The development default account is `admin / change-me`. It is only for local development. Production must use a new password and a new JWT secret in server-side configuration.

## Backup And Recovery Reminder

- Create a manual backup before deployment, restore, import, or migration work.
- Restore automatically creates a `pre-restore-*.zip` backup, but operators should still verify disk space and data directory permissions first.
- Audit logs record high-risk operations, but logs must not be treated as a substitute for backups.

## Deferred Items

These remain `延期/未验收` by user decision and are not release blockers for this candidate:

- Empty Secret preservation browser verification in settings.
- Comment switch browser verification in settings.
- Image hosting provider deep integration and complete upload provider verification.
- Real AI provider integration.
- Full hands-on production server deployment rehearsal.
