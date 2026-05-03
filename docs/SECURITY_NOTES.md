# Security Notes

## Secret Storage

- JWT Secret、管理员密码、AI Key、OSS Key、GitHub OAuth Secret 只能保存在后端 `.env` 或服务端配置。
- 前台只能读取 `GET /api/settings/public` 返回的公开站点配置。
- 后台 settings 接口也不得返回 Secret 明文，只能返回 `xxxConfigured` 布尔值。
- 不得把 Secret 写入 `frontend/`、`admin/` 或任何会进入构建产物的文件。

## Settings Boundary

- `GET /api/settings/public` 只能返回站点标题、副标题、作者、头像、简介、社交链接、主题、背景图、公开音乐配置和公开评论显示选项。
- `GET /api/admin/settings` 必须要求管理员 JWT，且不得回显 AI Key、OSS Key、GitHub OAuth Secret 明文。
- 后台配置只能通过 `aiKeyConfigured`、`accessKeyConfigured`、`secretKeyConfigured`、`ossKeyConfigured`、`githubOAuthSecretConfigured` 等布尔值表达 Secret 是否已配置。
- `PUT /api/admin/settings` 中 Secret 字段为空字符串、`null` 或未传时，必须保持旧值；只有传入明确新值时才允许覆盖。
- GitHub OAuth Secret 仅作为服务端配置或后台写入字段存在，前台评论区只允许读取公开显示配置，不接入或暴露真实 OAuth Secret。
- 每次发布前必须对 `frontend/dist` 和 `admin/dist` 做静态搜索，确认没有默认密码、JWT Secret、AI Key、OSS Key、GitHub OAuth Secret 或真实 Secret 值。

## Public SEO Endpoints

- `GET /api/rss.xml`、`GET /api/sitemap.xml` 和 `GET /robots.txt` 是公开接口，不需要 JWT。
- RSS 和 sitemap 只能包含公开内容，`draft=true` 的 posts/moments/chatters 不得进入输出。
- RSS description 必须经过 XML/HTML 转义，不得输出未经转义的 Markdown/HTML。
- robots 必须禁止爬取 `/admin`，不得暴露 `.env`、备份目录、服务器绝对路径或 Secret。
- OpenGraph、Twitter Card、RSS、Sitemap 使用的站点 URL 只能来自公开 base URL 或当前浏览器 origin，不得写入后台 admin 地址或私有配置。

## Uploads

- 2026-05-03 起，本地上传入口支持图片、音频、视频和歌词文本资源，但仍必须要求管理员 JWT，并继续执行扩展名、MIME 和大小三重校验。
- 允许的音频/视频/歌词资源只用于本地文件托管和 URL 回填，不代表允许执行脚本或上传任意二进制文件。
- 上传返回 URL 可写入头像、背景、相册照片、封面、音乐 URL、歌词 URL 或后续视频字段；结构化 JSON 的保存仍必须走后端 API 和安全写入封装。
- 上传大小按类型分档限制：图片默认 10 MB，音频默认 100 MB，视频默认 200 MB，歌词 `.lrc/.txt` 默认 1 MB；禁止关闭大小限制或允许任意文件类型。

- 上传接口必须要求管理员 JWT。
- 后端必须同时校验扩展名、MIME 和大小。
- 当前允许：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`、`.mp3`、`.wav`、`.ogg`、`.m4a`、`.mp4`、`.webm`、`.mov`、`.lrc`、`.txt`。
- 当前允许 MIME：按 `UPLOAD_ALLOWED_TYPES` 配置校验图片/音频/视频；歌词文件只允许文本类型。
- 当前大小上限：图片 10 MB、音频 100 MB、视频 200 MB、歌词 1 MB。

## Slug And Paths

- `slug` 必须通过 `validate_slug`。
- 禁止空字符串、`..`、`/`、`\` 和白名单外字符。
- 所有数据路径必须通过 `resolve_data_path`，最终路径必须仍位于 `backend/data` 内。
- 禁止业务路由拼接任意文件系统路径后写入。

## Markdown And Comments

- 前台 Markdown 渲染必须经过 DOMPurify 清洗。
- 评论提交内容必须由后端清洗后保存。
- 新评论只允许 GitHub 登录身份提交；未登录必须返回 401，不得回退到匿名评论。
- GitHub OAuth code flow 必须由后端完成并校验 CSRF `state`；OAuth Client Secret 只能保存在后端 `.env` 或服务端配置。
- 前端只允许读取 `/api/auth/github/me` 返回的 configured 状态和 GitHub 公开用户信息，不能获得 OAuth access token 或 Secret。
- 评论 JSON 不得保存 GitHub access token，只保存必要的 GitHub 登录名、头像 URL、显示名和评论内容。
- Markdown 内容允许用户输入，但渲染时不得直接插入未经清洗的 HTML。
- 后台删除评论必须要求管理员 JWT。
- 后台评论索引 `GET /api/admin/comments/index` 必须要求管理员 JWT，只返回 `resource`、`slug`、`count`、`updatedAt`、`title` 等管理索引字段。
- 删除评论前必须备份对应评论 JSON 文件。
- 评论开关和最大长度必须在后端 API 强制执行，不能只依赖前端 UI。
- 旧本地邮箱评论配置不再作为后台主流程展示；新评论固定使用 GitHub 登录身份，不再接受前端传入作者/邮箱。
- 评论内容和昵称写入前必须继续用 bleach 清洗，前端展示不得直接渲染危险 HTML。
- 删除不存在的评论必须返回 404，不允许静默成功。
- 评论管理不进入第一阶段本地 `pendingOperations`，删除操作当前为管理员确认后直接持久化写回后端 JSON。

## JSON And Markdown Writes

- 所有 JSON/Markdown 读写必须走 `backend/app/services/file_store.py`。
- 写入必须使用临时文件 + 原子替换。
- 覆盖或删除已有文件前必须调用 `backup_file`。
- 公开内容接口不得返回 `draft=true` 内容；`include_drafts=true` 只能在管理员 JWT 下使用。
- 文章发布、撤回发布、编辑和删除必须写审计日志；删除 Markdown 前必须备份原文件。
- 禁止业务路由或业务 service 直接 `open(..., "w")` 写 JSON/Markdown。
- friends/projects/music/photos 的表单化管理和高级 JSON 编辑都必须通过 `JsonStore.write` 写入，不允许前端绕过 API 直接改文件。
- 高级 JSON 编辑只作为兜底入口，保存前必须校验 JSON 格式且根节点必须为数组。
- 图片上传只写入上传文件并返回 URL；照片记录仍需通过 `/api/photos` 写入 JSON，且不进入本地 `pendingOperations`。

## Audit Logs And Backups

- 后台审计日志写入 `backend/data/audit/audit.log`，使用 JSON Lines，每条日志必须包含时间、操作者、动作、资源、目标、结果和说明。
- 审计日志写入失败不得阻断主业务操作，但删除、恢复、导入、导出、上传、settings 修改和内容写入等高风险动作应尽量记录。
- 审计日志 `detail` 必须清洗 `secret`、`password`、`token`、`key`、`authorization` 等字段，不得记录 Secret 明文。
- 所有手动备份、下载备份、恢复备份、导入和导出接口必须要求管理员 JWT。
- 手动备份只能写入 `backend/data/.manual_backups/{timestamp}.zip`，文件名必须使用时间戳避免覆盖。
- 备份不得包含 `.env`、`.venv`、`node_modules`、`dist`、前端源码或 `.manual_backups` 本身。
- 备份中的 `settings.json` 必须剔除 Secret 字段后再写入 zip；生产 Secret 应保存在后端 `.env` 或服务端配置。
- 下载和恢复备份时必须校验 zip 文件名，禁止 `..`、`/`、`\` 和非 `.zip` 名称。
- 恢复和导入 zip 时必须检查 zip 内每个路径，禁止绝对路径、`..`、不在允许备份范围内的路径和排除目录。
- 恢复或导入前必须自动创建恢复前备份，避免误操作无法回滚。
- 后台恢复页面必须显示明确风险提示：恢复会覆盖当前 `backend/data` 内容，系统会先创建恢复前备份。

## 生产部署安全

- 生产配置应从 `backend/.env.production.example` 复制到服务端环境文件，例如 `/etc/srblogs/backend.env`，不得提交真实 Secret。
- 生产必须修改 `ADMIN_PASSWORD` 和 `JWT_SECRET`，不得使用本地开发默认值。
- `CORS_ORIGINS` 生产环境不得使用 `*`，只能包含可信前台和后台域名。
- `PUBLIC_BASE_URL` 只能配置公开站点 origin，用于 RSS、Sitemap、robots、OpenGraph 和上传 URL；不得配置后台管理地址。
- Nginx 不得直接暴露 `.env`、`.manual_backups`、`audit`、前端源码、`node_modules` 或构建内部目录。
- `GET /api/admin/system/status` 必须要求管理员 JWT，只能返回目录存在性和读写状态，不得返回环境变量内容或 Secret。
- systemd 日志通过 `journalctl` 查看；Nginx access/error log 应保存在系统日志目录，排查时不得粘贴 Secret。

## Pending Queue Scope

状态机固定为：

- `editing`：正在编辑，尚未进入暂存队列。
- `pending`：已加入暂存队列，等待应用。
- `applied`：已成功写入后端数据。
- `failed`：应用失败，保留错误信息，允许重试或移除。

第一阶段本地 `pendingOperations` 只覆盖：

- settings 修改
- 文章新建
- 文章编辑
- 文章删除
- 草稿发布

图片上传、Secret 修改、评论管理暂不进入本地 `pendingOperations`。第一阶段队列在刷新页面后会丢失；第二阶段再做服务端持久化。
# 2026-05-03 安全补充：GitHub 评论与前台入口

- GitHub OAuth 登录入口只能放在前台文章详情评论区；后台设置页只负责配置 Client ID 和 Secret configured 状态，不承担访客登录。
- 未登录用户提交评论必须返回 `401`，不能回退到匿名评论、邮箱评论或前端伪造作者。
- 前台只能读取 `/api/auth/github/me` 的 configured 状态和 GitHub 公开用户信息；OAuth Secret、access token、管理员 JWT 不得进入前端构建产物。
- 留言板只是前台展示名称，后端仍使用既有 comments 存储；不得为了文案变化新增匿名提交旁路。
- 音乐页和首页共享全局播放状态不应保存任何 Secret；歌词文件上传仍按文本类安全限制处理。
