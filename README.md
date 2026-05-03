# SRBlogs

> 当前进度：P0 100%，P1 约 99%，P2 约 88%。本轮补修顶层 Toast、前台 GitHub 评论入口、后台 GitHub-only 评论设置、相册组编辑、紧凑首页音乐播放器、歌词高度和名片 hover/tooltip。

SRBlogs 是一个基于 **Vue 3 + Vite + TypeScript + Tailwind CSS + FastAPI** 的个人博客系统。当前工程是对标 XinghuisamaBlogs 产品方向的 Vue3/FastAPI 重制版，不复制原项目源码、图片、文案或私有素材。

## 技术栈

- 前台：Vue 3、Vite、TypeScript、Tailwind CSS 3.4
- 后台：Vue 3、Vite、TypeScript、Tailwind CSS 3.4
- 后端：FastAPI、JWT、Markdown Front Matter、JSON 文件存储
- 数据：`backend/data` 中的 Markdown、JSON、评论、上传文件和备份

## 视觉与交互

- 前台采用统一毛玻璃 token、卡片 hover、标签、按钮和阅读排版样式，规则见 [docs/UI_STYLE_GUIDE.md](docs/UI_STYLE_GUIDE.md)。
- 背景控制包含主题、背景、弹幕和“氛围”开关；关闭氛围后会停用樱花、萤火、CyberCat 和点击光效等装饰动效。
- 首页第二阶段结构包含铺满式顶栏、名片 + 音乐播放器、歌词/播放状态区、最新文章、最新更新内容、昼夜模式卡片和底部状态区。
- 设置中心支持公开主题 token、字体族和字号档位配置；前台昼夜模式通过 CSS 变量应用。
- 评论采用 GitHub 登录后评论；OAuth Secret 只在后端配置，前端只读取登录状态和 GitHub 公开用户信息。
- 音乐播放状态提升到全局，首页和 `/music` 页面共享播放进度；音乐管理支持歌词 URL / `.lrc` / `.txt`。
- 照片墙支持相册组，每组最多 50 张照片，旧单图数据仍兼容展示。
- P0/P1 功能已收口，P2 视觉增强仍按验收清单逐轮推进，不引入大型动画库、不做 3D/Three.js。

## 项目结构

```text
SRBlogs/
├── frontend/               # 读者端博客 SPA
├── admin/                  # 后台管理 SPA
├── backend/                # FastAPI 后端
│   ├── app/                # API、服务和配置
│   └── data/               # Markdown、JSON、评论、上传和备份
├── deploy/                 # Linux 部署脚本、Nginx、systemd 和健康检查
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

默认账号仅用于本地开发。生产前必须基于 `backend/.env.production.example` 配置服务端环境文件，并修改 `ADMIN_PASSWORD` 和 `JWT_SECRET`。

## API 文档

启动后端后访问：

```text
http://127.0.0.1:8000/docs
```

详细接口契约见 [docs/API_CONTRACT.md](docs/API_CONTRACT.md)。

日常使用步骤见 [docs/USER_GUIDE.md](docs/USER_GUIDE.md)，包含登录后台、写文章、草稿发布、评论管理、媒体管理、站点设置、备份恢复、审计日志和前台搜索/标签/归档使用说明。

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

仓库中的示例数据用于本地演示和回归验证，包含公开文章、草稿、动态、杂谈、友链、项目、音乐、照片和 about 内容。运行时生成的手动备份、审计日志、上传缓存和 `.backups` 文件不应作为发布代码提交。

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

生产发布候选参考文件：

- `backend/.env.production.example`：生产环境变量模板，不包含真实 Secret。
- `deploy/build-all.sh`：构建前台、后台并检查后端语法。
- `deploy/start-backend.sh`：Linux 后端启动脚本。
- `deploy/srblogs-backend.service`：systemd 示例。
- `deploy/nginx.srblogs.conf`：Nginx 示例。
- `deploy/healthcheck.sh`：生产健康检查脚本。
- [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md)：生产发布清单。
- [CHANGELOG.md](CHANGELOG.md) 与 [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md)：发布说明。

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
- 审计日志与备份恢复已通过人工验收并可在矩阵中标记为 `已完成`。
- 后台写作、草稿、发布/撤回、删除文章和 pendingOperations 第一阶段已通过人工验收并在矩阵中标记为 `已完成`。
- 设置中心剩余项已完成验收：空 Secret 保留、评论开关、图床 local 上传、AI 设置边界和部署文档核验均已通过；真实 OSS/Gitalk/AI 联调仍不属于当前 P0/P1 收口范围。
- 最终总回归已完成 API/HTTP 快速验证：完整内容生产演示流、评论前后台同步、审计日志、手动备份、下载备份、恢复前备份、RSS/Sitemap/robots、Secret 扫描均通过。
- 当前进度估算：P0 100%，P1 100%，P2 约 74%；P2 已进入首页结构追平与昼夜主题系统阶段，仍需按人工验收清单继续确认。
- 真实服务器、域名和 HTTPS 部署实操仍标记为 `部署实操待执行`；当前仓库提供的是上线准备脚本、Nginx/systemd 示例、环境变量模板和部署检查清单。
- 发布前总检查见 [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)。
# SRBlogs 当前补充

> 当前进度：P0 100%，P1 约 98%，P2 约 90%。本轮补修前台 GitHub 评论入口、文章/杂谈三列图片列表、音乐页左播放器右歌词/歌单布局、首页播放器紧凑化和非首页标题居中；真实 GitHub OAuth 回跳仍需配置后人工验收。

> 最新补充：前台评论区统一命名为“留言板”，GitHub 未配置提示改为访客视角；文章页新增“矩阵网格 / 中枢链路”双模式；顶部导航移除归档入口但 `/archive` 保留；搜索栏和播放器图标按钮进一步轻量化。
