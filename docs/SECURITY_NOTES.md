# Security Notes

## 管理员凭据

- 生产环境推荐通过 `/install` 初始化管理员账号。
- 新安装和 `backend/scripts/reset_admin.py` 写入 `ADMIN_PASSWORD_HASH`，不再写入明文 `ADMIN_PASSWORD`。
- `ADMIN_PASSWORD` 仅作为旧部署兼容字段保留；`deploy/doctor.sh` 检测到后会输出 WARN。
- `JWT_SECRET` 由安装向导自动生成；手动配置时必须使用长随机值。

## Secret 边界

- OAuth Secret、SMTP 密码、AI Key、OSS Key、JWT Secret 和管理员凭据只能保存在服务端环境文件或后端数据中。
- 不得把 Secret 写入 `frontend/`、`admin/`、构建产物、主题包、页面配置、公开 JSON 或日志。
- `/api/settings/public` 只能返回公开站点配置和 `xxxConfigured` 布尔状态，不得返回 Secret 明文。
- `GET /api/admin/settings` 也只能用布尔字段表达 Secret 是否已配置。

## 上传与文件

- 上传接口必须要求管理员 JWT，并校验 MIME、扩展名和大小。
- Nginx 不得直接暴露 `.env`、`.manual_backups`、`audit`、源代码目录、`node_modules` 或构建内部文件。
- 备份 zip 不得包含 `.env`、`.venv`、`node_modules`、`dist`、前端源码或 `.manual_backups` 本身。
- 恢复和导入 zip 必须拒绝绝对路径、`..`、路径穿越和非预期目录。

## OAuth 与评论

- GitHub OAuth Secret 与 QQ App Secret 只能在后端保存。
- OAuth 登录必须由后端生成授权地址，并校验 CSRF `state`。
- 前端留言区只显示访客友好提示，不暴露 `.env`、Secret、Client Secret 或服务端配置路径。
- 未登录提交评论必须返回 `401`。

## 部署安全

- `/etc/srblogs/backend.env` 安装期可允许 `srblogs` 写入；安装完成后建议收紧为 `root:srblogs 640` 或 `root:root 600`。
- systemd 服务统一使用 `srblogs-backend.service`。
- Nginx 后台 SPA 配置应使用 `/admin/` 独立 alias 和 history fallback，避免后台资源落到前台目录。
- 生产环境必须限制 `CORS_ORIGINS`，不要使用 `*`。

## 审计与日志

- 登录、内容写入、评论删除、设置修改、上传、备份、恢复、导入和导出应写入审计日志。
- 审计日志和部署脚本日志必须脱敏 `password`、`secret`、`token`、`key`、`authorization` 等字段。
- 排查时优先提供错误码、时间点和脱敏日志，不粘贴真实 Secret。
