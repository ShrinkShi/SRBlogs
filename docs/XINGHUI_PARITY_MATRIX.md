# XinghuisamaBlogs Parity Matrix

差距等级定义：

- `P0`：核心可用闭环，包括内容读取、内容写入、登录鉴权、设置读取、基础评论、构建运行、安全写文件。
- `P1`：关键体验，包括编辑器预览、草稿、暂存队列、搜索/标签、响应式、后台表单化设置、错误状态。
- `P2`：视觉增强和装饰特效，包括樱花、萤火、弹幕、动态背景细节、悬浮音乐细节、卡片动效和主题装饰。

状态定义：`未开始`、`进行中`、`已完成`、`延期`。只有满足本轮 Definition of Done 后才能标记为 `已完成`。

## Definition of Done

每轮只有全部完成后，才允许在本矩阵或 `HISTORY.md` 中标记为 `已完成`：

- `cd frontend && npm run build` 通过。
- `cd admin && npm run build` 通过。
- 后端启动并访问 `http://127.0.0.1:8000/api/health` 通过。
- 核心页面手动验收完成：首页、文章详情、后台仪表盘、编辑器、设置页。
- 涉及写入时检查 `backend/data` 实际文件变化。
- `HISTORY.md` 已追加本轮记录。
- `docs/XINGHUI_PARITY_MATRIX.md` 已更新完成状态。

## Local Verification Addresses

Windows 本地启动命令：

```powershell
.\start-backend.cmd
.\start-frontend.cmd
.\start-admin.cmd
```

或一次启动三个独立窗口：

```powershell
.\start-all.cmd
```

固定访问地址：

- frontend: `http://127.0.0.1:5173`
- admin: `http://127.0.0.1:5174/admin/`
- backend docs: `http://127.0.0.1:8000/docs`
- health: `http://127.0.0.1:8000/api/health`

前台和后台启动脚本必须使用 `npm.cmd run dev`；固定端口和 `--strictPort` 由各自 `package.json` 的 `dev` 脚本统一管理。端口被占用时脚本输出占用 PID 和 `taskkill /PID <pid> /F` 处理建议，不允许 Vite 静默跳端口。

## Current Round Verification

2026-05-02 安全备份与契约基础轮当前结果：

- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- `http://127.0.0.1:8000/api/health`：通过，返回 `{"ok":true,"app":"SRBlogs API"}`。
- `GET /api/settings/public`：通过，未返回常见 Secret 字段名。
- `GET /api/admin/settings`：通过，未返回 `clientSecret`、`accessKeySecret`、`token` 明文字段。
- `http://127.0.0.1:5173`：端口/页面检查未通过，连接失败。
- `http://127.0.0.1:5174/admin/`：端口/页面检查未通过，连接失败。
- 核心页面手动验收：首页、文章详情、后台仪表盘、编辑器、设置页未完成。
- `backend/data` 写入检查：本轮未执行写入探测，避免为验证改动用户内容。

结论：本轮基础代码和文档已落地，但未满足 Definition of Done，相关矩阵项只能保持 `进行中`。

2026-05-02 内容统计与闭环校验修正当前结果：

- 已修复 `DATA_DIR=backend/data` 在 `backend` 目录启动时解析到 `backend/backend/data` 的问题。
- `GET /api/posts`：2 条，首条 slug 为 `vue-fastapi-blog`。
- `GET /api/posts/{slug}`：可读取文章详情，首条详情 Markdown content 长度 755。
- `GET /api/moments`：2 条。
- `GET /api/chatters`：2 条。
- `GET /api/projects`：3 条。
- `GET /api/photos`：6 条。
- `GET /api/dashboard/stats`：`posts=2`、`moments=2`、`chatters=2`、`photos=6`。
- 浏览器手动验收：前台首页可打开、后台仪表盘可打开、登录可成功、CORS 问题已修复。
- 本轮未新增樱花、弹幕、CyberCat、动态背景等 P2 功能。
- 下一轮进入“文章与评论轮”，优先完成 P0：文章列表、文章详情、评论读写。

2026-05-02 文章与评论轮 P0 闭环当前结果：

- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 后端 `/api/health`：通过。
- 后台新建非草稿文章 `srblogs-p0-20260502130609`：成功。
- `backend/data/posts/srblogs-p0-20260502130609.md`：已真实写入。
- `GET /api/posts`：包含新文章。
- `GET /api/posts/srblogs-p0-20260502130609`：成功，Markdown content 长度 120。
- 非法 slug：返回 400。
- 空标题：返回 400。
- 重复 slug：返回 409。
- `POST /api/comments/posts/srblogs-p0-20260502130609`：成功。
- `GET /api/comments/posts/srblogs-p0-20260502130609`：返回 2 条评论。
- `backend/data/comments/posts-srblogs-p0-20260502130609.json`：已真实写入。
- 评论覆盖写入备份：`.backups` 中匹配备份数为 1。
- 评论 XSS 清洗：脚本和危险图片标签被移除，仅保留文本。
- 已有前台地址 `http://127.0.0.1:5173/posts/srblogs-p0-20260502130609`：返回 200。
- 本轮未新增 P2 装饰功能。
- 结论：P0 内容闭环已通过 API 和最小页面响应验证，但仍缺完整人工回归，矩阵项保持 `进行中`。

2026-05-02 文章详情与评论管理回归推进当前结果：

- 新增后台本地评论管理最小版：`/admin/comments`。
- 新增 `DELETE /api/comments/{resource}/{slug}/{comment_id}`，需要管理员 JWT。
- 删除不存在评论返回 404。
- 删除评论前会备份评论 JSON；备份时间戳已改为微秒级，避免同秒覆盖。
- 删除评论 API 验证通过：临时评论删除后列表回到 2 条，评论文件大小从 574 bytes 变为 365 bytes，备份数从 3 增加到 4。
- 评论 email 可选格式校验通过，非法邮箱返回 400。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 阻塞：当前 shell 环境启动 Vite dev server 报 `spawn EPERM`，因此 390px 移动端、TOC 点击滚动、分享按钮浏览器交互、后台评论管理浏览器交互未完成。
- 结论：评论管理 API 和构建已完成最小闭环，但完整浏览器人工回归未满足 Definition of Done，相关项保持 `进行中`。

2026-05-02 本地开发启动与浏览器回归修复轮当前结果：

- 新增 `start-backend.cmd`、`start-frontend.cmd`、`start-admin.cmd`、`start-all.cmd`。
- 前台 `dev` 脚本固定为 `vite --host 127.0.0.1 --port 5173 --strictPort`。
- 后台 `dev` 脚本固定为 `vite --host 127.0.0.1 --port 5174 --strictPort`。
- 前台和后台启动脚本显式使用 `npm.cmd run dev`，避免直接调用 `npm`；端口参数由 `package.json` 统一管理，避免重复传参。
- 启动脚本会检查 8000、5173、5174 端口占用；被占用时输出 PID 和处理建议，不静默换端口。
- 新增 `docs/MANUAL_QA_CHECKLIST.md`，浏览器人工回归项已落地。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- `GET /api/posts/srblogs-p0-20260502130609`：通过，返回标题 `SRBlogs P0 Content Loop`。
- `GET /api/comments/posts/srblogs-p0-20260502130609`：通过，返回 2 条评论。
- 删除评论 API：通过，临时评论删除成功，删除前备份数从 5 增加到 6。
- 端口探测：本轮探测时 8000、5173、5174 均无监听进程。
- 阻塞：Codex 工具 shell 环境中通过 `Start-Process` 和 `npm.cmd` 启动 Vite 仍报 `spawn EPERM`，完整浏览器人工回归需在普通 Windows 终端或双击脚本环境继续执行。
- 结论：本轮完成启动规避方案和自动化验证记录，但文章详情、评论、Markdown 编辑器、后台评论管理仍未满足浏览器人工回归要求，保持 `进行中`。

2026-05-02 Markdown 预览与评论索引主流程轮当前结果：

- 后台 Markdown 预览继续使用 `marked + DOMPurify`，并补齐 h1/h2/h3、段落、无序列表、有序列表、引用、inline code、代码块、表格、链接、图片样式。
- 新增 Markdown 预览测试样例和“插入预览测试样例”按钮。
- 前台文章 Markdown 样式同步补齐列表符号、有序编号、表格横向滚动和图片自适应，避免保存后前台文章详情同样显示异常。
- 新增 `GET /api/admin/comments/index`，需要管理员 JWT，返回已有评论的 `resource`、`slug`、`count`、`updatedAt`、`title`。
- 后台 `/admin/comments` 默认加载评论索引，不再要求用户先手动输入 slug；手动加载已移动到“高级加载”折叠区。
- 删除评论前有确认；删除成功后刷新评论列表和评论索引；删除失败在 UI 中显示错误。
- `JsonStore` 不再在构造时创建默认 JSON 文件，避免只读评论加载产生空文件。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- `GET /api/admin/comments/index`：通过，原始响应包含 `posts/srblogs-p0-20260502130609`，`count=3`，`title=SRBlogs P0 Content Loop`。
- 临时空 `DATA_DIR` 下评论索引返回 `[]`，不报 500。
- 前台提交临时评论、后台索引刷新、后台删除临时评论、删除前备份验证通过，备份数从 9 增加到 11。
- 删除不存在评论返回 404，非法邮箱返回 400，空昵称/空内容返回 400。
- 构建产物静态搜索未匹配到常见 Secret 字段名。
- 独立 `cmd.exe` 调用 `start-admin.cmd` 仍复现 `spawn EPERM`，5174 未监听；完整浏览器人工回归仍需在用户普通 Windows 终端环境完成。
- 结论：Markdown 预览和后台评论主流程已完成代码级修复与 API 验证，但仍需浏览器人工回归，相关项保持 `进行中`。

## Matrix

| 模块 | 原项目能力 | SRBlogs 当前状态 | 差距等级 | 实现轮次 | 状态 | 验收标准 |
| --- | --- | --- | --- | --- | --- | --- |
| 首页 | 毛玻璃首页、个人资料、最新内容、动态氛围组件 | 已有首页、ProfileCard、站点统计、最新文章/杂谈/动态组件；浏览器可打开，统计数据源已修复为非零 | P1 | 3 视觉首页轮 | 进行中 | 剩余差距：文章/评论 P0 闭环未完成，首页聚合模块仍需跟随真实内容状态做空状态、加载失败和移动端细节验收 |
| 文章列表 | 文章卡片、标签、摘要、封面、列表浏览 | Posts 页面真实读取 `/api/posts`，已补加载、空、错误状态、封面兜底、标签、日期、摘要和详情跳转；公开列表默认不含草稿 | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：需要完成更完整的浏览器人工回归、移动端检查和草稿公开性回归，满足 Definition of Done 后才能完成 |
| 文章详情 | Markdown 详情、代码高亮、评论、分享 | PostDetail 真实读取 `/api/posts/{slug}`，已补加载、404/错误状态、封面兜底、元信息展示、分享和评论挂载；MarkdownRenderer 继续使用 DOMPurify；前台 Markdown 样式已补齐列表编号、项目符号、表格滚动和图片自适应；人工回归项已写入 `docs/MANUAL_QA_CHECKLIST.md` | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：TOC 点击滚动、代码块视觉高亮、分享按钮交互、390px 移动端仍需浏览器人工验收 |
| 动态 | 类朋友圈短内容流和轻量评论 | 已有 Moments 页面和 moments Markdown 数据 | P1 | 6 媒体互动轮 | 未开始 | 动态列表、详情、评论、时间展示和移动端密度达到可用 |
| 杂谈 | 云端杂谈/碎片化文章卡片 | 已有 Chatter、ChatterDetail、LatestChatterCarousel | P1 | 6 媒体互动轮 | 未开始 | 杂谈列表和详情可读写，首页聚合展示正常 |
| 时间线 | 内容按时间汇总展示 | 已有 Timeline 页面 | P1 | 6 媒体互动轮 | 未开始 | 文章、动态、杂谈按时间排序，空数据有提示 |
| 照片墙 | 图片墙、封面、图集浏览 | 已有 Photowall 页面和 photos JSON | P1 | 6 媒体互动轮 | 未开始 | 图片数据可管理，前台瀑布/网格展示稳定，加载失败有兜底 |
| 音乐 | 网易云 ID 配置和悬浮/页面播放器 | 已有 Music 页面、CloudPlayer、FloatingPlayer | P1 | 6 媒体互动轮 | 未开始 | 音乐列表和悬浮播放器不阻塞页面，设置项可控制歌曲 ID |
| 友链 | 友链卡片和头像展示 | 已有 Friends 页面和 friends JSON | P1 | 6 媒体互动轮 | 未开始 | 友链增删改后前台展示一致，外链安全打开 |
| 项目 | 项目展示卡片、标签、状态 | 已有 Projects 页面和 projects JSON | P1 | 6 媒体互动轮 | 未开始 | 项目卡片支持封面、标签、状态和链接 |
| 评论 | Gitalk 风格评论，Issues/OAuth 配置 | 当前为本地 JSON 评论；GET/POST/DELETE 已验证；新增 `GET /api/admin/comments/index`；后台 `/admin/comments` 默认展示有评论的内容索引，点击后查看和删除评论，手动 slug 加载已移入“高级加载”；后端限制长度、拒绝空内容、校验可选邮箱并清洗 XSS；覆盖和删除评论文件会备份；人工回归项已写入 `docs/MANUAL_QA_CHECKLIST.md` | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：隐藏/恢复、审核、分页、Gitalk OAuth 不在本轮范围；后台评论管理浏览器交互和前后台同步人工回归仍需完成，不能标记完成 |
| 后台仪表盘 | 管理入口、统计、发布流程提示 | 已有 Dashboard 和 stats API；浏览器可打开，登录可成功，stats 已返回非零数据；本轮后端内容闭环验证通过 | P1 | 3 视觉首页轮 | 进行中 | 剩余差距：发布流程提示仍需与后台写作/暂存队列真实状态联动，核心页面还需完成完整手动验收记录 |
| Markdown 编辑器 | 沉浸式写作、预览、发布 | 已有 Editor、MarkdownEditor、MarkdownPreview；预览继续使用 `marked + DOMPurify`，并已补齐标题层级、段落、无序/有序列表、引用、inline code、代码块、表格、链接、图片样式；已新增 Markdown 测试样例；后台 API 新建非草稿文章真实写入 `backend/data/posts` 已验证，后台页面已标注当前直接持久化、pendingOperations 未实现 | P0 | 5 后台写作轮 | 进行中 | 剩余差距：仍需从后台浏览器输入测试 Markdown 并确认右侧预览、保存后前台文章详情表现一致；暂存队列仍未实现 |
| 草稿 | 草稿管理和发布 | 已有 Drafts 页面和 draft 字段 | P1 | 5 后台写作轮 | 未开始 | 草稿可创建、保存、发布，发布后前台可见 |
| 暂存队列 | 操作暂存后统一应用 | 尚未实现，计划第一阶段本地 pendingOperations | P1 | 5 后台写作轮 | 未开始 | settings、文章新建/编辑/删除、草稿发布进入本地队列；刷新丢失有明确提示；应用会真实写后端 |
| 图床 | 图床配置、上传、Token 测试 | 已有本地上传接口；OSS 预留 | P0 | 6 媒体互动轮 | 进行中 | 上传限制扩展名、MIME、大小；密钥只在后端配置；上传结果可用于内容 |
| AI 设置 | Gemini/兼容模型配置和后台助手 | 已有 `/api/chat` 后端代理和 ChatAssistant | P1 | 7 设置中心与生产化轮 | 进行中 | AI Key 只从后端环境读取，后台仅显示 configured 布尔值 |
| 评论设置 | GitHub OAuth/Gitalk 配置面板 | settings 中有 gitalkConfig；后台接口已隐藏 Secret 明文 | P1 | 7 设置中心与生产化轮 | 进行中 | Secret 不出现在前台 public settings 和后台响应中，只显示 configured 布尔值 |
| 部署文档 | Windows 启动、Vercel/GitHub 说明 | 已新增 Windows 专用启动脚本 `start-backend.cmd`、`start-frontend.cmd`、`start-admin.cmd`、`start-all.cmd`；`WINDOWS_START.md` 已记录固定地址、strictPort、端口占用 PID 提示；生产部署路线仍待补全 | P0 | 7 设置中心与生产化轮 | 进行中 | 剩余差距：需要补齐 Nginx/Systemd 或等价生产部署路径，并由普通 Windows 终端完成启动脚本人工验收后才能标记完成 |
