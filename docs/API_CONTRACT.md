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

前台公开读取。只返回公开站点配置：

```json
{
  "title": "SRBlogs",
  "authorName": "Author",
  "bio": "",
  "avatarUrl": "",
  "defaultPostCover": "",
  "photoWallImage": "",
  "bgImages": [],
  "themeColors": [],
  "cloudMusicIds": [],
  "danmakuList": [],
  "social": {},
  "counts": {},
  "chatterTitle": "",
  "chatterDescription": "",
  "buildDate": "",
  "theme": "nebula",
  "gitalkConfig": {
    "clientID": "",
    "repo": "",
    "owner": "",
    "admin": [],
    "clientSecretConfigured": false
  }
}
```

不得返回 `clientSecret`、AI Key、OSS Key、JWT Secret、管理员密码。

### GET `/admin/settings`

后台 JWT。返回可管理配置和 Secret 配置状态。Secret 不返回明文，只返回布尔值：

```json
{
  "title": "SRBlogs",
  "gitalkConfig": {
    "clientID": "",
    "repo": "",
    "owner": "",
    "admin": [],
    "clientSecretConfigured": true
  },
  "imageBed": {
    "driver": "local",
    "ossKeyConfigured": false
  },
  "ai": {
    "active": "a",
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

保存到 `backend/data/settings.json`，写入必须走 `safe_write_json`。如果请求未提供已有 Secret，服务端保留旧值。

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
