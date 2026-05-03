# HISTORY

## 2026-05-03 - 多平台留言登录与中文化回归修复

本轮目标：

- 修复 GitHub / QQ 留言状态互相影响的问题。
- 修复点击登录进入 Not Found 的风险。
- 恢复前台留言板与后台设置中心的中文 UI 文案。
- 继续降低搜索框高度并提高搜索框不透明度。

当前进度估算：

- P0：100%。
- P1：98%，多平台留言 API、未登录 401 和 OAuth 登录入口路由已通过自动验证；真实第三方授权仍依赖有效 GitHub/QQ 应用配置后做浏览器验收。
- P2：约 95%，搜索框细节与 UI 中文化已收口，仍需用户做最终浏览器视觉确认。

前台变更：

- `CommentBox` 优先读取 `comments.providers.github` 与 `comments.providers.qq`，GitHub 和 QQ 的 `enabled/configured` 状态独立判断。
- GitHub 已配置时显示“使用 GitHub 登录后留言”，QQ 未配置不会影响 GitHub。
- QQ 未配置时只显示“站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。”。
- 登录跳转会自动补齐 `/api` 前缀，避免 `VITE_API_BASE_URL` 不带 `/api` 时跳到错误路径。
- 留言板加载、发布、退出、错误和未配置提示均改为中文。
- `SearchBar` 与搜索页搜索框进一步降低高度，提高背景不透明度，并修复搜索框占位文案乱码。

后台变更：

- `SettingsPanels.vue` 中站点、主题、留言、图床、AI、部署检查、按钮、状态和高级 JSON 入口改为中文展示。
- Secret 状态显示为“已配置 / 未配置”，不再在 UI 中显示 true/false。
- 留言设置保留 GitHub 和 QQ 的独立开关、ID、Secret 状态和“留空则保持旧值，不回显明文”提示。

后端/API 变更：

- `GET /api/settings/public` 的 `comments` 增加 `providers.github` 与 `providers.qq` 独立状态：`enabled`、`configured`。
- 继续保留旧字段 `githubLoginConfigured`、`qqLoginConfigured` 兼容旧前端。
- GitHub / QQ OAuth callback URL 改为从当前后端请求生成，避免 `PUBLIC_BASE_URL` 指向前台时回调落到前台导致 Not Found。
- 未登录留言接口返回中文 401 错误信息。
- OAuth 未配置时返回访客友好的中文错误信息，不暴露 Secret、后端或 `.env` 细节。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/settings/public` 返回 `comments.providers.github.configured` 和 `comments.providers.qq.configured` 布尔值，未泄露 GitHub/QQ Secret。
- 通过：FastAPI TestClient `GET /api/auth/visitor/me` 返回 GitHub/QQ 独立 configured 状态且不返回 access token。
- 通过：FastAPI TestClient `GET /api/auth/github/login?returnTo=/posts/test` 返回 307，Location 指向 GitHub OAuth，不再是 404。
- 通过：FastAPI TestClient `GET /api/auth/qq/login?returnTo=/posts/test` 返回 307，Location 指向 QQ OAuth，不再是 404。
- 通过：FastAPI TestClient 未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401，响应为中文提示。
- 通过：构建产物 Secret 固定字符串搜索未匹配。
- 通过：构建产物和源码中未匹配旧英文访客提示 `GitHub messages are not enabled`、`QQ messages are not enabled`、`Please try again later`、`contact the site owner`。

遗留问题：

- 本轮未启动 dev server 做浏览器人工回归；前台留言板按钮、后台设置页中文化、搜索框高度/透明度和 390px 移动端仍需用户在浏览器确认。
- 真实 GitHub / QQ OAuth code flow 仍依赖有效第三方应用配置和回调地址白名单。

## 2026-05-03 - 多平台留言状态与中文化回归修复

本轮目标：

- 修复 GitHub / QQ 留言状态互相影响的问题。
- 修复登录跳转出现 Not Found 的风险。
- 恢复前台留言板和后台设置中心的中文 UI 文案。
- 继续压低搜索框高度并提升搜索框不透明度。

当前进度估算：

- P0：100%。
- P1：98%，多平台留言 API 与未登录 401 已通过自动验证；真实 OAuth 授权仍需有效应用配置后浏览器验收。
- P2：约 95%，搜索框细节和 UI 中文化已收口，仍需用户浏览器确认最终视觉。

前台变更：

- `CommentBox` 改为优先读取 `comments.providers.github` 和 `comments.providers.qq`，GitHub 与 QQ 的 enabled/configured 状态独立判断。
- GitHub 已配置时显示“使用 GitHub 登录后留言”，QQ 未配置不会再影响 GitHub。
- QQ 未配置时只显示“站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。”。
- 登录跳转会自动补齐 `/api` 前缀，避免 `VITE_API_BASE_URL` 不带 `/api` 时跳到错误路径。
- 留言板加载、发布、退出、错误和未配置提示改为中文。
- `SearchBar` 与搜索页搜索框进一步降低高度，提高背景不透明度，并修复搜索框占位文案乱码。

后台变更：

- `SettingsPanels.vue` 中站点、主题、留言、图床、AI、部署检查、按钮、状态和高级 JSON 入口改为中文展示。
- Secret 状态显示为“已配置 / 未配置”，不再在 UI 中显示 true/false。
- 留言设置保留 GitHub 和 QQ 的独立开关、ID、Secret 状态和“留空则保持旧值，不回显明文”提示。

后端/API 变更：

- `GET /api/settings/public` 的 `comments` 增加 `providers.github` 与 `providers.qq` 独立状态：
  - `enabled`
  - `configured`
- 继续保留旧字段 `githubLoginConfigured`、`qqLoginConfigured` 兼容旧前端。
- GitHub / QQ OAuth callback URL 改为从当前后端请求生成，避免 `PUBLIC_BASE_URL` 指向前台时回调落到前台导致 Not Found。
- 未登录留言接口返回中文 401 错误信息。
- OAuth 未配置时返回访客友好的中文错误信息，不暴露 Secret、后端或 `.env` 细节。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/settings/public` 返回 `comments.providers.github.configured` 和 `comments.providers.qq.configured` 布尔值，未泄露 GitHub/QQ Secret。
- 通过：FastAPI TestClient `GET /api/auth/visitor/me` 返回 GitHub/QQ 独立 configured 状态且不返回 access token。
- 通过：FastAPI TestClient `GET /api/auth/github/login?returnTo=/posts/test` 返回 307，Location 指向 GitHub OAuth，不再是 404。
- 通过：FastAPI TestClient `GET /api/auth/qq/login?returnTo=/posts/test` 返回 307，Location 指向 QQ OAuth，不再是 404。
- 通过：FastAPI TestClient 未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401，响应为中文提示。
- 通过：构建产物 Secret 固定字符串搜索未匹配。
- 通过：构建产物中未匹配旧英文访客提示 `GitHub messages are not enabled`、`QQ messages are not enabled`、`Please try again later`、`contact the site owner`。

遗留问题：

- 本轮未启动 dev server 做浏览器人工回归；前台留言板按钮、后台设置页中文化、搜索框高度/透明度和 390px 移动端仍需用户在浏览器确认。
- 真实 GitHub / QQ OAuth code flow 仍依赖有效第三方应用配置和回调地址白名单。

## 2026-05-03 - Multi-provider message login and search input polish

Goals:

- Extend the frontend message board from GitHub-only login to GitHub + QQ login choices.
- Add reusable message boards to the music page and photowall album dialog without changing the existing comment storage model.
- Keep OAuth secrets server-side only and expose only configured booleans to public settings.
- Reduce the shared search input height to about 75% of the previous size and make the input background more opaque.

Progress estimate:

- P0: 100%.
- P1: 100%.
- P2: about 96%. Browser visual QA for the new music/photo message boards and QQ real OAuth callback remains pending.

Frontend changes:

- `CommentBox` now uses generic visitor auth and shows both GitHub and QQ login choices when not logged in.
- `CommentBox` supports `posts`, `moments`, `chatters`, `music`, and `photos` resources.
- `/music` now includes a `music/global` message board while preserving global playback, lyrics, playlist, and volume state.
- `/photowall` album preview dialog now includes a per-album `photos/{albumSlug}` message board.
- Shared search inputs were tightened and made more opaque while keeping the search icon button.

Admin changes:

- Rebuilt `SettingsPanels.vue` into a stable ASCII-safe component after legacy encoded strings caused TypeScript parse failures.
- Message settings now include GitHub login enable, QQ login enable, GitHub Client ID, QQ App ID, configured-state display, and blank-secret preservation.
- Settings staging still excludes secret changes from local `pendingOperations`.

Backend/API changes:

- Added generic visitor auth cookie support while preserving existing GitHub endpoints.
- Added `GET /api/auth/visitor/me` and `POST /api/auth/visitor/logout`.
- Added QQ OAuth entry points: `GET /api/auth/qq/login` and `GET /api/auth/qq/callback`.
- Public settings now expose `comments.provider="multi"`, `githubLoginConfigured`, and `qqLoginConfigured` as booleans only.
- Comment creation now requires generic visitor login and records `provider` plus `providerId`; old comments remain compatible.
- Comment resources now include `music` and `photos`.
- Added `QQ_OAUTH_APP_ID` and `QQ_OAUTH_APP_SECRET` placeholders to env templates.

Verification:

- Passed: `cd frontend && npm run build`.
- Passed: `cd admin && npm run build`.
- Passed: `python -m compileall backend\app`.
- Passed: TestClient `GET /api/settings/public` returns `comments.githubLoginConfigured` and `comments.qqLoginConfigured` as booleans and does not expose OAuth secrets.
- Passed: TestClient `GET /api/auth/visitor/me` returns configured provider states and no access token.
- Passed: TestClient `GET /api/auth/qq/login?returnTo=/music` returns 503 when QQ OAuth is not configured, without exposing secret details.
- Passed: TestClient anonymous `POST /api/comments/music/global` returns 401.
- Passed: simulated configured QQ login returns 307 to QQ OAuth and sets state cookie.
- Passed: simulated configured GitHub login still returns 307 to GitHub OAuth and sets state cookie.

Remaining:

- Real QQ OAuth and GitHub OAuth callback flows require valid provider apps and browser QA.
- Music and photowall message board placement needs browser confirmation.
- Search input height/opacity needs browser confirmation at desktop and 390px widths.

## 2026-05-03 - GitHub 留言状态、相册弹窗滚动与中枢链路修复轮

本轮目标：
- 硬修前台留言板状态判断，区分留言板开关、GitHub 登录开关、OAuth configured 状态和用户登录态。
- 彻底修复后台照片墙相册编辑弹窗无法滚动的问题。
- 恢复文章页中枢链路左右交替，并保持卡片贴靠中心线。
- 放大搜索框，移除 `Search` 字样，增加深色搜索图标按钮。

当前进度估算：
- P0：100%。
- P1：98%，留言板状态判断与未登录 401 已通过 API 验证；真实 GitHub OAuth 授权回跳仍需配置 Client ID/Secret 后人工验收。
- P2：约 94%，中枢链路、搜索框和相册弹窗细节继续收口，仍需浏览器人工确认。

前台变更：
- `CommentBox` 改为读取公开 `comments.githubLoginEnabled` 和 `comments.githubLoginConfigured` 布尔字段，留言板全站默认开启，不再把“评论开启”和“GitHub OAuth configured”混为同一状态。
- 未登录且 GitHub 已配置时显示“使用 GitHub 登录后留言”按钮；未配置时显示访客友好提示，不显示匿名输入框。
- `SearchBar` 移除左侧 `Search` 字样，搜索框继续加长，右侧增加深色搜索图标按钮。
- 文章页搜索区宽度提升到桌面内容区约 82%；搜索页同样使用更大的输入框与图标按钮。
- 文章页中枢链路改回逐条纵向左右交替，左侧卡片右边缘贴近中心线，右侧卡片左边缘贴近中心线。

后台变更：
- 设置中心评论区增加独立“开启留言板”和“启用 GitHub 登录留言”状态，保存时写入 `comments.enabled` 与 `comments.githubLoginEnabled`。
- 照片墙相册编辑弹窗改为 85vh 固定高度，外层不滚动裁切，中间内容区独立 `overflow-y:auto`，底部保存/关闭按钮保留在可见区域。

后端/API 变更：
- `GET /api/settings/public` 的 `comments` 增加 `provider: "github"`、`githubLoginEnabled`、`githubLoginConfigured`，其中 configured 仅为布尔值，不返回 OAuth Secret。
- `GET /api/auth/github/login` 保持 `returnTo` 前台回跳参数，未配置时返回统一错误结构；已配置时由后端重定向到 GitHub OAuth。

文档变更：
- 更新 `HISTORY.md`、`docs/XINGHUI_PARITY_MATRIX.md`、`docs/API_CONTRACT.md`、`docs/SECURITY_NOTES.md`、`docs/USER_GUIDE.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/UI_STYLE_GUIDE.md`、`README.md`。

验证结果：
- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：`GET /api/settings/public` 返回 `comments.githubLoginConfigured` 布尔值，且未匹配 Secret 字段。
- 通过：直接调用 `public_settings` 模拟 GitHub Client ID/Secret 存在时，`comments.githubLoginConfigured` 为 `true` 且未回显 Secret。
- 通过：`GET /api/auth/github/me` 未登录状态返回 `{"configured":false,"user":null}`。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401。
- 通过：模拟已配置 GitHub OAuth 时，`GET /api/auth/github/login?returnTo=/posts/vue-fastapi-blog` 返回 GitHub 授权 307 并写入回跳 cookie。
- 通过：构建产物 Secret 固定字符串搜索未匹配 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`、`github_oauth_client_secret`、`change-me`。

遗留问题：
- 本轮未启动 dev server 做浏览器人工回归；前台 GitHub 登录按钮、照片弹窗滚动、中枢链路左右交替、搜索图标按钮和 390px 移动端仍需用户确认。
- 真实 GitHub OAuth code flow 仍需配置有效 Client ID/Secret 后验收。

## 2026-05-03 - 留言板 GitHub 入口硬修、相册滚动与列表细节收口轮

本轮目标：
- 修复前台留言板 GitHub 登录入口与访客视角未配置提示。
- 修复照片墙相册编辑弹窗内容过长时无法滚动的问题。
- 收口文章卡片标签沉底、中枢链路卡片比例、搜索/标题容器轻量化。
- 为首页播放器和音乐页播放器增加共享全局音量、静音和 localStorage 持久化。

当前进度估算：
- P0：100%。
- P1：98%，前台留言板入口、匿名 401 和 `returnTo` 登录入口已修复；GitHub OAuth 真实授权仍需配置 Client ID/Secret 后做浏览器人工验收。
- P2：约 93%，本轮完成列表页细节和相册弹窗滚动收口，仍需用户确认 390px 与真实浏览器视觉细节。

前台变更：
- `CommentBox` 重写为前台“留言板”组件：未登录时只显示“使用 GitHub 登录后留言”入口或访客友好的未开启提示，不再显示匿名输入框；登录跳转改为 `/api/auth/github/login?returnTo=当前前台路径`。
- 首页和 `/music` 播放器新增音量滑杆与静音按钮，复用 `player` 全局状态并写入 `localStorage`，切换页面后音量保持一致。
- 搜索输入框恢复正常输入框样式，页面标题/搜索区域外层通过 `page-title-block` 取消厚重边框和背景填充。
- 文章“中枢链路”模式卡片宽度收窄到约三分之一，并改为与矩阵网格一致的上图下文结构。
- 文章、杂谈、搜索结果等卡片标签区使用 flex + `mt-auto` 固定靠近卡片底部。
- 非首页主要页面标题区增加轻量化样式，不再使用大毛玻璃卡片包住标题。

后台变更：
- 结构化内容编辑弹窗改为固定 85vh 内部滚动结构，主体内容可纵向滚动，照片墙相册组大量缩略图不会被裁切，也不会把操作按钮挤出屏幕。
- 相册组编辑的增加、删除、拖动排序和设置封面逻辑保持不变。

后端/API 变更：
- `GET /api/auth/github/login` 现在优先支持 `returnTo` 参数，同时兼容旧的 `return_to`；相对路径会解析到前台来源，并限制绝对回跳地址只能来自允许来源。
- TestClient 验证：`GET /api/auth/github/me` 当前返回 `configured=false`，匿名留言提交继续返回 401；模拟已配置 OAuth 时 `/api/auth/github/login?returnTo=/posts/vue-fastapi-blog` 返回 307 并写入回跳 cookie。

文档变更：
- 更新 `HISTORY.md`、`docs/XINGHUI_PARITY_MATRIX.md`、`docs/UI_STYLE_GUIDE.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/API_CONTRACT.md`、`docs/SECURITY_NOTES.md`、`docs/USER_GUIDE.md`、`README.md`。

验证结果：
- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：FastAPI TestClient `GET /api/settings/public` 返回 200。
- 通过：FastAPI TestClient `GET /api/auth/github/me` 返回 `{"configured":false,"user":null}`。
- 通过：FastAPI TestClient `GET /api/auth/github/login?returnTo=/posts/vue-fastapi-blog` 未配置时返回 503，不泄露 Secret；模拟已配置时返回 GitHub 授权 307。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401。
- 通过：构建产物 Secret 固定字符串搜索未匹配 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`、`github_oauth_client_secret`、`change-me`。

遗留问题：
- 本轮未启动 dev server 做完整浏览器人工回归；前台留言板 GitHub 真实 OAuth 回跳、照片弹窗滚动、卡片沉底、中枢链路比例、标题轻量化、播放器音量控件和 390px 移动端仍需用户在浏览器中确认。
- GitHub OAuth 真实 code flow 需要配置 Client ID/Secret 后才能完整验收。
## 2026-05-03 - 留言体系收口 + 相册后台编辑 + 列表页细节统一轮

本轮目标：

- 将评论区统一为前台“留言板”体验，文案面向访客。
- 补全后台照片墙相册组编辑预览，确保封面也作为组内照片展示。
- 收口首页播放器图标按钮、名片 hover、卡片标签沉底、顶部导航和文章页双显示模式。

当前进度估算：

- P0：100%。
- P1：约 98%，GitHub OAuth 真实授权仍需配置后浏览器人工验收。
- P2：约 92%，本轮完成留言板 UI、文章双模式、轻量搜索栏和相册编辑预览补强，仍需人工确认视觉细节。

前台变更：

- `CommentBox` 重写为“留言板”：顶部标题、副标题、留言列表、GitHub 头像/用户名、访客状态、登录按钮、退出登录和发布留言区域统一。
- GitHub OAuth 未配置时的前台文案改为：“站点暂未开启 GitHub 登录留言，请稍后再试或联系站点管理员。”，不再使用后台配置视角文案。
- 顶部导航移除“归档”入口；`/archive` 页面仍可直接访问，SEO 和站内深链不受影响。
- 首页和音乐页播放器按钮去掉边框和背景，只保留图标，hover 变色/放大。
- 名片文章/杂谈/照片统计项 hover scale 提升到 1.5，仍不增加边框和背景。
- `PostList` 标签区使用 `mt-auto` 下沉到卡片底部。
- 文章页新增“矩阵网格 / 中枢链路”显示模式；中枢链路按时间线纵向排列，卡片左右交替，移动端退化为单列。
- 大搜索栏进一步轻量化，去掉外框和背景填充，仅保留底线、搜索标识、placeholder 和输入能力。

后台变更：

- `StructuredJsonManager` 在编辑相册时会把封面 URL 合并进组内照片列表，确保封面/第一张照片也显示为缩略图。
- 删除组内照片时先记录被删项，再更新封面，避免删除封面时封面状态不同步。

后端/API 变更：

- 本轮未新增后端接口。
- 通过 TestClient 确认未登录留言提交继续返回 401，GitHub OAuth 未配置状态为 `configured=false`。

文档变更：

- 更新 `HISTORY.md`、`docs/XINGHUI_PARITY_MATRIX.md`、`docs/UI_STYLE_GUIDE.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/API_CONTRACT.md`、`docs/SECURITY_NOTES.md`、`docs/USER_GUIDE.md`、`README.md`。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：FastAPI TestClient `GET /api/auth/github/me` 返回 `{"configured": false, "user": null}`。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401。
- 通过：构建产物 Secret 固定字符串搜索未匹配 `change-me`、`please-change-this-secret`、`JWT_SECRET=`、`ADMIN_PASSWORD=`、`GITHUB_OAUTH_CLIENT_SECRET`、`AI_A_API_KEY`、`OSS_ACCESS_KEY_SECRET`。

遗留问题：

- 本轮未启动 dev server 做完整浏览器人工回归；留言板真实 GitHub OAuth 回跳、相册组增加/删除/拖动排序、文章双模式、搜索栏视觉和 390px 移动端仍需用户确认。

## 2026-05-03 - 前台评论入口修正与列表页统一改版轮

本轮目标：

- 将 GitHub 评论登录入口收口到前台文章详情评论区，后台只保留 OAuth 配置。
- 统一文章页、杂谈页和非首页页面标题居中风格。
- 将音乐页改为左侧播放器、右侧歌词/歌单双页签布局。
- 继续精修首页音乐播放器、歌词区和名片 hover，不新增业务模块。

当前进度估算：

- P0：100%。
- P1：约 98%，真实 GitHub OAuth 授权回跳仍需配置 Client ID/Secret 后人工验收。
- P2：约 90%，本轮完成前台列表页和音乐页结构改版，仍需浏览器人工确认视觉细节。

前台变更：

- `CommentBox` 只依据 `comments.enabled` 和 GitHub 登录态控制评论入口；未登录时显示“使用 GitHub 登录后评论”，未配置 OAuth 时显示联系管理员提示，匿名评论入口保持关闭。
- 文章列表页改为居中标题/副标题、无外边框搜索栏、居中标签栏和三列图片卡片；移除 RSS 订阅按钮。
- 杂谈页改为与文章页一致的居中标题、搜索栏和三列图片卡片布局。
- `PostList` 统一为响应式图片卡片：大屏三列，中屏两列，小屏单列，封面在上、标题摘要标签在下。
- `/music` 改为左侧唱片式播放器、右侧“歌词 / 歌单”双页签，复用全局播放器状态，切换页面不销毁 audio。
- 首页音乐播放器右侧歌名、歌手、进度条和按钮居中收拢；歌词区移除 `lyrics` 字样并继续压缩高度；名片统计 hover scale 提升。
- Friends、Projects、Photowall、Search、Tags、TagDetail、Archive、Timeline、Moments、About 等非首页标题区改为居中展示。

后台变更：

- 本轮未新增后台业务模块；沿用已有 GitHub OAuth 配置、照片墙相册编辑和设置中心结构。

后端/API 变更：

- 本轮未新增后端接口。
- 通过 TestClient 确认 `GET /api/auth/github/me` 在未配置 OAuth 时返回 `configured=false`，未登录评论提交返回 401。

文档变更：

- 更新 `HISTORY.md` 和 `docs/XINGHUI_PARITY_MATRIX.md`，同步 P0/P1/P2 进度、前台 GitHub 评论、文章/杂谈/音乐页 P2 状态。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`、`docs/UI_STYLE_GUIDE.md`、`docs/USER_GUIDE.md`、`README.md`，补充前台 GitHub 评论入口、三列列表页、音乐页双栏布局和非首页标题居中验收项。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：FastAPI TestClient `GET /api/settings/public` 返回 200。
- 通过：FastAPI TestClient `GET /api/auth/github/me` 返回 `{"configured": false, "user": null}`。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401。
- 通过：构建产物 Secret 固定字符串搜索未匹配 `change-me`、`please-change-this-secret`、`JWT_SECRET=`、`ADMIN_PASSWORD=`、`GITHUB_OAUTH_CLIENT_SECRET`、`AI_A_API_KEY`、`OSS_ACCESS_KEY_SECRET`。

遗留问题：

- 本轮未启动 dev server 做完整浏览器人工回归；前台 GitHub OAuth 真实授权、相册组编辑拖拽、文章/杂谈三列视觉、音乐页双栏、390px 移动端仍需用户确认。
- GitHub OAuth 真实 code flow 需要配置 GitHub Client ID/Secret 后才能完整验收。

## 2026-05-03 - P1/P2 混合收口补修轮

本轮目标：

- 修复 Toast 仍落在页面底部的问题。
- 确认 GitHub 登录评论入口在前台文章详情，清理后台旧本地评论设置。
- 增强照片墙相册编辑、首页音乐播放器比例、歌词高度和名片 hover/tooltip。

当前进度估算：

- P0：100%。
- P1：约 99%，GitHub OAuth 真实授权回跳仍需配置 Client ID/Secret 后人工验收。
- P2：约 88%，仍需用户浏览器人工确认 Toast、首页比例和相册编辑体验。

前台变更：

- Toast 去掉 `.glass` 类依赖，改为专用 `toast-shell` fixed 顶层样式，避免被全局 `.glass { position: relative }` 覆盖。
- 前台评论区继续作为 GitHub 登录入口；未登录不显示评论输入框，未配置 OAuth 时显示“GitHub 登录未配置，请联系站点管理员”方向的提示。
- 前端评论启用逻辑只看 `comments.enabled`，不再受旧 `localEnabled` 影响。
- 首页音乐播放器改为紧凑横向结构：唱片在左，歌名、歌手、进度条和控制按钮在右；移除“今日播放”字样。
- 歌词组件高度减半，仍保持单行居中和长句字号自适应。
- 名片统计 hover 放大增强；GitHub、Email、QQ、微信图标 hover 变色并显示 tooltip，点击行为保持跳转或复制。

后台变更：

- 后台 Toast 同步去掉 `.glass` 依赖，保证顶部 fixed 显示。
- 评论设置页隐藏旧本地匿名评论、邮箱必填和邮箱显示主流程，只保留 GitHub 登录评论说明、开启评论、最大长度、GitHub Client ID/Repo/Owner 和 Secret configured 状态。
- 照片墙相册编辑支持预览组内照片、追加照片、确认删除单张照片、拖动排序、上移/下移和设为封面；每组仍最多 50 张。

后端/API 变更：

- GitHub OAuth 配置读取支持后端 `.env` 优先，也支持服务端 `settings.json` 中的 GitHub Client ID / Client Secret；Secret 仍不进入公开 settings 响应。
- 评论提交后端只检查 `comments.enabled` 和 GitHub 登录 cookie；未登录提交返回 401。

文档变更：

- 更新 `HISTORY.md`、`docs/XINGHUI_PARITY_MATRIX.md`、`docs/API_CONTRACT.md`、`docs/SECURITY_NOTES.md`、`docs/UI_STYLE_GUIDE.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/USER_GUIDE.md`，同步 GitHub-only 评论、相册编辑和 Toast 修复。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：`GET /api/settings/public` 返回 200，未匹配 `jwt_secret`、`admin_password`、`accesskeysecret`、`clientsecret`、`api_key`。
- 通过：`GET /api/auth/github/me` 返回 200；当前未配置 OAuth 时 `configured=false`。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401。
- 通过：构建产物固定 Secret 字符串搜索未匹配 `change-me`、`please-change-this-secret`、`JWT_SECRET=`、`ADMIN_PASSWORD=`、`GITHUB_OAUTH_CLIENT_SECRET`、`AI_A_API_KEY`、`OSS_ACCESS_KEY_SECRET`。
- 通过：`git diff --check` 无空白错误，仅有 Windows 换行提示。

遗留问题：

- 本轮未启动 dev server 做浏览器人工回归；Toast 顶部位置、首页音乐播放器与名片高度、相册拖动排序、GitHub OAuth 真实回跳和 390px 移动端仍需人工确认。

## 2026-05-03 - P1/P2 混合收口：GitHub 评论、全局音乐与相册组

本轮目标：

- 修复顶层 Toast、后台左侧层级导航、Markdown 分栏与字体颜色弹窗。
- 补齐点击音效设置、音乐跨页面持续播放、歌词上传、GitHub 登录评论、照片墙相册组、名片无边框化和轮播 hover 切换。
- 不改变技术栈，不新增复杂后端系统，不破坏 P0 已验收能力。

当前进度估算：

- P0：100%。
- P1：约 98%，GitHub OAuth 真实授权链路仍需配置 Client ID/Secret 后浏览器人工验收。
- P2：约 86%，仍需用户确认 Toast、后台导航、Markdown 拖拽、全局音乐、相册组和移动端视觉回归。

前台变更：

- Toast 改为 `Teleport` 到 `body` 的顶部固定层，成功为绿色、失败为红色，不再挤占页面流。
- 评论区改为 GitHub 登录后评论：未配置 OAuth 时显示未配置提示，未登录时显示 GitHub 登录按钮；匿名评论提交被后端拒绝。
- 首页和 `/music` 页面改为共享全局播放器状态，路由切换不会销毁 audio；首页播放器保留上一首、播放/暂停、下一首，移除歌单按钮。
- 首页歌词区优先读取当前歌曲的 `lyricUrl` 或内嵌 `lyrics`；无歌词时显示当前歌曲信息。
- 照片墙兼容旧单图数据，并支持相册组展示：列表显示封面，点击后进入相册预览和缩略图切换。
- 名片统计与联系方式去掉边框和填充，复制成功/失败统一走顶层 Toast。
- 首页轮播分页点支持 hover 预选切换，点击仍保留用于移动端。

后台变更：

- 左侧导航改为贴最左侧、铺满视口高度的垂直控制台侧栏；设置中心分区并入“系统 > 设置中心”的子层级。
- 设置页主体移除突兀的独立分区导航，保留当前分区内容和保存主流程。
- Markdown 编辑器左右分栏去除间距，增加可拖动分隔条；390px 下仍使用编辑/预览切换。
- Markdown 字体颜色改为自定义 popover，包含颜色选择器、文本输入和预设色，不再使用浏览器 `prompt`。
- 设置中心增加点击音效配置：启用开关、音量、音效 URL 和本地音频上传回填。
- 音乐管理增加歌词文件上传和内嵌歌词字段；照片墙管理改为相册表单，支持每组最多 50 张照片的批量上传和单张移除。

后端/API 变更：

- 新增 GitHub OAuth 评论登录接口：`/api/auth/github/login`、`/api/auth/github/callback`、`/api/auth/github/me`、`/api/auth/github/logout`。
- 评论 `POST /api/comments/{resource}/{slug}` 改为需要 GitHub 登录 cookie；新评论写入 GitHub 用户名和头像，旧评论继续展示。
- `/api/settings/public` 增加公开的 `interaction` 点击音效配置和 `githubOAuth.configured` 状态，不返回 Secret。
- 上传服务增加 `.lrc` / `.txt` 歌词文件，限制 1 MB；图片 10 MB、音频 100 MB、视频 200 MB 继续分档限制。
- `backend/.env.example` 增加 GitHub OAuth Client ID/Secret 占位字段，不填真实值。

文档变更：

- 更新本轮记录、矩阵、API 契约、安全说明、UI 风格、人工验收清单、用户手册和 README，标注 GitHub OAuth 需要服务端配置后再做真实授权验收。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有既有 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient `GET /api/health` 返回 200。
- 通过：`GET /api/settings/public` 返回 200，未匹配 Secret/Password/JWT/API Key 明文字段。
- 通过：`GET /api/auth/github/me` 返回 200；当前未配置 OAuth 时 `configured=false`。
- 通过：未登录 `POST /api/comments/posts/vue-fastapi-blog` 返回 401，匿名评论入口被后端拒绝。
- 通过：管理员登录后上传 `.lrc` 歌词文件返回 200；非法 `.exe` 上传返回 415。测试歌词文件和本轮测试审计记录随后已清理，避免留下运行时垃圾。
- 通过：构建产物 Secret 固定字符串搜索未匹配 `change-me`、`please-change-this-secret`、`JWT_SECRET=`、`ADMIN_PASSWORD=`、`GITHUB_OAUTH_CLIENT_SECRET`、`AI_A_API_KEY`、`OSS_ACCESS_KEY_SECRET`；`sk-*` 模式命中 CSS/高亮库的 `sk-image`、`sk-border` 等非 Secret 字符串。

遗留问题：

- GitHub OAuth 真实 code flow 需要配置 GitHub Client ID/Secret 后由浏览器人工验收。
- 本轮未启动 dev server 做完整浏览器人工回归；Toast、后台三级导航、Markdown 拖拽、全局音乐、歌词显示、相册组和 390px 视觉仍需用户确认。

## 2026-05-03 - P2 交互细节与后台弹窗化收口轮

本轮目标：

- 修复复制提示不可见的问题，将 Toast 改为全局顶层提示。
- 收口后台设置页导航、主题配置视觉、结构化内容弹窗化、Markdown 近全屏编辑器、上传分档限制、点击音效和冗余播放器。
- 不新增业务模块，不破坏 P0/P1 已验收能力。

当前进度估算：

- P0：100%。
- P1：100%。
- P2：约 84%，仍需用户浏览器人工确认弹窗、上传和点击音效体验。

前台变更：

- 前台 Toast 改为顶部居中固定层，`z-index` 高于普通组件，不再挤占页面布局；成功提示为绿色，失败提示为红色。
- 移除右下角冗余悬浮音乐播放器，保留首页主音乐播放器和 `/music` 页面。
- 移除跟随鼠标指针的大型光晕，保留静态氛围背景层。
- 新增可交互元素点击音效：只响应按钮、链接、表单控件、导航项等交互元素，空白点击不播放；提供“点击音”开关，音量和触发频率受控。
- 昼夜模式卡片内容改为水平/垂直居中，hover 继续保持轻微缩放。
- MarkdownRenderer 允许安全的 `style` 属性，用于受控字体颜色 span；仍继续通过 DOMPurify 清洗。

后台变更：

- 后台 Toast 同步改为顶部固定成功提示。
- `/admin/settings` 内部二级导航从左侧突出导航卡改为轻量顶部标签，不再抢占左侧主导航结构。
- 主题与背景 token 配置优化为中文名称、内部 key、小预览色块、颜色选择器和文本输入框组合；日间/夜间分组更清晰。
- 友链、项目、音乐、照片等结构化内容的新增/编辑表单改为居中弹窗；列表页默认不显示右侧常驻表单，弹窗支持遮罩关闭和未保存确认。
- Markdown 编辑器改为按钮触发的近全屏弹窗，弹窗内左侧编辑、右侧预览；390px 下可切换编辑/预览。
- Markdown 编辑器新增可收起快捷工具栏，支持加粗、斜体、无序列表、有序列表、引用、行内代码、代码块、表格、链接、图片和字体颜色插入。
- 关于页 Markdown 编辑同样改为近全屏弹窗。

后端/API 变更：

- 上传大小限制按类型分档：图片 10 MB、音频 100 MB、视频 200 MB。
- 上传仍继续校验扩展名、MIME 和大小；非法类型返回 415，超出对应类型限制返回 413。

文档变更：

- 更新 `docs/API_CONTRACT.md` 和 `docs/SECURITY_NOTES.md`，同步上传类型和大小分档限制。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`、`docs/UI_STYLE_GUIDE.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/USER_GUIDE.md`、`README.md`，记录本轮交互收口状态。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，仍有 Markdown 编辑器相关 chunk 体积提示。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient 访问 `/api/health` 返回 200 和 `{"ok":true,"app":"SRBlogs API"}`；直接探测 `127.0.0.1:8000` 时当前未发现已运行的后端进程。
- 通过：构建产物 Secret 模式静态搜索未匹配 `please-change-this-secret`、`change-me`、`changeme`、`admin123`、`password123`、`sk-*`、`AKIA*`、`-----BEGIN`、`JWT_SECRET=`、`ADMIN_PASSWORD=`。
- 待用户浏览器人工确认：顶层 Toast、后台设置页轻量标签、主题 token 视觉、90MB 音频上传、结构化内容弹窗、Markdown 弹窗工具栏、点击音效、冗余播放器移除和 390px 回归。

遗留问题：

- P2 仍不标记为完成；当前重点进入交互细节和视觉一致性人工确认阶段。

## 2026-05-03 - P2 第三阶段：轮播追平与后台结构修复轮

本轮目标：

- 优先修复后台写作页和关于页 Markdown 编辑页动态导入失败回归。
- 按人工验收要求重构首页轮播区为“文章轮播 + 照片轮播 + 更新轮播 + 独立昼夜切换卡片”。
- 收口无图组件 hover、复制提示、歌词单行自适应、后台垂直父子导航、暂存区隐藏、主题颜色选择器和本地资源上传体验。

当前进度估算：

- P0：100%。
- P1：100%，本轮修复写作页与关于页动态导入回归后恢复。
- P2：约 80%，仍需用户浏览器人工确认首页轮播、后台导航和上传体验后继续推进。

前台变更：

- 前台导航栏移除“后台入口”，后台仍可通过 `/admin/` 独立访问。
- 首页轮播区改为目标布局：左侧三分之一为最新文章轮播，右侧上层为照片墙轮播，右侧下层为最新更新轮播和独立昼夜模式卡片。
- 最新文章、照片墙和最新更新均为真实轮播，支持自动切换和分页点切换；有图轮播图片铺满卡片，文字和分页点位于图片内部。
- 无图组件 hover 统一为轻微缩放，覆盖名片、歌词区、音乐播放器、昼夜切换卡片、底部状态区等。
- 复制 email/QQ/微信成功时使用绿色提示，失败时使用错误提示。
- 歌词区强制单行居中，长句按长度自动降低字号，短句恢复较大字号。
- 首页音乐播放器保持唱片式结构，包含唱片、歌名、歌手、进度条、上一首/播放暂停/下一首图标按钮，无 URL 时显示可读提示。

后台变更：

- `/admin/editor` 和 `/admin/about` 改为静态导入关键 Markdown 页面，修复 `Failed to fetch dynamically imported module` 导致页面打不开的问题。
- 后台左侧导航改为垂直平铺的父子目录结构，包含总览、内容、互动、媒体、系统等分组。
- 右侧“操作暂存区”支持完全隐藏，隐藏后中间主操作区自动扩宽，并提供恢复入口。
- 设置中心“主题与背景”token 配置增加中文展示名称和颜色选择器，保留内部 token 键和值输入框。
- 结构化内容上传字段支持按字段指定 `accept`，音乐管理的歌曲 URL 支持本地音频/视频上传并回填 URL。

后端/API 变更：

- `/api/upload` 的允许类型从图片扩展为配置允许的图片、音频和视频文件，仍继续校验扩展名、MIME 和大小。
- 未新增复杂后端系统，未修改核心内容数据结构。

文档变更：

- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录 P2 第三阶段当前状态。
- 更新 `docs/UI_STYLE_GUIDE.md`，补充首页轮播布局、hover 规则、后台导航和上传规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充本轮人工验收项。
- 更新 `docs/API_CONTRACT.md` 和 `docs/SECURITY_NOTES.md`，同步本地上传支持图片/音频/视频。
- 更新 `docs/USER_GUIDE.md` 和 `README.md`，同步后台导航、主题配置和本地资源上传说明。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`，存在 Vite chunk 体积提示；本轮为修复关键 Markdown 页面动态导入回归，将 Editor/AboutEdit 改为静态导入。
- 通过：`python -m compileall backend\app`。
- 通过：`http://127.0.0.1:8000/api/health` 返回 `{"ok":true,"app":"SRBlogs API"}`。
- 通过：构建产物 Secret 模式静态搜索未匹配 `please-change-this-secret`、`change-me`、`changeme`、`admin123`、`password123`、`sk-*`、`AKIA*`、`-----BEGIN`、`JWT_SECRET=`、`ADMIN_PASSWORD=`。
- 待用户浏览器人工确认：首页轮播区、顶部导航动画、名片复制提示、音乐播放器、歌词区、hover 动效、后台左侧导航、设置页颜色选择器、本地资源上传和 390px 移动端。

遗留问题：

- P2 不标记为完成；本轮将 P2 从约 68% 推进到约 80%。
- 真实服务器部署、真实 OSS/Gitalk/AI 联调仍不属于本轮范围。

## 2026-05-03 - P2 首页轮播与播放器收口轮

本轮目标：

- 只修复上一轮 P2 人工验收未通过项，不新增业务模块。
- 完成首页三组轮播、唱片式音乐播放器、名片结构、歌词居中、旧首页板块移除和 hover 规则修正。
- 保持 P0/P1 已验收功能不回退。

当前进度估算：

- P0：100%。
- P1：100%。
- P2：约 72%，仍需浏览器人工确认后继续推进。

前台变更：

- 首页旧板块“内容发现、站点仪表盘、最新文章、云端杂谈、最近瞬间”已从首页移除，相关路由和功能保留。
- 首页改为固定结构：名片 + 唱片式音乐播放器、居中歌词区、三组轮播卡片、底部状态区。
- 三组首页轮播已落地：最新文章轮播、最新更新内容轮播、主题模式轮播；轮播支持自动切换和分页点切换。
- 最新文章轮播读取公开文章数据；最新更新内容聚合公开 posts/moments/chatters，继续依赖公开 API 默认排除草稿。
- ProfileCard 重构为头像、名字 Shrink、简介、文章/杂谈/照片统计链接，以及 GitHub、邮箱、QQ、微信图标操作。
- 邮箱、QQ、微信点击复制，成功/失败通过现有 toast 提示；GitHub 默认跳转 `https://github.com/ShrinkShi`。
- 首页音乐播放器改为唱片结构：唱片、歌名、歌手、进度条、上一首/播放暂停/下一首图标按钮；无 URL 时不报错并显示提示。
- 歌词区改为水平居中和视觉垂直居中；无歌词时显示当前歌曲信息或占位文案。
- 顶部导航收起/展开动画放慢到约 560ms，滚动隐藏、上滚显示和鼠标到顶部显示逻辑不变。
- hover 规则调整：有图组件 hover 只放大图片；无图组件 hover 轻微缩放组件本体，不再以上移作为主效果。

后端/API 变更：

- 本轮未新增后端接口。
- 本轮未修改后端数据结构。

文档变更：

- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录本轮 P2 首页轮播与播放器收口状态。
- 更新 `docs/UI_STYLE_GUIDE.md`，补充首页轮播、唱片播放器和 hover 规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充本轮人工验收项。
- 更新 `README.md`，同步首页 P2 结构说明。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 已尝试：`http://127.0.0.1:8000/api/health` 当前未连接到后端运行进程，本轮未强制启动常驻后端。
- 通过：构建产物真实密钥模式静态搜索未匹配 `please-change-this-secret`、`change-me`、`changeme`、`admin123`、`password123`、长格式 `sk-*`、`AKIA*`、`-----BEGIN`、`JWT_SECRET=`、`ADMIN_PASSWORD=`。
- 说明：宽泛搜索 Secret 字段名会命中后台设置页的表单字段标识，这不是 Secret 明文泄露；本轮按真实密钥值和默认敏感占位符模式验证。

遗留问题：

- 首页三组轮播、唱片播放器、名片复制、hover、390px 移动端和顶部导航慢动画仍需用户浏览器人工确认。
- P2 不标记为完成；本轮仅将 P2 从约 62% 推进到约 72% 的实现状态。

## 2026-05-03 - P2 第二阶段：首页结构追平与昼夜主题系统轮

本轮目标：

- 将首页从基础视觉统一推进到更接近目标的结构：铺满式顶栏、名片 + 音乐播放器、歌词区、不对称内容模块、昼夜模式卡和底部状态区。
- 建立昼夜模式 CSS token 体系，并让设置中心支持核心主题 token、字体和字号配置。
- 保持 P0/P1 已验收功能不回退，不新增复杂后端系统，不引入大型动画库或 3D。

当前进度估算：

- P0：100%。
- P1：100%。
- P2：约 74%。

前台变更：

- `AppNav` 改为铺满式玻璃顶栏，内部与 `sr-page-shell` 对齐；支持向下滚动隐藏、向上滚动显示、鼠标移到顶部区域显示。
- `Home` 重组为：第一排 ProfileCard + 首页音乐播放器，第二排歌词/播放状态区，第三排最新文章 + 最新更新内容 + 昼夜模式卡片，随后保留内容发现、站点统计、最新文章/杂谈、动态和底部状态区。
- 首页“最新更新内容”复用公开 `posts`、`moments`、`chatters` 聚合并按日期排序；公开 API 默认排除草稿。
- 首页底部新增北京时间实时显示、网站运行时间和技术栈展示。
- 新增昼夜模式本地偏好 `sr-color-mode`，首页模式卡可一键切换日间/夜间。
- `App.vue` 根据公开 `themeConfig` 和当前昼夜模式写入 CSS 变量，支持字体族和字号档位。

后台变更：

- `/admin/settings` 的“主题与背景”分区新增字体族、字号档位、日间 token、夜间 token 表单。
- 主题 token 作为公开视觉配置保存，不进入 Secret 体系；Secret 输入和保留规则不变。

后端/API 变更：

- `GET /api/settings/public` 新增公开字段 `themeConfig`，只包含颜色、字体和字号等非敏感 token。
- 未新增复杂后端接口；首页最新更新流由前端复用现有公开 API 聚合。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充 `themeConfig` 公开契约。
- 更新 `docs/UI_STYLE_GUIDE.md`，补充铺满式顶栏、首页结构、昼夜 token 体系。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`、`docs/RELEASE_CHECKLIST.md`，补充首页结构、顶栏滚动、昼夜模式和主题配置验收项。
- 更新 `docs/USER_GUIDE.md`，补充主题与昼夜模式配置说明。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步 P2 约 74% 和主题配置矩阵项。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient 访问 `/api/health` 返回 200 和 `ok=true`。
- 通过：`GET /api/settings/public` 返回 200，且包含 `themeConfig`。
- 通过：构建产物 Secret 静态搜索未匹配 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me`。

遗留问题：

- 首页结构、昼夜模式、顶部导航滚动隐藏/显示、后台设置页主题配置、390px 移动端仍需浏览器人工验收。
- 当前昼夜模式为 CSS token 体系，少量旧页面仍存在历史 Tailwind 颜色类，后续 P2 可继续做全站 token 化细化。
- 未做真实歌词解析；无歌词字段时歌词区展示当前歌曲信息和播放状态。

## 2026-05-02 - P2 视觉统一与氛围增强轮

本轮目标：

- 在 P0/P1 均已收口到 100% 的基础上，正式恢复 P2 推进。
- 系统化整理前台毛玻璃 token、卡片 hover、按钮、标签、阅读页层次和现有氛围动效控制。
- 提升后台控制台质感，但不改变后台主流程、不新增业务模块、不新增后端接口。

当前进度估算：

- P0：100%。
- P1：100%。
- P2：约 62%。

前台变更：

- `frontend/src/styles.css` 新增统一视觉 token 和工具类：`sr-card`、`sr-card-hover`、`sr-hero-panel`、`sr-chip`、`sr-button-primary`、`sr-button-ghost`、状态色和 reduced-motion 规则。
- `GlassCard` 默认接入统一 `sr-card`，hover 状态改为统一 `sr-card-hover`。
- 首页 Hero 增强为统一 hero panel，主要按钮、内容发现入口、技术栈卡、ProfileCard、SiteDashboard 和最新文章卡片接入统一动效。
- 文章详情标题区与 Markdown 正文阅读区增加更清楚的视觉层级，标签样式统一为 `sr-chip-cyan`。
- 背景控制增加“氛围”开关；`Sakura`、`Fireflies`、`CyberCat`、点击光效均尊重本地 `sr-ambience` 设置。
- 移动端默认隐藏樱花、萤火等装饰层，弹幕密度降低，避免遮挡阅读区。

后台变更：

- `admin/src/styles.css` 增加后台视觉 token、`admin-card-hover`、状态色、危险按钮、输入 focus 和 reduced-motion 规则。
- 后台侧边栏 active 状态增加边框和左侧高亮，强调当前控制台位置。
- 后台继续保持工具型布局，不改变审计日志、备份恢复、评论管理、写作和设置中心主流程。

后端/API 变更：

- 本轮未新增后端接口。
- 本轮未修改后端数据结构。

文档变更：

- 更新 `docs/UI_STYLE_GUIDE.md`，记录 P2 视觉 token、氛围开关、卡片动效、后台控制台和移动端规则。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，将 P2 从冻结调整为系统化推进中，并记录当前 P2 进度。
- 更新 `docs/MANUAL_QA_CHECKLIST.md` 和 `docs/RELEASE_CHECKLIST.md`，补充 P2 视觉回归、关闭/降低动效、移动端和后台控制台检查项。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient 访问 `/api/health` 返回 200 和 `ok=true`。
- 通过：构建产物 Secret 静态搜索未匹配 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me`。
- 待执行：前台首页、文章详情、搜索/标签/归档、媒体页、后台主要页面和 390px 移动端浏览器人工回归。
- 待执行：关闭/降低动效后的浏览器人工检查。

遗留问题：

- P2 本轮只做现有视觉系统化和氛围控制，不做新增特效库、不做 3D、不做大型动画。
- MarkdownRenderer 与 MarkdownEditor chunk 仍较大，沿用此前记录，后续如需要再单独做体积拆分。
- P2 不标记为完成，需用户确认首页、文章阅读页、后台控制台和移动端视觉回归后继续推进。

## 2026-05-02 - P1 最终微调与真实使用清单轮

本轮目标：

- 在 P0 已收口到 100% 的基础上，将 P1 从 98% 收口到 100%。
- 减少真实日常使用摩擦，统一后台操作反馈，清理明显测试残留，并补齐真实使用手册。
- 不新增业务模块，不新增前台页面，不新增 P2 视觉特效。

当前进度估算：

- P0：100%。
- P1：100%。
- P2：40%，冻结。

前台变更：

- 未新增前台页面或视觉特效。
- 保持搜索、标签、归档、RSS/Sitemap/robots、评论和文章详情等已验收链路不变。

后台变更：

- 后台 API 错误拦截补充 401/403 可读提示：登录失效会提示重新登录，权限不足会提示确认管理员权限。
- 写作页保存成功提示区分草稿和已发布状态，slug 输入旁增加用途和字符规则说明，草稿勾选文案直接说明前台是否可见。
- 文章管理的发布、撤回和删除确认文案更明确，说明前台可见性变化、删除后 404 和备份恢复成本。
- 评论删除确认文案补充“直接写回后端 JSON、覆盖前备份”，删除成功提示说明索引和列表已刷新。
- 备份恢复页补充创建备份后的外部保存建议、下载成功提示和恢复风险确认。
- 设置中心顶部说明公开设置和私有 Secret 边界，强调 Secret 输入框留空会保留旧值。

后端/API 变更：

- 本轮未新增后端接口。
- 保持所有 JSON/Markdown 写入继续走既有安全写入封装。

文档与清理变更：

- 新增 `docs/USER_GUIDE.md`，覆盖登录后台、新建文章、保存草稿、发布、编辑、删除、评论管理、媒体管理、站点设置、备份、恢复、审计日志、前台搜索/标签/归档、RSS/Sitemap/robots 和常见问题。
- 更新 `.gitignore`，忽略 `backend/data/.manual_backups/*`、`backend/data/**/.backups/*`、`backend/data/audit/*.log`、`*.tsbuildinfo`、`*.tmp`、`*.bak` 等运行时产物。
- 更新 `README.md`，加入真实使用手册入口，并说明演示数据用途和运行时备份/审计/上传缓存不应作为发布代码提交。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步 P0 100%、P1 100%、P2 40% 冻结；P1 后续仅保留长期优化。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：前台主要页面 HTTP 快速回归。
- 通过：后台主要页面 HTTP 快速回归。
- 通过：完整内容生产流抽查。
- 通过：备份恢复抽查。
- 通过：审计日志抽查。
- 通过：构建产物 Secret 搜索。
- 通过：`git status --short` 检查，运行时备份、`.backups`、审计日志和 `tsbuildinfo` 已由 `.gitignore` 防止后续误提交；当前仅保留源码/文档变更以及删除旧验证残留的清理记录。

遗留问题：

- P2 视觉增强继续冻结，不推进樱花、弹幕、CyberCat、动态背景等系统化增强。
- 真实服务器、域名和 HTTPS 部署实操仍保持 `部署实操待执行`。
- P1 后续只保留长期优化项，例如更细的端到端浏览器自动化、体积拆分和真实生产环境演练。

## 2026-05-02 - 最终总回归与真实部署准备轮

本轮目标：

- 冻结 P2，完成 P0/P1 最终收口前的全项目总回归。
- 验证完整内容生产演示流、数据安全、备份恢复、部署准备和文档一致性。
- 不新增业务功能，不新增视觉特效，不重构已通过人工验收的模块。

当前进度估算：

- P0：约 100%。
- P1：约 98%。
- P2：40%，冻结。

前台变更：

- 未新增前台页面或 P2 视觉特效。
- 使用当前 5173 服务对主要前台路径完成 HTTP 快速回归：`/`、`/posts`、`/posts/vue-fastapi-blog`、`/moments`、`/chatters`、`/friends`、`/projects`、`/music`、`/photowall`、`/about`、`/timeline`、`/search`、`/tags`、`/tags/Vue`、`/archive`、不存在路由均返回 SPA 壳 200。
- API 级确认不存在文章和不存在杂谈 slug 返回 404。

后台变更：

- 未重构后台主流程。
- 使用当前 5174 服务对后台路径完成 HTTP 快速回归：`/admin/`、`/admin/editor`、`/admin/posts`、`/admin/comments`、`/admin/friends`、`/admin/projects`、`/admin/music`、`/admin/photos`、`/admin/settings`、`/admin/audit`、`/admin/backups` 均返回 SPA 壳 200。
- 根据用户人工验收结果，后台写作、草稿、发布/撤回、删除文章和 pendingOperations 第一阶段已通过，本轮同步矩阵状态。

后端/API 变更：

- 本轮未新增后端业务接口。
- 完整内容生产演示流通过 TestClient 验证：登录、新建草稿、前台隐藏草稿、发布文章、公开列表/详情可见、提交评论、后台评论索引可见、删除评论、前台评论消失、编辑文章、前台详情更新、撤回发布、公开详情 404、删除文章、审计日志记录完整。
- 备份恢复通过 TestClient 验证：创建手动备份、列表可见、下载 zip、zip 不包含 `.env`、`settings.json` 备份内容已清洗 Secret 关键字段、恢复前自动创建 `pre-restore-*.zip`、非法备份名路径穿越被拒绝。

文档变更：

- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，将文章列表、文章详情、后台仪表盘、Markdown 编辑器、草稿、暂存队列按已通过人工验收结果标记为 `已完成`。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，将部署文档从整体完成调整为 `部署实操待执行`：文档、脚本、Nginx、systemd、env 模板已核验，但真实服务器、域名和 HTTPS 实操不在本轮执行。
- 更新 `README.md`、`docs/MANUAL_QA_CHECKLIST.md`、`docs/RELEASE_CHECKLIST.md`、`docs/RELEASE_NOTES.md`，同步最终回归、发布准备、P0/P1/P2 进度和部署实操待执行状态。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：TestClient `/api/health` 返回 200。
- 通过：TestClient `/api/rss.xml`、`/api/sitemap.xml`、`/robots.txt` 返回 200；`robots.txt` 包含 `Disallow: /admin`。
- 通过：`GET /api/settings/public` 和管理员 `GET /api/admin/settings` 不包含当前 `backend/.env` 中的非空 Secret 值。
- 通过：`GET /api/posts`、`GET /api/search?q=vue`、`GET /api/tags`、`GET /api/archive`、`GET /api/friends`、`GET /api/projects`、`GET /api/music`、`GET /api/photos` 均返回 200。
- 通过：完整内容生产演示流，包含草稿、发布、评论、删除评论、编辑、撤回发布、删除文章、审计日志。
- 通过：手动备份、备份列表、下载备份、恢复备份、恢复前备份、路径穿越拒绝。
- 通过：`frontend/dist` 和 `admin/dist` 生成成功；构建产物 Secret 值静态扫描未命中。
- 通过：`backend/.env.production.example` 不含开发默认 Secret，明确要求生产修改 `ADMIN_PASSWORD` 和 `JWT_SECRET`。
- 通过：`deploy/nginx.srblogs.conf` 包含前台、后台、`/api/`、`/uploads/`、`client_max_body_size`；`deploy/srblogs-backend.service` 未包含本地 Windows 路径。
- 已尝试但未执行：Edge headless 390px 检查受本机权限限制失败，工具侧无法完成真实浏览器像素级验证；本轮保留用户人工验收作为最终依据。

遗留问题：

- P2 视觉增强继续冻结，不进入系统化增强。
- 真实服务器部署、域名和 HTTPS 实操仍标记为 `部署实操待执行`；当前完成的是部署准备、脚本和文档核验。
- 本轮验证按要求产生了审计日志、手动备份 zip、恢复前备份 zip、评论空文件和文章删除备份，作为数据写入、备份和审计验证痕迹保留。

## 2026-05-02 - 后台写作、草稿与暂存队列最终收口轮

本轮目标：

- 冻结 P2，继续收口 P0/P1。
- 补齐后台文章管理、写作页、草稿发布/撤回、文章删除和 pendingOperations 第一阶段的验收缺口。
- 不新增业务模块，不新增视觉特效，不重构已通过验收的媒体、评论、搜索、SEO、审计和备份恢复模块。

当前进度估算：

- P0：约 98%。
- P1：约 92%。
- P2：40%，冻结。

前台变更：

- 未新增前台页面或视觉特效。
- 公开文章详情现在不会返回 `draft=true` 内容；草稿详情公开访问返回 404。

后台变更：

- `/admin/posts` 文章管理补齐标题/slug 搜索、更新时间展示、发布、设为草稿、暂存发布、暂存删除、删除错误提示和草稿不可公开预览提示。
- `/admin/editor` 保存前新增 Markdown 内容不能为空校验。
- `pendingOperations` 新增“一键应用全部”。
- `pendingOperations` 第一阶段新增非 Secret 设置修改暂存；Secret 修改、图片上传、评论管理仍明确不进入本地暂存队列。
- 后台详情读取草稿时显式传 `include_drafts=true` 并依赖管理员 JWT。

后端/API 变更：

- `ContentItem` 增加 `updatedAt` 字段，来自 Markdown 文件 mtime。
- `GET /api/posts`、`/api/moments`、`/api/chatters` 的 `include_drafts=true` 现在必须携带管理员 JWT；未登录返回 401。
- `GET /api/posts/{slug}` 等详情接口默认只返回已发布内容；草稿公开详情返回 404。
- 管理端可携带 JWT 并传 `include_drafts=true` 读取草稿详情。
- 发布、撤回发布、编辑、删除继续写审计日志；删除前继续备份 Markdown 文件。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充 `include_drafts=true` 的管理员 JWT 要求、草稿公开 404、`updatedAt`、重复 slug 409、非法 slug 400、更新/删除不存在 404、发布/撤回审计说明。
- 更新 `docs/SECURITY_NOTES.md`，补充公开接口不得返回草稿、`include_drafts=true` 必须管理员 JWT、文章发布/撤回/删除审计和删除前备份规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充文章列表搜索、更新时间、撤回发布、一键应用全部和非 Secret 设置暂存验收项。
- 更新 `docs/RELEASE_CHECKLIST.md`，补充草稿保护、状态切换、错误码、审计和 pendingOperations 检查项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步当前进度估算；后台写作、草稿、暂存队列保持 `进行中`，等待用户最终人工验收后再标记完成。
- 更新 `README.md`，同步设置中心剩余项已通过、后台写作/草稿/暂存队列等待最终人工验收的状态。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：TestClient `GET /api/health` 返回 200，`{"ok": true, "app": "SRBlogs API"}`。
- 通过：后台新建草稿文章，`backend/data/posts/{slug}.md` 实际生成。
- 通过：前台 `GET /api/posts` 不显示草稿。
- 通过：公开 `GET /api/posts/{slug}` 对草稿返回 404。
- 通过：未登录传 `include_drafts=true` 返回 401；管理员 JWT 下列表和详情可读取草稿。
- 通过：后台发布草稿后，前台 `/api/posts` 显示文章，公开详情可读取正文。
- 通过：后台编辑已发布文章后，公开详情正文更新。
- 通过：后台撤回发布后，前台 `/api/posts` 不显示文章，公开详情返回 404。
- 通过：后台删除文章后，前台列表不显示，公开详情返回 404。
- 通过：删除文章前 `backend/data/posts/.backups` 生成备份，本轮验证备份增量为 1。
- 通过：重复 slug 返回 409。
- 通过：非法 slug 返回 400。
- 通过：删除不存在文章返回 404。
- 通过：审计日志包含 `posts.create`、`posts.publish`、`posts.update`、`posts.unpublish`、`posts.delete`，并包含重复创建和删除不存在的 failed 记录。
- 通过：源码/构建检查确认 pendingOperations 覆盖 `createPost`、`editPost`、`deletePost`、`publishDraft`、`updateSettings`，支持单项应用、移除、失败重试和一键应用全部。
- 通过：构建产物 Secret 值静态搜索，未发现 `backend/.env` 中非空 Secret 值进入 `frontend/dist` 或 `admin/dist`。

遗留问题：

- 本轮没有启动浏览器人工验收；后台写作、草稿、暂存队列在 `docs/XINGHUI_PARITY_MATRIX.md` 中保持 `进行中`。
- pendingOperations 是第一阶段前端本地队列，刷新页面会丢失；服务端持久化队列仍不在本轮范围。
- 本轮验证生成了文章删除备份和审计日志，作为写入/备份/审计验收痕迹保留。

## 2026-05-02 - 发布候选与部署演练轮

本轮目标：

- 将 SRBlogs 整理为可交付、可部署、可演示的发布候选版本。
- 补齐生产环境变量模板、Linux 部署资产、生产健康检查、目录/日志规范、发布清单和发布说明。
- 不新增业务功能，不新增 P2 视觉特效，不处理设置中心此前延期项。

前台变更：

- 未改动前台业务页面和视觉特效。
- 重新执行前台生产构建，生成 `frontend/dist`。

后台变更：

- 未改动已通过验收的后台业务主流程。
- 重新执行后台生产构建，生成 `admin/dist`。

后端/API 变更：

- 新增 `GET /api/admin/system/status`，需要管理员 JWT，返回 app、环境、data/uploads 目录存在性和读写状态，不返回 Secret。
- `backend/app/config.py` 新增 `UPLOAD_MAX_SIZE` 和 `UPLOAD_ALLOWED_TYPES` 配置项。
- 上传服务改为读取后端配置中的上传大小和 MIME 白名单，仍保持扩展名、MIME、大小限制。

部署与配置变更：

- 新增 `backend/.env.production.example`，包含 APP、DATA_DIR、PUBLIC_BASE_URL、管理员、JWT、CORS、上传、AI、OSS、GitHub OAuth 占位字段，并明确生产必须修改 `ADMIN_PASSWORD` 和 `JWT_SECRET`。
- 新增 `deploy/build-all.sh`、`deploy/start-backend.sh`、`deploy/srblogs-backend.service`、`deploy/nginx.srblogs.conf`、`deploy/healthcheck.sh`、`deploy/README.md`。
- 同步修复 `deploy/nginx/srblogs.conf`、`deploy/systemd/srblogs.service`、`deploy/setup.sh`，统一使用 `/opt/srblogs` 和 `/etc/srblogs/backend.env` 占位路径，不写死本机 Windows 路径。

文档变更：

- 新增 `docs/PRODUCTION_CHECKLIST.md`。
- 新增 `CHANGELOG.md`。
- 新增 `docs/RELEASE_NOTES.md`。
- 更新 `README.md`，补充生产 env 模板、deploy 目录、生产检查清单和审计/备份已通过状态。
- 更新 `WINDOWS_START.md`，指向生产 env 模板、deploy 文档和生产检查清单。
- 更新 `docs/DEPLOYMENT.md`，统一生产部署流程、Nginx、systemd、healthcheck、目录、日志和生产预检说明。
- 更新 `docs/API_CONTRACT.md`，补充 `GET /api/admin/system/status`。
- 更新 `docs/SECURITY_NOTES.md`，补充生产部署安全规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md` 和 `docs/RELEASE_CHECKLIST.md`，补充发布候选与生产部署检查项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，将审计日志与备份恢复标记为 `已完成`；部署文档继续保持 `延期/未验收`，因为本轮不做真实服务器部署和 HTTPS 实操。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端并访问 `http://127.0.0.1:8000/api/health`，返回 200；验证后已停止临时进程。
- 通过：真实 HTTP `GET /api/rss.xml` 返回 200，`Content-Type=application/rss+xml; charset=utf-8`。
- 通过：真实 HTTP `GET /api/sitemap.xml` 返回 200，`Content-Type=application/xml; charset=utf-8`。
- 通过：真实 HTTP `GET /robots.txt` 返回 200，`Content-Type=text/plain; charset=utf-8`。
- 通过：真实 HTTP `GET /api/settings/public` 返回 200。
- 通过：TestClient `GET /api/settings/public` 未匹配 `admin_password`、`jwt_secret`、`api_key`、`accessKeySecret`、`clientSecret`、`githubOAuthSecret`、`authorization` 等敏感字段名。
- 通过：登录后 TestClient `GET /api/admin/system/status` 返回 200，包含 `app`、`backendRunning`、`environment`、`dataPath`、`uploads`、`version`。
- 通过：构建产物 Secret 值静态搜索，未发现 `backend/.env` 中非空 Secret 值进入 `frontend/dist` 或 `admin/dist`。
- 通过：`deploy/nginx.srblogs.conf` 静态检查包含 `/admin/`、`/api/`、`/uploads/`、`/robots.txt`、gzip、缓存、`client_max_body_size` 和后端反代。
- 通过：`deploy/srblogs-backend.service` 和 `deploy/systemd/srblogs.service` 未匹配本地 Windows 路径。
- 通过：`backend/.env.production.example` 未匹配开发默认 `ADMIN_PASSWORD=change-me` 或 `JWT_SECRET=please-change-this-secret`，AI/OSS/GitHub Secret 字段为空占位。
- 通过：`docs/PRODUCTION_CHECKLIST.md` 覆盖构建、环境变量、Secret、CORS、后端健康、Nginx、systemd、前台、后台、RSS/Sitemap/robots、上传、审计、备份、恢复、回滚和已知延期项。
- 已清理：临时后端 HTTP 探测日志文件；未留下 8000 监听进程。

遗留问题：

- 本轮按要求不做真实服务器部署、真实域名 HTTPS 申请、云端备份、OSS/Gitalk/AI 真实联调。
- 设置中心此前跳过的空 Secret 不覆盖、评论开关、图床设置与上传流程、AI 设置、部署文档完整实操核验继续保持 `延期/未验收`。
- 后端系统状态接口验证时产生登录审计记录，`backend/data/audit/audit.log` 有正常审计写入。

## 2026-05-02 - 管理端审计日志与数据备份恢复轮

本轮目标：

- 提升后台数据安全和可恢复能力。
- 新增后台操作审计日志、手动备份、备份列表、备份下载、恢复前自动备份、恢复备份、导入导出。
- 不新增前台视觉特效，不扩展前台新业务页面，不处理设置中心此前延期项。

前台变更：

- 本轮未改动前台业务页面和视觉特效。

后台变更：

- 新增 `/admin/audit` 审计日志页面，支持 action/resource/关键词筛选、加载更多、加载/空/错误状态和失败日志状态标识。
- 新增 `/admin/backups` 备份恢复页面，支持创建手动备份、备份列表、下载备份、二次确认恢复、导出数据和导入 zip。
- 后台导航新增“审计”和“备份”入口。
- 备份下载使用 axios blob 请求，保留 JWT Authorization，不使用裸链接绕过鉴权。

后端/API 变更：

- 新增 `backend/app/services/audit_service.py`，审计日志写入 `backend/data/audit/audit.log`，日志字段包含 `id`、`time`、`actor`、`action`、`resource`、`target`、`result`、`message`、`ip`、`detail`。
- 新增 `backend/app/services/backup_service.py`，手动备份写入 `backend/data/.manual_backups/{timestamp}.zip`。
- 新增 `backend/app/api/admin_tools.py`。
- 新增 `GET /api/admin/audit/logs`，支持 `limit`、`offset`、`action`、`resource`、`q`。
- 新增 `POST /api/admin/backups`、`GET /api/admin/backups`、`GET /api/admin/backups/{name}/download`、`POST /api/admin/backups/{name}/restore`。
- 新增 `GET /api/admin/export` 和 `POST /api/admin/import`。
- 备份范围覆盖 posts、moments、chatters、comments、photos、friends.json、projects.json、music.json、settings.json、about.md、uploads。
- 备份排除 `.env`、`.venv`、`node_modules`、`dist`、前端源码和 `.manual_backups` 本身；`settings.json` 写入 zip 前会剔除 Secret 字段。
- 恢复和导入前自动创建 `pre-restore-*.zip`。
- 登录成功/失败、内容创建/编辑/删除、发布/撤回、评论创建/删除、settings 修改、结构化 JSON 保存、上传、备份、恢复、导入、导出均尽量写入审计日志；日志写入失败不阻断主业务。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充审计日志、备份、下载、恢复、导入导出接口契约。
- 更新 `docs/SECURITY_NOTES.md`，补充审计日志、备份 zip、Secret 剔除、路径穿越防护和恢复前备份规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，增加审计日志与备份恢复人工验收项。
- 更新 `docs/RELEASE_CHECKLIST.md`，增加发布前审计和备份恢复检查。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，新增审计日志与备份恢复模块，状态保持 `进行中`。
- 更新 `README.md`，补充后台审计/备份路由和数据目录说明。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：TestClient 登录后 `POST /api/admin/backups` 创建备份，返回 `20260502215203745663.zip`。
- 通过：`GET /api/admin/backups` 返回备份列表。
- 通过：`GET /api/admin/backups/{name}/download` 返回 `application/zip`。
- 通过：备份 zip 检查不包含 `.env`。
- 通过：备份 zip 中 `settings.json` 未匹配 `secret`、`password`、`token`、`apikey`、`api_key`、`accesskey` 等敏感词。
- 通过：`POST /api/admin/backups/{name}/restore` 成功，且 `.manual_backups` 新增 `pre-restore-*.zip`。
- 通过：`GET /api/admin/export` 返回 `application/zip`。
- 通过：下载和恢复接口对 `..evil.zip`、`not-a-zip` 等非法名称返回 400。
- 通过：新增并删除一条测试评论后，`GET /api/admin/audit/logs?q=comment` 能看到 `comment.create` 和 `comment.delete`。
- 通过：`GET /api/admin/audit/logs?resource=backups` 能看到备份相关审计记录。
- 通过：构建产物真实 Secret 值扫描未命中 `backend/.env` 中敏感值。
- 未通过固定端口探测：当前工具环境中 8000、5174 未运行；尝试临时启动 uvicorn 的权限审批超时，改用 TestClient 完成 API 级验证。
- 未完成：`/admin/audit` 和 `/admin/backups` 仍需用户浏览器人工验收后才能标记完成。

遗留问题：

- 后续用户已确认审计日志与备份恢复人工验收通过，矩阵已在发布候选轮更新为 `已完成`。
- 设置中心此前跳过的空 Secret 不覆盖、评论开关、图床设置与上传、AI 设置、部署文档实操核验继续保持 `延期/未验收`。

## 2026-05-02 - 性能、可访问性与体验稳定轮

本轮目标：

- 提升前台和后台加载体验、图片性能、错误兜底、移动端可读性和基础键盘可访问性。
- 不新增 P2 视觉特效，不重构已通过验收的搜索、标签、归档、媒体、评论、Markdown、SEO/RSS/Sitemap/robots 模块。

前台变更：

- 新增 `frontend/src/components/SafeImage.vue`，统一处理图片懒加载、`alt`、解码和加载失败兜底。
- 文章列表、文章详情、ProfileCard、友链、项目、音乐、照片墙图片接入 SafeImage，降低失效图片破坏布局的风险。
- 新增 `frontend/src/components/StateBlock.vue`，文章列表、搜索、归档页面开始复用统一加载/错误状态。
- 照片墙放大预览增加 `dialog` 语义、关闭按钮和 Esc 关闭，缩小移动端误阻塞风险。
- 评论表单补齐 label、autocomplete、提交中禁用、成功/失败可读反馈；继续使用文本插值展示评论，不渲染危险 HTML。
- 前台导航、背景控制、悬浮播放器、CloudPlayer、分享按钮补齐 `type` 或 `aria-label`；移动端不再启用鼠标跟随大光效。

后台变更：

- 后台主布局改为 `xl:grid-cols-[260px_minmax(0,1fr)_300px]`，避免内容列被撑破。
- 后台侧栏在窄屏和高内容场景下可滚动，减少遮挡主内容的风险。
- 暂存区按钮补齐 `type`、展开状态和可读文案；不改变 pendingOperations 行为。
- 登录表单、写作页标题/slug/日期/标签/摘要/封面输入补齐 autocomplete 或 `aria-label`。

后端/API 变更：

- 本轮未新增后端业务接口。
- 使用 TestClient 回归 `GET /api/search?q=vue`、`GET /api/rss.xml`、`GET /api/sitemap.xml`、`GET /robots.txt` 和不存在文章 slug 的 404。

文档变更：

- `docs/XINGHUI_PARITY_MATRIX.md` 标记 SEO/订阅/分享已完成，并新增性能/可访问性/体验稳定项为 `进行中`。
- `docs/MANUAL_QA_CHECKLIST.md` 增加性能、移动端、图片兜底和可访问性验收项。
- `docs/RELEASE_CHECKLIST.md` 增加性能与可访问性发布前检查。
- `README.md` 增加性能与可访问性说明。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：当前 8000 后端 `/api/health` 返回 `{"ok":true,"app":"SRBlogs API"}`。
- 通过：已有 5173 服务对 `/`、`/posts`、`/search`、`/tags`、`/archive`、`/friends`、`/projects`、`/music`、`/photowall`、`/about`、`/posts/no-such-slug` 均返回 200 SPA 壳。
- 通过：已有 5174 服务对 `/admin/`、`/admin/editor`、`/admin/posts`、`/admin/comments`、`/admin/friends`、`/admin/projects`、`/admin/music`、`/admin/photos`、`/admin/settings` 均返回 200 SPA 壳。
- 通过：TestClient `GET /api/search?q=vue` 返回 200，`total=4`。
- 通过：TestClient `GET /api/rss.xml` 返回 200，content-type 为 `application/rss+xml`。
- 通过：TestClient `GET /api/sitemap.xml` 返回 200，content-type 为 `application/xml`。
- 通过：TestClient `GET /robots.txt` 返回 200，并包含 `Disallow: /admin`。
- 通过：TestClient `GET /api/posts/no-such-slug` 返回 404。
- 通过：构建产物 Secret 真实值扫描，检查 `backend/.env` 中 2 个敏感值，未在 `frontend/dist` 或 `admin/dist` 命中。
- 记录：`frontend/dist` 总大小约 1.23 MB，`admin/dist` 总大小约 1.70 MB；`MarkdownRenderer` 和 `MarkdownEditor` chunk 超过 500 kB，但位于懒加载路径。

遗留问题：

- 当前工具环境没有可用 headless browser，390px 真实视觉回归、Tab 顺序、图片失败视觉兜底和后台窄屏表单操作仍需用户浏览器人工确认。
- 性能/可访问性/体验稳定项保持 `进行中`，不得在人工验收前标记完成。
- 设置中心此前跳过的空 Secret 不覆盖、评论开关、图床设置与上传、AI 设置、部署文档实操核验继续保持 `延期/未验收`。

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

## 2026-05-02 - 评论索引 API 路由确认与同步复测轮

本轮目标：

- 针对人工验收中 `/api/admin/comments/index` 返回 404 的问题，确认并修复评论索引 API 与后台评论管理主流程。
- 不重构已通过人工验收的 Markdown 预览。
- 不新增 P2 视觉特效，不进入媒体互动轮。

前台变更：

- 本轮未改动前台文章详情和 Markdown 渲染。
- 前台评论错误处理沿用已有 UI：空昵称、空内容、非法邮箱均会在评论区显示错误，不只写控制台。

后台变更：

- 后台评论管理索引加载失败时，如果遇到 404/Not Found，会在 UI 中提示检查后端是否已重启到最新代码，并确认 `/api/admin/comments/index` 是否出现在 `/docs`。
- 后台评论管理主流程仍保持：打开页面自动请求评论索引，点击索引项加载评论，手动 `resource/slug` 只保留在“高级加载”折叠区。

后端/API 变更：

- 复查确认当前代码已在 `backend/app/api/comments.py` 定义 `GET /api/admin/comments/index`。
- 复查确认当前代码已在 `backend/app/main.py` 通过 `app.include_router(comments_admin_router, prefix="/api")` 注册，最终路径为 `/api/admin/comments/index`。
- 该接口继续要求管理员 JWT；未登录访问返回 401。
- 无评论或 comments 目录不存在时返回 `[]`，不返回 404。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动当前代码后端到 `127.0.0.1:8024`，`GET /docs` 返回 200，`/openapi.json` 中包含 `/api/admin/comments/index`。
- 通过：临时启动当前代码后端到 `127.0.0.1:8021`，未登录调用 `GET /api/admin/comments/index` 返回 401，登录后返回 200。
- 通过：登录后 `GET /api/admin/comments/index` 返回包含 `posts/post-1777703928848` 和 `posts/srblogs-p0-20260502130609` 的索引；其中 `posts-post-1777703928848.json` 能正确反推 `resource=posts`、`slug=post-1777703928848`。
- 通过：临时后端返回的原始索引包含 `{"resource":"posts","slug":"post-1777703928848","count":1,"updatedAt":"2026-05-02 14:41","title":"测试"}`。
- 通过：前台 API 提交评论到 `posts/post-1777703928848` 后，`GET /api/comments/posts/post-1777703928848` 能读到该评论；后台 DELETE 删除后再次 GET，该评论消失。
- 通过：删除评论前备份验证，`backend/data/comments/.backups` 中 `posts-post-1777703928848` 匹配备份数从 1 增加到 3。
- 通过：删除不存在评论返回 404。
- 通过：空昵称提交返回 400。
- 通过：空评论内容提交返回 400。
- 通过：非法邮箱提交返回 400。
- 通过：XSS 评论内容保存为 `alert(1)safe`，脚本标签未保留。
- 发现：当前正在运行的 `127.0.0.1:8000` 后端进程仍返回 404；其 `/openapi.json` 不包含 `/api/admin/comments/index`，说明 8000 是旧代码进程或未重载进程。`netstat` 显示 8000 有 Python 进程监听，未在本轮强制终止用户进程。

遗留问题：

- 需要重启当前 8000 后端进程，使其加载最新代码；重启后 `/docs` 应能看到 `GET /api/admin/comments/index`。
- 评论模块仍保持 `进行中`，等待用户确认自动索引、点击加载、删除、count 同步和前台同步消失全部通过。

## 2026-05-02 - 首页响应式溢出修复轮

本轮目标：

- 只修复前台首页响应式布局和横向溢出问题。
- 不新增 P2 视觉特效，不进入媒体互动轮。
- 不重构评论管理、Markdown 编辑器、文章详情 TOC/分享逻辑。

前台变更：

- `App.vue` 主内容容器改为统一的 `.sr-page-shell`，避免 `max-width`、padding 和 viewport 宽度不一致造成裁切。
- `AppNav.vue` 顶部导航改用 `.sr-page-shell`，移动菜单断点从 `md` 调整为 `lg` 以下，避免 768-1023px 宽度下导航链接挤出。
- `Home.vue` 首页首屏双列从 `lg` 调整到 `xl`，并使用 `minmax(0, ...)` 和 `min-w-0` 防止 grid 子项撑破 viewport。
- `ProfileCard.vue` 增加 `min-w-0`、文本换行和 420px 以下统计项单列布局，防止右栏被裁切。
- `SiteDashboard.vue` 统计卡片改为 `sm:grid-cols-3`、`lg:grid-cols-5`，并为子项补 `min-w-0` 和换行。
- `BackgroundSlider.vue` 在中等宽度下从右侧 fixed 改到底部左侧横排，`xl` 以上恢复右侧竖排，避免覆盖 ProfileCard。
- `FloatingPlayer.vue` 弹出面板宽度改为 `min(290px, calc(100vw - 2rem))`，移动端不再横向撑出。
- `frontend/src/styles.css` 新增 `.sr-page-shell`，并为 `html/#app` 增加横向裁切保护；这不是唯一修复手段，主要布局已通过断点和 `min-w-0` 处理。

后台变更：

- 本轮未修改后台评论管理和 Markdown 编辑器。

后端/API 变更：

- 本轮未修改后端业务 API。

文档变更：

- 更新 `docs/MANUAL_QA_CHECKLIST.md`，新增首页 1440px、1280px、1024px、390px 响应式验收项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步首页响应式修复进展和剩余人工验收要求。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8025` 并访问 `/api/health`，返回 `health=True`。
- 已尝试：使用 Edge headless + DevTools Protocol 对构建产物做 1440px、1280px、1024px、390px 自动尺寸采样；当前工具环境下 Edge 调试端口/WebSocket 未稳定建立，未能完成自动浏览器采样。
- 代码级确认：修复已覆盖主容器宽度、导航宽度、首页双列断点、ProfileCard 换行、SiteDashboard 换行、主题按钮 fixed 位置和 FloatingPlayer 移动端宽度。

遗留问题：

- 需要用户在普通浏览器中按 `docs/MANUAL_QA_CHECKLIST.md` 完成首页 1440px、1280px、1024px、390px 人工验收。
- 首页仍保持 `进行中`，不得标记为 `已完成`，直到用户确认响应式人工验收通过。

## 2026-05-02 - 首页组件裁切二次修复轮

本轮目标：

- 修复首页无横向滚动条但 ProfileCard 和 SiteDashboard 组件内容被裁切的问题。
- 不通过 `overflow-x: hidden` 假装修复，必须让内容自身完整显示和换行。
- 不重构评论管理、Markdown 编辑器，不新增 P2 视觉特效，不进入媒体互动轮。

前台变更：

- 移除 `Home.vue` 根容器的 `overflow-hidden`，避免首页内容被父级直接裁掉。
- 首页 Hero + ProfileCard 外层改为 `.home-hero-grid`，使用 `repeat(auto-fit, minmax(min(100%, 24rem), 1fr))`；宽屏 1280px 以上才切换为 `minmax(0, 1.35fr) minmax(20rem, .65fr)`。
- `.home-hero-grid > *` 显式设置 `min-width: 0` 和 `max-width: 100%`，防止 grid 子项撑破或被裁切。
- `ProfileCard` 保持 `max-width: 100%`，内部统计区改为 `repeat(auto-fit, minmax(min(100%, 5.5rem), 1fr))`，社交按钮继续允许换行。
- `SiteDashboard` 统计区改为 `.home-stats-grid`，使用 `repeat(auto-fit, minmax(min(100%, 9.5rem), 1fr))`，最后一个“照片”卡片必须参与换行而不是被隐藏或裁掉。
- 移除 `#app` 的 `overflow-x: clip`，保留 `html/body` 横向隐藏仅作为兜底；布局本身依赖 grid 换行和宽度约束。
- `BackgroundSlider` 在 `xl` 以上固定到主内容外侧安全区域，避免覆盖 ProfileCard；中等宽度继续在底部左侧。

后台变更：

- 本轮未修改后台。

后端/API 变更：

- 本轮未修改后端 API。

文档变更：

- 更新 `docs/MANUAL_QA_CHECKLIST.md`，明确“无横向滚动条但组件被裁切”仍为不通过。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录首页组件裁切二次修复仍待人工验收。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8026` 并访问 `/api/health`，返回 `health=True`。
- 已尝试：使用 Edge headless 截图验证 1440px、1280px、1024px、390px；当前工具环境下 Edge headless 因 Crashpad/Mojo 权限错误未能生成截图。
- 代码级确认：本轮不再依赖首页父级裁切，ProfileCard 和 SiteDashboard 均改为 auto-fit 响应式网格。

遗留问题：

- 需要用户在普通浏览器重新人工验收 1440px、1280px、1024px、390px。
- 首页继续保持 `进行中`，不得标记为 `已完成`，直到 ProfileCard、统计卡片和 fixed 控件均确认完整可见。

## 2026-05-02 - 首页左右边距统一修复轮

本轮目标：

- 只修复首页左右边距不一致和主内容视觉上向右顶出的问题。
- 不新增 P2 视觉特效，不重构评论管理，不重构 Markdown 编辑器，不修改后端接口。

前台变更：

- `.sr-page-shell` 主容器宽度从 `min(calc(100% - 2rem), 80rem)` 调整为 `min(calc(100% - 3rem), 80rem)`，常规视口左右保留约 24px 安全边距。
- 480px 以下 `.sr-page-shell` 使用 `min(calc(100% - 1.5rem), 80rem)`，保证 390px 下左右 padding 仍一致。
- Hero + ProfileCard 双列断点从 1280px 调整到 1360px，避免 1280px 宽度下为了并排牺牲右边距；1280px 默认单列或自然换行。
- `BackgroundSlider` 右侧固定按钮只在 `2xl` 以上恢复右侧竖排，中等宽度继续底部左侧，避免右侧视觉空间干扰主内容判断。
- 首页主要区域仍共用 `.sr-page-shell`，导航、Hero/ProfileCard、SiteDashboard、LatestPosts 均在同一居中容器内。

后台变更：

- 本轮未修改后台。

后端/API 变更：

- 本轮未修改后端。

文档变更：

- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充首页左右边距一致和导航/首页共用宽度验收项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录首页左右边距修复仍待人工验收。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8027` 并访问 `/api/health`，返回 `health=True`。
- 代码级确认：主内容容器、顶部导航和首页主要区块使用同一 `.sr-page-shell`；1280px 不再强制 Hero/ProfileCard 并排。

遗留问题：

- 需要用户在普通浏览器确认 1440px、1280px、1024px、390px 下左右边距基本一致。
- 首页继续保持 `进行中`，不得标记为 `已完成`，直到用户确认左右边距一致。

## 2026-05-02 - 首页最新文章列表撑宽修复轮

本轮目标：

- 只修复首页内容列表布局导致的整体宽度异常问题。
- 不新增 P2 视觉特效，不修改评论系统、Markdown 编辑器或后端接口。

前台变更：

- `LatestPostsCarousel.vue` 从横向滚动 `flex + overflow-x-auto + min-w-[280/360px]` 改为真正响应式网格。
- 最新文章网格使用 `grid-cols-1 md:grid-cols-2 xl:grid-cols-3`，因此 4 篇文章在当前主容器宽度下会换到第二行第一列，不再继续排成第一行第四列。
- 移除最新文章卡片的固定 `min-width`，改为 `min-w-0`，防止卡片撑宽主容器。
- 最新文章 section/header 增加 `min-w-0`、`max-w-full` 和标题区域换行约束。
- `LatestChatterCarousel.vue` 同步补 `min-w-0`、`max-w-full`，并从 `md:grid-cols-3` 调整为 `grid-cols-1 md:grid-cols-2 xl:grid-cols-3`，避免杂谈列表在中等宽度撑宽。
- `MomentTimeline.vue` 补 `min-w-0`、`max-w-full`，避免时间线卡片参与横向撑宽。

后台变更：

- 本轮未修改后台。

后端/API 变更：

- 本轮未修改后端。

文档变更：

- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充“最新文章不是横向滚动轨道”和“4 篇文章应换行”的验收项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录首页最新文章列表撑宽修复仍待人工验收。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8028` 并访问 `/api/health`，返回 `health=True`。
- 代码级确认：首页最新文章区域不再使用 `overflow-x-auto`、固定 `min-width` 横向轨道；卡片数量变化不应再改变主容器宽度。

遗留问题：

- 需要用户人工确认 4 篇文章时第 4 张卡确实换到第二行第一列。
- 首页继续保持 `进行中`，不得标记为 `已完成`，直到用户确认没有任何 section 再撑宽整个首页。

## 2026-05-02 - 后台写作闭环 / 草稿 / 暂存队列第一阶段

本轮目标：

- 完善后台文章管理、草稿发布、写作保存错误提示和本地 pendingOperations 第一阶段。
- 证明文章可以创建为草稿、发布、编辑、删除，并与前台公开列表和详情联动。
- 不新增 P2 视觉特效，不重构 Markdown 预览和评论管理主流程。

前台变更：

- 本轮未修改前台页面代码。
- 通过 API 验证 `draft=true` 文章不会出现在公开 `GET /api/posts` 列表中；发布为 `draft=false` 后公开列表可见，删除后公开列表移除且详情返回 404。

后台变更：

- 新增 `admin/src/stores/pending.ts`，提供本地 pendingOperations 队列，状态包含 `editing`、`pending`、`applied`、`failed`。
- 后台右侧“操作暂存区”改为显示真实本地队列，支持应用、重试和移除，并明确提示刷新页面会丢失，图片上传、Secret 修改、评论管理不进入本队列。
- `/admin/posts` 文章管理页补齐标题、slug、日期、标签、draft 状态、编辑、删除、前台预览，并支持全部/已发布/草稿筛选。
- 文章删除支持“立即删除”和“暂存删除”；立即删除会调用真实后端 DELETE，暂存删除只有点击暂存区“应用”后才写后端。
- 写作页保留“保存”直接持久化，同时新增“加入暂存”“立即发布”“发布加入暂存”，并对空标题、空 slug、非法 slug、保存失败和保存成功显示 UI 提示。
- 草稿页改为列出 draft=true 文章，支持继续编辑、立即发布和发布暂存。
- 管理端登录页移除默认密码填充，避免默认管理员密码进入 admin 构建产物。

后端/API 变更：

- 本轮未新增后端接口。
- 继续复用既有 `POST /api/posts`、`PUT /api/posts/{slug}`、`DELETE /api/posts/{slug}`。
- 写入和删除仍走 `MarkdownStore` -> `safe_write_text` / `backup_file`，未新增业务路由直接 `open(..., "w")` 写文件。

文档变更：

- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，同步后台写作、草稿和暂存队列第一阶段进展，状态保持 `进行中`。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充后台文章管理、草稿、删除、暂存队列第一阶段验收项。
- `docs/API_CONTRACT.md` 本轮无接口变化，未调整契约。
- `docs/SECURITY_NOTES.md` 已有 pendingOperations 范围和写入安全规则，本轮未新增安全规则。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8033` 并访问 `/api/health`，返回 `health=True`。
- 通过：新建草稿 `draft-loop-20260502183231`，`backend/data/posts/draft-loop-20260502183231.md` 真实创建。
- 通过：草稿创建后公开 `GET /api/posts` 不包含该 slug。
- 通过：发布草稿为 `draft=false` 后，公开 `GET /api/posts` 包含该 slug，`GET /api/posts/draft-loop-20260502183231` 可读取详情。
- 通过：编辑文章后标题变为 `Edited Draft Loop Test`。
- 通过：非法 slug 返回 400。
- 通过：空标题返回 400。
- 通过：重复 slug 返回 409。
- 通过：删除文章后源文件不存在，公开详情返回 404，公开列表不再包含该 slug。
- 通过：删除前备份验证，`backend/data/posts/.backups` 中该 slug 匹配备份数从 2 增加到 3。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me`。
- 已清理：测试文章正文文件已通过 DELETE API 删除；删除产生的备份文件保留为本轮写入/备份验证痕迹。

遗留问题：

- 后台写作、草稿和暂存队列第一阶段仍需用户在浏览器中人工验收：列表筛选、编辑跳转、UI 错误提示、暂存区应用/失败状态、刷新丢失提示。
- 暂存队列当前为前端内存态，刷新页面会丢失；第二阶段才做服务端持久化。
- settings 修改未纳入本轮 pendingOperations；图片上传、Secret 修改、评论管理按计划不进入本地 pendingOperations。
- 不得把“后台写作”“草稿”“暂存队列”标记为 `已完成`，直到浏览器人工验收通过。

## 2026-05-02 - 媒体与结构化内容管理轮

本轮目标：

- 将 friends/projects/music/photos 的后台管理从“默认 JSON 文本框”升级为表单化主流程。
- 保留高级 JSON 编辑作为兜底，并要求 JSON 格式错误时阻止保存。
- 完善四类内容的前台动态读取、加载状态、空状态、错误状态和基础展示。
- 不新增 P2 视觉特效，不重构文章、评论、Markdown、暂存队列。

前台变更：

- `Friends.vue` 改为带加载、空、错误状态的动态友链页，展示名称、简介、头像/图标、标签，外链使用新标签页打开。
- `Projects.vue` 改为带加载、空、错误状态的项目页，展示名称、描述、技术栈、链接、仓库链接、状态和封面。
- `Music.vue` 改为带加载、空、错误状态的歌单页，按 `sort` 排序并将后端歌单绑定到 `CloudPlayer`。
- `CloudPlayer` 在歌曲存在 `url` 时使用原生 audio 执行播放/暂停/结束后切歌；仅配置云音乐 ID 时保留基础状态切换和数据展示。
- `Photowall.vue` 改为带加载、空、错误状态的照片墙，图片懒加载，点击可放大预览，并展示标题、描述、日期、标签。
- `frontend/src/types.ts` 补充 friends/projects/music/photos 的结构化字段。

后台变更：

- 新增 `admin/src/components/StructuredJsonManager.vue`，统一提供列表区、编辑表单、新增、保存、删除、加载/错误/空状态、成功反馈和高级 JSON 折叠区。
- `FriendsManage.vue` 改为表单化管理名称、URL、描述、头像/图标 URL、标签。
- `ProjectsManage.vue` 改为表单化管理名称、描述、技术栈、项目链接、GitHub/Gitee 链接、封面 URL、状态。
- `MusicManage.vue` 改为表单化管理歌曲标题、艺术家、封面 URL、歌曲 URL、云音乐 ID、排序。
- `PhotowallManage.vue` 改为表单化管理图片 URL、标题、描述、日期、标签，并支持调用上传接口后自动填入 URL。
- 高级 JSON 编辑保留在折叠区，根节点不是数组或 JSON 格式错误时会显示错误并阻止保存。

后端/API 变更：

- 本轮未新增后端路由，继续复用 `GET/PUT /api/friends`、`GET/PUT /api/projects`、`GET/PUT /api/music`、`GET/PUT /api/photos` 和 `POST /api/upload`。
- friends/projects/music/photos 写入继续通过 `JsonStore.write` -> `safe_write_json`，覆盖前生成 `.backups` 备份。
- 上传接口仍要求管理员 JWT，并校验扩展名、MIME 和 5 MB 大小限制。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充结构化 JSON API 字段、GET/PUT 契约和备份要求。
- 更新 `docs/SECURITY_NOTES.md`，补充结构化 JSON 管理、高级 JSON 校验和图片上传不进入 pendingOperations 的规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，新增媒体与结构化内容管理人工验收项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，照片墙、音乐、友链、项目状态改为 `进行中` 并写明剩余人工验收差距。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：`http://127.0.0.1:8000/api/health` 返回 `ok=true`。
- 通过：`GET /api/friends` 返回 3 条。
- 通过：`GET /api/projects` 返回 3 条。
- 通过：`GET /api/music` 返回 3 条。
- 通过：`GET /api/photos` 返回 6 条。
- 通过：friends 新增/编辑/删除 API 验证，新增后可读、编辑后可读、删除后消失，`backend/data/.backups/friends.json.*.bak` 数量从 0 增加到 3。
- 通过：projects 新增/编辑/删除 API 验证，新增后可读、编辑后可读、删除后消失，`backend/data/.backups/projects.json.*.bak` 数量从 0 增加到 3。
- 通过：music 新增/编辑/删除 API 验证，新增后可读、编辑后可读、删除后消失，`backend/data/.backups/music.json.*.bak` 数量从 0 增加到 3。
- 通过：photos 新增/编辑/删除 API 验证，新增后可读、编辑后可读、删除后消失，`backend/data/photos/.backups/photos.json.*.bak` 数量从 0 增加到 3。
- 通过：上传接口最小验证，`POST /api/upload` 返回 200、URL 和 size；测试上传文件随后已清理。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`api_key`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me`。

遗留问题：

- 本轮完成代码和 API 验证，但 friends/projects/music/photos 的后台表单页和前台页面仍需用户浏览器人工验收。
- 媒体与结构化内容管理模块保持 `进行中`，不得标记为 `已完成`。
- 图片上传、Secret 修改、评论删除继续不进入本地 pendingOperations。

## 2026-05-02 - 设置中心与生产化轮

本轮目标：

- 根据用户人工验收结果，将媒体与结构化内容管理相关矩阵项标记为 `已完成`。
- 完善 `/admin/settings`，补齐站点公开信息、主题与背景、评论设置、图床设置、AI 设置、部署与安全提示。
- 固化公开/私有配置边界：前台只读公开配置，后台不回显 Secret 明文，空 Secret 不覆盖旧值。
- 补充 Windows/服务器部署文档和生产前检查。
- 不新增 P2 视觉特效，不改动已通过人工验收的媒体模块。

前台变更：

- 前台首页兼容 `siteTitle`、`author`、`avatar`、`description`、`socialLinks` 等公开设置字段。
- `ProfileCard` 兼容新版公开站点信息字段，同时保留旧字段兜底。
- `CommentBox` 改为读取 `/api/settings/public` 的公开评论设置。
- 评论关闭时，文章详情显示“评论已关闭。”并隐藏提交表单；重新开启后恢复本地评论表单。
- 评论最大长度、是否要求邮箱等校验改为优先跟随公开评论设置。

后台变更：

- `/admin/settings` 从单一 JSON 编辑升级为分区表单主流程。
- 设置中心分区包括：站点公开信息、主题与背景、评论设置、图床设置、AI 设置、部署与安全提示。
- 支持编辑站点标题、副标题、作者、头像、简介、社交链接、背景图、主题、公开音乐 ID、评论开关、图床配置和 AI 配置。
- 后台仅展示 `aiKeyConfigured`、`accessKeyConfigured`、`secretKeyConfigured`、`ossKeyConfigured`、`githubOAuthSecretConfigured` 等布尔状态，不展示 Secret 明文。
- Secret 输入框为空时表示保持原值；只有输入明确新值时才提交覆盖。
- 高级 JSON 编辑保留为折叠兜底入口，保存前要求根节点为对象。

后端/API 变更：

- `GET /api/settings/public` 明确只返回前台需要的公开字段：站点信息、主题、背景、公开音乐配置和公开评论显示选项。
- `GET /api/admin/settings` 继续要求管理员 JWT，返回后台配置和 Secret configured 布尔值，但不回显 Secret 明文。
- `PUT /api/admin/settings` 继续要求管理员 JWT，并实现空字符串、`null` 或未传 Secret 时保留原值。
- 设置写入继续走 `safe_write_json`，覆盖前生成 `backend/data/.backups/settings.json.*.bak`。

文档变更：

- 媒体与结构化内容管理经用户浏览器人工验收通过后，`docs/XINGHUI_PARITY_MATRIX.md` 中照片墙、音乐、友链、项目已标记为 `已完成`。
- 新增 `docs/DEPLOYMENT.md`，包含后端 FastAPI 启动、前端/后台 build、Nginx 示例、systemd 示例、`backend/data` 权限、生产 `.env`、HTTPS 和生产前检查。
- 更新 `WINDOWS_START.md`，补充设置中心地址、公开/后台 settings 接口、Secret 不回显说明和生产前必须修改默认密码/JWT Secret。
- 更新 `docs/API_CONTRACT.md`，补充 settings 公开/后台字段边界、Secret preserve 语义和配置布尔字段。
- 更新 `docs/SECURITY_NOTES.md`，补充 settings Secret 边界、空 Secret 保留旧值、构建产物 Secret 检查和评论配置规则。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，补充设置中心与生产化人工验收项。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：FastAPI TestClient 访问 `/api/health` 返回 200 且 `ok=true`。
- 通过：`GET /api/settings/public` 不包含 Secret 字段和值。
- 通过：登录后 `GET /api/admin/settings` 不回显 GitHub OAuth Secret、OSS Secret、AI Key 明文。
- 通过：`PUT /api/admin/settings` 写入临时 Secret 后，后台只返回 configured 布尔值，不返回明文。
- 通过：再次 `PUT /api/admin/settings` 传空 Secret 后，configured 布尔值保持为 true，验证空 Secret 不覆盖旧值。
- 通过：修改站点标题后，`GET /api/settings/public` 可读取新标题；验证结束后已恢复原 `backend/data/settings.json` 内容。
- 通过：关闭评论后，公开设置中 `comments.enabled=false`；重新开启后恢复为 true。
- 通过：上传接口最小验证，`POST /api/upload` 返回 200、URL 和 size；测试上传文件随后已清理。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me` 或本轮临时 Secret 值。
- 未通过固定端口探测：当前 `127.0.0.1:8000` 未监听，直接访问 `http://127.0.0.1:8000/api/health` 连接失败；本轮未强行保留常驻后端进程。

遗留问题：

- 设置中心与生产化仍需用户在浏览器中人工验收：设置分区、保存状态、站点信息同步、评论开关表现、图床测试按钮、AI 设置保存、部署文档可执行性。
- 由于固定端口 8000 当前未启动，本轮只记录 TestClient 级 health 通过，不把设置中心与生产化标记为 `已完成`。
- Secret 修改不进入本地 pendingOperations；图片上传、评论删除仍按既定计划不进入本地 pendingOperations。

## 2026-05-02 - 全站回归与交付整理轮

本轮目标：

- 不新增大功能，不新增 P2 视觉特效。
- 做全站路由、示例数据、启动脚本、README、发布清单和矩阵状态整理。
- 明确设置中心与生产化中被用户主动跳过的验收项为“延期/未验收”，不得标记为已完成。

前台变更：

- 新增前台 404 页面 `frontend/src/views/NotFound.vue`，不存在路由不再白屏。
- 前台路由新增 `/chatters` 和 `/chatters/:slug`，旧 `/chatter` 和 `/chatter/:slug` 保留重定向。
- 顶部导航和首页杂谈聚合链接统一改为 `/chatters`。
- `Moments.vue`、`Chatter.vue`、`Timeline.vue`、`About.vue` 补齐加载状态、空状态和错误状态。
- `Chatter.vue` 列表详情跳转改为 `/chatters/{slug}`。

后台变更：

- 后台路由新增 catch-all 重定向到 `/admin/`，避免未知后台路径白屏。
- 未改动已通过人工验收的评论管理、Markdown 编辑器、媒体管理和暂存队列主流程。

后端/API 变更：

- 新增 `backend/data/posts/demo-draft.md` 作为最小示例草稿，保证演示数据至少包含 1 篇 `draft=true` 文章。
- 本轮未新增后端接口。

文档变更：

- 重写 `README.md` 作为项目总入口，包含项目简介、技术栈、项目结构、Windows 启动、三端手动启动、默认账号、API 文档、数据目录、部署链接和常见问题。
- 新增 `docs/RELEASE_CHECKLIST.md`，覆盖本地启动、前台页面、后台页面、内容写入、评论、媒体管理、设置中心、Secret、构建、部署前检查和已知延期项。
- 更新 `docs/API_CONTRACT.md`，移除旧 settings 示例，统一为当前 `/api/settings/public` 和 `/api/admin/settings` 字段边界。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，新增全站前台路由和后台路由回归检查项。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，动态、杂谈、时间线从未开始调整为进行中；图床、AI 设置、评论设置、部署文档标记为 `延期/未验收`，并写明原因为用户决定跳过本轮验收。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8000` 并访问 `/api/health`，返回 `{"ok":true,"app":"SRBlogs API"}`；验证后已关闭该临时进程。
- 通过：TestClient `GET /api/posts` 返回 4 篇公开文章。
- 通过：TestClient `GET /api/settings/public` 返回 200。
- 通过：TestClient `GET /api/friends` 返回 3 条。
- 通过：TestClient `GET /api/projects` 返回 3 条。
- 通过：TestClient `GET /api/music` 返回 3 条。
- 通过：TestClient `GET /api/photos` 返回 6 条。
- 通过：示例数据检查：posts 共 5 篇，其中公开 4 篇、草稿 1 篇；moments 2 条；chatters 2 条；friends 3 条；projects 3 条；music 3 首；photos 6 张；`about.md` 存在。
- 通过：`frontend/dist/index.html` 和 `admin/dist/index.html` 均已生成。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me` 或本轮临时 Secret 值。

遗留问题：

- 本轮没有做真实浏览器全站人工回归；新增的路由与状态仍需按 `docs/MANUAL_QA_CHECKLIST.md` 和 `docs/RELEASE_CHECKLIST.md` 逐项确认。
- 设置中心跳过项保持 `延期/未验收`：空 Secret 不覆盖旧值、评论开关、图床设置与上传流程、AI 设置、部署文档完整实操核验。
- 不得把设置中心与生产化整体标记为已完成。

## 2026-05-02 - 内容发现与归档扩张轮

本轮目标：

- 增强内容发现能力，新增全站搜索、标签页、标签筛选、内容归档和首页发现入口。
- 不新增 P2 视觉特效，不重构已通过验收的媒体、评论、Markdown、设置中心基础结构。
- 所有数据读取继续通过 FastAPI API，前端不直接读取 `backend/data` 文件。

前台变更：

- 新增 `/search` 页面，支持关键词、类型筛选、标签快捷筛选、URL query 同步、加载/空/错误状态和结果跳转。
- 新增 `/tags` 页面，显示标签列表、数量、类型和最近日期。
- 新增 `/tags/:tag` 页面，展示该标签下的内容，并支持按类型筛选；不存在标签显示空状态。
- 新增 `/archive` 页面，按年份和月份展示 posts/moments/chatters，记录项可跳转详情页。
- 首页新增轻量“内容发现”入口，提供搜索、标签、归档和最近更新链接，没有重做首页布局。
- 前台导航增加搜索和归档入口。
- 新增 `DiscoveryResultCard.vue` 作为搜索和标签结果卡片复用组件。

后台变更：

- 本轮未修改后台主流程；未扩展后台搜索管理，避免影响前台主任务。

后端/API 变更：

- 新增 `backend/app/api/discovery.py` 并注册到 FastAPI。
- 新增 `GET /api/search`，支持 `q`、`type`、`tag`、`limit`、`offset`。
- 搜索覆盖 posts、moments、chatters、projects、photos、friends、music；公开结果排除 `draft=true`。
- `q` 和 `tag` 都为空时返回最近公开内容；无匹配时返回空列表。
- 标签筛选为大小写不敏感包含匹配，因此 `tag=Vue` 可匹配 `Vue3`。
- 新增 `GET /api/tags`，合并 posts、moments、chatters、projects 的标签统计。
- 新增 `GET /api/archive`，按年月聚合 posts、moments、chatters；时间解析失败会放入 unknown 分组，不应导致 500。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充 `/api/search`、`/api/tags`、`/api/archive` 契约。
- 更新 `README.md`，补充前台主要路由。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，新增内容发现与归档人工验收项。
- 更新 `docs/RELEASE_CHECKLIST.md`，补充搜索、标签、归档发布前检查。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，记录内容发现轮当前结果；新增页面未人工验收前保持 `进行中`。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：临时启动后端到 `127.0.0.1:8000` 并访问 `/api/health`，返回 200。
- 通过：`GET /api/search?q=vue` 返回 200，匹配 4 条。
- 通过：`GET /api/search?q=vue&type=posts` 返回 200，匹配 2 条。
- 通过：`GET /api/search?tag=Vue` 返回 200，匹配 3 条。
- 通过：`GET /api/tags` 返回 200，当前 17 个标签。
- 通过：`GET /api/archive` 返回 200，当前 2 个年份分组。
- 通过：搜索不存在关键词 `definitely-no-match-xyz` 返回 200 和空结果。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me` 或本轮临时 Secret 值。
- 通过：用构建产物和临时 SPA fallback 静态服务器探测 `/search`、`/tags`、`/tags/Vue3`、`/archive`，均返回 200 且包含 SPA 根节点。
- 已尝试但未通过：`vite preview` 在当前工具 shell 环境继续触发 `spawn EPERM`，因此页面响应检查改用构建产物静态服务器完成。
- 已尝试但未执行：本机 Python 环境未安装 Playwright，无法在工具内完成 390px 移动端渲染自动检查；该项保留为浏览器人工验收。

遗留问题：

- `/search`、`/tags`、`/tags/:tag`、`/archive` 仍需用户浏览器人工验收，包括 390px 移动端检查、搜索空状态、不存在标签空状态和结果跳转。
- 本轮未做全文索引数据库、AI 搜索、后台搜索管理增强、真实 OSS/Gitalk/OAuth 或设置中心延期项。
- 内容发现相关矩阵项保持 `进行中`，不得标记为 `已完成`。

## 2026-05-02 - SEO、订阅与分享增强轮

本轮目标：

- 提升 SRBlogs 的可发现性、可分享性和可订阅性。
- 新增基础动态 meta、OpenGraph、Twitter Card、RSS、Sitemap、robots 和前台 RSS 入口。
- 不做服务端渲染、不迁移 Next.js、不接入复杂 SEO 平台、不做 AI 搜索、不新增 P2 视觉特效。

前台变更：

- 新增 `frontend/src/composables/useSeo.ts`，统一设置 `title`、`description`、OpenGraph 和 Twitter Card。
- 首页、文章列表、文章详情、瞬间、杂谈、友链、项目、音乐、照片墙、关于、时间线、搜索、标签、标签详情、归档和 404 页面已接入统一 SEO 工具。
- 文章详情 SEO 来源优先使用文章标题、摘要和封面；不存在或加载失败时 title 显示 404/内容不存在。
- `frontend/index.html` 更新基础 title、description、OG、Twitter Card 和 RSS alternate link。
- 文章列表页和关于页新增 RSS 入口。
- `ShareButtons.vue` 增强复制链接：成功显示提示，失败时显示可读失败提示，并保留 X 分享链接但不依赖第三方 SDK。

后台变更：

- 本轮未修改后台页面和后台业务流程。

后端/API 变更：

- 新增 `backend/app/api/seo.py` 并注册到 FastAPI。
- 新增 `GET /api/rss.xml`：公开 RSS 2.0，包含已发布 posts 和部分 chatters，排除 `draft=true`。
- 新增 `GET /api/sitemap.xml`：公开 XML sitemap，包含公开固定路由、已发布 posts 详情、chatters 详情和 tags 详情，排除 `draft=true`。
- 新增 `GET /robots.txt`：允许公开前台页面，禁止 `/admin`，并指向 sitemap。
- RSS description 使用 XML/HTML 转义；RSS/Sitemap/robots 不需要 JWT，不输出 Secret。
- SEO 链接基于 `PUBLIC_BASE_URL`；开发默认将 `127.0.0.1:8000` 兜底转换为前台 `127.0.0.1:5173`。

文档变更：

- 更新 `docs/API_CONTRACT.md`，补充 RSS、Sitemap、robots 契约。
- 更新 `README.md`，补充 SEO 与订阅公开地址。
- 更新 `docs/MANUAL_QA_CHECKLIST.md`，新增 SEO、订阅与分享人工验收项。
- 更新 `docs/RELEASE_CHECKLIST.md`，新增 SEO 与订阅发布前检查。
- 更新 `docs/SECURITY_NOTES.md`，补充公开 SEO 端点安全规则。
- 更新 `docs/XINGHUI_PARITY_MATRIX.md`，将内容发现与归档相关项按用户人工验收结果标记为 `已完成`，新增 SEO/订阅/分享项并保持 `进行中`。

验证结果：

- 通过：`cd frontend && npm run build`。
- 通过：`cd admin && npm run build`。
- 通过：`python -m compileall backend\app`。
- 通过：TestClient `GET /api/rss.xml` 返回 200，`Content-Type=application/rss+xml`，包含 RSS item，不包含 `demo-draft` 草稿和 Secret pattern。
- 通过：TestClient `GET /api/sitemap.xml` 返回 200，`Content-Type=application/xml`，包含 `<urlset>`，不包含 `demo-draft` 草稿和 Secret pattern。
- 通过：TestClient `GET /robots.txt` 返回 200，包含 `Disallow: /admin`，不包含 Secret pattern。
- 通过：临时启动后端到 `127.0.0.1:8000`，`GET /api/rss.xml`、`GET /api/sitemap.xml`、`GET /robots.txt` 均可通过 HTTP 打开。
- 通过：`frontend/dist/index.html` 基础 title 为 `SRBlogs`，包含 description、OG、Twitter Card 和 RSS alternate link。
- 通过：构建产物静态搜索未匹配到 `clientSecret`、`accessKeySecret`、`secretKey`、`apiKey`、`jwt_secret`、`admin_password`、`please-change-this-secret`、`change-me` 或本轮临时 Secret 值。
- 已尝试但未通过：使用 Edge headless 验证文章详情运行时动态 title/meta/og 时，当前工具环境返回空 DOM；未能完成浏览器自动验收。

遗留问题：

- 文章详情动态 title/meta/og 随文章变化、文章详情复制链接可用、RSS 入口可见仍需用户浏览器人工验收。
- 本轮未做 SSR，因此搜索引擎对 SPA 运行时 meta 的抓取能力取决于爬虫是否执行 JavaScript；RSS/Sitemap/robots 已由后端直接提供。
- SEO/订阅/分享矩阵项保持 `进行中`，不得标记为 `已完成`，直到人工验收通过。
## 2026-05-03 - Album modal scroll focused fix

Scope:
- Focused fix for `/admin/photos` create/edit album modal only.
- No new business module and no frontend route redesign.

Progress:
- P0: 100%.
- P1: 99%.
- P2: 95%.

Changes:
- Replaced the album edit modal wrapper from `GlassCard` to a direct `glass` flex container so header, scroll body, and footer are real flex children.
- Modal height is constrained to `85vh`; the middle form body owns `overflow-y:auto`.
- Album photo grid no longer owns a fixed clipped height. It grows naturally and scrolls through the modal body.
- Photo thumbnails now use a stable 90px preview height with `object-cover`, a cover badge, and drag hint.
- Batch upload, delete, move/drop sorting, cover selection, save, and close controls are preserved.

Validation:
- Passed: `cd frontend && npm run build`.
- Passed: `cd admin && npm run build`.
- Passed: `python -m compileall backend\app`.
- Passed: frontend/admin dist Secret scan.

Remaining manual QA:
- Browser check for `/admin/photos` create album modal scrolling.
- Browser check for `/admin/photos` edit album modal scrolling.
- Browser check that all album photos are visible through the modal right-side scroll area at desktop and 390px.
