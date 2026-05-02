# HISTORY

## 2026-05-02 - 安全备份与契约基础轮

本轮目标：

- 建立 SRBlogs 对标 XinghuisamaBlogs 的工程执行文档。
- 引入统一文件服务，开始约束 JSON/Markdown 读写。
- 拆分 settings 的公开读取和后台管理接口，避免 Secret 明文进入前台构建产物。

前台变更：

- 前台 settings 读取切换为 `GET /api/settings/public`。
- 前台 API 错误提示兼容统一错误响应的 `message` 字段。

后台变更：

- 设置面板切换为 `GET /api/admin/settings` 和 `PUT /api/admin/settings`。
- 后台 settings 响应只展示 Secret 配置状态，不展示 Secret 明文。

后端/API 变更：

- 新增 `backend/app/services/file_store.py`，提供 `safe_read_json`、`safe_write_json`、`safe_read_text`、`safe_write_text`、`backup_file`、`validate_slug`、`resolve_data_path`。
- Markdown、JSON、about、comments 读写迁入统一文件服务。
- 新增 `GET /api/settings/public`、`GET /api/admin/settings`、`PUT /api/admin/settings`。
- 上传接口增加扩展名、MIME 和 5 MB 大小限制。
- FastAPI 增加统一错误响应结构 `{ code, message, detail }`。

文档变更：

- 新增 `docs/XINGHUI_PARITY_MATRIX.md`。
- 新增 `docs/API_CONTRACT.md`。
- 新增 `docs/SECURITY_NOTES.md`。
- 新增 `docs/UI_STYLE_GUIDE.md`。

验证结果：

- 通过：`cd frontend && npm run build`
- 通过：`cd admin && npm run build`
- 通过：后端启动并访问 `http://127.0.0.1:8000/api/health`，返回 `{"ok":true,"app":"SRBlogs API"}`。
- 通过：`GET /api/settings/public` 返回 200，未匹配到 `clientSecret`、`api_key`、`accessKeySecret`、`jwt_secret`、`admin_password` 等敏感字段名。
- 通过：默认管理员登录后访问 `GET /api/admin/settings` 返回 200，未匹配到 `clientSecret`、`accessKeySecret`、`token` 明文字段。
- 通过：`python -m compileall backend\app`
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`。
- 已尝试但未通过：固定地址端口检查中，`http://127.0.0.1:5173` 和 `http://127.0.0.1:5174/admin/` 均返回连接失败；后续不要在本轮继续运行 `npm run dev` 等长时间前台命令。
- 未完成：首页、文章详情、后台仪表盘、编辑器、设置页仍需浏览器手动验收。
- 未执行：未对现有 `backend/data` 做写入探测，避免为验证而改动用户内容；后续涉及真实写入功能时必须检查实际文件变化和备份。

遗留问题：

- 暂存队列第一阶段尚未实现。
- UI 视觉追平尚未开始。
- 由于 5173/5174 端口检查和核心页面手动验收未完成，`docs/XINGHUI_PARITY_MATRIX.md` 中基础安全项保持 `进行中`，不得标记为 `已完成`。

## 2026-05-02 - 内容统计与闭环校验修正

本轮目标：

- 修复前台首页和后台仪表盘统计为 0 的问题。
- 检查核心内容 API 的真实响应。
- 确认下一轮进入“文章与评论轮”，优先完成 P0 内容闭环。

前台变更：

- 未新增任何 P2 视觉特效。
- 前台首页统计依赖的后端数据路径问题已在后端修复，文章、动态、杂谈、项目数据可被正常读取。

后台变更：

- 未新增视觉功能。
- 后台仪表盘统计源修复后可返回非零数据。

后端/API 变更：

- 修复 `backend/app/config.py` 的 `data_path` 解析：`DATA_DIR=backend/data` 从 `backend` 目录启动时不再错误指向 `backend/backend/data`。
- 修复 `GET /api/dashboard/stats` 的照片统计，优先统计 `backend/data/photos/photos.json` 中的照片条目。

API 实测结果：

- `GET /api/posts`：2 条，首条 slug 为 `vue-fastapi-blog`。
- `GET /api/posts/{slug}`：可读取文章详情，首条详情 content 长度 755，Markdown 正文存在。
- `GET /api/moments`：2 条。
- `GET /api/chatters`：2 条。
- `GET /api/projects`：3 条。
- `GET /api/photos`：6 条。
- `GET /api/dashboard/stats`：`posts=2`、`moments=2`、`chatters=2`、`photos=6`。

浏览器手动验收结果：

- 前台首页可打开。
- 后台仪表盘可打开。
- 登录可成功。
- CORS 问题已修复。

验证结果：

- 通过：短暂启动当前后端到 `127.0.0.1:8010` 并检查上述 API 响应。
- 通过：`python -m compileall backend\app`。
- 未运行：本轮未再执行 `npm run dev` 前台/后台长时间命令。

遗留问题：

- 下一轮进入“文章与评论轮”。
- P0 优先级：文章列表、文章详情、评论读写。
- 评论读写还需要做真实写入验证，并检查 `backend/data/comments` 文件变化和备份策略。

## 2026-05-02 - 文章与评论轮 P0 闭环

本轮目标：

- 完成文章列表、文章详情、评论读写和最小后台写作保存验证。
- 证明内容可以被安全读取、渲染、评论、保存。
- 不新增樱花、弹幕、CyberCat、动态背景等 P2 装饰功能。

前台变更：

- `Posts.vue` 增加加载状态、空状态、加载失败状态和重试入口。
- `PostList.vue` 增加封面兜底、图片加载失败兜底、日期、摘要、标签和详情跳转保留。
- `PostDetail.vue` 增加加载状态、404/错误状态、封面兜底、标签/日期/标题/摘要展示，继续使用 `MarkdownRenderer` 安全渲染 Markdown。
- `CommentBox.vue` 增加评论加载状态、提交中状态、提交成功反馈、提交失败反馈，前端展示评论继续使用文本插值而非危险 HTML。
- 调整页面顶部留白和目录锚点偏移，减少 sticky 顶部导航遮挡内容。
- 降低弹幕透明度，避免覆盖主要阅读区域；未新增任何 P2 特效。

后台变更：

- `Editor.vue` 增加保存中状态、错误反馈、空标题前端拦截，并明确提示当前保存会直接持久化写入后端 Markdown 文件，`pendingOperations` 暂存队列尚未实现。
- `JsonManageBase.vue` 文案改为“高级 JSON 编辑”，说明后续再表单化。

后端/API 变更：

- `ContentMeta.title` 增加非空校验。
- `CommentCreate.author` 和 `CommentCreate.content` 增加去空白后的非空校验。
- `POST /api/posts` 新建重复 slug 返回 409。
- 非法 slug 继续返回 400。
- Markdown 写入继续通过 `safe_write_text`，评论 JSON 写入继续通过 `safe_write_json`，覆盖已有评论文件时会生成备份。

文档变更：

- 更新 `docs/XINGHUI_PARITY_MATRIX.md` 中文章列表、文章详情、评论、Markdown 编辑器、后台仪表盘状态和剩余差距。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：后端临时启动到 `127.0.0.1:8011` 并访问 `/api/health`，返回 `health=True`。
- 通过：后台 JWT 登录成功。
- 通过：后台新建非草稿文章 `srblogs-p0-20260502130609`。
- 通过：文章文件真实写入 `backend/data/posts/srblogs-p0-20260502130609.md`。
- 通过：`GET /api/posts` 包含新文章。
- 通过：`GET /api/posts/srblogs-p0-20260502130609` 返回标题 `SRBlogs P0 Content Loop`，Markdown content 长度 120。
- 通过：非法 slug 新建返回 400。
- 通过：空标题新建返回 400。
- 通过：重复 slug 新建返回 409。
- 通过：`POST /api/comments/posts/srblogs-p0-20260502130609` 成功写入评论。
- 通过：`GET /api/comments/posts/srblogs-p0-20260502130609` 返回 2 条评论。
- 通过：评论文件真实写入 `backend/data/comments/posts-srblogs-p0-20260502130609.json`。
- 通过：第二次评论写入前生成备份，`backend/data/comments/.backups` 中匹配备份数为 1。
- 通过：评论 XSS 清洗，`<script>alert(1)</script>Hello` 保存为 `alert(1)Hello`，`<img src=x onerror=alert(1)>Second comment` 保存为 `Second comment`。
- 通过：未启动新的 `npm run dev`，仅探测已有前台地址，`http://127.0.0.1:5173/posts/srblogs-p0-20260502130609` 返回 200。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`。

遗留问题：

- 文章列表、文章详情、评论、Markdown 编辑器仍保持 `进行中`，因为完整浏览器手动验收和长期回归尚未完成，不能标记为 `已完成`。
- 评论删除、审核、分页、Gitalk/OAuth 不在本轮范围内。
- 暂存队列仍未实现，后台写作当前为直接持久化。

## 2026-05-02 - 文章详情与评论管理回归推进

本轮目标：

- 推进文章详情和评论区从 API 可用到浏览器可用。
- 新增后台本地评论管理最小版。
- 不新增樱花、弹幕、CyberCat、动态背景等 P2 装饰功能。

前台变更：

- 评论表单增加邮箱格式校验，邮箱仍为可选。
- 评论区已有加载、空、错误、提交中、成功/失败反馈；长评论使用 `whitespace-pre-wrap` 和 `break-words` 展示。
- 前台评论继续使用文本插值展示，不渲染危险 HTML。

后台变更：

- 新增 `admin/src/views/CommentsManage.vue`。
- 后台新增 `/admin/comments` 路由。
- 管理侧导航新增“评论”入口。
- 评论管理最小版支持按 `resource/slug` 加载评论列表和删除评论。
- 隐藏/恢复评论本轮未实现，当前仅支持删除。

后端/API 变更：

- 新增 `DELETE /api/comments/{resource}/{slug}/{comment_id}`，需要管理员 JWT。
- 删除不存在的评论返回 404。
- 删除评论写回 JSON 时继续走 `JsonStore.write` -> `safe_write_json`，删除前会备份原评论 JSON。
- `backup_file` 备份文件名改为微秒级时间戳，避免同一秒多次写入覆盖备份。
- 评论 email 增加后端可选格式校验，非法邮箱返回 400。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充删除评论 API。
- 更新 `docs/SECURITY_NOTES.md`，补充后台删除评论安全规则。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步评论管理进展和剩余差距。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：`GET /api/posts/srblogs-p0-20260502130609` 返回标题 `SRBlogs P0 Content Loop`，Markdown content 长度 120。
- 通过：`GET /api/comments/posts/srblogs-p0-20260502130609` 返回 2 条评论。
- 通过：非法邮箱评论提交返回 400。
- 通过：创建临时评论后调用 `DELETE /api/comments/posts/srblogs-p0-20260502130609/{comment_id}`，返回 `ok=True`。
- 通过：删除后 `GET /api/comments/posts/srblogs-p0-20260502130609` 仍返回 2 条，说明临时评论已从列表移除。
- 通过：删除前评论文件大小 574 bytes，删除后 365 bytes，`backend/data/comments` 实际文件发生变化。
- 通过：删除前备份验证，`.backups` 中匹配备份数从 3 增加到 4。
- 通过：删除不存在评论返回 404。
- 阻塞：尝试用 `Start-Process` 启动前台/后台 Vite dev server 时，Vite 在当前 shell 环境报 `spawn EPERM`，因此本轮无法由工具完成 390px 移动端和完整浏览器交互验收。
- 已知：上一轮已有前台文章详情地址 `http://127.0.0.1:5173/posts/srblogs-p0-20260502130609` 返回 200；本轮未继续等待 `npm run dev` 常驻命令退出。

遗留问题：

- 文章详情浏览器完整人工回归仍未完成：TOC 点击滚动、代码块视觉高亮、分享按钮浏览器交互、390px 移动端可读性仍需在可用浏览器环境中确认。
- 后台评论管理浏览器完整人工回归未完成，但 build 和 API 删除闭环已通过。
- 后台写作浏览器人工回归未完成，本轮未新增写作保存数据。
- 文章列表、文章详情、评论、Markdown 编辑器继续保持 `进行中`，不得标记为 `已完成`。

## 2026-05-02 - 本地开发启动与浏览器回归修复轮

本轮目标：

- 修复或规避当前工具 shell 环境中 Vite dev server 的 `spawn EPERM` 阻塞。
- 落地 Windows 专用启动脚本和固定端口检查，避免 Vite 自动跳端口。
- 建立文章详情、评论区、后台评论管理、后台写作的浏览器人工回归清单。
- 不新增樱花、弹幕、CyberCat、动态背景等 P2 装饰功能。

前台变更：

- `frontend/package.json` 的 `dev` 脚本固定为 `vite --host 127.0.0.1 --port 5173 --strictPort`。
- 新增 `start-frontend.cmd`，显式使用 `npm.cmd run dev` 启动前台，并在端口 5173 被占用时输出占用 PID 和处理建议。

后台变更：

- `admin/package.json` 的 `dev` 脚本固定为 `vite --host 127.0.0.1 --port 5174 --strictPort`。
- 新增 `start-admin.cmd`，显式使用 `npm.cmd run dev` 启动后台，并在端口 5174 被占用时输出占用 PID 和处理建议。

后端/API 变更：

- 新增 `start-backend.cmd`，固定启动 `127.0.0.1:8000`，并在端口 8000 被占用时输出占用 PID 和处理建议。
- 新增 `start-all.cmd`，通过独立窗口分别启动后端、前台和后台。
- 本轮未新增业务 API，保留上一轮评论删除 API 和内容读写闭环。

文档变更：

- 新增 `docs/MANUAL_QA_CHECKLIST.md`，覆盖前台文章详情、前台评论区、后台评论管理和后台写作人工回归项。
- 更新 `WINDOWS_START.md`，改为推荐使用 `start-backend.cmd`、`start-frontend.cmd`、`start-admin.cmd`、`start-all.cmd`，并记录固定访问地址、strictPort、端口占用 PID 提示。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步本轮验证结果和剩余阻塞。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8015` 并访问 `/api/health`，返回 `health=True`。
- 通过：`GET /api/posts/srblogs-p0-20260502130609` 返回标题 `SRBlogs P0 Content Loop`。
- 通过：`GET /api/comments/posts/srblogs-p0-20260502130609` 返回 2 条评论。
- 通过：创建临时评论后调用 `DELETE /api/comments/posts/srblogs-p0-20260502130609/{comment_id}`，返回 `ok=True`。
- 通过：删除评论前备份验证，`.backups` 中匹配备份数从 5 增加到 6。
- 通过：本轮端口探测时 `8000`、`5173`、`5174` 均无监听进程，说明没有遗留常驻 dev server。
- 阻塞：在当前 Codex 工具 shell 环境中，即使通过 `Start-Process` 和 `npm.cmd` 启动前台/后台 Vite dev server，仍会报 `spawn EPERM`；因此未完成浏览器人工回归。

遗留问题：

- 需要用户在普通 Windows 终端或双击脚本方式启动 `start-all.cmd` 后，按 `docs/MANUAL_QA_CHECKLIST.md` 完成浏览器人工验收。
- 文章详情、评论、Markdown 编辑器、后台评论管理仍保持 `进行中`，不得标记为 `已完成`。
- 暂存队列仍未实现，后台写作仍为直接持久化。

## 2026-05-02 - Markdown 预览与评论索引主流程轮

本轮目标：

- 修复后台 Markdown 编辑器预览接近纯文本的问题。
- 后台评论管理从手动输入 `resource/slug` 调整为默认展示“有评论的内容索引”。
- 保持当前技术栈和 FastAPI + `backend/data` 文件存储方案。
- 不新增樱花、弹幕、CyberCat、动态背景等 P2 装饰功能，不进入媒体互动轮。

前台变更：

- 补齐前台 `.prose-sr` 的 Markdown 列表、表格、h1、图片自适应样式，避免 Tailwind reset 导致列表符号和有序编号不可见。
- 前台评论区在开发环境显示当前 `resource/slug` 调试信息，生产环境不显示，用于确认前后台评论使用同一 slug。

后台变更：

- `MarkdownPreview.vue` 继续使用 `marked + DOMPurify`，并明确输出到 `.prose-sr prose-sr-admin`。
- 后台 Markdown 预览补齐 h1/h2/h3、段落、无序列表、有序列表、引用、inline code、代码块、表格、链接、图片样式。
- 新增 `admin/src/constants/markdownSample.ts`，提供包含标题、列表、代码块、引用、表格、链接和图片的测试样例。
- `MarkdownEditor.vue` 新增“插入预览测试样例”按钮。
- `CommentsManage.vue` 重构为默认加载评论索引；点击索引项后查看评论。
- 后台评论管理显示标题、resource、slug、评论数、最近更新时间和当前请求的 `resource/slug`。
- 手动 `resource/slug` 加载移动到“高级加载”折叠区。
- 删除评论前增加确认；删除成功后自动刷新评论列表和评论索引；删除失败会在 UI 中显示错误。
- 评论管理继续不进入 `pendingOperations`，删除为直接持久化操作。

后端/API 变更：

- 新增 `GET /api/admin/comments/index`，需要管理员 JWT。
- 评论索引扫描 `backend/data/comments`，从 `posts-slug.json` 等文件名反推 `resource/slug`。
- 评论索引返回 `resource`、`slug`、`count`、`updatedAt`、`title`。
- `title` 优先读取对应 Markdown Front Matter 的标题，内容文件不存在时回退为 slug。
- comments 目录不存在或没有评论时返回 `[]`，不返回 500。
- `JsonStore` 不再在构造时创建默认 JSON 文件，避免 GET/高级加载等只读操作产生空文件；真实写入仍走 `safe_write_json`。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充 `GET /api/admin/comments/index`。
- 更新 `docs/SECURITY_NOTES.md`，补充后台评论索引和评论管理直接持久化规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充 Markdown 预览和“后台评论管理不需要手动输入 slug”的验收项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步 Markdown 编辑器与评论管理当前进展。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8020` 并访问 `/api/health`，返回 `health=True`。
- 通过：后台登录获取 JWT。
- 通过：`GET /api/admin/comments/index` 返回评论索引，包含 `posts/srblogs-p0-20260502130609`，原始响应中 `count=3`、`title=SRBlogs P0 Content Loop`。
- 通过：comments 目录不存在或无评论的临时 `DATA_DIR` 下，`GET /api/admin/comments/index` 返回 `[]`。
- 通过：前台 `POST /api/comments/posts/srblogs-p0-20260502130609` 创建临时评论后，后台评论索引可刷新到该内容记录；随后 DELETE 删除临时评论成功。
- 通过：删除不存在评论返回 404。
- 通过：非法邮箱评论提交返回 400。
- 通过：空昵称/空内容评论提交返回 400。
- 通过：删除评论前备份验证，`.backups` 中匹配备份数从 9 增加到 11。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`。
- 通过：当前端口探测时 `8000`、`5173`、`5174` 均无监听进程，没有遗留常驻 dev server。
- 阻塞：本轮再次使用独立 `cmd.exe` 调用 `start-admin.cmd` 探测 Vite dev server，5174 未监听，仍复现 `spawn EPERM`。
- 修正：`start-frontend.cmd` 和 `start-admin.cmd` 改为只调用 `npm.cmd run dev`，固定端口和 `--strictPort` 由各自 `package.json` 统一管理，避免命令参数重复。
- 代码级确认：后台和前台 Markdown 渲染入口仍调用 `DOMPurify.sanitize`；后台/前台 `.prose-sr` 已显式包含列表编号、项目符号、表格横向滚动、代码块背景和图片自适应样式。

遗留问题：

- 本轮没有在 Codex 工具环境完成浏览器人工回归；Markdown 预览和后台评论管理仍需用户按 `docs/MANUAL_QA_CHECKLIST.md` 在浏览器确认。
- 文章详情、评论、Markdown 编辑器继续保持 `进行中`，不得标记为 `已完成`。
- 评论隐藏/恢复、审核、分页仍未实现，不在本轮范围。
- 暂存队列仍未实现，评论管理也不进入 pendingOperations。
