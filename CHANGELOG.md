# Changelog

## 2026-05-02 - Release Candidate

### Added

- Vue 3 frontend with home, posts, post detail, moments, chatters, friends, projects, music, photowall, about, timeline, search, tags, and archive routes.
- FastAPI backend with Markdown/JSON file storage, safe slug checks, atomic writes, backups, comments, uploads, settings, dashboard stats, search, tags, archive, RSS, sitemap, and robots.
- Admin console with editor, posts, comments, friends, projects, music, photos, settings, audit logs, and backup/restore pages.
- Markdown preview and frontend article rendering with DOMPurify cleaning.
- Local comment create/read/delete flow with XSS cleaning, validation, and backup before overwrite/delete.
- Structured content management for friends, projects, music, and photos with form-first admin workflows.
- SEO metadata, OpenGraph/Twitter Card runtime updates, RSS feed, sitemap, robots, and share copy feedback.
- Audit log and manual backup/restore/export/import APIs and admin pages.
- Production deployment assets under `deploy/`, production env template, health check script, and release checklists.

### Security

- Secret fields are kept in backend environment/server config and are not returned by public settings.
- Admin settings return configured booleans instead of Secret plaintext.
- Uploads validate extension, MIME type, and size.
- Manual backup zips exclude `.env`, frontend source, dependency/build folders, and `.manual_backups`; `settings.json` is sanitized before inclusion.
- Backup download/restore/import/export and audit logs require admin JWT.

### Deferred

- Settings empty Secret preservation browser verification.
- Comment switch browser verification.
- Real OSS image hosting integration.
- Real AI provider integration.
- Full hands-on production server deployment rehearsal.
