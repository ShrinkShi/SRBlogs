# XinghuisamaBlogs Parity Matrix

差距等级定义：

- `P0`：核心可用闭环，包括内容读取、内容写入、登录鉴权、设置读取、基础评论、构建运行、安全写文件。
- `P1`：关键体验，包括编辑器预览、草稿、暂存队列、搜索/标签、响应式、后台表单化设置、错误状态。
- `P2`：视觉增强和装饰特效，包括樱花、萤火、弹幕、动态背景细节、悬浮音乐细节、卡片动效和主题装饰。

状态定义：`未开始`、`进行中`、`已完成`、`延期/未验收`。只有满足本轮 Definition of Done 后才能标记为 `已完成`。

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

2026-05-02 评论索引 API 路由确认与同步复测轮当前结果：

- 人工验收发现当前 `127.0.0.1:8000` 返回 `/api/admin/comments/index` 404。
- 复查代码确认 `backend/app/api/comments.py` 已定义 `GET /api/admin/comments/index`，`backend/app/main.py` 已注册 `comments_admin_router`。
- 当前 8000 进程的 `/openapi.json` 不包含 `/api/admin/comments/index`，说明浏览器连接的是旧代码进程或未重载进程。
- 用当前工作区代码临时启动后端后，`/docs` 返回 200，`/openapi.json` 包含 `/api/admin/comments/index`。
- 临时后端未登录访问 `/api/admin/comments/index` 返回 401，登录后返回 200。
- 登录后索引响应包含 `posts/post-1777703928848`，能从 `posts-post-1777703928848.json` 反推 `resource=posts`、`slug=post-1777703928848`。
- 前台 API 提交评论到 `posts/post-1777703928848` 后能通过 `GET /api/comments/posts/post-1777703928848` 读到；后台 DELETE 删除后再次 GET 该评论消失。
- 删除评论前备份验证通过，`posts-post-1777703928848` 匹配备份数从 1 增加到 3。
- 空昵称、空内容、非法邮箱均返回 400；删除不存在评论返回 404；XSS 评论内容保存为清洗后的文本。
- 当前环境对旧 8000 监听进程 PID 2560 的查询/终止受限，未继续强制处理用户进程。需要用户在普通终端关闭旧后端并重新运行 `start-backend.cmd`。
- 结论：代码与临时后端验证已通过，但用户 8000 实际后端需重启后才能完成浏览器回归；评论模块继续保持 `进行中`。

2026-05-02 首页响应式溢出修复轮当前结果：

- 主内容容器和顶部导航统一使用 `.sr-page-shell`，宽度为 `min(calc(100% - 2rem), 80rem)`。
- 首页 Hero + ProfileCard 双列从 `lg` 推迟到 `xl`，1024px 附近默认单列，减少右栏裁切风险。
- 首页 grid 子项补充 `min-w-0`、`minmax(0, ...)` 和文本换行。
- ProfileCard 在 420px 以下统计项改为单列，避免小屏挤压。
- SiteDashboard 统计块改为 `sm` 三列、`lg` 五列，窄屏自动换行。
- 顶部导航桌面链接从 `lg` 起展示，`lg` 以下使用菜单，避免中等宽度导航溢出。
- 主题/背景/弹幕 fixed 控件在中等宽度下移到底部左侧横排，`xl` 以上恢复右侧竖排。
- FloatingPlayer 弹出面板宽度限制为 `min(290px, calc(100vw - 2rem))`。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- 已尝试 Edge headless + DevTools Protocol 自动尺寸采样，但当前工具环境未能稳定建立调试连接；需用户继续在普通浏览器中人工验收 1440px、1280px、1024px、390px。
- 结论：首页响应式代码修复已落地，但未完成用户人工验收，首页继续保持 `进行中`。

2026-05-02 首页组件裁切二次修复轮当前结果：

- 人工验收确认上一轮仍存在 ProfileCard 和 SiteDashboard 被裁切，不能视为完成。
- 已移除 `Home.vue` 根容器的 `overflow-hidden`，避免父级直接裁掉内容。
- Hero + ProfileCard 改为 `.home-hero-grid`，默认使用 `auto-fit + minmax(min(100%, 24rem), 1fr)`，1280px 以上才并排为主列 + ProfileCard 列。
- ProfileCard 统计区改为 auto-fit 响应式网格，卡片和内部内容都限制在 `max-width: 100%` 内。
- SiteDashboard 统计区改为 `.home-stats-grid`，所有统计卡片参与自动换行，不隐藏“照片”卡片。
- 移除 `#app` 的 `overflow-x: clip`，全局横向隐藏只保留为兜底，主要修复依赖响应式网格和 `min-w-0/max-width`。
- BackgroundSlider 在 `xl` 以上定位到主内容外侧安全区域，中等宽度继续底部左侧，减少遮挡 ProfileCard。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- 已尝试 Edge headless 截图验证，但当前工具环境因 Crashpad/Mojo 权限错误未能生成截图；仍需用户浏览器人工验收。
- 结论：首页继续保持 `进行中`，无横向滚动条但组件被裁切明确视为不通过。

2026-05-02 首页左右边距统一修复轮当前结果：

- `.sr-page-shell` 主容器宽度调整为 `min(calc(100% - 3rem), 80rem)`，常规视口左右保留约 24px；480px 以下左右保留约 12px。
- Hero + ProfileCard 双列断点从 1280px 调整到 1360px，1280px 下不再为了并排牺牲右侧边距。
- 顶部导航、首页 Hero/ProfileCard、SiteDashboard、LatestPosts 均继续处于同一 `.sr-page-shell` 主容器内。
- 主题/背景/弹幕 fixed 控件只在 `2xl` 以上回到右侧竖排，中等宽度保留底部左侧，避免干扰主内容右边距。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- 结论：首页左右边距修复已落地，但需用户人工确认 1440px、1280px、1024px、390px 视觉居中；首页保持 `进行中`。

2026-05-02 首页最新文章列表撑宽修复轮当前结果：

- 人工判断首页右边距异常可能由“最新文章”横向列表撑宽页面导致。
- `LatestPostsCarousel.vue` 已从横向滚动 `flex + overflow-x-auto + min-w-[280/360px]` 改为 `grid-cols-1 md:grid-cols-2 xl:grid-cols-3` 响应式网格。
- 最新文章卡片移除固定 `min-width`，改用 `min-w-0`，4 篇文章应在 xl 三列布局下换到第二行第一列。
- `LatestChatterCarousel.vue` 同步补 `min-w-0/max-w-full`，并改为 `grid-cols-1 md:grid-cols-2 xl:grid-cols-3`，避免中等宽度撑宽。
- `MomentTimeline.vue` 补 `min-w-0/max-w-full`。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- 结论：首页内容列表撑宽风险已修复，但需用户确认 4 篇文章换行和整体左右边距恢复正常；首页保持 `进行中`。

2026-05-02 后台写作闭环 / 草稿 / 暂存队列第一阶段当前结果：

- `/admin/posts` 已补齐文章列表字段、全部/已发布/草稿筛选、编辑、删除、前台预览和暂存删除入口。
- 写作页保留“保存”直接持久化，并新增“加入暂存”“立即发布”“发布加入暂存”；空标题、空 slug、非法 slug、保存成功和保存失败均有 UI 文案入口。
- 草稿页可列出 `draft=true` 文章，支持继续编辑、立即发布和发布暂存。
- 新增本地 `pendingOperations` 队列，支持文章新建、文章编辑、文章删除、草稿发布；状态为 `editing`、`pending`、`applied`、`failed`；刷新页面会丢失，并已在 UI 中提示。
- 自动化验证已通过：新建草稿真实写入 `backend/data/posts`；公开列表默认隐藏草稿；发布后公开列表可见且详情可读；编辑可写入；删除后详情返回 404 且删除前备份数增加。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- 临时后端 `/api/health`：通过。
- 结论：后台写作 P0 链路代码和 API 验证已推进，但仍需浏览器人工验收暂存区交互、错误提示和列表筛选；相关模块保持 `进行中`。

2026-05-02 媒体与结构化内容管理轮当前结果：

- 新增 `StructuredJsonManager` 通用后台管理组件，friends/projects/music/photos 均以表单化管理作为主流程，并保留高级 JSON 折叠编辑作为兜底。
- 友链管理支持名称、URL、描述、头像/图标 URL、标签；项目管理支持名称、描述、技术栈、项目链接、仓库链接、封面 URL、状态；音乐管理支持标题、艺术家、封面 URL、歌曲 URL、云音乐 ID、排序；照片管理支持图片 URL、标题、描述、日期、标签和上传填 URL。
- 前台 Friends/Projects/Music/Photowall 均补齐加载状态、空状态、错误状态和动态读取展示；项目/友链外链新标签打开；照片墙支持懒加载和点击预览；CloudPlayer 在歌曲存在 URL 时支持原生 audio 播放/暂停。
- API 级验证通过：friends/projects/music/photos 均完成新增、编辑、删除、重新读取确认；对应 JSON 覆盖写入前 `.backups` 备份数增加；上传接口返回 URL 且测试上传文件已清理。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- `http://127.0.0.1:8000/api/health`：通过。
- 结论：媒体结构化内容的代码和 API 闭环已完成，但仍需用户浏览器人工验收四个后台表单页和四个前台页面，相关模块保持 `进行中`。

2026-05-02 设置中心与生产化轮当前结果：

- `/admin/settings` 已拆分为站点公开信息、主题与背景、评论设置、图床设置、AI 设置、部署与安全提示六个分区。
- 后台 settings 表单支持加载状态、保存中状态、保存成功和保存失败提示；高级 JSON 作为折叠兜底。
- `GET /api/settings/public` 调整为只返回公开站点字段和公开评论显示选项：`siteTitle`、`subtitle`、`author`、`avatar`、`description`、`socialLinks`、`theme`、`bgImages`、`cloudMusicIds`、`comments`。
- `GET /api/admin/settings` 继续要求 JWT，Secret 不回显明文，只返回 configured 布尔值。
- `PUT /api/admin/settings` 已完成代码与 API 级验证：空 Secret 不覆盖旧值；浏览器人工验收由用户决定跳过，记录为未验收。
- 前台评论区会读取公开评论设置；关闭评论后显示“评论已关闭”并隐藏提交框，重新开启后恢复表单；浏览器人工验收由用户决定跳过，记录为未验收。
- 新增 `docs/DEPLOYMENT.md`，补充后端 FastAPI、前端/后台 build、Nginx、systemd、backend/data 权限、生产 `.env`、HTTPS 和生产前检查。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- TestClient `/api/health`：通过；当前 `127.0.0.1:8000` 未监听，因此固定端口 health 需用户启动后复测。
- 构建产物 Secret 搜索通过。
- 结论：设置中心与生产化代码和 API 验证已推进；空 Secret 不覆盖旧值、评论开关、图床设置与上传流程、AI 设置、部署文档完整实操核验均为用户主动跳过的延期/未验收项，不得标记为已完成。

2026-05-02 内容发现与归档扩张轮当前结果：

- 新增 `GET /api/search`，支持 `q`、`type`、`tag`、`limit`、`offset`，覆盖 posts/moments/chatters/projects/photos/friends/music；公开结果排除 draft。
- 新增 `GET /api/tags`，合并 posts/moments/chatters/projects 标签。
- 新增 `GET /api/archive`，按年月聚合 posts/moments/chatters。
- 前台新增 `/search`、`/tags`、`/tags/:tag`、`/archive`；首页新增轻量内容发现入口。
- `cd frontend && npm run build`、`cd admin && npm run build`、`python -m compileall backend\app`：通过。
- API 验证：`/api/search?q=vue`、`/api/search?q=vue&type=posts`、`/api/search?tag=Vue`、`/api/tags`、`/api/archive` 均返回 200。
- 结论：内容发现与归档扩张轮已通过用户人工验收，搜索、标签、归档相关项可标记为 `已完成`。

2026-05-02 SEO、订阅与分享增强轮当前结果：

- 新增前台 `useSeo` 工具，统一设置 title、description、OpenGraph 和 Twitter Card。
- 主要前台页面已接入动态 meta；文章详情会使用文章标题、摘要和封面，错误状态显示 404/内容不存在。
- 新增 `GET /api/rss.xml`、`GET /api/sitemap.xml` 和 `GET /robots.txt`，均为公开接口，不需要 JWT。
- 文章列表和关于页新增 RSS 入口；文章详情分享复制链接增加失败提示。
- `cd frontend && npm run build`、`cd admin && npm run build`、`python -m compileall backend\app`：通过。
- TestClient 验证 RSS、Sitemap、robots 均返回 200，不包含 `demo-draft` 草稿和 Secret pattern；robots 包含 `Disallow: /admin`。
- 结论：SEO/订阅/分享已通过用户人工验收，RSS、Sitemap、robots、文章分享相关项可标记为 `已完成`。

2026-05-02 性能、可访问性与体验稳定轮当前结果：

- 新增前台 `SafeImage` 图片组件，统一懒加载、alt 和加载失败兜底；文章封面、个人头像、项目/友链/音乐/照片墙图片均已接入。
- 新增前台 `StateBlock` 通用状态块，并在文章列表、搜索、归档等页面复用加载/错误状态。
- 照片墙预览增加 dialog 语义、关闭按钮和 Esc 关闭；评论表单补齐 label、提交中禁用和错误/成功可读反馈。
- 前台导航、背景控制、播放器、分享按钮补齐按钮类型或 aria-label；移动端背景光效降低为桌面端启用。
- 后台主布局修复为 `minmax(0,1fr)` 内容列，侧栏窄屏可滚动；暂存区按钮补齐类型和展开状态；登录/写作输入补齐 autocomplete/aria-label。
- 构建体积检查：前台 dist 约 1.23 MB，后台 dist 约 1.70 MB；MarkdownRenderer 与 MarkdownEditor chunk 仍超过 500 kB，但位于文章详情/编辑器懒加载路径，未引入大型新依赖。
- 构建、后端编译、主要前后台路由 HTTP 探测、RSS/Sitemap/Search 回归、真实 Secret 值静态扫描均通过。
- 当前工具环境未提供可用 headless browser，因此 390px 真实视觉回归、Tab 顺序和图片失败视觉兜底仍需用户浏览器人工确认；相关模块不因本轮自动标记完成。

2026-05-02 管理端审计日志与数据备份恢复轮当前结果：

- 新增后台审计日志服务，写入 `backend/data/audit/audit.log`，覆盖登录、内容写入/删除、评论新增/删除、settings 修改、结构化 JSON 保存、上传、备份、恢复、导入、导出等操作。
- 新增 `GET /api/admin/audit/logs`，支持 `limit`、`offset`、`action`、`resource`、`q` 筛选，必须管理员 JWT。
- 新增手动备份服务，备份写入 `backend/data/.manual_backups/{timestamp}.zip`，恢复前自动创建 `pre-restore-{timestamp}.zip`。
- 新增 `POST /api/admin/backups`、`GET /api/admin/backups`、`GET /api/admin/backups/{name}/download`、`POST /api/admin/backups/{name}/restore`、`GET /api/admin/export`、`POST /api/admin/import`。
- 备份 zip 排除 `.env`、`.venv`、`node_modules`、`dist`、前端源码和 `.manual_backups` 本身；`settings.json` 写入 zip 前剔除 Secret 字段。
- 后台新增 `/admin/audit` 和 `/admin/backups` 页面，提供日志筛选、备份列表、手动备份、下载、恢复、导出和导入入口。
- API 验证通过：创建备份、列表、下载、恢复前备份、审计日志、评论创建/删除审计、导出、路径穿越防护、zip 不含 `.env` 与 Secret 字段。
- 当前工具环境无法启动固定 8000/5174 服务进行真实浏览器页面验收，`/admin/audit` 和 `/admin/backups` 仍需用户人工确认后才能标记完成。

## Matrix

| 模块 | 原项目能力 | SRBlogs 当前状态 | 差距等级 | 实现轮次 | 状态 | 验收标准 |
| --- | --- | --- | --- | --- | --- | --- |
| 首页 | 毛玻璃首页、个人资料、最新内容、动态氛围组件 | 已有首页、ProfileCard、站点统计、最新文章/杂谈/动态组件；浏览器可打开，统计数据源已修复为非零；已移除首页父级裁切，Hero/ProfileCard 和 SiteDashboard 改为 auto-fit 响应式网格；最新文章从横向滚动轨道改为 1/2/3 列响应式网格，4 篇文章应换到第二行 | P1 | 3 视觉首页轮 | 进行中 | 剩余差距：需要用户人工确认 4 篇文章时正确换行、页面左右边距恢复正常、没有任何 section 再撑宽整个首页；通过前不得标记完成 |
| 文章列表 | 文章卡片、标签、摘要、封面、列表浏览 | Posts 页面真实读取 `/api/posts`，已补加载、空、错误状态、封面兜底、标签、日期、摘要和详情跳转；公开列表默认不含草稿，本轮已通过 API 验证草稿隐藏、发布后可见、删除后移除 | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：需要完成更完整的浏览器人工回归、移动端检查和后台草稿发布/删除后的前台浏览器联动确认，满足 Definition of Done 后才能完成 |
| 文章详情 | Markdown 详情、代码高亮、评论、分享 | PostDetail 真实读取 `/api/posts/{slug}`，已补加载、404/错误状态、封面兜底、元信息展示、分享和评论挂载；MarkdownRenderer 继续使用 DOMPurify；前台 Markdown 样式已补齐列表编号、项目符号、表格滚动和图片自适应；人工回归项已写入 `docs/MANUAL_QA_CHECKLIST.md` | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：TOC 点击滚动、代码块视觉高亮、分享按钮交互、390px 移动端仍需浏览器人工验收 |
| 动态 | 类朋友圈短内容流和轻量评论 | Moments 页面真实读取 `/api/moments`，本轮补齐加载、空、错误状态；详情复用 PostDetail | P1 | 6 媒体互动轮 | 进行中 | 剩余差距：动态详情、评论和 390px 移动端仍需浏览器人工回归 |
| 杂谈 | 云端杂谈/碎片化文章卡片 | Chatter 页面真实读取 `/api/chatters`，本轮公开路由统一为 `/chatters` 和 `/chatters/:slug`，旧 `/chatter` 保留重定向；已补加载、空、错误状态 | P1 | 6 媒体互动轮 | 进行中 | 剩余差距：杂谈详情、首页聚合跳转和移动端仍需浏览器人工回归 |
| 时间线 | 内容按时间汇总展示 | Timeline 页面真实读取 `/api/moments`，已补齐加载、空、错误状态；新增 `/archive` 使用 `/api/archive` 聚合 posts/moments/chatters 按年月浏览；归档页面已通过人工验收 | P1 | 6 媒体互动轮 / 内容发现轮 | 已完成 | `/archive` 按年月展示公开内容、跳转详情、空/加载/错误状态和首页入口均已通过人工验收；`/timeline` 保留为视觉时间线 |
| 搜索 | 全站内容发现 | 新增 `GET /api/search` 和前台 `/search`，支持关键词、类型、标签、URL query、加载/空/错误状态和结果跳转；搜索结果覆盖文章、瞬间、杂谈、项目、照片、友链、音乐且排除草稿；已通过人工验收 | P1 | 内容发现轮 | 已完成 | `/search`、关键词搜索、类型筛选、标签筛选、空结果和首页搜索入口均已通过人工验收 |
| 标签 | 标签聚合与标签内容页 | 新增 `GET /api/tags`、`/tags`、`/tags/:tag`，合并 posts/moments/chatters/projects 标签，支持标签数量、类型和内容列表；已通过人工验收 | P1 | 内容发现轮 | 已完成 | `/tags`、`/tags/:tag`、不存在标签空状态和首页热门标签入口均已通过人工验收 |
| 照片墙 | 图片墙、封面、图集浏览 | 前台 Photowall 动态读取 `/api/photos`，已有加载/空/错误状态、懒加载、点击放大预览、标题/描述/日期/标签展示；后台照片管理已改为表单化主流程，支持上传接口填入 URL，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 照片墙懒加载、点击放大、上传填 URL、后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 音乐 | 网易云 ID 配置和悬浮/页面播放器 | 前台 Music 动态读取 `/api/music`，已有加载/空/错误状态、歌曲列表和 CloudPlayer 数据绑定；CloudPlayer 在歌曲存在 URL 时支持原生 audio 播放/暂停；后台歌单管理已改为表单化主流程，支持标题、艺术家、封面、URL/云音乐 ID、排序，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 音乐播放、后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 友链 | 友链卡片和头像展示 | 前台 Friends 动态读取 `/api/friends`，已有加载/空/错误状态、头像兜底、标签和新标签外链；后台友链管理已改为表单化主流程，支持新增/编辑/删除名称、URL、描述、头像/图标、标签，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 友链后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 项目 | 项目展示卡片、标签、状态 | 前台 Projects 动态读取 `/api/projects`，已有加载/空/错误状态、封面、描述、技术栈、状态、项目链接、仓库链接；后台项目管理已改为表单化主流程，支持新增/编辑/删除并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 项目后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 评论 | Gitalk 风格评论，Issues/OAuth 配置 | 当前为本地 JSON 评论；GET/POST/DELETE 已验证；新增 `GET /api/admin/comments/index`；后台 `/admin/comments` 默认展示有评论的内容索引，点击后查看和删除评论，手动 slug 加载已移入“高级加载”；后端限制长度、拒绝空内容、校验可选邮箱并清洗 XSS；覆盖和删除评论文件会备份；人工回归项已写入 `docs/MANUAL_QA_CHECKLIST.md` | P0 | 4 文章与评论轮 | 进行中 | 剩余差距：隐藏/恢复、审核、分页、Gitalk OAuth 不在本轮范围；后台评论管理浏览器交互和前后台同步人工回归仍需完成，不能标记完成 |
| 后台仪表盘 | 管理入口、统计、发布流程提示 | 已有 Dashboard 和 stats API；浏览器可打开，登录可成功，stats 已返回非零数据；右侧暂存区已接入本地 pendingOperations 队列并显示应用/重试/移除操作 | P1 | 3 视觉首页轮 | 进行中 | 剩余差距：暂存区仍需浏览器人工验收；核心页面还需完成完整手动验收记录 |
| Markdown 编辑器 | 沉浸式写作、预览、发布 | 已有 Editor、MarkdownEditor、MarkdownPreview；预览继续使用 `marked + DOMPurify`，并已补齐标题层级、段落、无序/有序列表、引用、inline code、代码块、表格、链接、图片样式；已新增 Markdown 测试样例；写作页支持直接保存、加入暂存、立即发布、发布加入暂存，并显示空标题、空 slug、非法 slug、保存成功/失败提示 | P0 | 5 后台写作轮 | 进行中 | 剩余差距：仍需从后台浏览器确认错误提示、直接保存、暂存应用和保存后前台文章详情表现一致；不满足人工验收前不得完成 |
| 草稿 | 草稿管理和发布 | Drafts 页面可列出 draft=true 文章，支持继续编辑、立即发布和发布暂存；API 验证草稿真实写入、公开列表隐藏、发布后公开列表可见且详情可读 | P1 | 5 后台写作轮 | 进行中 | 剩余差距：需要浏览器人工确认草稿入口、筛选、编辑、发布后前台联动和 UI 提示 |
| 暂存队列 | 操作暂存后统一应用 | 已实现第一阶段本地 pendingOperations，覆盖文章新建、文章编辑、文章删除、草稿发布；状态为 `editing`、`pending`、`applied`、`failed`；点击“应用”才调用真实后端 API；刷新页面会丢失并已在 UI 中提示；图片上传、Secret 修改、评论管理不进入本队列 | P1 | 5 后台写作轮 | 进行中 | 剩余差距：需要浏览器人工确认加入暂存不写后端、应用后才写入、失败后显示错误并可重试/移除；settings 修改未纳入本轮 |
| 图床 | 图床配置、上传、Token 测试 | 设置中心已提供 provider、publicBaseUrl、bucket、region、endpoint、AccessKey configured、Secret configured 和新密钥输入；后台不回显密钥明文；本地上传 API 测试通过；上传接口继续校验类型、MIME 和大小 | P0 | 7 设置中心与生产化轮 | 延期/未验收 | 原因：用户决定跳过本轮图床表单、上传流程和空 Secret 保留旧值的浏览器人工验收；不得标记完成 |
| AI 设置 | Gemini/兼容模型配置和后台助手 | 设置中心已提供 provider、baseUrl、model、enableChat、aiKeyConfigured 和新 API Key 输入；后台不回显 API Key 明文；构建产物 Secret 搜索通过 | P1 | 7 设置中心与生产化轮 | 延期/未验收 | 原因：用户决定跳过本轮 AI 设置浏览器验收和真实大模型联调；不得标记完成 |
| 评论设置 | GitHub OAuth/Gitalk 配置面板 | 设置中心已提供评论开关、邮箱要求、最大长度、邮箱显示、本地评论开关和 Gitalk/GitHub 占位字段；前台评论区已尊重 enabled/localEnabled，关闭后隐藏提交框 | P1 | 7 设置中心与生产化轮 | 延期/未验收 | 原因：用户决定跳过本轮评论开关浏览器人工验收；不得标记完成 |
| 部署文档 | Windows 启动、Vercel/GitHub 说明 | 已新增 Windows 专用启动脚本 `start-backend.cmd`、`start-frontend.cmd`、`start-admin.cmd`、`start-all.cmd`；`WINDOWS_START.md` 已记录固定地址、strictPort、端口占用 PID 和设置中心提示；新增 `docs/DEPLOYMENT.md`，包含 Nginx、systemd、backend/data 权限、生产 `.env`、HTTPS 和生产前检查 | P0 | 7 设置中心与生产化轮 | 延期/未验收 | 原因：用户决定跳过本轮服务器部署文档完整实操核验；不得标记完成 |
| SEO/订阅/分享 | Meta、OpenGraph、RSS、Sitemap、robots、分享 | 已新增统一 SEO meta 工具；主要前台页面接入 title/description/OG/Twitter Card；后端新增 RSS、Sitemap、robots；前台新增 RSS 入口；分享复制增加成功/失败提示；已通过用户人工验收 | P1 | SEO、订阅与分享增强轮 | 已完成 | RSS、Sitemap、robots、动态 meta、RSS 入口和分享复制均已通过人工验收 |
| 性能/可访问性/体验稳定 | 图片性能、移动端可读性、错误兜底、键盘可访问性、构建体积可控 | 已补 SafeImage 图片懒加载/兜底、StateBlock 通用状态、照片预览关闭能力、评论表单 label、前台导航/播放器/背景控制 aria、后台侧栏窄屏滚动和输入 aria；构建体积已记录，Markdown 相关 chunk 仍需后续观察 | P1 | 性能、可访问性与体验稳定轮 | 进行中 | 剩余差距：390px 真实浏览器视觉回归、键盘 Tab 顺序、图片失败视觉兜底、后台窄屏表单操作仍需人工确认；不得在人工验收前标记完成 |
| 审计日志与备份恢复 | 后台操作审计、数据备份、下载、恢复、导入导出 | 已新增审计日志服务、`/admin/audit`、手动备份服务、`/admin/backups`、下载、恢复、导出和导入 API；恢复前自动创建 pre-restore 备份；备份 zip 排除 `.env` 和 Secret 字段；API 级验证已通过 | P0 | 管理端审计日志与数据备份恢复轮 | 进行中 | 剩余差距：需要用户浏览器人工确认 `/admin/audit` 日志筛选、`/admin/backups` 创建/下载/恢复/导入导出主流程和 UI 错误状态；通过前不得标记完成 |
