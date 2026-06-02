# 前台环形功能菜单

`FloatingAppWheel` 是前台左下角的环形应用转轮菜单，用于承载站内轻量功能入口。它只负责展示、展开收起、拖动定位、滚轮旋转和触发 action，不在组件内硬编码业务逻辑。

## 相关文件

- `frontend/src/components/FloatingAppWheel.vue`：菜单渲染组件。
- `frontend/src/composables/useFloatingAppWheel.ts`：展开、拖动、滚轮锚定和位置持久化。
- `frontend/src/config/floatingApps.ts`：应用注册表。
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
- `route`：跳转站内路由，例如 `/posts`。
- `external`：在新标签页打开外部链接。
- `toggle`：切换全局组件状态，例如悬浮音乐播放器。
- `custom`：自定义动作，需要在 `App.vue` 的 action 分发逻辑中注册。

## 如何新增应用

1. 如需新图标，先在 `FloatingAppIcon` 中增加图标名，并在 `FloatingAppWheel.vue` 的 `iconPath()` 注册 SVG path。
2. 在 `floatingApps.ts` 中添加应用项，设置 `id`、`name`、`icon`、`actionType`、`action` 和 `order`。
3. 如果是 `modal`、`toggle` 或 `custom`，在 `App.vue` 的 `handleFloatingAppAction()` 中注册对应行为。
4. 验证 tooltip、点击行为、拖动位置和移动端显示。
5. 运行 `cd frontend && npm run build`。

## 交互规则

- 点击悬浮球展开或收起菜单。
- 拖动悬浮球会移动整个转轮，位置会限制在视口内并写入 `localStorage`。
- 只有鼠标位于菜单区域且菜单展开时，滚轮事件才会被拦截。
- 滚轮不是分页模式，而是按应用为单位更新 `focusedIndex`。
- 向下滚动切到下一个应用，向上滚动切到上一个应用。
- 应用数量不固定，新增应用后通过滚轮轮换查看。

## 注意事项

- 不要在菜单组件里写业务逻辑，业务动作统一在 action 分发层处理。
- 不要写死应用数量或固定 5 个圆点。
- 不要保留旧的左下角单按钮入口，避免和转轮重复。
- 移动端需要保留安全边距，悬浮球不能拖出屏幕。
- 如新增全局浮层，确认 z-index 不会遮挡设置弹窗、搜索弹窗和音乐播放器。
