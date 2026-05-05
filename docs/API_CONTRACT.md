## 2026-05-05 Theme Package And Page Padding Addendum

`GET /api/settings/public` 与 `GET/PUT /api/admin/settings` 的公开主题配置新增页面边距与 day/night 背景壁纸组能力。公开接口只返回视觉与布局字段，不返回任何 Secret。

前台主体内容最大宽度固定以 `1160px` 为基准，页面编辑组件宽度按 12 栅格比例计算。`themeConfig.layout.pagePadding` 只作为浏览器边缘安全留白配置，不参与页面组件宽度、组件高度、grid row/column 或 `pageLayouts` 计算。`pageLayouts` 中的 `w/h/rowSpan` 继续独立控制组件布局，二者不得互相覆盖。

后端保存时应将边距限制在安全范围内：

- `desktop`: `24..480`
- `tablet`: `16..120`
- `mobile`: `8..40`

主题配置字段：

```json
{
  "themeConfig": {
    "activeTheme": "shrink-red-glass",
    "layout": {
      "pagePadding": {
        "desktop": 180,
        "tablet": 72,
        "mobile": 18
      }
    },
    "themePackages": {
      "shrink-red-glass": {
        "id": "shrink-red-glass",
        "name": "Shrink 红白黑玻璃主题",
        "modes": {
          "day": {
            "bgImages": [{ "url": "/uploads/day.jpg", "name": "白天背景", "enabled": true }],
            "activeBgIndex": 0
          },
          "night": {
            "bgImages": [{ "url": "/uploads/night.jpg", "name": "夜间背景", "enabled": true }],
            "activeBgIndex": 0
          }
        },
        "layout": {
          "pagePadding": { "desktop": 180, "tablet": 72, "mobile": 18 }
        },
        "componentTheme": {},
        "pageLayouts": {}
      }
    }
  }
}
```

规则：
- `pagePadding.desktop/tablet/mobile` 分别控制前台桌面、平板、移动端内容左右边距，主题导入/导出与一键应用可以携带该字段。
- `modes.day.bgImages` 与 `modes.night.bgImages` 是当前主题日间/夜间独立背景壁纸组；旧版 `bgImage` 或 `bgImages` 导入时应兼容迁移。
- 后台主题管理可以新建、编辑、删除主题；当前启用主题不可直接删除。
- 主题包导出不得包含 GitHub/QQ Secret、AI Key、OSS Secret、管理员 token 或服务端绝对路径。

## 2026-05-05 Page Layout Row Span 与主题预设补充

### 页面布局组件字段

`GET /api/pages/config`、`GET /api/admin/pages/config` 和 `PUT /api/admin/pages/config` 的页面布局组件继续使用公开布局配置，并新增 `rowSpan` 字段：

```json
{
  "order": 1,
  "w": 4,
  "h": 4,
  "rowSpan": 2,
  "visible": true
}
```

字段说明：
- `w`：桌面端 12 栅格中的列跨度，支持小数输入，但前台会限制在可用栅格范围内。
- `h`：组件高度系数，用于计算组件最小高度。
- `rowSpan`：CSS Grid 行跨度，默认 `1`，首页四组件区域可使用 `2` 实现左侧高卡片跨两行。
- `visible`：是否在前台显示该组件。

兼容规则：
- 旧配置缺少 `rowSpan` 时按默认值 `1` 兜底。
- 首页默认布局升级为 `layoutVersion >= 2`，其中 `latestPostsCarousel` 默认 `w=4`、`h=4`、`rowSpan=2`，用于形成左高右分区的四组件布局。
- 前台公开接口不得返回 Secret、access token、服务端绝对路径或后台私有配置。

### 主题预设

全局主题预设通过现有后台设置保存流程写入 `themeConfig`，未新增单独业务接口：
- `白昼红白主题`：白/浅灰基底，红色作为强调色。
- `夜幕红黑主题`：黑/深灰基底，红色作为强调色。

组件级 `themeConfig.componentTheme` 仍保留独立覆盖能力。应用预设时应更新全局 token 和默认组件主题，但不得回显或覆盖任何 OAuth、AI、OSS 等 Secret 字段。

## 2026-05-05 Page Component Settings Contract

页面编辑组件设置由两类公开配置共同组成：

- 布局配置：`GET /api/pages/config` 与 `GET/PUT /api/admin/pages/config` 中的 `pageLayouts.{page}.components.{componentId}`。
- 组件主题配置：`GET /api/settings/public` 与 `GET/PUT /api/admin/settings` 中的 `themeConfig.componentTheme.{componentKey}`。

布局字段：

```json
{
  "order": 1,
  "w": 6,
  "h": 2,
  "visible": true
}
```

组件主题字段：

```json
{
  "label": "首页名片",
  "day": { "bg": "#ffffff", "text": "#111827" },
  "night": { "bg": "#111827", "text": "#f8fafc" },
  "opacity": 0.9,
  "size": "medium",
  "fontFamily": "",
  "fontSize": 16,
  "textColor": "#111827",
  "textAlign": "left",
  "fontWeight": "normal",
  "fontStyle": "normal"
}
```

保存规则：

- 保存布局设置时必须保留组件主题字段。
- 保存外观或字体设置时必须保留 `order/w/h/visible`。
- 保存字体设置时不得覆盖 `day/night/opacity/size`。
- 缺失字段必须在前台和后台使用默认值兜底，不得导致白屏。
- 公开接口只能返回公开视觉配置，不得返回 OAuth、AI、OSS 或其他 Secret 明文。

## 2026-05-05 Component Typography Addendum

组件级主题配置继续通过后台设置接口保存，并通过公开设置接口下发给前台。`themeConfig.componentTheme.{componentKey}` 可以包含以下公开视觉字段：

```json
{
  "label": "首页名片",
  "day": { "bg": "#ffffff", "text": "#111827", "accent": "#111827", "border": "#e5e7eb" },
  "night": { "bg": "#111827", "text": "#f8fafc", "accent": "#93c5fd", "border": "#334155" },
  "opacity": 0.9,
  "size": "medium",
  "fontFamily": "",
  "fontSize": 16,
  "textColor": "#111827",
  "textAlign": "left",
  "fontWeight": "normal",
  "fontStyle": "normal"
}
```

字段说明：
- `fontFamily`：组件字体族，空字符串表示使用全站默认字体。
- `fontSize`：组件文字字号，单位为 `px`。
- `textColor`：组件文字颜色，缺失时回退到组件主题文字色。
- `textAlign`：`left`、`center` 或 `right`。
- `fontWeight`：`normal`、`700` 或兼容 CSS 字重值。
- `fontStyle`：`normal` 或 `italic`。

安全边界：
- 这些字段属于公开视觉配置，可以出现在 `GET /api/settings/public`。
- `GET /api/admin/settings` 和 `PUT /api/admin/settings` 仍不得回显任何 OAuth、AI、OSS Secret 明文。
- 旧组件缺失字体字段时，前台必须使用默认值兜底，不得白屏。

## 2026-05-04 Page Config Precision Addendum

### GET `/api/pages/config`

公开读取页面文案与首页布局配置，不需要 JWT，不返回 Secret。

首页布局字段补充：

- `homeLayout.components.{componentId}.order`：组件顺序，数值越小越靠前。
- `homeLayout.components.{componentId}.w`：桌面端逻辑宽度，范围 `1` 到 `12`，支持 `0.1` 精度。前台将其映射到 120 子列布局，即 `grid span = round(w * 10)`。
- `homeLayout.components.{componentId}.h`：组件高度系数，范围 `0.5` 到 `6`，支持 `0.1` 精度。前台将其映射为组件 `min-height`。
- `homeLayout.components.{componentId}.visible`：是否显示该组件。

固定首页组件 ID：

- `profileCard`
- `musicPlayer`
- `lyrics`
- `latestPostsCarousel`
- `photoCarousel`
- `updatesCarousel`
- `themeToggle`
- `statusBar`

### GET `/api/admin/pages/config`

后台读取页面配置，需要管理员 JWT。返回结构与公开接口一致，但仍不得包含 Secret、access token、服务端绝对路径或私有配置明文。

### PUT `/api/admin/pages/config`

后台保存页面配置，需要管理员 JWT。写入必须走安全 JSON 写入封装并生成备份；保存失败返回统一错误结构 `{ code, message, detail }`。

允许保存精细尺寸：

```json
{
  "homeLayout": {
    "layoutVersion": 1,
    "components": {
      "profileCard": { "order": 1, "w": 6.5, "h": 2.4, "visible": true }
    }
  }
}
```

`w`、`h` 超出范围时后端或后台 UI 应归一化到安全范围，前台缺失配置时使用默认布局兜底。

## 2026-05-03 Pages Config API

### GET `/api/pages/config`

公开读取前台页面文案和首页布局配置，不需要 JWT。

响应示例：

```json
{
  "pageText": {
    "posts": { "title": "文章归档", "subtitle": "从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。" }
  },
  "homeProfile": {
    "author": "Shrink",
    "avatar": "/uploads/avatar.png",
    "description": "首页简介",
    "socialLinks": { "github": "https://github.com/ShrinkShi" }
  },
  "homeLayout": {
    "layoutVersion": 1,
    "components": {
      "profileCard": { "order": 1, "w": 6, "h": 2, "visible": true },
      "musicPlayer": { "order": 2, "w": 6, "h": 2, "visible": true },
      "lyrics": { "order": 3, "w": 12, "h": 1, "visible": true },
      "latestPostsCarousel": { "order": 4, "w": 4, "h": 3, "visible": true },
      "photoCarousel": { "order": 5, "w": 8, "h": 2, "visible": true },
      "updatesCarousel": { "order": 6, "w": 8, "h": 2, "visible": true },
      "themeToggle": { "order": 7, "w": 4, "h": 2, "visible": true },
      "statusBar": { "order": 8, "w": 12, "h": 1, "visible": true }
    }
  }
}
```

### GET `/api/admin/pages/config`

后台读取页面配置，需要管理员 JWT。结构同公开响应，不返回 Secret。

### PUT `/api/admin/pages/config`

后台保存页面配置，需要管理员 JWT。

- 写入文件：`backend/data/page_config.json`。
- 写入方式：`JsonStore.write`，底层继续走安全 JSON 写入和备份。
- 高风险变更写审计日志：`pages.config.update`。
- `homeLayout.components` 必须使用固定组件 ID：`profileCard`、`musicPlayer`、`lyrics`、`latestPostsCarousel`、`photoCarousel`、`updatesCarousel`、`themeToggle`、`statusBar`。
- `w` 表示 12 栅格宽度，`h` 表示高度档位，`order` 表示桌面排序。
- 该接口不得保存脚本、HTML 片段、Secret、access token 或服务器绝对路径。
- 接口兼容 `home.components` 旧/文档别名，但当前前后台主契约以 `homeLayout.components` 为准；两者同时存在时以后者为准。

### `themeConfig.opacity`

`GET /api/settings/public` 会返回公开透明度配置，后台通过 `PUT /api/admin/settings` 保存。该字段只控制前台视觉透明度，不包含任何私密配置。

```json
{
  "themeConfig": {
    "opacity": {
      "toolboxSettingsPanel": 0.92,
      "toolboxSearchPanel": 0.92,
      "toolboxCalculatorPanel": 0.9,
      "homeCard": 0.82,
      "homeCarousel": 0.82,
      "contentCard": 0.82,
      "photoCard": 0.82,
      "musicPanel": 0.88,
      "messageBoard": 0.86,
      "navBar": 0.72
    }
  }
}
```

- 所有值限制在 `0.60` 到 `1.00`。
- 后台设置页提供滑块和数字输入。
- 前台通过 CSS 变量应用，工具箱设置/搜索/计算器弹窗必须读取对应透明度字段。
- 公开响应不得包含 GitHub/QQ OAuth Secret、OSS Secret、AI Key、JWT Secret 或管理员密码。

## 2026-05-03 Page Editor Legacy Note

早期曾尝试把页面编辑数据挂在 `GET /api/settings/public` 的 `pageText/pageLayouts` 下。当前实现已改为独立 `GET /api/pages/config` 与 `PUT /api/admin/pages/config`，前台首页和各页面文案应优先读取 `/api/pages/config`。旧字段仅作兼容说明，不作为新增实现入口。

```json
{
  "pageText": {
    "home": { "title": "首页", "subtitle": "名片、音乐、歌词、轮播与状态区。" },
    "posts": { "title": "文章归档", "subtitle": "从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。" },
    "chatters": { "title": "云端杂谈", "subtitle": "长一点的念头，短一点的文章。" },
    "photos": { "title": "图片", "subtitle": "相册记录从后端 JSON 动态读取。" },
    "music": { "title": "音乐歌单", "subtitle": "全局播放器、歌词和歌单共享同一播放状态。" },
    "projects": { "title": "项目陈列柜", "subtitle": "记录正在构建和已经完成的作品。" },
    "friends": { "title": "星际友链", "subtitle": "把值得长期访问的站点放在这里。" },
    "about": { "title": "关于", "subtitle": "关于 SRBlogs 与站点作者。" }
  },
  "pageLayouts": {
    "home": {
      "blocks": [
        { "id": "profile", "label": "名片", "x": 4, "y": 6, "w": 42, "h": 24 }
      ]
    }
  }
}
```

- 上方 `pageText/pageLayouts` 是旧兼容结构示例；新实现使用 `pageText/homeProfile/homeLayout`。
- 后台通过 `PUT /api/admin/pages/config` 保存这些字段；写入 `backend/data/page_config.json`，底层仍走安全 JSON 写入流程。
- `pageText` / `homeProfile` / `homeLayout` 不得包含脚本、HTML 片段、Secret、access token 或服务端路径。
- 关于页 Markdown 仍通过 `GET /api/about` 与管理员 `PUT /api/about` 读写。

## 2026-05-03 Interaction And Page Layout Addendum

`GET /api/settings/public` 的公开 `interaction` 字段包含：

```json
{
  "interaction": {
    "clickSoundEnabled": true,
    "clickSoundVolume": 0.05,
    "clickSoundUrl": "",
    "clickEffectEnabled": true
  }
}
```

- `clickSoundEnabled` 表示站点是否允许前台点击音效；为 `false` 时游客本地设置不能强行开启。
- `clickEffectEnabled` 只表示站点是否允许前台鼠标点击视觉特效；为 `false` 时游客本地设置不能强行开启。
- 公开接口不得返回点击音效以外的私有配置，也不得返回任何 Secret。
- 游客本地开关存储在浏览器 localStorage；站点级开关关闭时前端必须禁用游客覆盖。

后台页面编辑第一阶段通过 `PUT /api/admin/settings` 保存 `pageLayouts` 配置，例如：

```json
{
  "pageLayouts": {
    "home": {
      "title": "首页页面",
      "subtitle": "首页页面的标题、副标题和预览布局。",
      "note": "编辑首页名片和核心模块说明",
      "blocks": [
        { "id": "hero", "label": "标题区域", "x": 6, "y": 8, "w": 88, "h": 18 }
      ]
    }
  }
}
```

`pageLayouts` 属于后台页面编辑配置，不应包含 Secret，不替代文章、图片、音乐等业务数据。

# API Contract

## 2026-05-03 工具箱与整合页 API 复用说明

本轮未新增后端接口，也未改变现有数据结构。

- `/posts` 正经板块继续读取公开 `GET /api/posts`，草稿不进入公开列表。
- `/posts?section=chatters` 杂谈板块读取公开 `GET /api/chatters`。
- 图片页继续读取公开 `GET /api/photos`，并以相册组形式展示。
- 工具箱全局搜索弹窗复用 `GET /api/search` 和 `GET /api/tags`。
- 工具箱游客设置只写入浏览器 localStorage，不调用后台私有配置接口。
- 音乐音量设置复用前端全局播放器状态，不新增 API。

安全边界：

- 工具箱和游客设置不得读取 `/api/admin/settings`。
- 公开搜索、文章、杂谈、图片接口不得返回后台 Secret。
- OAuth、OSS、AI 等 Secret 仍只能保存在后端 `.env` 或服务端配置中。

## 2026-05-03 多平台留言 Provider 状态契约修订

`GET /api/settings/public` 的留言配置必须使用稳定结构，并且只暴露布尔状态：

```json
{
  "comments": {
    "enabled": true,
    "maxLength": 1000,
    "providers": {
      "github": {
        "enabled": true,
        "configured": true,
        "clientIdConfigured": true,
        "secretConfigured": true
      },
      "qq": {
        "enabled": true,
        "configured": false,
        "appIdConfigured": true,
        "secretConfigured": false
      }
    }
  }
}
```

- `comments.enabled` 只表示全站留言板是否开放。
- `providers.github.enabled` 只表示是否允许 GitHub 登录留言。
- `providers.github.configured = clientIdConfigured && secretConfigured`。
- `providers.qq.configured = appIdConfigured && secretConfigured`。
- GitHub 与 QQ 必须独立判断；QQ 未配置不得影响 GitHub。
- 不得返回 GitHub OAuth Secret、QQ App Secret、access token 或 `.env` 路径。

认证入口：

- `GET /api/auth/github/login?returnTo=/posts/{slug}`：启动 GitHub OAuth。已配置时返回 307 跳转 GitHub；未配置时返回中文友好错误，不返回 404。
- `GET /api/auth/github/callback`：校验 state，服务端换 token，写入访客登录 cookie，并跳回 `returnTo`。
- `GET /api/auth/qq/login?returnTo=/posts/{slug}`：启动 QQ OAuth。未配置时返回中文友好错误，不返回 404。
- `GET /api/auth/qq/callback`：校验 state，服务端换 token，写入访客登录 cookie，并跳回 `returnTo`。
- `GET /api/auth/visitor/me`：返回 `{ configured: { github, qq }, user }`，不返回 access token。
- `POST /api/auth/visitor/logout`：清除访客登录态。
- 未登录 `POST /api/comments/{resource}/{slug}` 返回 `401`，消息为“请先登录后再留言。”。

## 2026-05-03 多平台留言公开状态修订

`GET /api/settings/public` 的 `comments` 字段优先使用多平台结构：

```json
{
  "comments": {
    "enabled": true,
    "provider": "multi",
    "providers": {
      "github": { "enabled": true, "configured": true },
      "qq": { "enabled": true, "configured": false }
    },
    "githubLoginEnabled": true,
    "githubLoginConfigured": true,
    "qqLoginEnabled": true,
    "qqLoginConfigured": false,
    "maxLength": 1000
  }
}
```

- `providers.github` 与 `providers.qq` 独立判断，QQ 未配置不得影响 GitHub。
- `configured` 只能是布尔值，不得返回 GitHub OAuth Secret、QQ App Secret、access token、`.env` 路径或服务端私有配置。
- 旧字段 `githubLoginConfigured`、`qqLoginConfigured` 暂时保留，用于兼容旧前端。

访客登录接口：

- `GET /api/auth/github/login?returnTo=/posts/{slug}`：启动 GitHub OAuth。后端生成 CSRF `state`，callback URL 使用当前后端请求生成，避免回调落到前台导致 404。
- `GET /api/auth/github/callback`：校验 `state`，服务端换取 token，写入 HttpOnly 访客登录 cookie 后跳回 `returnTo`。
- `GET /api/auth/qq/login?returnTo=/posts/{slug}`：启动 QQ OAuth，行为同上。
- `GET /api/auth/qq/callback`：校验 `state`，服务端换取 token 和公开资料，写入 HttpOnly 访客登录 cookie 后跳回 `returnTo`。
- `GET /api/auth/visitor/me`：返回 `{ configured: { github, qq }, user }`，不返回 access token。
- `POST /api/auth/visitor/logout`：清除访客登录 cookie。
- `POST /api/comments/{resource}/{slug}`：需要访客登录态；未登录返回 `401` 和中文错误提示。

前台未配置提示必须面向访客，例如“站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。”，不得出现 Secret、后端、`.env` 等配置细节。

Base path: `/api`

缁熶竴閿欒鍝嶅簲锛?
```json
{ "code": "ERROR_CODE", "message": "鐢ㄦ埛鍙閿欒", "detail": {} }
```

鐘舵€佺爜绾﹀畾锛?
- `400`锛氬弬鏁般€佹牸寮忋€乻lug銆丣SON/Markdown 鏍￠獙澶辫触銆?- `401`锛氭湭鐧诲綍鎴?token 缂哄け/澶辨晥銆?- `403`锛氬凡鐧诲綍浣嗘棤鏉冮檺銆?- `404`锛氳祫婧愪笉瀛樺湪銆?- `409`锛歴lug 鍐茬獊銆佺増鏈啿绐併€侀噸澶嶆彁浜ゃ€?- `413`锛氫笂浼犳枃浠惰繃澶с€?- `415`锛氫笂浼犵被鍨嬫垨 MIME 涓嶅厑璁搞€?- `500`锛氭湇鍔＄鏈鏈熼敊璇€?
鏁忔劅閰嶇疆涓嶅緱杩涘叆鍓嶇鏋勫缓浜х墿銆侸WT Secret銆佺鐞嗗憳瀵嗙爜銆丄I Key銆丱SS Key銆丟itHub OAuth Secret 鍙兘淇濆瓨鍦ㄥ悗绔?`.env` 鎴栨湇鍔＄閰嶇疆涓€?
## Content APIs

閫傜敤浜?`/api/posts`銆乣/api/moments`銆乣/api/chatters`銆?
### GET `/{section}`

鍏紑璇诲彇宸插彂甯冨唴瀹癸紝榛樿涓嶈繑鍥?`draft=true`銆傚悗鍙版惡甯︾鐞嗗憳 JWT 鍙紶 `include_drafts=true` 鏌ョ湅鑽夌锛涙湭鐧诲綍浼?`include_drafts=true` 杩斿洖 `401`銆?
鍝嶅簲锛?
```json
[
  {
    "slug": "welcome",
    "meta": {
      "title": "鏍囬",
      "date": "2026-05-02 12:00",
      "tags": ["Vue3"],
      "draft": false,
      "cover": "",
      "summary": ""
    },
    "content": "Markdown 姝ｆ枃",
    "updatedAt": "2026-05-02 12:30"
  }
]
```

### GET `/{section}/{slug}`

鍏紑璇诲彇鍗曟潯宸插彂甯冨唴瀹广€俙slug` 蹇呴』閫氳繃 `validate_slug`锛岀姝㈣矾寰勭┛瓒娿€俙draft=true` 鍐呭鍦ㄥ叕寮€璇︽儏涓繑鍥?`404`锛涘悗鍙版惡甯︾鐞嗗憳 JWT 鍙紶 `include_drafts=true` 璇诲彇鑽夌璇︽儏锛屾湭鐧诲綍浼犺鍙傛暟杩斿洖 `401`銆?
### POST `/{section}`

鍚庡彴 JWT銆傝姹備綋锛?
```json
{
  "slug": "new-post",
  "meta": {
    "title": "鏍囬",
    "date": "",
    "tags": [],
    "draft": false,
    "cover": "",
    "summary": ""
  },
  "content": "Markdown 姝ｆ枃"
}
```

鍝嶅簲涓轰繚瀛樺悗鐨?`ContentItem`銆傞噸澶?slug 杩斿洖 `409`锛岄潪娉?slug 杩斿洖 `400`銆?
### PUT `/{section}/{slug}`

鍚庡彴 JWT銆傝姹備綋鍚?POST銆傚厑璁搁€氳繃 body 涓殑鏂?`slug` 閲嶅懡鍚嶏紝鏃ф枃浠跺垹闄ゅ墠蹇呴』澶囦唤銆傛洿鏂颁笉瀛樺湪鍐呭杩斿洖 `404`锛涢噸鍛藉悕鍒板凡鏈?slug 杩斿洖 `409`銆俙draft=true -> false` 璁颁负鍙戝竷锛宍draft=false -> true` 璁颁负鎾ゅ洖鍙戝竷锛屽苟鍐欏叆瀹¤鏃ュ織銆?
### DELETE `/{section}/{slug}`

鍚庡彴 JWT銆傚垹闄ゅ墠蹇呴』澶囦唤骞跺啓瀹¤鏃ュ織锛涘垹闄や笉瀛樺湪鍐呭杩斿洖 `404`銆傚搷搴旓細

```json
{ "ok": true }
```

## Settings APIs

### GET `/settings/public`

鍓嶅彴鍏紑璇诲彇銆傚彧杩斿洖鍏紑绔欑偣閰嶇疆鍜屽叕寮€璇勮鏄剧ず閫夐」锛?
```json
{
  "siteTitle": "SRBlogs",
  "subtitle": "鍓爣棰?,
  "author": "Author",
  "avatar": "https://example.com/avatar.png",
  "description": "绔欑偣绠€浠?,
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

`themeConfig` 鏄叕寮€瑙嗚閰嶇疆锛屽彧鍏佽鍖呭惈棰滆壊銆佸瓧浣撳拰瀛楀彿妗ｄ綅绛夐潪鏁忔劅 token銆備笉寰楄繑鍥?GitHub OAuth Secret銆丄I Key銆丱SS Key銆丣WT Secret銆佺鐞嗗憳瀵嗙爜锛屼篃涓嶅緱杩斿洖鍚庡彴绉佹湁瀛楁銆?
### GET `/admin/settings`

鍚庡彴 JWT銆傝繑鍥炲彲绠＄悊閰嶇疆鍜?Secret 閰嶇疆鐘舵€併€係ecret 涓嶈繑鍥炴槑鏂囷紝鍙繑鍥炲竷灏斿€硷細

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

鍚庡彴 JWT銆傝姹備綋锛?
```json
{ "data": { "title": "SRBlogs", "theme": "nebula" } }
```

淇濆瓨鍒?`backend/data/settings.json`锛屽啓鍏ュ繀椤昏蛋 `safe_write_json`銆俙PUT /api/admin/settings` 涓?Secret 瀛楁涓虹┖瀛楃涓层€乣null` 鎴栨湭浼犳椂锛屽悗绔繀椤讳繚鐣欐棫鍊硷紱鍙湁浼犲叆鏄庣‘鏂板€兼椂鎵嶈鐩栥€備繚瀛樺悗鍝嶅簲浠嶄笉寰楀洖鏄?Secret 鏄庢枃銆?
## Structured JSON APIs

閫傜敤浜?`/friends`銆乣/projects`銆乣/music`銆乣/photos`銆?
### GET `/{resource}`

鍏紑璇诲彇缁撴瀯鍖栧唴瀹瑰垪琛ㄣ€俙/photos` 瀹為檯瀛樺偍鍦?`backend/data/photos/photos.json`銆?
鍝嶅簲绀轰緥锛?
```json
[
  {
    "name": "绔欑偣鍚嶇О",
    "url": "https://example.com",
    "description": "璇存槑",
    "tags": ["Blog"]
  }
]
```

鍚勮祫婧愪富瀛楁锛?- `/friends`锛歚name`銆乣url`銆乣description`銆乣avatar`銆乣tags`
- `/projects`锛歚name`銆乣description`銆乣tags`銆乣url`銆乣repo`銆乣cover`銆乣status`
- `/music`锛歚title`銆乣artist`銆乣cover`銆乣url`銆乣lyricUrl`銆乣lyrics`銆乣id`銆乣sort`
- `/photos`锛氬吋瀹规棫鍗曞浘 `{ url, title, description, date, tags }`锛涙柊鐩稿唽缁勬帹鑽?`{ title, description, cover, date, tags, photos: [{ url, title, description, date, tags }] }`锛屾瘡缁勬渶澶?50 寮犮€?
### PUT `/{resource}`

鍚庡彴 JWT銆傝姹備綋锛?
```json
{ "data": [] }
```

璇存槑锛?- 鍚庡彴涓绘祦绋嬪簲浣跨敤琛ㄥ崟鍖栫鐞嗭紝淇濈暀楂樼骇 JSON 缂栬緫浣滀负鍏滃簳銆?- 楂樼骇 JSON 蹇呴』鏄暟缁勶紱鍓嶇搴斿湪鍙戦€佸墠鏍￠獙 JSON 鏍煎紡銆?- 鍐欏叆蹇呴』閫氳繃 `JsonStore.write` -> `safe_write_json`锛岃鐩栧墠鐢熸垚 `.backups` 澶囦唤銆?- 鍥剧墖涓婁紶銆丼ecret 淇敼銆佽瘎璁哄垹闄や笉杩涘叆鏈湴 `pendingOperations`銆?
## Discovery APIs

### GET `/search`

鍏紑杞婚噺鎼滅储銆傛暟鎹潵鑷悗绔?Markdown/JSON 璇诲彇锛屼笉浣跨敤鍓嶇鐩磋鏂囦欢锛屼笉鎺ュ叆鍏ㄦ枃绱㈠紩鏁版嵁搴撱€?
Query 鍙傛暟锛?
- `q`锛氬叧閿瘝锛岄粯璁ょ┖瀛楃涓层€?- `type`锛歚all`銆乣posts`銆乣moments`銆乣chatters`銆乣projects`銆乣photos`銆乣friends`銆乣music`锛岄粯璁?`all`銆?- `tag`锛氭爣绛剧瓫閫夛紝澶у皬鍐欎笉鏁忔劅锛屽綋鍓嶆敮鎸佸寘鍚尮閰嶏紝渚嬪 `Vue` 鍙尮閰?`Vue3`銆?- `limit`锛氶粯璁?20锛岃寖鍥?1-100銆?- `offset`锛氶粯璁?0銆?
鎼滅储鑼冨洿锛?
- `posts`銆乣moments`銆乣chatters`锛歚title`銆乣summary`銆乣tags`銆乣content`銆?- `projects`锛歚name`銆乣description`銆乣tags`銆?- `photos`锛歚title`銆乣description`銆?- `friends`锛歚name`銆乣description`銆乣url`銆?- `music`锛歚title`銆乣artist`銆?
`draft=true` 鐨勫唴瀹逛笉寰楄繘鍏ュ叕寮€鎼滅储銆俙q` 鍜?`tag` 閮戒负绌烘椂锛屾帴鍙ｈ繑鍥炴渶杩戝叕寮€鍐呭锛涙病鏈夊尮閰嶇粨鏋滄椂杩斿洖绌烘暟缁勶紝涓嶈繑鍥?500銆?
鍝嶅簲锛?
```json
{
  "items": [
    {
      "type": "posts",
      "title": "鏂囩珷鏍囬",
      "slug": "post-slug",
      "summary": "鎽樿",
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

鍏紑鏍囩缁熻銆傚悎骞?`posts`銆乣moments`銆乣chatters`銆乣projects` 鐨?`tags`锛岃崏绋夸笉杩涘叆缁熻銆?
鍝嶅簲锛?
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

鍏紑褰掓。銆傛寜骞存湀鑱氬悎 `posts`銆乣moments`銆乣chatters`锛岃崏绋夸笉杩涘叆褰掓。銆傛椂闂磋В鏋愬け璐ョ殑鏁版嵁鏀惧叆 `unknown` 鍒嗙粍锛屼笉搴斿鑷?500銆?
鍝嶅簲锛?
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
              "title": "鏍囬",
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

鍏紑 RSS 2.0 Feed锛屼笉闇€瑕?JWT銆傝嚦灏戝寘鍚凡鍙戝竷 posts锛屽彲鍖呭惈閮ㄥ垎 chatters锛沗draft=true` 鍐呭涓嶅緱杩涘叆 RSS銆?
鍝嶅簲绫诲瀷锛歚application/rss+xml; charset=utf-8`

姣忎釜 item 鑷冲皯鍖呭惈 `title`銆乣link`銆乣guid`銆乣pubDate`銆乣description`銆俙description` 蹇呴』鍋?XML/HTML 杞箟銆傜珯鐐归摼鎺ュ熀浜?`PUBLIC_BASE_URL`锛涘紑鍙戦粯璁ゅ厹搴曚负 `http://127.0.0.1:5173`銆?
### GET `/api/sitemap.xml`

鍏紑 XML Sitemap锛屼笉闇€瑕?JWT銆傚寘鍚叕寮€鍓嶅彴鍥哄畾璺敱銆佸凡鍙戝竷 posts 璇︽儏椤点€乧hatters 璇︽儏椤靛拰鏍囩璇︽儏椤碉紱`draft=true` 鍐呭涓嶅緱杩涘叆 sitemap銆?
鍝嶅簲绫诲瀷锛歚application/xml; charset=utf-8`

姣忎釜 url 鑷冲皯鍖呭惈 `loc`锛涙湁鍙В鏋愭棩鏈熸椂鎻愪緵 `lastmod`銆?
### GET `/robots.txt`

鍏紑 robots 鏂囦欢锛屼笉闇€瑕?JWT銆傚繀椤荤姝㈢埇鍙栧悗鍙拌矾寰勶紝骞舵寚鍚?sitemap銆?
```text
User-agent: *
Allow: /
Disallow: /admin
Sitemap: https://example.com/api/sitemap.xml
```

## Upload API

2026-05-03 鏇存柊锛歚POST /api/upload` 缁х画瑕佹眰绠＄悊鍛?JWT锛屼絾鏈湴璧勬簮涓婁紶鑼冨洿浠庡浘鐗囨墿灞曚负鍥剧墖銆侀煶棰戙€佽棰戝拰姝岃瘝鏂囨湰銆傚悗鍙拌〃鍗曞彲灏嗕笂浼犺繑鍥炵殑 URL 鍥炲～鍒板ご鍍忋€佽儗鏅€佺収鐗?鐩稿唽銆佸皝闈€侀煶涔?URL銆佹瓕璇?URL 鎴栧悗缁棰戝瓧娈点€傛帴鍙ｄ粛蹇呴』鍚屾椂鏍￠獙鎵╁睍鍚嶃€丮IME 鍜屽ぇ灏忥紱闈炴硶绫诲瀷杩斿洖 `415`锛岃秴澶ф枃浠惰繑鍥?`413`銆?
褰撳墠榛樿鍏佽锛?
- 鍥剧墖锛歚.jpg`銆乣.jpeg`銆乣.png`銆乣.gif`銆乣.webp`銆乣.svg`
- 闊抽锛歚.mp3`銆乣.wav`銆乣.ogg`銆乣.m4a`
- 瑙嗛锛歚.mp4`銆乣.webm`銆乣.mov`
- 姝岃瘝锛歚.lrc`銆乣.txt`
- MIME锛歚image/jpeg`銆乣image/png`銆乣image/gif`銆乣image/webp`銆乣image/svg+xml`銆乣audio/mpeg`銆乣audio/wav`銆乣audio/ogg`銆乣audio/mp4`銆乣video/mp4`銆乣video/webm`銆乣video/quicktime`
- 澶у皬涓婇檺鎸夌被鍨嬪垎妗ｏ細鍥剧墖榛樿 10 MB锛岄煶棰戦粯璁?100 MB锛岃棰戦粯璁?200 MB锛屾瓕璇嶉粯璁?1 MB锛涗笉鍏佽鏃犻檺鍒朵笂浼犮€?- 閿欒淇℃伅闇€鏄庣‘鎸囧嚭鍥剧墖銆侀煶棰戙€佽棰戞垨姝岃瘝瓒呰繃瀵瑰簲闄愬埗锛屾柟渚垮悗鍙?UI 鏄剧ず鍙閿欒銆?
### POST `/upload`

鍚庡彴 JWT銆俙multipart/form-data` 瀛楁锛歚file`銆?
闄愬埗锛?
- 鎵╁睍鍚嶏細鍥剧墖銆侀煶棰戙€佽棰戝拰姝岃瘝鏂囦欢鐧藉悕鍗曪紝绂佹鍙墽琛屾枃浠躲€?- MIME锛氬浘鐗?闊抽/瑙嗛蹇呴』鍖归厤閰嶇疆鐧藉悕鍗曪紱姝岃瘝浠呭厑璁?`.lrc`/`.txt` 鐨勬枃鏈被鍨嬨€?- 澶у皬锛氬浘鐗?10 MB銆侀煶棰?100 MB銆佽棰?200 MB銆佹瓕璇?1 MB銆?
鍝嶅簲锛?
```json
{ "filename": "uuid.png", "url": "http://127.0.0.1:8000/uploads/uuid.png", "size": 1234 }
```

## Comments API

### GET `/comments/{resource}/{slug}`

鍏紑璇诲彇銆俙resource` 浠呭厑璁?`posts`銆乣moments`銆乣chatters`锛宍slug` 蹇呴』閫氳繃 `validate_slug`銆?
鍝嶅簲浼氳鍙栧叕寮€璇勮閰嶇疆锛?
- 鏃ц瘎璁哄彲鑳藉寘鍚湰鍦颁綔鑰呭悕鎴栬劚鏁忛偖绠憋紱鏂拌瘎璁轰粎浣跨敤 GitHub 鐧诲綍韬唤銆?- 鍓嶅彴涓嶅緱鐩存帴娓叉煋鍗遍櫓 HTML銆?
### POST `/comments/{resource}/{slug}`

GitHub 鐧诲綍鍚庢彁浜ゃ€傛柊璇勮鍙厑璁?GitHub 鐧诲綍杩欎竴绉嶈韩浠斤紱鍚庣閫氳繃 `srblogs_github_user` HttpOnly cookie 璇诲彇 GitHub 鐢ㄦ埛锛屼笉鎺ュ彈鍓嶇浼€犱綔鑰呰韩浠姐€?
璇锋眰浣擄細

```json
{ "content": "comment" }
```

鍝嶅簲锛?
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

鎻愪氦瑙勫垯锛?
- `comments.enabled=false` 鏃惰繑鍥?`403`锛屼笉寰楃户缁彁浜ゃ€?- 鏈櫥褰?GitHub 鏃惰繑鍥?`401`銆?- `comments.maxLength` 鍔ㄦ€侀檺鍒惰瘎璁洪暱搴︼紝瓒呰繃杩斿洖 `400`銆?- 鎻愪氦鍐呭蹇呴』鐢?bleach 娓呮礂銆?- 鏂拌瘎璁哄搷搴斾腑鐨?`email` 鍥哄畾涓虹┖瀛楃涓诧紝閬垮厤鎭㈠鍖垮悕/閭璇勮鍏ュ彛銆?
### GitHub Auth For Comments

- `GET /auth/github/me`锛氳繑鍥?`{ configured, user }`銆備笉闇€瑕?JWT锛屼笉杩斿洖 OAuth Secret銆?- `GET /auth/github/login?returnTo=...`锛氬惎鍔?GitHub OAuth code flow锛屽悗绔敓鎴愬苟鏍￠獙 CSRF `state`锛涘吋瀹规棫鍙傛暟 `return_to`銆?- `GET /auth/github/callback`锛氬悗绔娇鐢?GitHub OAuth Secret 鎹㈠彇 access token锛岃鍙?GitHub 鍏紑鐢ㄦ埛淇℃伅锛屽啓鍏?HttpOnly 鐧诲綍 cookie 鍚庤烦鍥?`returnTo` 瀵瑰簲椤甸潰銆?- `POST /auth/github/logout`锛氭竻闄よ瘎璁虹櫥褰?cookie銆?
GitHub OAuth Client Secret 鍙兘淇濆瓨鍦ㄥ悗绔?`.env` 鎴栨湇鍔＄閰嶇疆銆傛湭閰嶇疆鏃讹紝鍓嶅彴鐣欒█鏉垮繀椤绘樉绀鸿瀹㈠弸濂芥彁绀猴紝涓嶈兘鍥為€€鍒板尶鍚嶈瘎璁恒€?
### DELETE `/comments/{resource}/{slug}/{comment_id}`

鍚庡彴 JWT銆傚垹闄ゆ湰鍦拌瘎璁恒€傚垹闄ゅ墠 `JsonStore.write` 蹇呴』閫氳繃 `safe_write_json` 澶囦唤鍘熻瘎璁?JSON銆?
鍝嶅簲锛?
```json
{ "ok": true }
```

閿欒锛?
- `401`锛氭湭鐧诲綍鎴?token 缂哄け/澶辨晥銆?- `404`锛氳瘎璁?ID 涓嶅瓨鍦ㄣ€?
### GET `/admin/comments/index`

鍚庡彴 JWT銆傝繑鍥炲凡鏈夎瘎璁虹殑鍐呭绱㈠紩锛屼緵鍚庡彴璇勮绠＄悊榛樿鍒楄〃浣跨敤銆傛壂鎻?`backend/data/comments` 涓嬬殑璇勮 JSON 鏂囦欢锛涚洰褰曚笉瀛樺湪鎴栨病鏈夎瘎璁烘椂杩斿洖绌烘暟缁勶紝涓嶈繑鍥?500銆?
璇ユ帴鍙ｅ繀椤诲嚭鐜板湪 `http://127.0.0.1:8000/docs`銆傚鏋滄祻瑙堝櫒璋冪敤杩斿洖 404锛屼紭鍏堢‘璁?8000 鍚庣杩涚▼鏄惁宸查噸鍚埌褰撳墠浠ｇ爜銆?
鍝嶅簲锛?
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

璇存槑锛?
- 鏂囦欢鍚嶅舰濡?`posts-srblogs-p0-20260502130609.json` 鏃讹紝鍙嶆帹 `resource=posts`銆乣slug=srblogs-p0-20260502130609`銆?- `resource` 浠呭厑璁?`posts`銆乣moments`銆乣chatters`銆?- `title` 浼樺厛璇诲彇瀵瑰簲鍐呭 Markdown Front Matter 鐨?`meta.title`锛涘唴瀹规枃浠朵笉瀛樺湪鏃跺洖閫€涓?`slug`銆?- 鍙繑鍥炲悗鍙拌瘎璁虹储寮曢渶瑕佺殑淇℃伅锛屼笉杩斿洖閭涔嬪鐨勯澶栬瘎璁鸿鎯咃紝涔熶笉杩斿洖浠讳綍 Secret銆?
## Dashboard API

### GET `/dashboard/stats`

鍚庡彴 JWT銆傚搷搴旓細

```json
{ "posts": 0, "moments": 0, "chatters": 0, "photos": 0 }
```

## Admin Audit API

### GET `/admin/audit/logs`

鍚庡彴 JWT銆傝鍙?`backend/data/audit/audit.log` 瀹¤鏃ュ織銆?
Query锛?- `limit`锛氶粯璁?50锛屾渶澶?200銆?- `offset`锛氶粯璁?0銆?- `action`锛氬彲閫夛紝绮剧‘绛涢€夊姩浣滐紝渚嬪 `posts.create`銆乣comment.delete`銆乣backup.restore`銆?- `resource`锛氬彲閫夛紝绮剧‘绛涢€夎祫婧愶紝渚嬪 `posts`銆乣comments`銆乣backups`銆?- `q`锛氬彲閫夛紝妯＄硦鎼滅储 actor/action/resource/target/result/message銆?
鍝嶅簲锛?```json
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

鏃ュ織涓嶅緱鍖呭惈 Secret 鏄庢枃銆傛棩蹇楀啓鍏ュけ璐ヤ笉寰楀鑷翠富涓氬姟鎿嶄綔澶辫触銆?
### GET `/admin/system/status`

鍚庡彴 JWT銆傝繑鍥炵敓浜у仴搴锋鏌ユ墍闇€鐨勯潪鏁忔劅绯荤粺鐘舵€併€?
鍝嶅簲锛?```json
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

涓嶅緱杩斿洖 `.env` 鍐呭銆佺鐞嗗憳瀵嗙爜銆丣WT Secret銆丄I Key銆丱SS Key 鎴?OAuth Secret銆?
## Admin Backup API

### POST `/admin/backups`

鍚庡彴 JWT銆傚垱寤烘墜鍔ㄥ浠斤紝鍐欏叆 `backend/data/.manual_backups/{timestamp}.zip`銆?
澶囦唤鑼冨洿锛歚posts`銆乣moments`銆乣chatters`銆乣comments`銆乣photos`銆乣friends.json`銆乣projects.json`銆乣music.json`銆乣settings.json`銆乣about.md`銆乣uploads`銆備笉鍖呭惈 `.env`銆乣.venv`銆乣node_modules`銆乣dist`銆佸墠绔簮鐮佹垨鎵嬪姩澶囦唤鐩綍鏈韩銆俙settings.json` 鍐欏叆 zip 鍓嶄細鍓旈櫎 Secret 瀛楁銆?
鍝嶅簲锛?```json
{ "name": "20260502120000000000.zip", "createdAt": "2026-05-02T12:00:00", "size": 12345 }
```

### GET `/admin/backups`

鍚庡彴 JWT銆傝繑鍥炴墜鍔ㄥ浠藉垪琛ㄣ€?
```json
[
  { "name": "20260502120000000000.zip", "createdAt": "2026-05-02T12:00:00", "size": 12345 }
]
```

### GET `/admin/backups/{name}/download`

鍚庡彴 JWT銆備笅杞藉浠?zip銆俙name` 蹇呴』鏄綋鍓?`.manual_backups` 涓嬬殑鍚堟硶 `.zip` 鏂囦欢鍚嶏紝绂佹 `..`銆乣/`銆乣\` 鍜岄潪 zip 鍚嶇О銆?
### POST `/admin/backups/{name}/restore`

鍚庡彴 JWT銆傛仮澶嶅浠姐€傛仮澶嶅墠浼氳嚜鍔ㄥ垱寤?`pre-restore-{timestamp}.zip`銆?
鍝嶅簲锛?```json
{ "ok": true, "restored": "20260502120000000000.zip", "preRestoreBackup": "pre-restore-20260502121000000000.zip" }
```

閿欒锛?- `400`锛氬浠藉悕闈炴硶銆亃ip 鍐呰矾寰勪笉瀹夊叏銆亃ip 鍖呭惈涓嶅厑璁歌矾寰勩€?- `404`锛氬浠戒笉瀛樺湪銆?- `500`锛氭仮澶嶈繃绋嬪彂鐢熸湭棰勬湡閿欒銆?
### GET `/admin/export`

鍚庡彴 JWT銆傚鍑哄綋鍓嶅唴瀹规暟鎹?zip銆傝涔夌瓑鍚屽垱寤?`export-{timestamp}.zip` 鍚庝笅杞斤紝涓嶅寘鍚?`.env` 鎴?Secret 鏄庢枃瀛楁銆?
### POST `/admin/import`

鍚庡彴 JWT銆備笂浼?zip 骞跺鍏ャ€傚鍏ュ墠鑷姩鍒涘缓鎭㈠鍓嶅浠斤紱zip 鍐呰矾寰勫繀椤诲畨鍏ㄤ笖浠呭厑璁歌惤鍦ㄥ浠借寖鍥村唴銆傚鍏ュけ璐ヤ笉寰楃牬鍧忕幇鏈夋暟鎹€?
## Chat API

### POST `/chat`

鍚庡彴 JWT銆侫I Key 鍙粠鍚庣鐜鍙橀噺璇诲彇銆?
璇锋眰浣擄細

```json
{
  "provider": "a",
  "messages": [{ "role": "user", "content": "hello" }],
  "stream": false
}
```

鍝嶅簲涓轰笂娓稿吋瀹?OpenAI `/chat/completions` 鐨?JSON锛涙湭閰嶇疆鏃惰繑鍥烇細

```json
{ "content": "AI endpoint is not configured." }
```
# 2026-05-03 濂戠害琛ュ厖锛氬墠鍙?GitHub 璇勮鍏ュ彛

- GitHub 璇勮鐧诲綍鍏ュ彛灞炰簬鍓嶅彴鏂囩珷璇︽儏璇勮鍖猴紱鍚庡彴鍙彁渚?OAuth 閰嶇疆鍜岃瘎璁虹鐞嗭紝涓嶆彁渚涜瀹㈢櫥褰曞叆鍙ｃ€?- `GET /api/auth/github/me` 渚涘墠鍙扮暀瑷€鏉垮垽鏂?`{ configured, user }`銆傛湭閰嶇疆鏃跺墠鍙板簲鏄剧ず鈥滅珯鐐规殏鏈紑鍚?GitHub 鐣欒█锛岃绋嶅悗鍐嶈瘯鎴栬仈绯荤珯鐐圭鐞嗗憳銆傗€?- `POST /api/comments/{resource}/{slug}` 瀵规湭鐧诲綍 GitHub 鐨勮姹傝繑鍥?`401`锛屼笉寰楀洖閫€鍒板尶鍚嶄綔鑰呮垨閭璇勮銆?- 鍓嶅彴灞曠ず鍚嶇О缁熶竴涓衡€滅暀瑷€鏉库€濄€傛帴鍙ｈ矾寰勪粛淇濇寔 `/api/comments/...`锛岄伩鍏嶇牬鍧忔棦鏈夋暟鎹拰鍚庡彴绠＄悊濂戠害銆?- OAuth 鏈厤缃椂锛屽墠鍙版枃妗堝簲闈㈠悜璁垮锛屼緥濡傗€滅珯鐐规殏鏈紑鍚?GitHub 鐧诲綍鐣欒█锛岃绋嶅悗鍐嶈瘯鎴栬仈绯荤珯鐐圭鐞嗗憳銆傗€濓紝涓嶅緱瑕佹眰璁垮鈥滈厤缃悗绔€濄€?- 鏈疆鏈柊澧炴帴鍙ｏ紱鐓х墖澧欑浉鍐岀粍鍜岄煶涔愭瓕璇嶄粛澶嶇敤鏃㈡湁 `/api/photos`銆乣/api/music`銆乣/api/upload` 濂戠害銆?
## 2026-05-03 鐣欒█鏉夸笌鎾斁鍣ㄨˉ鍏?
- 鍓嶅彴鐣欒█鏉夸娇鐢?`GET /api/auth/github/me` 鍒ゆ柇 `{ configured, user }`銆俙configured=false` 鏃跺墠鍙版樉绀鸿瀹㈠弸濂芥彁绀猴紝涓嶆毚闇?OAuth Secret 鎴栨湇鍔＄閰嶇疆缁嗚妭銆?
## 2026-05-03 GitHub 鐣欒█ returnTo 濂戠害淇

- `GET /api/auth/github/login?returnTo=/posts/{slug}` 鏄墠鍙扮暀瑷€鏉垮惎鍔?GitHub 鐧诲綍鐨勪富鍏ュ彛锛涘悗绔吋瀹规棫鍙傛暟 `return_to`銆?- `returnTo` 鏀寔鍓嶅彴鐩稿璺緞銆傚悗绔細瑙ｆ瀽涓哄厑璁哥殑鍓嶅彴鏉ユ簮锛屽苟鎷掔粷闈炵櫧鍚嶅崟缁濆 URL 鍥炶烦锛岄伩鍏嶅紑鏀鹃噸瀹氬悜銆?- OAuth 鏈厤缃椂璇ユ帴鍙ｈ繑鍥炵粺涓€閿欒缁撴瀯锛屼笉杩斿洖 Client Secret銆丱Auth Secret銆乣.env` 璺緞鎴?access token銆?- `GET /api/auth/github/me` 杩斿洖 `{ "configured": boolean, "user": null | { "login": string, "name": string, "avatar": string, "html_url": string } }`锛屼笉杩斿洖 access token銆?- `POST /api/comments/{resource}/{slug}` 蹇呴』鏈?GitHub 鐧诲綍鎬侊紱鏈櫥褰曡繑鍥?`401`锛屾棫鐣欒█浠嶅彲鍏紑璇诲彇銆?
## 2026-05-03 鐣欒█鏉垮叕寮€閰嶇疆濂戠害

`GET /api/settings/public` 鐨?`comments` 瀛楁鍥哄畾涓哄叕寮€甯冨皵鐘舵€侊紝涓嶈繑鍥?Secret锛?
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

- `enabled=false`锛氬墠鍙版樉绀衡€滅暀瑷€鏉挎殏鏃跺叧闂€濄€?- `enabled=true` 涓?`githubLoginConfigured=false`锛氬墠鍙版樉绀衡€滅珯鐐规殏鏈紑鍚?GitHub 鐣欒█锛岃绋嶅悗鍐嶈瘯鎴栬仈绯荤珯鐐圭鐞嗗憳銆傗€?- `enabled=true` 涓?`githubLoginConfigured=true` 涓旀湭鐧诲綍锛氬墠鍙版樉绀衡€滀娇鐢?GitHub 鐧诲綍鍚庣暀瑷€鈥濇寜閽€?- `githubLoginConfigured` 鍙兘鏄?boolean锛涗笉寰楄繑鍥?OAuth Secret銆乤ccess token 鎴栨湇鍔＄閰嶇疆璺緞銆?- `POST /api/comments/{resource}/{slug}` 缁х画瑕佹眰 GitHub 鐧诲綍鎬侊紱鏈櫥褰曡繑鍥?`401` 缁熶竴閿欒鍝嶅簲銆?- 棣栭〉鍜岄煶涔愰〉闊抽噺灞炰簬鍓嶇鏈湴鐘舵€侊紝涓嶆柊澧?API锛涢煶閲忓拰闈欓煶鐘舵€佸啓鍏ユ祻瑙堝櫒 `localStorage`銆?

## 2026-05-03 Visitor Auth and Multi-provider Message Board

Public settings `GET /api/settings/public` returns message provider status only:

```json
{
  "comments": {
    "enabled": true,
    "provider": "multi",
    "githubLoginEnabled": true,
    "githubLoginConfigured": true,
    "qqLoginEnabled": true,
    "qqLoginConfigured": false,
    "maxLength": 1000
  }
}
```

No OAuth secret, access token, admin JWT, or server-only config may appear in this response.

Visitor auth endpoints:

- `GET /api/auth/visitor/me`: returns `{ "configured": { "github": true, "qq": false }, "user": null | { "provider", "id", "name", "avatar" } }`.
- `POST /api/auth/visitor/logout`: clears visitor login cookies.
- `GET /api/auth/github/login?returnTo=/path`: starts GitHub OAuth and sets CSRF state cookie.
- `GET /api/auth/github/callback`: validates state, exchanges code server-side, stores visitor login cookie, redirects to `returnTo`.
- `GET /api/auth/qq/login?returnTo=/path`: starts QQ OAuth and sets CSRF state cookie.
- `GET /api/auth/qq/callback`: validates state, exchanges code server-side, reads QQ public profile, stores visitor login cookie, redirects to `returnTo`.

Message endpoints now accept resources `posts`, `moments`, `chatters`, `music`, and `photos`:

- `GET /api/comments/{resource}/{slug}` remains public and returns old and new comments.
- `POST /api/comments/{resource}/{slug}` requires visitor login. Anonymous requests return `401`.
- New messages store `provider` and `providerId`; older `githubLogin` comments remain display-compatible.

## 2026-05-04 Component Theme and Music Likes

### Settings: component theme

`GET /api/settings/public` and `GET /api/admin/settings` include public component style tokens under `themeConfig.componentTheme`.

The response only contains public style values. It must not include OAuth secrets, AI keys, OSS secrets, admin JWTs, or access tokens.

Example shape:

```json
{
  "themeConfig": {
    "opacity": {
      "toolboxSettingsPanel": 0.92,
      "toolboxSearchPanel": 0.92,
      "toolboxCalculatorPanel": 0.9
    },
    "componentTheme": {
      "topNav": {
        "label": "顶部导航栏",
        "day": {
          "bg": "#f8fbff",
          "text": "#152033",
          "accent": "#2563eb",
          "border": "#d8e3f5"
        },
        "night": {
          "bg": "#121827",
          "text": "#f4f7fb",
          "accent": "#67e8f9",
          "border": "#3a465d"
        },
        "opacity": 0.72,
        "size": "medium"
      }
    }
  }
}
```

Rules:

- `opacity` accepts `0..1`; `0` means fully transparent and may make a component visually invisible.
- `size` is one of `small`, `medium`, `large`.
- Missing or invalid component tokens are normalized to defaults.
- Internal keys remain English; user-facing labels are Chinese.

### Music likes

Music items include:

```json
{
  "id": "song-id",
  "title": "歌曲名",
  "artist": "歌手",
  "url": "/uploads/song.mp3",
  "likes": 0
}
```

Old songs without `likes` are read as `0`.

#### POST `/api/music/{song_id}/likes`

Updates a public like count for a song. This endpoint does not require visitor login. The frontend uses localStorage to avoid duplicate likes from the same browser in the first stage.

Request:

```json
{ "data": { "liked": true } }
```

Response:

```json
{ "id": "song-id", "likes": 1, "liked": true }
```

Errors:

- `400` invalid request body.
- `404` song not found.
- `500` unexpected write failure.

Write behavior:

- Likes are clamped to nonnegative values.
- Updates use the existing safe JSON write path and backup behavior for `music.json`.
## 2026-05-04 Multi-Page Page Layout Contract

### GET `/api/pages/config`

公开读取页面文案和布局配置，不需要 JWT，不返回 Secret、access token、服务端绝对路径或后台私有配置。

响应核心结构：

```json
{
  "pageText": {
    "posts": { "title": "文章归档", "subtitle": "..." },
    "photos": { "title": "图片", "subtitle": "..." }
  },
  "homeProfile": {
    "author": "Shrink",
    "avatar": "/uploads/avatar.png",
    "description": "首页简介",
    "socialLinks": { "github": "https://github.com/ShrinkShi" }
  },
  "pageLayouts": {
    "home": {
      "layoutVersion": 1,
      "components": {
        "profileCard": {
          "label": "名片",
          "type": "profileCard",
          "order": 1,
          "w": 6,
          "h": 2,
          "visible": true,
          "locked": true,
          "props": {}
        }
      }
    },
    "posts": { "layoutVersion": 1, "components": {} },
    "photos": { "layoutVersion": 1, "components": {} },
    "music": { "layoutVersion": 1, "components": {} },
    "projects": { "layoutVersion": 1, "components": {} },
    "friends": { "layoutVersion": 1, "components": {} },
    "about": { "layoutVersion": 1, "components": {} }
  }
}
```

布局字段：

- `order`：组件顺序，数值越小越靠前。
- `w`：桌面端 12 栅格宽度，建议范围 `1..12`，支持小数。
- `h`：组件最小高度系数，建议范围 `0.5..8`，支持小数。
- `visible`：是否显示组件。
- `locked`：核心组件标记。核心组件可隐藏，不应删除内容数据。
- `type`：组件类型，例如 `pageTitle`、`contentList`、`customText`、`customMarkdown`、`imageBlock`、`linkButton`、`divider`。
- `props`：组件公开展示参数。不得保存 Secret 或脚本。

兼容规则：

- 旧配置只有 `home` 或 `homeLayout` 时，后端自动补齐 `pageLayouts`。
- 缺失页面使用默认配置，不返回 404。
- 前台接口失败时可使用默认布局兜底。

### GET `/api/admin/pages/config`

后台读取完整页面编辑配置，需要管理员 JWT。返回结构与公开接口保持一致，但同样不得返回 Secret 明文。

### PUT `/api/admin/pages/config`

后台保存页面配置，需要管理员 JWT。

要求：

- 写入必须走现有安全 JSON 写入封装。
- 保存前生成备份或沿用 `JsonStore` 备份机制。
- 保存操作写审计日志。
- 保存某个页面时不得覆盖其他页面配置。
- 删除/隐藏组件只改变页面布局引用，不删除文章、相册、音乐、项目、友链等真实内容数据。
- 错误响应继续使用 `{ "code": "ERROR_CODE", "message": "用户可读错误", "detail": {} }`。
## 2026-05-05 Theme Package Contract

### Theme package shape

Theme packages are public presentation configuration. They must not contain secrets, access tokens, backend paths, executable HTML, or scripts.

```json
{
  "id": "shrink-red-glass",
  "name": "Shrink 红白黑玻璃主题",
  "description": "白天白灰红，夜间黑灰红的毛玻璃主题。",
  "version": 1,
  "author": "Shrink",
  "createdAt": "2026-05-05T00:00:00Z",
  "updatedAt": "2026-05-05T00:00:00Z",
  "modes": {
    "day": {
      "bgImage": "",
      "overlayColor": "#ffffff",
      "overlayOpacity": 0.62,
      "pageBg": "#f7f7f7",
      "cardBg": "#ffffff",
      "cardOpacity": 0.72,
      "textPrimary": "#111111",
      "textSecondary": "#555555",
      "accent": "#e11d48",
      "accentHover": "#be123c",
      "border": "rgba(0,0,0,0.12)",
      "shadow": "rgba(0,0,0,0.14)",
      "fontFamily": "",
      "fontSizeBase": 16,
      "titleScale": 1.2,
      "radius": 24,
      "blur": 18
    },
    "night": {
      "bgImage": "",
      "overlayColor": "#000000",
      "overlayOpacity": 0.62,
      "pageBg": "#050505",
      "cardBg": "#111111",
      "cardOpacity": 0.72,
      "textPrimary": "#f5f5f5",
      "textSecondary": "#b5b5b5",
      "accent": "#e11d48",
      "accentHover": "#fb7185",
      "border": "rgba(255,255,255,0.16)",
      "shadow": "rgba(0,0,0,0.45)",
      "fontFamily": "",
      "fontSizeBase": 16,
      "titleScale": 1.2,
      "radius": 24,
      "blur": 18
    }
  },
  "componentTheme": {},
  "pageLayouts": {}
}
```

### `GET /api/settings/public`

Public settings include the active red/white/black glass theme package and component style tokens:

- `theme`: active theme id. Legacy ids `nebula`, `sakura`, `aurora`, and `cyber` are normalized to `shrink-red-glass`.
- `themeConfig.themePackages`: public theme package registry.
- `themeConfig.activeTheme`: active package id.
- `themeConfig.componentTheme`: public per-component visual overrides.
- `themeConfig.opacity`: public opacity shortcuts retained for compatibility.

No secret fields may be returned.

### `PUT /api/admin/settings`

Admin settings can save theme packages, active theme, component overrides, and theme opacity values. Empty secret fields still preserve previous secret values. Theme package import/export is handled by the admin UI using this settings contract plus the existing page config contract when layouts are included.

### Page layouts inside theme packages

Theme export may include `pageLayouts`. Import/apply can choose whether to write those layouts to `/api/admin/pages/config`. If the user imports colors only, `pageLayouts` must not overwrite the current page layout configuration.
