# Release Checklist

本清单用于全站回归与交付整理。没有完成浏览器人工验收的模块，不得在 `docs/XINGHUI_PARITY_MATRIX.md` 标记为 `已完成`。

## 1. 本地启动检查

- [ ] `start-backend.cmd` 使用相对路径启动后端。
- [ ] `start-frontend.cmd` 使用 `npm.cmd run dev`，固定 `5173`，启用 `--strictPort`。
- [ ] `start-admin.cmd` 使用 `npm.cmd run dev`，固定 `5174`，启用 `--strictPort`。
- [ ] `start-all.cmd` 分别打开后端、前台、后台窗口。
- [ ] 端口占用时脚本输出 PID 和 `taskkill /PID <PID> /F` 建议。
- [ ] `http://127.0.0.1:8000/api/health` 返回正常。
- [ ] `http://127.0.0.1:5173` 可打开。
- [ ] `http://127.0.0.1:5174/admin/` 可打开。

## 2. 前台页面检查

- [ ] `/` 不白屏，首页左右边距和最新文章换行正常。
- [ ] `/posts` 有加载、空、错误状态，草稿默认不显示。
- [ ] `/posts/:slug` 可打开真实文章，不存在 slug 显示错误状态。
- [ ] `/search` 可打开，关键词、类型和标签筛选可用。
- [ ] `/tags` 可打开并显示标签数量。
- [ ] `/tags/:tag` 可打开；不存在标签显示空状态。
- [ ] `/archive` 可打开并按年月展示 posts/moments/chatters。
- [ ] `/moments` 有加载、空、错误状态。
- [ ] `/chatters` 有加载、空、错误状态。
- [ ] `/chatters/:slug` 可打开真实杂谈，不存在 slug 显示错误状态。
- [ ] `/friends`、`/projects`、`/music`、`/photowall` 不白屏。
- [ ] `/about` 可展示 `about.md`，加载失败有 UI 错误。
- [ ] `/timeline` 有加载、空、错误状态。
- [ ] 不存在路由显示 404 页面。
- [ ] 390px 宽度无严重横向溢出，sticky 导航不遮挡正文。

## 3. 后台页面检查

- [ ] `/admin/` 仪表盘可进入。
- [ ] `/admin/editor` 可进入写作页。
- [ ] `/admin/posts` 可进入文章管理。
- [ ] `/admin/comments` 可进入评论管理。
- [ ] `/admin/friends`、`/admin/projects`、`/admin/music`、`/admin/photos` 可进入表单化管理页。
- [ ] `/admin/settings` 可进入设置中心。
- [ ] `/admin/audit` 可进入审计日志页面。
- [ ] `/admin/backups` 可进入备份恢复页面。
- [ ] 未登录或登录过期时跳转登录页。
- [ ] API 失败时页面显示 UI 错误，不只写 console。
- [ ] 删除类操作都有确认。
- [ ] 高级 JSON 编辑不作为默认主流程。

## 3.1 审计日志与备份恢复检查
- [ ] 登录成功/失败、文章写入、评论删除、settings 修改、结构化内容保存、上传、手动备份、恢复、导入、导出有审计记录。
- [ ] `GET /api/admin/audit/logs` 需要 JWT，并支持 limit、offset、action、resource、q。
- [ ] 审计日志不包含 Secret 明文。
- [ ] `POST /api/admin/backups` 可创建手动备份。
- [ ] `GET /api/admin/backups` 可列出备份。
- [ ] `GET /api/admin/backups/{name}/download` 可下载备份且需要 JWT。
- [ ] `POST /api/admin/backups/{name}/restore` 恢复前自动创建 `pre-restore-*.zip`。
- [ ] 备份 zip 不包含 `.env`、`.venv`、`node_modules`、`dist`、前端源码或 `.manual_backups`。
- [ ] 备份 zip 中 `settings.json` 不包含 Secret 明文字段。
- [ ] 下载/恢复路径穿越名称返回 400 或 404，不读取任意文件。
- [ ] 导出数据 zip 可下载，导入 zip 前会自动备份当前数据。

## 4. 内容写入检查

- [ ] 后台新建非草稿文章后，`backend/data/posts` 产生文件。
- [ ] 前台文章列表出现新文章。
- [ ] 前台文章详情可打开新文章。
- [ ] 后台新建草稿后，前台公开文章列表不显示。
- [ ] 草稿发布后，前台公开文章列表显示。
- [ ] 已发布文章撤回为草稿后，前台列表不显示，公开详情返回 404 或错误状态。
- [ ] 未登录传 `include_drafts=true` 返回 401。
- [ ] 重复 slug 返回 409，非法 slug 返回 400，更新/删除不存在文章返回 404。
- [ ] 删除文章前生成备份，删除后前台详情显示 404/错误状态。
- [ ] 文章创建、编辑、发布、撤回发布、删除均有审计日志。
- [ ] 文章新建、编辑、删除、草稿发布和非 Secret 设置修改可进入本地 pendingOperations 并应用。

## 5. 评论检查

- [ ] 前台评论 GET/POST 正常。
- [ ] 空昵称、空内容、非法邮箱被拒绝并显示 UI 错误。
- [ ] XSS 内容不会危险渲染。
- [ ] 后台评论索引默认显示有评论内容。
- [ ] 后台删除评论前生成备份。
- [ ] 删除后前台刷新评论消失。

## 6. 媒体管理检查

- [ ] 友链可新增、编辑、删除，前台同步。
- [ ] 项目可新增、编辑、删除，前台同步。
- [ ] 音乐可新增、编辑、删除，前台播放器读取歌单。
- [ ] 照片可新增、编辑、删除，前台照片墙同步。
- [ ] 上传图片后 URL 可填入照片记录。
- [ ] 每次覆盖写入前 `.backups` 有备份。

## 7. 设置中心检查

- [ ] 站点公开信息保存后，前台首页同步。
- [ ] 主题与背景保存后，前台读取正常。
- [ ] 评论开关关闭后，文章详情显示“评论已关闭”且不显示提交框。
- [ ] 图床配置可保存，Secret 不回显。
- [ ] AI 配置可保存，API Key 不回显。
- [ ] Secret 输入留空时不覆盖旧值。
- [ ] 高级 JSON 只作为折叠兜底，JSON 非对象时阻止保存。

## 8. Secret 检查

- [ ] `GET /api/settings/public` 不包含 Secret。
- [ ] `GET /api/admin/settings` 不回显 Secret 明文。
- [ ] `frontend/dist` 不包含默认密码、JWT Secret、AI Key、OSS Key、GitHub OAuth Secret 或真实 Secret 值。
- [ ] `admin/dist` 不包含默认密码、JWT Secret、AI Key、OSS Key、GitHub OAuth Secret 或真实 Secret 值。
- [ ] 生产 `.env` 不提交到 Git。

## 8.1 SEO 与订阅检查

- [ ] `GET /api/rss.xml` 返回 RSS 2.0 XML。
- [ ] `GET /api/sitemap.xml` 返回 XML sitemap。
- [ ] `GET /robots.txt` 包含 `Disallow: /admin`。
- [ ] RSS 和 sitemap 不包含草稿。
- [ ] 文章详情动态 title/meta/og 随文章变化。
- [ ] 前台 RSS 入口可见。
- [ ] 文章详情复制链接可用。

## 8.2 性能与可访问性检查
- [ ] 前台主要页面图片具备懒加载、alt 和失败兜底。
- [ ] 前台主要页面 API 失败时显示可读错误，不白屏。
- [ ] 390px 下首页、文章详情、搜索、标签、归档、照片墙无严重横向溢出。
- [ ] 390px 下后台写作、设置、评论管理可滚动操作，侧栏不遮挡主内容。
- [ ] 照片墙预览可通过关闭按钮和 Esc 关闭。
- [ ] 评论表单、搜索框、后台登录和写作表单可通过键盘聚焦。
- [ ] 保存/提交中按钮禁用，避免重复提交。
- [ ] 构建体积已检查，Markdown 相关大 chunk 已记录且不影响首屏主包。

## 9. 构建检查

- [ ] `cd frontend && npm run build` 通过。
- [ ] `cd admin && npm run build` 通过。
- [ ] `python -m compileall backend\app` 通过。
- [ ] `frontend/dist` 已生成。
- [ ] `admin/dist` 已生成。

## 10. 部署前检查

- [ ] `backend/.env.production.example` 已复制到服务端环境文件，例如 `/etc/srblogs/backend.env`。
- [ ] `ADMIN_PASSWORD` 已修改。
- [ ] `JWT_SECRET` 已修改。
- [ ] `CORS_ORIGINS` 已收紧。
- [ ] DEBUG/开发端口不暴露。
- [ ] Secret 不在构建产物中。
- [ ] HTTPS 已配置。
- [ ] `backend/data` 已备份。
- [ ] `backend/data` 权限只给后端进程所需读写权限。
- [ ] 上传大小限制有效。
- [ ] `deploy/nginx.srblogs.conf` 已按域名调整，并通过 `nginx -t`。
- [ ] `deploy/srblogs-backend.service` 已按部署路径调整，并通过 `systemctl status`。
- [ ] `deploy/healthcheck.sh` 检查后端、前台、后台、RSS、Sitemap、robots。
- [ ] `docs/PRODUCTION_CHECKLIST.md` 已逐项核对。

## 11. 已知延期项

- [ ] 真实服务器、域名和 HTTPS 部署实操：当前仓库已完成部署脚本、Nginx/systemd/env 模板和文档核验，但未在真实服务器执行，应保持 `部署实操待执行`。
- [ ] 真实 OSS 深度联调：当前已完成 local 上传和配置边界，不做云厂商实连。
- [ ] 真实 Gitalk/GitHub OAuth：当前保留配置占位和 Secret 边界，不接入 OAuth。
- [ ] 真实 AI 提供商联调：当前完成配置保存、Key 不回显和开关边界，不调用真实模型。
- [ ] P2 视觉增强：继续冻结，不新增樱花、弹幕、CyberCat、动态背景等功能。

## 12. 最终总回归记录项

- [ ] 完整内容生产演示流：草稿、发布、详情、评论、后台评论删除、编辑、撤回发布、删除文章。
- [ ] 审计日志包含文章 create/publish/update/unpublish/delete 和 comment create/delete。
- [ ] 手动备份创建、列表、下载、恢复和恢复前备份均通过。
- [ ] 备份 zip 不包含 `.env`，构建产物不包含服务端 Secret 值。
- [ ] 前台和后台主路径均完成快速回归，不白屏。
