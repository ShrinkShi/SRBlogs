# 前台左侧应用侧边栏

`FloatingAppSidebar` 是前台左侧的应用入口。它替代旧的环形转轮菜单：收起时显示一个左下角圆形应用图标，展开后以 iOS 风格网格展示应用图标和名称，底部固定展示账户信息。

## 相关文件

- `frontend/src/components/FloatingAppSidebar.vue`：侧边栏渲染、账户面板和应用点击。
- `frontend/src/config/floatingApps.ts`：应用注册表。
- `frontend/src/stores/session.ts`：游客、GitHub/QQ 和管理员登录状态。
- `frontend/src/App.vue`：集中处理应用 action。

## 应用注册格式

```ts
type FloatingAppActionType =
  | 'modal'
  | 'route'
  | 'external'
  | 'toggle'
  | 'custom'

type FloatingAppItem = {
  id: string
  name: string
  icon: FloatingAppIcon
  actionType: FloatingAppActionType
  action: string
  enabled?: boolean
  adminOnly?: boolean
  order?: number
  tooltip?: string
}
```

示例：

```ts
{
  id: 'settings',
  name: '设置',
  icon: 'settings',
  actionType: 'modal',
  action: 'settings',
  order: 10,
  tooltip: '打开游客设置'
}
```

## actionType 说明

- `modal`：打开站内弹窗，例如 `settings`、`search`、`calculator`。
- `route`：跳转前台路由，例如 `/posts`。
- `external`：打开外部或独立应用地址，例如 `/admin/content/articles`。
- `toggle`：切换全局组件状态，例如悬浮音乐播放器。
- `custom`：自定义动作。新增前应在 `App.vue` 中集中注册处理逻辑。

## 账号与权限规则

- 默认身份为游客。
- GitHub/QQ 登录用于评论身份，评论会自动读取 OAuth 用户头像和昵称。
- 管理员登录复用后台账号密码与 `/api/auth/login`。
- `adminOnly` 应用只在管理员登录后显示。

## 如何新增应用

1. 如需新图标，先在 `FloatingAppIcon` 中增加图标名，并在 `FloatingAppSidebar.vue` 的 `iconPath()` 注册 SVG path。
2. 在 `floatingApps.ts` 中添加应用项，设置 `id`、`name`、`icon`、`actionType`、`action` 和 `order`。
3. 如果只给管理员使用，加 `adminOnly: true`。
4. 如果是 `modal`、`toggle` 或 `custom`，在 `App.vue` 的 `handleFloatingAppAction()` 中注册行为。
5. 运行 `cd frontend && npm run build`。

## 交互规则

- 收起态：左下角显示单个圆形应用图标。
- 展开态：左侧侧边栏显示应用网格，名称位于图标下方。
- 底部账户区显示头像、用户名和身份。
- 点击账户区打开账号面板，可 GitHub 登录、管理员登录或退出。
- `adminOnly` 应用不会对游客或普通 OAuth 用户显示。

## 注意事项

- 不要把应用数量写死在组件中。
- 不要在侧边栏组件中硬编码内容管理业务。
- 移动端要保持可滚动，避免侧边栏遮挡主要内容后无法关闭。
- 管理类入口优先复用已有后台安全接口，逐步迁移到前台原地编辑。
