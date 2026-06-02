# SRBlogs 前台组件模板库

本文档用于约束前台新增组件的结构、命名和交互风格，避免后续继续产生一次性组件。

## 设计基线

- 固定夜间主题：黑色底、红色强调、白色主文字、低透明边框。
- 组件默认不使用厚重卡片，优先使用轻边框、留白和细分割线。
- 管理能力迁移到前台时，应复用现有 API，不直接 iframe 后台页面。
- 成功/失败反馈统一使用 `useUiStore().showToast()`。
- 禁止在组件内使用 `window.alert`、`window.confirm`、`window.prompt`。

## Modal 模板

适用于设置、内容编辑、相册新增等弹窗。

```vue
<Teleport to="body">
  <Transition name="front-modal-pop">
    <div v-if="open" class="front-modal-backdrop" role="dialog" aria-modal="true" @click.self="close">
      <section class="front-modal-shell">
        <header class="front-modal-head">
          <strong>标题</strong>
          <button type="button" aria-label="关闭" @click="close">...</button>
        </header>
        <main class="front-modal-body">...</main>
        <footer class="front-modal-footer">...</footer>
      </section>
    </div>
  </Transition>
</Teleport>
```

要求：
- `Esc` 可关闭，危险未保存场景应使用项目内确认弹窗。
- 关闭按钮必须有 `aria-label`。
- 弹窗内滚动，不让页面主体滚动错乱。

## 内容编辑模板

适用于文章、杂谈、说说等 Markdown 内容。

固定结构：
- 左侧：标题、Markdown 编写/预览、工具栏、正文。
- 右侧：类型、日期、标签、简介、封面、高级设置。
- 底部：`存为草稿`、`取消`、`保存草稿/发布`。

当前实现参考：
- `frontend/src/components/FrontContentEditorModal.vue`
- `frontend/src/components/MarkdownToolbar.vue`
- `frontend/src/utils/markdownTools.ts`

新增内容类型时，只扩展 `section` 映射和保存 payload，不复制整套编辑器。

## 结构化 JSON 编辑模板

适用于相册、友链、项目、音乐等 JSON 列表。

固定结构：
- 标题、描述、日期、标签为基础字段。
- 上传使用 `contentApi.upload()`。
- 保存使用 `contentApi.adminPutJson()`。
- 仅管理员可见入口，普通访客不渲染按钮。

当前实现参考：
- `frontend/src/components/FrontPhotoEditorModal.vue`

## 按钮规范

- 常规按钮：`.sr-button sr-button-regular`，白色填充、黑色文字、胶囊圆角。
- 重点按钮：`.sr-button-green`（绿色填充黑字）、`.sr-button-red`（红色填充白字）、`.sr-button-black`（黑色填充白字）。
- 纯文字操作：使用 `frontend/src/components/ui/SrTextButton.vue`，无边框、无背景、无下划线，适合编辑、删除、复制、回复等轻操作。
- 图标按钮：圆形、透明底；只有确实需要强调时才加轻边框。
- 管理员新增按钮统一使用 `.frontend-admin-create-btn`。

纯文字按钮示例：

```vue
<SrTextButton>编辑</SrTextButton>
<SrTextButton tone="danger">删除</SrTextButton>
```

## 登录与权限

- 游客/GitHub/QQ 与管理员是互斥身份。
- 管理员登录前必须退出 GitHub/QQ。
- GitHub/QQ 登录前必须退出管理员。
- 前端只隐藏入口，后端仍必须校验管理员 token。

## 安全检查清单

新增或修改组件后至少检查：
- 是否输出了 Secret、Token、密码。
- 是否用了原生弹窗。
- `target="_blank"` 是否有 `rel="noopener noreferrer"`。
- `v-html` 是否经过 DOMPurify 或等价白名单处理。
- 上传是否复用现有 `/upload`，不要绕过后端校验。
- 管理操作是否只在 `session.isAdmin` 下渲染，并由后端二次鉴权。
