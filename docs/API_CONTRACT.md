# API Contract

Base path: `/api`

统一错误响应：

```json
{ "code": "ERROR_CODE", "message": "用户可读错误", "detail": {} }
```

状态码约定：

- `400`：参数、格式、slug、JSON/Markdown 校验失败。
- `401`：未登录或 token 缺失/失效。
- `403`：已登录但无权限。
- `404`：资源不存在。
- `409`：slug 冲突、版本冲突、重复提交。
- `413`：上传文件过大。
- `415`：上传类型或 MIME 不允许。
- `500`：服务端未预期错误。

敏感配置不得进入前端构建产物。JWT Secret、管理员密码、AI Key、OSS Key、GitHub OAuth Secret 只能保存在后端 `.env` 或服务端配置中。

## Content APIs

适用于 `/api/posts`、`/api/moments`、`/api/chatters`。

### GET `/{section}`

公开读取已发布内容，默认不返回 `draft=true`。后台携带管理员 JWT 可传 `include_drafts=true` 查看草稿；未登录传 `include_drafts=true` 返回 `401`。

响应：

```json
[
  {
    "slug": "welcome",
    "meta": {
      "title": "标题",
      "date": "2026-05-02 12:00",
      "tags": ["Vue3"],
      "draft": false,
      "cover": "",
      "summary": ""
    },
    "content": "Markdown 正文",
    "updatedAt": "2026-05-02 12:30"
  }
]
```

### GET `/{section}/{slug}`

公开读取单条已发布内容。`slug` 必须通过 `validate_slug`，禁止路径穿越。`draft=true` 内容在公开详情中返回 `404`；后台携带管理员 JWT 可传 `include_drafts=true` 读取草稿详情，未登录传该参数返回 `401`。

### POST `/{section}`

后台 JWT。请求体：

```json
{
  "slug": "new-post",
  "meta": {
    "title": "标题",
    "date": "",
    "tags": [],
    "draft": false,
    "cover": "",
    "summary": ""
  },
  "content": "Markdown 正文"
}
```

响应为保存后的 `ContentItem`。重复 slug 返回 `409`，非法 slug 返回 `400`。

### PUT `/{section}/{slug}`

后台 JWT。请求体同 POST。允许通过 body 中的新 `slug` 重命名，旧文件删除前必须备份。更新不存在内容返回 `404`；重命名到已有 slug 返回 `409`。`draft=true -> false` 记为发布，`draft=false -> true` 记为撤回发布，并写入审计日志。

### DELETE `/{section}/{slug}`

后台 JWT。删除前必须备份并写审计日志；删除不存在内容返回 `404`。响应：

```json
{ "ok": true }
```

## Settings APIs

### GET `/settings/public`

前台公开读取。只返回公开站点配置和公开评论显示选项：

```json
{
  "siteTitle": "SRBlogs",
  "subtitle": "副标题",
  "author": "Author",
  "avatar": "https://example.com/avatar.png",
  "description": "站点简介",
  "socialLinks": {
    "github": "https://github.com/example"
  },
  "theme": "nebula",
  "themeConfig": {
    "fontFamily": "",
    "fontScale": "medium",
    "day": {
      "bgPage": "#eaf3f8",
      "bgCard": "rgba(255,255,255,.68)",
      "bgCardElevated": "rgba(255,255,255,.82)",
      "borderGlass": "rgba(14,116,144,.16)",
      "textPrimary": "rgba(15,23,42,.94)",
      "textSecondary": "rgba(30,41,59,.72)",
      "accent": "#0891b2",
      "accentSoft": "rgba(8,145,178,.12)",
      "navBg": "rgba(255,255,255,.72)",
      "homePanelBg": "rgba(255,255,255,.72)",
      "shadowGlow": "rgba(8,145,178,.2)"
    },
    "night": {
      "bgPage": "#050713",
      "bgCard": "rgba(255,255,255,.105)",
      "bgCardElevated": "rgba(255,255,255,.16)",
      "borderGlass": "rgba(255,255,255,.2)",
      "textPrimary": "rgba(247,251,255,.96)",
      "textSecondary": "rgba(247,251,255,.74)",
      "accent": "#67e8f9",
      "accentSoft": "rgba(103,232,249,.16)",
      "navBg": "rgba(7,12,28,.64)",
      "homePanelBg": "rgba(255,255,255,.105)",
      "shadowGlow": "rgba(34,211,238,.42)"
    }
  },
  "bgImages": [],
  "cloudMusicIds": [],
  "comments": {
    "enabled": true,
    "requireEmail": false,
    "maxLength": 1000,
    "showEmail": false,
    "githubOnly": true,
    "gitalk": {
      "clientID": "",
      "repo": "",
      "owner": "",
      "admin": []
    }
  }
}
```

`themeConfig` 是公开视觉配置，只允许包含颜色、字体和字号档位等非敏感 token。不得返回 GitHub OAuth Secret、AI Key、OSS Key、JWT Secret、管理员密码，也不得返回后台私有字段。

### GET `/admin/settings`

后台 JWT。返回可管理配置和 Secret 配置状态。Secret 不返回明文，只返回布尔值：

```json
{
  "siteTitle": "SRBlogs",
  "themeConfig": {
    "fontFamily": "",
    "fontScale": "medium",
    "day": {},
    "night": {}
  },
  "gitalkConfig": {
    "clientID": "",
    "repo": "",
    "owner": "",
    "admin": [],
    "githubOAuthSecretConfigured": true
  },
  "imageBed": {
    "provider": "local",
    "accessKeyConfigured": false,
    "secretKeyConfigured": false,
    "ossKeyConfigured": false
  },
  "ai": {
    "provider": "a",
    "aiKeyConfigured": false
  },
  "serverSecrets": {
    "jwtSecretConfigured": true,
    "adminPasswordConfigured": true,
    "ossKeyConfigured": false,
    "aiKeyConfigured": false,
    "githubOAuthSecretConfigured": true
  }
}
```

### PUT `/admin/settings`

后台 JWT。请求体：

```json
{ "data": { "title": "SRBlogs", "theme": "nebula" } }
```

保存到 `backend/data/settings.json`，写入必须走 `safe_write_json`。`PUT /api/admin/settings` 中 Secret 字段为空字符串、`null` 或未传时，后端必须保留旧值；只有传入明确新值时才覆盖。保存后响应仍不得回显 Secret 明文。

## Structured JSON APIs

适用于 `/friends`、`/projects`、`/music`、`/photos`。

### GET `/{resource}`

公开读取结构化内容列表。`/photos` 实际存储在 `backend/data/photos/photos.json`。

响应示例：

```json
[
  {
    "name": "站点名称",
    "url": "https://example.com",
    "description": "说明",
    "tags": ["Blog"]
  }
]
```

各资源主字段：
- `/friends`：`name`、`url`、`description`、`avatar`、`tags`
- `/projects`：`name`、`description`、`tags`、`url`、`repo`、`cover`、`status`
- `/music`：`title`、`artist`、`cover`、`url`、`lyricUrl`、`lyrics`、`id`、`sort`
- `/photos`：兼容旧单图 `{ url, title, description, date, tags }`；新相册组推荐 `{ title, description, cover, date, tags, photos: [{ url, title, description, date, tags }] }`，每组最多 50 张。

### PUT `/{resource}`

后台 JWT。请求体：

```json
{ "data": [] }
```

说明：
- 后台主流程应使用表单化管理，保留高级 JSON 编辑作为兜底。
- 高级 JSON 必须是数组；前端应在发送前校验 JSON 格式。
- 写入必须通过 `JsonStore.write` -> `safe_write_json`，覆盖前生成 `.backups` 备份。
- 图片上传、Secret 修改、评论删除不进入本地 `pendingOperations`。

## Discovery APIs

### GET `/search`

公开轻量搜索。数据来自后端 Markdown/JSON 读取，不使用前端直读文件，不接入全文索引数据库。

Query 参数：

- `q`：关键词，默认空字符串。
- `type`：`all`、`posts`、`moments`、`chatters`、`projects`、`photos`、`friends`、`music`，默认 `all`。
- `tag`：标签筛选，大小写不敏感，当前支持包含匹配，例如 `Vue` 可匹配 `Vue3`。
- `limit`：默认 20，范围 1-100。
- `offset`：默认 0。

搜索范围：

- `posts`、`moments`、`chatters`：`title`、`summary`、`tags`、`content`。
- `projects`：`name`、`description`、`tags`。
- `photos`：`title`、`description`。
- `friends`：`name`、`description`、`url`。
- `music`：`title`、`artist`。

`draft=true` 的内容不得进入公开搜索。`q` 和 `tag` 都为空时，接口返回最近公开内容；没有匹配结果时返回空数组，不返回 500。

响应：

```json
{
  "items": [
    {
      "type": "posts",
      "title": "文章标题",
      "slug": "post-slug",
      "summary": "摘要",
      "url": "/posts/post-slug",
      "tags": ["Vue", "FastAPI"],
      "date": "2026-05-02",
      "score": 10
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### GET `/tags`

公开标签统计。合并 `posts`、`moments`、`chatters`、`projects` 的 `tags`，草稿不进入统计。

响应：

```json
[
  {
    "tag": "Vue3",
    "count": 2,
    "types": ["posts", "projects"],
    "latestDate": "2026-05-02"
  }
]
```

### GET `/archive`

公开归档。按年月聚合 `posts`、`moments`、`chatters`，草稿不进入归档。时间解析失败的数据放入 `unknown` 分组，不应导致 500。

响应：

```json
{
  "years": [
    {
      "year": "2026",
      "months": [
        {
          "month": "05",
          "items": [
            {
              "type": "posts",
              "title": "标题",
              "slug": "slug",
              "url": "/posts/slug",
              "date": "2026-05-02",
              "tags": ["Vue3"]
            }
          ]
        }
      ]
    }
  ]
}
```

## SEO And Subscription APIs

### GET `/api/rss.xml`

公开 RSS 2.0 Feed，不需要 JWT。至少包含已发布 posts，可包含部分 chatters；`draft=true` 内容不得进入 RSS。

响应类型：`application/rss+xml; charset=utf-8`

每个 item 至少包含 `title`、`link`、`guid`、`pubDate`、`description`。`description` 必须做 XML/HTML 转义。站点链接基于 `PUBLIC_BASE_URL`；开发默认兜底为 `http://127.0.0.1:5173`。

### GET `/api/sitemap.xml`

公开 XML Sitemap，不需要 JWT。包含公开前台固定路由、已发布 posts 详情页、chatters 详情页和标签详情页；`draft=true` 内容不得进入 sitemap。

响应类型：`application/xml; charset=utf-8`

每个 url 至少包含 `loc`；有可解析日期时提供 `lastmod`。

### GET `/robots.txt`

公开 robots 文件，不需要 JWT。必须禁止爬取后台路径，并指向 sitemap。

```text
User-agent: *
Allow: /
Disallow: /admin
Sitemap: https://example.com/api/sitemap.xml
```

## Upload API

2026-05-03 更新：`POST /api/upload` 继续要求管理员 JWT，但本地资源上传范围从图片扩展为图片、音频、视频和歌词文本。后台表单可将上传返回的 URL 回填到头像、背景、照片/相册、封面、音乐 URL、歌词 URL 或后续视频字段。接口仍必须同时校验扩展名、MIME 和大小；非法类型返回 `415`，超大文件返回 `413`。

当前默认允许：

- 图片：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`
- 音频：`.mp3`、`.wav`、`.ogg`、`.m4a`
- 视频：`.mp4`、`.webm`、`.mov`
- 歌词：`.lrc`、`.txt`
- MIME：`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/svg+xml`、`audio/mpeg`、`audio/wav`、`audio/ogg`、`audio/mp4`、`video/mp4`、`video/webm`、`video/quicktime`
- 大小上限按类型分档：图片默认 10 MB，音频默认 100 MB，视频默认 200 MB，歌词默认 1 MB；不允许无限制上传。
- 错误信息需明确指出图片、音频、视频或歌词超过对应限制，方便后台 UI 显示可读错误。

### POST `/upload`

后台 JWT。`multipart/form-data` 字段：`file`。

限制：

- 扩展名：图片、音频、视频和歌词文件白名单，禁止可执行文件。
- MIME：图片/音频/视频必须匹配配置白名单；歌词仅允许 `.lrc`/`.txt` 的文本类型。
- 大小：图片 10 MB、音频 100 MB、视频 200 MB、歌词 1 MB。

响应：

```json
{ "filename": "uuid.png", "url": "http://127.0.0.1:8000/uploads/uuid.png", "size": 1234 }
```

## Comments API

### GET `/comments/{resource}/{slug}`

公开读取。`resource` 仅允许 `posts`、`moments`、`chatters`，`slug` 必须通过 `validate_slug`。

响应会读取公开评论配置：

- 旧评论可能包含本地作者名或脱敏邮箱；新评论仅使用 GitHub 登录身份。
- 前台不得直接渲染危险 HTML。

### POST `/comments/{resource}/{slug}`

GitHub 登录后提交。新评论只允许 GitHub 登录这一种身份；后端通过 `srblogs_github_user` HttpOnly cookie 读取 GitHub 用户，不接受前端伪造作者身份。

请求体：

```json
{ "content": "comment" }
```

响应：

```json
{
  "id": "uuid",
  "author": "GitHub Display Name",
  "email": "",
  "avatar": "https://avatars.githubusercontent.com/...",
  "githubLogin": "github-user",
  "content": "comment",
  "created_at": "2026-05-02 12:00"
}
```

提交规则：

- `comments.enabled=false` 时返回 `403`，不得继续提交。
- 未登录 GitHub 时返回 `401`。
- `comments.maxLength` 动态限制评论长度，超过返回 `400`。
- 提交内容必须用 bleach 清洗。
- 新评论响应中的 `email` 固定为空字符串，避免恢复匿名/邮箱评论入口。

### GitHub Auth For Comments

- `GET /auth/github/me`：返回 `{ configured, user }`。不需要 JWT，不返回 OAuth Secret。
- `GET /auth/github/login?returnTo=...`：启动 GitHub OAuth code flow，后端生成并校验 CSRF `state`；兼容旧参数 `return_to`。
- `GET /auth/github/callback`：后端使用 GitHub OAuth Secret 换取 access token，读取 GitHub 公开用户信息，写入 HttpOnly 登录 cookie 后跳回 `returnTo` 对应页面。
- `POST /auth/github/logout`：清除评论登录 cookie。

GitHub OAuth Client Secret 只能保存在后端 `.env` 或服务端配置。未配置时，前台留言板必须显示访客友好提示，不能回退到匿名评论。

### DELETE `/comments/{resource}/{slug}/{comment_id}`

后台 JWT。删除本地评论。删除前 `JsonStore.write` 必须通过 `safe_write_json` 备份原评论 JSON。

响应：

```json
{ "ok": true }
```

错误：

- `401`：未登录或 token 缺失/失效。
- `404`：评论 ID 不存在。

### GET `/admin/comments/index`

后台 JWT。返回已有评论的内容索引，供后台评论管理默认列表使用。扫描 `backend/data/comments` 下的评论 JSON 文件；目录不存在或没有评论时返回空数组，不返回 500。

该接口必须出现在 `http://127.0.0.1:8000/docs`。如果浏览器调用返回 404，优先确认 8000 后端进程是否已重启到当前代码。

响应：

```json
[
  {
    "resource": "posts",
    "slug": "srblogs-p0-20260502130609",
    "count": 3,
    "updatedAt": "2026-05-02 14:01",
    "title": "SRBlogs P0 Content Loop"
  }
]
```

说明：

- 文件名形如 `posts-srblogs-p0-20260502130609.json` 时，反推 `resource=posts`、`slug=srblogs-p0-20260502130609`。
- `resource` 仅允许 `posts`、`moments`、`chatters`。
- `title` 优先读取对应内容 Markdown Front Matter 的 `meta.title`；内容文件不存在时回退为 `slug`。
- 只返回后台评论索引需要的信息，不返回邮箱之外的额外评论详情，也不返回任何 Secret。

## Dashboard API

### GET `/dashboard/stats`

后台 JWT。响应：

```json
{ "posts": 0, "moments": 0, "chatters": 0, "photos": 0 }
```

## Admin Audit API

### GET `/admin/audit/logs`

后台 JWT。读取 `backend/data/audit/audit.log` 审计日志。

Query：
- `limit`：默认 50，最大 200。
- `offset`：默认 0。
- `action`：可选，精确筛选动作，例如 `posts.create`、`comment.delete`、`backup.restore`。
- `resource`：可选，精确筛选资源，例如 `posts`、`comments`、`backups`。
- `q`：可选，模糊搜索 actor/action/resource/target/result/message。

响应：
```json
{
  "items": [
    {
      "id": "uuid",
      "time": "2026-05-02T12:00:00",
      "actor": "admin",
      "action": "posts.create",
      "resource": "posts",
      "target": "post-slug",
      "result": "success",
      "message": "Content created",
      "ip": "127.0.0.1",
      "detail": {}
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

日志不得包含 Secret 明文。日志写入失败不得导致主业务操作失败。

### GET `/admin/system/status`

后台 JWT。返回生产健康检查所需的非敏感系统状态。

响应：
```json
{
  "app": "SRBlogs API",
  "backendRunning": true,
  "environment": "production",
  "dataPath": {
    "path": "/opt/srblogs/backend/data",
    "exists": true,
    "readable": true,
    "writable": true
  },
  "uploads": {
    "path": "/opt/srblogs/backend/data/uploads",
    "exists": true,
    "readable": true,
    "writable": true
  },
  "version": "release-candidate"
}
```

不得返回 `.env` 内容、管理员密码、JWT Secret、AI Key、OSS Key 或 OAuth Secret。

## Admin Backup API

### POST `/admin/backups`

后台 JWT。创建手动备份，写入 `backend/data/.manual_backups/{timestamp}.zip`。

备份范围：`posts`、`moments`、`chatters`、`comments`、`photos`、`friends.json`、`projects.json`、`music.json`、`settings.json`、`about.md`、`uploads`。不包含 `.env`、`.venv`、`node_modules`、`dist`、前端源码或手动备份目录本身。`settings.json` 写入 zip 前会剔除 Secret 字段。

响应：
```json
{ "name": "20260502120000000000.zip", "createdAt": "2026-05-02T12:00:00", "size": 12345 }
```

### GET `/admin/backups`

后台 JWT。返回手动备份列表。

```json
[
  { "name": "20260502120000000000.zip", "createdAt": "2026-05-02T12:00:00", "size": 12345 }
]
```

### GET `/admin/backups/{name}/download`

后台 JWT。下载备份 zip。`name` 必须是当前 `.manual_backups` 下的合法 `.zip` 文件名，禁止 `..`、`/`、`\` 和非 zip 名称。

### POST `/admin/backups/{name}/restore`

后台 JWT。恢复备份。恢复前会自动创建 `pre-restore-{timestamp}.zip`。

响应：
```json
{ "ok": true, "restored": "20260502120000000000.zip", "preRestoreBackup": "pre-restore-20260502121000000000.zip" }
```

错误：
- `400`：备份名非法、zip 内路径不安全、zip 包含不允许路径。
- `404`：备份不存在。
- `500`：恢复过程发生未预期错误。

### GET `/admin/export`

后台 JWT。导出当前内容数据 zip。语义等同创建 `export-{timestamp}.zip` 后下载，不包含 `.env` 或 Secret 明文字段。

### POST `/admin/import`

后台 JWT。上传 zip 并导入。导入前自动创建恢复前备份；zip 内路径必须安全且仅允许落在备份范围内。导入失败不得破坏现有数据。

## Chat API

### POST `/chat`

后台 JWT。AI Key 只从后端环境变量读取。

请求体：

```json
{
  "provider": "a",
  "messages": [{ "role": "user", "content": "hello" }],
  "stream": false
}
```

响应为上游兼容 OpenAI `/chat/completions` 的 JSON；未配置时返回：

```json
{ "content": "AI endpoint is not configured." }
```
# 2026-05-03 契约补充：前台 GitHub 评论入口

- GitHub 评论登录入口属于前台文章详情评论区；后台只提供 OAuth 配置和评论管理，不提供访客登录入口。
- `GET /api/auth/github/me` 供前台留言板判断 `{ configured, user }`。未配置时前台应显示“站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。”
- `POST /api/comments/{resource}/{slug}` 对未登录 GitHub 的请求返回 `401`，不得回退到匿名作者或邮箱评论。
- 前台展示名称统一为“留言板”。接口路径仍保持 `/api/comments/...`，避免破坏既有数据和后台管理契约。
- OAuth 未配置时，前台文案应面向访客，例如“站点暂未开启 GitHub 登录留言，请稍后再试或联系站点管理员。”，不得要求访客“配置后端”。
- 本轮未新增接口；照片墙相册组和音乐歌词仍复用既有 `/api/photos`、`/api/music`、`/api/upload` 契约。

## 2026-05-03 留言板与播放器补充

- 前台留言板使用 `GET /api/auth/github/me` 判断 `{ configured, user }`。`configured=false` 时前台显示访客友好提示，不暴露 OAuth Secret 或服务端配置细节。

## 2026-05-03 GitHub 留言 returnTo 契约修订

- `GET /api/auth/github/login?returnTo=/posts/{slug}` 是前台留言板启动 GitHub 登录的主入口；后端兼容旧参数 `return_to`。
- `returnTo` 支持前台相对路径。后端会解析为允许的前台来源，并拒绝非白名单绝对 URL 回跳，避免开放重定向。
- OAuth 未配置时该接口返回统一错误结构，不返回 Client Secret、OAuth Secret、`.env` 路径或 access token。
- `GET /api/auth/github/me` 返回 `{ "configured": boolean, "user": null | { "login": string, "name": string, "avatar": string, "html_url": string } }`，不返回 access token。
- `POST /api/comments/{resource}/{slug}` 必须有 GitHub 登录态；未登录返回 `401`，旧留言仍可公开读取。

## 2026-05-03 留言板公开配置契约

`GET /api/settings/public` 的 `comments` 字段固定为公开布尔状态，不返回 Secret：

```json
{
  "comments": {
    "enabled": true,
    "provider": "github",
    "githubLoginEnabled": true,
    "githubLoginConfigured": true,
    "maxLength": 1000
  }
}
```

- `enabled=false`：前台显示“留言板暂时关闭”。
- `enabled=true` 且 `githubLoginConfigured=false`：前台显示“站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。”
- `enabled=true` 且 `githubLoginConfigured=true` 且未登录：前台显示“使用 GitHub 登录后留言”按钮。
- `githubLoginConfigured` 只能是 boolean；不得返回 OAuth Secret、access token 或服务端配置路径。
- `POST /api/comments/{resource}/{slug}` 继续要求 GitHub 登录态；未登录返回 `401` 统一错误响应。
- 首页和音乐页音量属于前端本地状态，不新增 API；音量和静音状态写入浏览器 `localStorage`。
