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
