# XinghuisamaBlogs Parity Matrix

差距等级定义：

- `P0`：核心可用闭环，包括内容读取、内容写入、登录鉴权、设置读取、基础评论、构建运行、安全写文件。
- `P1`：关键体验，包括编辑器预览、草稿、暂存队列、搜索/标签、响应式、后台表单化设置、错误状态。
- `P2`：视觉增强和装饰特效，包括樱花、萤火、弹幕、动态背景细节、悬浮音乐细节、卡片动效和主题装饰。

状态定义：`未开始`、`进行中`、`已完成`、`延期/未验收`、`部署实操待执行`、`冻结/未开始系统化增强`。只有满足本轮 Definition of Done 后才能标记为 `已完成`。

## 当前进度估算

2026-05-03 P2 第二阶段：首页结构追平 + 昼夜主题系统轮后：

- `P0`：约 100%。内容读取/写入、登录鉴权、公开草稿保护、评论、媒体管理、设置边界、安全写入、审计日志、备份恢复、构建运行和 Secret 扫描均已通过验证；真实服务器部署实操单独标记为待执行。
- `P1`：约 100%。搜索、标签、归档、SEO/RSS/Sitemap、后台写作、草稿、pendingOperations 第一阶段、设置中心表单化、错误状态、操作反馈、真实使用手册和发布准备均已收口；后续仅保留长期优化。
- `P2`：约 74%。已完成铺满式顶部导航、滚动隐藏/显示、首页“名片 + 音乐播放器 + 歌词区 + 不对称内容模块 + 底部状态区”、最新更新聚合、昼夜模式卡片、主题 token 体系和设置中心核心 token 配置；仍需浏览器人工回归后继续推进。

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
- `PUT /api/admin/settings` 已完成验证：AI API Key、图床 AccessKey/SecretKey、GitHub OAuth Secret 空值不覆盖旧值，后台只返回 configured 状态。
- 前台评论区会读取公开评论设置；关闭评论后显示“评论已关闭”并隐藏提交框，重新开启后恢复表单；requireEmail、maxLength、showEmail 边界已验证。
- 新增 `docs/DEPLOYMENT.md`，补充后端 FastAPI、前端/后台 build、Nginx、systemd、backend/data 权限、生产 `.env`、HTTPS 和生产前检查。
- `cd frontend && npm run build`：通过。
- `cd admin && npm run build`：通过。
- `python -m compileall backend\app`：通过。
- TestClient `/api/health`：通过；当前 `127.0.0.1:8000` 未监听，因此固定端口 health 需用户启动后复测。
- 构建产物 Secret 搜索通过。
- 结论：设置中心与生产化代码、API 和人工验收项已收口；真实 OSS/Gitalk/AI 联调不属于当前 P0/P1 范围，真实服务器部署实操另列为待执行。

2026-05-02 内容发现与归档扩张轮当前结果：

- 新增 `GET /api/search`，支持 `q`、`type`、`tag`、`limit`、`offset`，覆盖 posts/moments/chatters/projects/photos/friends/music；公开结果排除 draft。
- 新增 `GET /api/tags`，合并 posts/moments/chatters/projects 标签。
- 新增 `GET /api/archive`，按年月聚合 posts/moments/chatters。
- 前台新增 `/search`、`/tags`、`/tags/:tag`、`/archive`；首页新增轻量内容发现入口。
- `cd frontend && npm run build`、`cd admin && npm run build`、`python -m compileall backend\app`、TestClient `/api/health`：通过。
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
- 用户已确认审计日志与数据备份恢复轮通过人工验收，`/admin/audit`、`/admin/backups`、备份下载、恢复前备份和高风险操作审计可标记为 `已完成`。

2026-05-02 发布候选与部署演练轮当前结果：

- 新增 `backend/.env.production.example`，明确生产必须修改 `ADMIN_PASSWORD`、`JWT_SECRET`，并限制 `CORS_ORIGINS` 不使用 `*`。
- 新增 `deploy/build-all.sh`、`deploy/start-backend.sh`、`deploy/srblogs-backend.service`、`deploy/nginx.srblogs.conf`、`deploy/healthcheck.sh` 和 `deploy/README.md`。
- 新增 `GET /api/admin/system/status`，管理员 JWT 保护，返回 app、环境、data/uploads 目录存在性和读写状态，不返回 Secret。
- 新增 `docs/PRODUCTION_CHECKLIST.md`、`CHANGELOG.md`、`docs/RELEASE_NOTES.md`，并同步生产部署、目录、日志、备份和发布说明。
- 本轮不做真实服务器部署和 HTTPS 申请；设置中心此前跳过的五项已在后续设置中心收口轮补测通过。

2026-05-02 设置中心剩余验收与生产部署实操核验轮当前结果：

- 空 Secret 不覆盖旧值已验证：AI API Key、图床 AccessKey/SecretKey、GitHub OAuth Secret 设置测试值后，后台只返回 configured 状态；空字符串保存后原值仍保留。
- 评论配置已补强到后端强制执行：`comments.enabled=false` 返回 403 并阻止提交；`requireEmail`、`maxLength` 对 API 生效；公开评论邮箱按 `showEmail` 隐藏或脱敏。
- 图床设置与上传流程已验证：local/oss/custom 配置字段可保存，local 上传返回 URL，非图片返回 415，超大图片返回 413。
- AI 设置已验证：provider/baseUrl/model/enableChat 可保存，API Key 不回显；后台 AI 助手在 `enableChat=false` 时显示未启用提示并禁用输入。
- 部署文档与脚本已核验一致性：README、DEPLOYMENT、PRODUCTION_CHECKLIST、Nginx、systemd、env 模板的端口、命令、路径和 Secret 提示一致。
- 本轮进度估算：P0 约 96%，P1 约 91%，P2 约 40% 且冻结。

2026-05-02 后台写作、草稿与暂存队列最终收口轮当前结果：

- 后端公开内容接口已收紧：公开列表/详情默认不返回草稿，`include_drafts=true` 必须管理员 JWT。
- 文章管理页补齐标题/slug 搜索、更新时间、发布/设为草稿、暂存发布、暂存删除、删除错误提示和草稿不可公开预览提示。
- 写作页补齐 Markdown 内容不能为空校验；编辑已有文章继续通过管理员详情接口加载草稿。
- pendingOperations 补齐一键应用全部和非 Secret 设置修改暂存；Secret 修改、图片上传、评论管理仍不进入本地暂存队列。
- API 验证通过：新建草稿、公开隐藏、管理员可见、发布、公开详情、编辑、撤回发布、公开详情 404、删除、删除前备份、重复 slug 409、非法 slug 400、删除不存在 404、审计日志。
- 用户已完成最终人工验收：后台写作、草稿、发布/撤回、删除文章和 pendingOperations 第一阶段通过，本轮可标记完成。

2026-05-02 最终总回归与真实部署准备轮当前结果：

- 完整内容生产演示流通过：登录、新建草稿、发布、文章详情、评论、后台评论索引、删除评论、编辑、撤回发布、删除文章、审计日志、手动备份、下载备份和恢复备份。
- 前台主要路径和后台主要路径在当前 5173/5174 服务下完成 HTTP 快速回归，均返回 SPA 壳 200；不存在内容 slug 通过 API 返回 404。
- 构建、编译、RSS、Sitemap、robots、settings Secret 边界、构建产物 Secret 扫描和部署资产静态检查均通过。
- 本轮进度估算：P0 约 100%，P1 约 98%，P2 约 40% 且冻结。

2026-05-02 P1 最终微调与真实使用清单轮当前结果：

- 后台操作反馈完成小范围统一：登录失效、权限不足、文章保存/发布/删除、评论删除、备份创建/下载/恢复提示更明确。
- 新增 `docs/USER_GUIDE.md`，覆盖后台登录、文章、草稿、发布、编辑、删除、评论、媒体、设置、备份、恢复、审计日志、搜索/标签/归档和 RSS/Sitemap/robots。
- `.gitignore` 已补充运行时备份、`.backups`、审计日志、上传缓存和 TypeScript build info 忽略规则，降低误提交运行时垃圾的风险。
- 本轮进度估算：P0 约 100%，P1 约 100%，P2 约 40% 且冻结；P1 后续仅保留长期优化。

2026-05-02 P2 视觉统一与氛围增强轮当前结果：

- 前台新增统一视觉 token 和工具类：`sr-card`、`sr-card-hover`、`sr-hero-panel`、`sr-chip`、`sr-button-primary`、`sr-button-ghost`、状态色和 reduced-motion 规则。
- 首页 Hero、ProfileCard、SiteDashboard、内容发现入口和最新文章卡片已接入统一卡片/按钮/hover 体系，继续保持响应式容器和不撑宽约束。
- 文章详情标题区与 Markdown 正文阅读区增加层级分隔，标签样式统一；Markdown 渲染、DOMPurify、TOC、评论和分享逻辑未改动。
- 背景控制新增“氛围”开关，樱花、萤火、CyberCat、点击光效均尊重本地开关；移动端默认降低装饰密度。
- 后台样式新增控制台 token、`admin-card-hover`、状态色、危险按钮、输入 focus 和侧边栏 active 强化。
- `cd frontend && npm run build`、`cd admin && npm run build`、`python -m compileall backend\app`：通过。
- 构建产物 Secret 静态搜索：通过，未匹配敏感字段名或默认 Secret 占位。
- 本轮进度估算：P0 约 100%，P1 约 100%，P2 约 62%；P2 继续保持进行中，需浏览器人工回归确认首页、文章阅读页、后台控制台、390px 和关闭动效状态。

2026-05-03 P2 第二阶段：首页结构追平 + 昼夜主题系统轮当前结果：

- 前台顶部导航从胶囊式调整为铺满式玻璃顶栏，内部仍与 `sr-page-shell` 对齐；支持向下滚动隐藏、向上滚动显示、鼠标移到顶部显示。
- 首页重组为第一排“ProfileCard + 首页音乐播放器”、第二排歌词/播放状态区、第三排最新文章/最新更新/昼夜模式不对称模块、内容发现入口、站点统计和底部状态区。
- 最新更新内容复用公开 posts/moments/chatters 聚合，按日期排序，草稿由公开 API 默认排除；未新增复杂后端系统。
- 新增昼夜主题 CSS token：`--bg-page`、`--bg-card`、`--bg-card-elevated`、`--border-glass`、`--text-primary`、`--text-secondary`、`--accent`、`--accent-soft`、`--nav-bg`、`--home-panel-bg`、`--shadow-glow`。
- `/admin/settings` 的“主题与背景”分区新增字体族、字号档位、日间 token、夜间 token 表单；`GET /api/settings/public` 公开返回 `themeConfig`，不包含 Secret。
- `cd frontend && npm run build`、`cd admin && npm run build`、`python -m compileall backend\app`、TestClient `/api/health` 和 `/api/settings/public`：通过。
- 构建产物 Secret 静态搜索：通过。
- 本轮进度估算：P0 约 100%，P1 约 100%，P2 约 74%；P2 仍需首页、文章详情、媒体页、后台设置页、390px、昼夜切换和顶栏滚动交互的浏览器人工回归。

## Matrix

| 模块 | 原项目能力 | SRBlogs 当前状态 | 差距等级 | 实现轮次 | 状态 | 验收标准 |
| --- | --- | --- | --- | --- | --- | --- |
| 首页 | 毛玻璃首页、个人资料、最新内容、动态氛围组件 | 已有首页、ProfileCard、站点统计、最新文章/杂谈/动态组件；浏览器可打开，统计数据源已修复为非零；响应式布局已通过用户人工验收；P2 第二阶段已重组为名片 + 音乐播放器、歌词区、不对称最新文章/最新更新/昼夜模式模块、内容发现入口和底部状态区 | P1/P2 | 3 视觉首页轮 / P2 视觉统一轮 / P2 首页结构追平轮 | 已完成 / P2 进行中 | P1 首页主要内容、ProfileCard、统计卡片、最新文章换行和左右边距均已通过人工验收；P2 新首页结构、歌词区、模式卡、底部状态区仍需浏览器人工回归 |
| 文章列表 | 文章卡片、标签、摘要、封面、列表浏览 | Posts 页面真实读取 `/api/posts`，已补加载、空、错误状态、封面兜底、标签、日期、摘要和详情跳转；公开列表默认不含草稿；后台草稿发布/撤回/删除后的公开列表联动已通过 API 与人工验收 | P0 | 4 文章与评论轮 / 最终总回归轮 | 已完成 | 公开列表隐藏草稿、发布后可见、撤回/删除后消失、构建与回归验证均通过 |
| 文章详情 | Markdown 详情、代码高亮、评论、分享 | PostDetail 真实读取 `/api/posts/{slug}`，已补加载、404/错误状态、封面兜底、元信息展示、分享和评论挂载；MarkdownRenderer 继续使用 DOMPurify；Markdown 显示、TOC、分享和移动端基础可读性已通过用户人工验收；本轮增强标题区、标签和正文阅读区层次 | P0/P2 | 4 文章与评论轮 / 最终总回归轮 / P2 视觉统一轮 | 已完成 / P2 进行中 | 已发布文章详情可打开，草稿/删除后公开详情返回 404，Markdown/TOC/分享/评论区基础体验通过验收；P2 阅读体验仍需浏览器人工回归 |
| 动态 | 类朋友圈短内容流和轻量评论 | Moments 页面真实读取 `/api/moments`，本轮补齐加载、空、错误状态；详情复用 PostDetail | P1 | 6 媒体互动轮 | 进行中 | 剩余差距：动态详情、评论和 390px 移动端仍需浏览器人工回归 |
| 杂谈 | 云端杂谈/碎片化文章卡片 | Chatter 页面真实读取 `/api/chatters`，本轮公开路由统一为 `/chatters` 和 `/chatters/:slug`，旧 `/chatter` 保留重定向；已补加载、空、错误状态 | P1 | 6 媒体互动轮 | 进行中 | 剩余差距：杂谈详情、首页聚合跳转和移动端仍需浏览器人工回归 |
| 时间线 | 内容按时间汇总展示 | Timeline 页面真实读取 `/api/moments`，已补齐加载、空、错误状态；新增 `/archive` 使用 `/api/archive` 聚合 posts/moments/chatters 按年月浏览；归档页面已通过人工验收 | P1 | 6 媒体互动轮 / 内容发现轮 | 已完成 | `/archive` 按年月展示公开内容、跳转详情、空/加载/错误状态和首页入口均已通过人工验收；`/timeline` 保留为视觉时间线 |
| 搜索 | 全站内容发现 | 新增 `GET /api/search` 和前台 `/search`，支持关键词、类型、标签、URL query、加载/空/错误状态和结果跳转；搜索结果覆盖文章、瞬间、杂谈、项目、照片、友链、音乐且排除草稿；已通过人工验收 | P1 | 内容发现轮 | 已完成 | `/search`、关键词搜索、类型筛选、标签筛选、空结果和首页搜索入口均已通过人工验收 |
| 标签 | 标签聚合与标签内容页 | 新增 `GET /api/tags`、`/tags`、`/tags/:tag`，合并 posts/moments/chatters/projects 标签，支持标签数量、类型和内容列表；已通过人工验收 | P1 | 内容发现轮 | 已完成 | `/tags`、`/tags/:tag`、不存在标签空状态和首页热门标签入口均已通过人工验收 |
| 照片墙 | 图片墙、封面、图集浏览 | 前台 Photowall 动态读取 `/api/photos`，已有加载/空/错误状态、懒加载、点击放大预览、标题/描述/日期/标签展示；后台照片管理已改为表单化主流程，支持上传接口填入 URL，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 照片墙懒加载、点击放大、上传填 URL、后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 音乐 | 网易云 ID 配置和悬浮/页面播放器 | 前台 Music 动态读取 `/api/music`，已有加载/空/错误状态、歌曲列表和 CloudPlayer 数据绑定；CloudPlayer 在歌曲存在 URL 时支持原生 audio 播放/暂停；后台歌单管理已改为表单化主流程，支持标题、艺术家、封面、URL/云音乐 ID、排序，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 音乐播放、后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 友链 | 友链卡片和头像展示 | 前台 Friends 动态读取 `/api/friends`，已有加载/空/错误状态、头像兜底、标签和新标签外链；后台友链管理已改为表单化主流程，支持新增/编辑/删除名称、URL、描述、头像/图标、标签，并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 友链后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 项目 | 项目展示卡片、标签、状态 | 前台 Projects 动态读取 `/api/projects`，已有加载/空/错误状态、封面、描述、技术栈、状态、项目链接、仓库链接；后台项目管理已改为表单化主流程，支持新增/编辑/删除并保留高级 JSON 折叠编辑；API 验证新增/编辑/删除和备份通过；浏览器人工验收已通过 | P1 | 6 媒体互动轮 | 已完成 | 项目后台表单新增/编辑/删除、前台同步展示均已通过人工验收 |
| 评论 | Gitalk 风格评论，Issues/OAuth 配置 | 当前为本地 JSON 评论；GET/POST/DELETE、评论索引、后台评论管理、删除备份、前后台同步均已通过验证和人工验收；本轮新增后端强制执行评论开关、邮箱必填、动态最大长度，公开邮箱按配置隐藏或脱敏；Gitalk OAuth 不接入 | P0 | 4 文章与评论轮 / 设置中心收口轮 | 已完成 | 本地评论读写、后台索引、删除、备份、XSS 清洗、评论开关、requireEmail、maxLength、showEmail 边界均已完成；GitHub OAuth 不属于当前 P0/P1 |
| 后台仪表盘 | 管理入口、统计、发布流程提示 | 已有 Dashboard 和 stats API；浏览器可打开，登录可成功，stats 已返回非零数据；右侧暂存区已接入本地 pendingOperations 队列并显示应用/重试/移除操作 | P1 | 3 视觉首页轮 / 后台写作最终收口轮 | 已完成 | 仪表盘、登录、真实统计、暂存区入口和后台主路径回归均已通过 |
| Markdown 编辑器 | 沉浸式写作、预览、发布 | Markdown 预览标题、无序列表、有序列表、代码块、表格已通过人工验收；写作页支持直接保存、加入暂存、立即发布、发布加入暂存，并显示空标题、空 slug、非法 slug、空 Markdown、保存成功/失败提示；DOMPurify 清洗保持生效 | P0 | 5 后台写作轮 / 后台写作最终收口轮 | 已完成 | 用户已确认后台写作新建/编辑、Markdown 预览、错误提示、保存后前台详情一致性和构建验证通过 |
| 草稿 | 草稿管理和发布 | Drafts 页面可列出 draft=true 文章，支持继续编辑、立即发布和发布暂存；后端强制公开列表/详情不返回草稿，发布后公开可见，撤回发布后公开详情 404；状态切换写审计日志 | P1 | 5 后台写作轮 / 后台写作最终收口轮 | 已完成 | 草稿创建、后台可见、前台隐藏、发布可见、撤回隐藏、详情 404 和审计日志均已通过验证和人工验收 |
| 暂存队列 | 操作暂存后统一应用 | 已实现第一阶段本地 pendingOperations，覆盖文章新建、文章编辑、文章删除、草稿发布、非 Secret 设置修改；状态为 `editing`、`pending`、`applied`、`failed`；支持单项应用、移除、失败重试和一键应用全部；刷新页面会丢失并已在 UI 中提示；图片上传、Secret 修改、评论管理不进入本队列 | P1 | 5 后台写作轮 / 后台写作最终收口轮 | 已完成 | 用户已确认加入暂存不立即写后端、应用后真实写入、失败显示错误、移除和一键应用全部可用 |
| 图床 | 图床配置、上传、Token 测试 | 设置中心已提供 provider、publicBaseUrl、bucket、region、endpoint、AccessKey configured、Secret configured 和新密钥输入；本轮验证 local/oss/custom 配置保存、AccessKey/Secret 不回显、空 Secret 不覆盖旧值、本地上传返回 URL、非图片 415、超大文件 413 | P0 | 7 设置中心与生产化轮 / 设置中心收口轮 | 已完成 | 图床配置边界、本地上传、类型/MIME/大小限制、Secret 不回显和空值不覆盖均已验证；真实 OSS 深度联调不属于本轮 |
| AI 设置 | Gemini/兼容模型配置和后台助手 | 设置中心已提供 provider、baseUrl、model、enableChat、aiKeyConfigured 和新 API Key 输入；本轮验证 API Key 不回显、空 API Key 不覆盖旧值、enableChat=false 时后台聊天页显示未启用提示并禁用输入；`/api/chat` 只读取服务端环境配置 | P1 | 7 设置中心与生产化轮 / 设置中心收口轮 | 已完成 | AI 设置保存边界、Secret 不泄露、开关提示和构建产物 Secret 搜索均已通过；真实大模型联调不属于本轮 |
| 主题配置 | 昼夜模式、组件级颜色、字体和字号 | 设置中心“主题与背景”分区新增字体族、字号档位、日间 token、夜间 token，公开 settings 返回 `themeConfig`；前台首页模式卡可切换昼夜模式并应用 CSS 变量 | P2 | P2 首页结构追平轮 | 进行中 | 保存后前台刷新生效、昼夜切换、390px、色彩可读性和 Secret 不泄露仍需浏览器人工验收 |
| 评论设置 | GitHub OAuth/Gitalk 配置面板 | 设置中心已提供评论开关、邮箱要求、最大长度、邮箱显示、本地评论开关和 Gitalk/GitHub 占位字段；本轮补强后端强制执行 enabled/localEnabled、requireEmail、maxLength，公开邮箱按 showEmail 隐藏或脱敏；GitHub OAuth Secret 空值不覆盖旧值且不回显 | P1 | 7 设置中心与生产化轮 / 设置中心收口轮 | 已完成 | 评论关闭、邮箱必填、非法邮箱、长度限制、邮箱隐藏/脱敏和 GitHub OAuth Secret 边界均已验证；真实 Gitalk/OAuth 不接入 |
| 部署文档 | Windows 启动、Vercel/GitHub 说明 | 已新增 Windows 专用启动脚本、生产 env 模板、Nginx/systemd/build/healthcheck 部署资产、`docs/DEPLOYMENT.md`、`docs/PRODUCTION_CHECKLIST.md`、`CHANGELOG.md` 和发布说明；README、DEPLOYMENT、PRODUCTION_CHECKLIST、Nginx、systemd、env 模板端口、命令、路径、Secret 和 PUBLIC_BASE_URL 说明已核验 | P0 | 7 设置中心与生产化轮 / 发布候选与部署演练轮 / 设置中心收口轮 | 部署实操待执行 | 文档、脚本结构、Nginx、systemd、data 权限、Secret/CORS/备份/上传/RSS/Sitemap/robots 检查项已核验；真实服务器、域名和 HTTPS 实操尚未执行，不标记为完全完成 |
| SEO/订阅/分享 | Meta、OpenGraph、RSS、Sitemap、robots、分享 | 已新增统一 SEO meta 工具；主要前台页面接入 title/description/OG/Twitter Card；后端新增 RSS、Sitemap、robots；前台新增 RSS 入口；分享复制增加成功/失败提示；已通过用户人工验收 | P1 | SEO、订阅与分享增强轮 | 已完成 | RSS、Sitemap、robots、动态 meta、RSS 入口和分享复制均已通过人工验收 |
| 性能/可访问性/体验稳定 | 图片性能、移动端可读性、错误兜底、键盘可访问性、构建体积可控 | 已补 SafeImage 图片懒加载/兜底、StateBlock 通用状态、照片预览关闭能力、评论表单 label、前台导航/播放器/背景控制 aria、后台侧栏窄屏滚动和输入 aria；性能稳定轮已通过验证，构建体积已记录，Markdown 相关 chunk 仍需后续观察 | P1 | 性能、可访问性与体验稳定轮 | 已完成 | 前后台主要页面稳定性、错误兜底、移动端基础适配、图片失败兜底和可访问性基础修复已通过验证；后续仅保留体积优化观察项 |
| 审计日志与备份恢复 | 后台操作审计、数据备份、下载、恢复、导入导出 | 已新增审计日志服务、`/admin/audit`、手动备份服务、`/admin/backups`、下载、恢复、导出和导入 API；恢复前自动创建 pre-restore 备份；备份 zip 排除 `.env` 和 Secret 字段；API 级验证和用户人工验收均已通过 | P0 | 管理端审计日志与数据备份恢复轮 | 已完成 | 后台审计日志、备份列表、手动备份、下载、恢复、恢复前备份和高风险操作审计均已通过人工验收 |
| P2 视觉增强 | 樱花、萤火、弹幕、动态背景细节、悬浮音乐细节、卡片动效和主题装饰 | 已有基础毛玻璃、背景和播放器氛围；已完成统一 token、卡片/按钮/标签动效、文章阅读层次、后台控制台样式、氛围开关、铺满式顶栏、首页结构追平、昼夜模式卡片和设置中心主题 token 配置 | P2 | P2 视觉统一与氛围增强轮 / P2 首页结构追平轮 | 进行中 | 当前 P2 约 74%；需继续完成浏览器人工回归，确认首页结构、昼夜切换、顶栏滚动隐藏/显示、390px、关闭动效和后台设置页不影响 P0/P1 |
