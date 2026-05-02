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
- [ ] 未登录或登录过期时跳转登录页。
- [ ] API 失败时页面显示 UI 错误，不只写 console。
- [ ] 删除类操作都有确认。
- [ ] 高级 JSON 编辑不作为默认主流程。

## 4. 内容写入检查

- [ ] 后台新建非草稿文章后，`backend/data/posts` 产生文件。
- [ ] 前台文章列表出现新文章。
- [ ] 前台文章详情可打开新文章。
- [ ] 后台新建草稿后，前台公开文章列表不显示。
- [ ] 草稿发布后，前台公开文章列表显示。
- [ ] 删除文章前生成备份，删除后前台详情显示 404/错误状态。

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

## 9. 构建检查

- [ ] `cd frontend && npm run build` 通过。
- [ ] `cd admin && npm run build` 通过。
- [ ] `python -m compileall backend\app` 通过。
- [ ] `frontend/dist` 已生成。
- [ ] `admin/dist` 已生成。

## 10. 部署前检查

- [ ] `ADMIN_PASSWORD` 已修改。
- [ ] `JWT_SECRET` 已修改。
- [ ] `CORS_ORIGINS` 已收紧。
- [ ] DEBUG/开发端口不暴露。
- [ ] HTTPS 已配置。
- [ ] `backend/data` 已备份。
- [ ] `backend/data` 权限只给后端进程所需读写权限。
- [ ] 上传大小限制有效。

## 11. 已知延期项

- [ ] 空 Secret 不覆盖旧值的浏览器人工验收：用户决定跳过本轮，不标记完成。
- [ ] 评论开关浏览器人工验收：用户决定跳过本轮，不标记完成。
- [ ] 图床设置与上传流程完整人工验收：用户决定跳过本轮，不标记完成。
- [ ] AI 设置真实联调：用户决定跳过本轮，不标记完成。
- [ ] 部署文档完整服务器实操核验：用户决定跳过本轮，不标记完成。
