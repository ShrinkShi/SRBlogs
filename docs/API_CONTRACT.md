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

公开读取。后台可传 `include_drafts=true` 查看草稿。

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
    "content": "Markdown 正文"
  }
]
```

### GET `/{section}/{slug}`

公开读取单条内容。`slug` 必须通过 `validate_slug`，禁止路径穿越。

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

响应为保存后的 `ContentItem`。

### PUT `/{section}/{slug}`

后台 JWT。请求体同 POST。允许通过 body 中的新 `slug` 重命名，旧文件删除前必须备份。

### DELETE `/{section}/{slug}`

后台 JWT。删除前必须备份。响应：

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
  "bgImages": [],
  "cloudMusicIds": [],
  "comments": {
    "enabled": true,
    "requireEmail": false,
    "maxLength": 1000,
    "showEmail": false,
    "localEnabled": true,
    "gitalk": {
      "clientID": "",
      "repo": "",
      "owner": "",
      "admin": []
    }
  }
}
```

不得返回 GitHub OAuth Secret、AI Key、OSS Key、JWT Secret、管理员密码，也不得返回后台私有字段。

### GET `/admin/settings`

后台 JWT。返回可管理配置和 Secret 配置状态。Secret 不返回明文，只返回布尔值：

```json
{
  "siteTitle": "SRBlogs",
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
- `/music`：`title`、`artist`、`cover`、`url`、`id`、`sort`
- `/photos`：`url`、`title`、`description`、`date`、`tags`

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

### POST `/upload`

后台 JWT。`multipart/form-data` 字段：`file`。

限制：

- 扩展名：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`
- MIME：`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/svg+xml`
- 大小：不超过 5 MB

响应：

```json
{ "filename": "uuid.png", "url": "http://127.0.0.1:8000/uploads/uuid.png", "size": 1234 }
```

## Comments API

### GET `/comments/{resource}/{slug}`

公开读取。`resource` 仅允许 `posts`、`moments`、`chatters`，`slug` 必须通过 `validate_slug`。

### POST `/comments/{resource}/{slug}`

公开提交。请求体：

```json
{ "author": "name", "email": "optional@example.com", "content": "comment" }
```

响应：

```json
{
  "id": "uuid",
  "author": "name",
  "email": "optional@example.com",
  "content": "comment",
  "created_at": "2026-05-02 12:00"
}
```

提交内容必须用 bleach 清洗。

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
