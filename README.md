# SRBlogs

SRBlogs 是一个基于 **Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI** 的个人博客系统。当前工程是对标 XinghuisamaBlogs 产品方向的 Vue3/FastAPI 重制版，不复制原项目源码、图片、文案或私有素材。

## 技术栈

- 前台：Vue 3、Vite、TypeScript、Tailwind CSS 3.4
- 后台：Vue 3、Vite、TypeScript、Tailwind CSS 3.4
- 后端：FastAPI、JWT、Markdown Front Matter、JSON 文件存储
- 数据：`backend/data` 中的 Markdown、JSON、评论、上传文件和备份

## 项目结构

```text
SRBlogs/
├── frontend/               # 读者端博客 SPA
├── admin/                  # 后台管理 SPA
├── backend/                # FastAPI 后端
│   ├── app/                # API、服务和配置
│   └── data/               # Markdown、JSON、评论、上传和备份
├── docs/                   # 契约、安全、验收、部署和发布文档
├── start-backend.cmd       # Windows 后端启动
├── start-frontend.cmd      # Windows 前台启动
├── start-admin.cmd         # Windows 后台启动
├── start-all.cmd           # Windows 三端启动
└── WINDOWS_START.md
```

## Windows 本地启动

推荐直接运行：

```powershell
.\start-all.cmd
```

固定访问地址：

- 前台：`http://127.0.0.1:5173`
- 后台：`http://127.0.0.1:5174/admin/`
- 后端文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

也可以分别启动：

```powershell
.\start-backend.cmd
.\start-frontend.cmd
.\start-admin.cmd
```

前台和后台脚本固定端口并使用 `--strictPort`。如果端口被占用，脚本会输出占用 PID 和 `taskkill` 处理建议。

## 手动启动

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

前台：

```powershell
cd frontend
npm install
npm run dev
```

后台：

```powershell
cd admin
npm install
npm run dev
```

`npm run dev` 是常驻开发服务，不会自然退出。

## 默认后台账号

```text
用户名：admin
密码：change-me
```

默认账号仅用于本地开发。生产前必须修改 `backend/.env` 中的 `ADMIN_PASSWORD` 和 `JWT_SECRET`。

## API 文档

启动后端后访问：

```text
http://127.0.0.1:8000/docs
```

详细接口契约见 [docs/API_CONTRACT.md](docs/API_CONTRACT.md)。

## 后台主要路由

- `/admin/`：仪表盘
- `/admin/editor`：Markdown 写作
- `/admin/posts`、`/admin/drafts`：文章与草稿
- `/admin/comments`：本地评论管理
- `/admin/audit`：后台操作审计日志
- `/admin/backups`：数据备份、下载、恢复、导入导出
- `/admin/friends`、`/admin/projects`、`/admin/music`、`/admin/photos`：结构化内容管理
- `/admin/settings`：设置中心

## 前台主要路由

- `/`：首页
- `/posts`、`/posts/:slug`：文章列表和详情
- `/search`：全站搜索
- `/tags`、`/tags/:tag`：标签索引和标签内容
- `/archive`：内容归档
- `/moments`、`/moments/:slug`：动态
- `/chatters`、`/chatters/:slug`：杂谈
- `/friends`、`/projects`、`/music`、`/photowall`：结构化内容
- `/about`、`/timeline`：关于和视觉时间线

## SEO 与订阅

公开接口：

- RSS：`http://127.0.0.1:8000/api/rss.xml`
- Sitemap：`http://127.0.0.1:8000/api/sitemap.xml`
- Robots：`http://127.0.0.1:8000/robots.txt`

前台文章列表和关于页提供 RSS 入口。生产环境请在后端 `.env` 设置 `PUBLIC_BASE_URL`，用于 RSS、Sitemap、robots 和上传 URL。

## 性能与可访问性

- 前台图片统一通过安全图片组件处理懒加载、`alt` 和加载失败兜底。
- 主要列表、搜索、归档等页面有加载、空状态和错误状态，API 失败时不应白屏。
- Markdown 代码块和表格允许自身横向滚动，避免撑宽整页。
- 后台侧栏在窄屏下可滚动，写作、设置、评论管理等页面需保持可操作。
- 当前 MarkdownRenderer 和 MarkdownEditor 构建 chunk 偏大，但分别位于文章详情和编辑器懒加载路径；发布前仍需关注体积和首屏体验。

## 数据目录

`backend/data` 是当前文件存储根目录：

- `posts/*.md`：文章
- `moments/*.md`：动态
- `chatters/*.md`：杂谈
- `comments/*.json`：评论
- `friends.json`、`projects.json`、`music.json`：结构化内容
- `photos/photos.json`：照片墙数据
- `uploads/`：本地上传文件
- `.backups/`：覆盖写入或删除前的备份
- `audit/audit.log`：后台操作审计日志
- `.manual_backups/*.zip`：后台手动备份、导出和恢复前备份

所有 JSON/Markdown 写入必须通过后端安全写入封装，禁止业务路由直接 `open(..., "w")` 写文件。
手动备份不包含 `.env`、前端源码、`node_modules`、`dist` 或 `.manual_backups` 本身；`settings.json` 写入备份前会剔除 Secret 字段。

## 构建

```powershell
cd frontend
npm run build
```

```powershell
cd admin
npm run build
```

```powershell
python -m compileall backend\app
```

构建产物：

- `frontend/dist`
- `admin/dist`

## 部署

服务器部署说明见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)，包含：

- FastAPI 启动
- 前台/后台 build
- Nginx 反向代理示例
- systemd 服务示例
- `backend/data` 权限
- 生产 `.env`
- HTTPS 和生产前检查

## 常见问题

### Tailwind v3/v4 问题

本项目当前固定使用 Tailwind CSS `3.4.17`。不要直接升级到 Tailwind v4，否则现有配置和样式入口可能不兼容。

### `pydantic_core` 安装损坏

重新创建后端虚拟环境：

```powershell
cd backend
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Vite 端口跳转和 CORS

前台固定 `5173`，后台固定 `5174`，并启用 `--strictPort`。如果端口被占用，先释放端口，不要让 Vite 自动跳端口，否则可能触发 CORS 或回调地址不一致。

### `npm run dev` 一直不退出

这是正常行为。Vite dev server 是常驻进程。需要停止时在对应终端按 `Ctrl+C`。

### 8000 端口占用或权限问题

检查占用：

```powershell
netstat -ano | findstr :8000
```

确认进程可以停止后再执行：

```powershell
taskkill /PID <PID> /F
```

## 当前交付状态

- 友链、项目、音乐、照片墙已通过人工验收并在矩阵中标记为 `已完成`。
- 设置中心与生产化已有基础实现，但空 Secret 保留、评论开关、图床设置/上传、AI 设置、部署文档实操核验仍按用户决定标记为延期/未验收。
- 发布前总检查见 [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)。
