# UI Style Guide

本文档约束 SRBlogs 的前台视觉、后台控制台和 P2 氛围增强。P2 可以提升质感，但不得破坏 P0/P1 内容闭环、移动端可读性和可访问性。

## Design Tokens

前台统一使用 `frontend/src/styles.css` 中的 CSS 变量和工具类：

- `--glass-bg` / `--glass-bg-strong` / `--glass-border` / `--glass-line`：毛玻璃底色、边框和分割线。
- `--text-primary` / `--text-secondary` / `--text-muted`：正文、次级说明和弱化文字。
- `--accent-cyan` / `--accent-pink` / `--accent-emerald`：主强调、辅助强调和成功语义。
- `--glow-cyan` / `--glow-pink`：只用于小面积辉光，不用于大面积背景。
- `--status-danger` / `--status-success` / `--status-warning` / `--status-info`：危险、成功、警告和信息状态。

优先复用这些工具类：

- `sr-page-shell` / `sr-section`：统一页面最大宽度和居中容器。
- `sr-card`：统一毛玻璃卡片。
- `sr-card-hover`：统一卡片 hover，位移不超过 3px。
- `sr-hero-panel`：首页或重要标题区使用的增强面板。
- `sr-chip` / `sr-chip-cyan`：标签、状态、社交链接。
- `sr-button-primary` / `sr-button-ghost`：主要按钮和次级按钮。
- `sr-status-*`：状态文本。

不要在新页面继续手写一套互相不一致的毛玻璃、阴影、hover 和状态色。

## Global Background

- 前台允许动态背景、弹幕、樱花、萤火、点击光效等氛围组件，但必须低于正文层级。
- 背景特效不得遮挡正文、评论框、搜索框、导航、设置面板和主要按钮。
- 移动端默认降低密度：樱花、萤火、CyberCat 等装饰层应隐藏或弱化。
- 用户必须能通过背景控制里的“氛围”开关关闭装饰动效；关闭后页面仍保持基本美观。
- `prefers-reduced-motion: reduce` 下必须显著降低动画影响。

## GlassCard

- `GlassCard` 用于独立信息块、工具面板和重复卡片。
- 不要嵌套大面积卡片。重复项目可以是卡片，但页面 section 不要全做成多层浮动卡片。
- 前台卡片可以更有层次；后台卡片保持信息密度和可重复操作。
- hover 只允许轻微位移、边框、背景或阴影变化，不允许改变布局尺寸。

## Navigation

- 顶部导航和首页主内容必须使用一致的页面宽度约束。
- sticky 导航不得遮挡正文标题。
- 中窄屏下导航按钮不得超出视口。
- 后台侧边栏 active 状态必须明确，当前页应有边框、底色或左侧强调线。

## Page Width

- 前台主要页面使用 `width: min(calc(100% - 3rem), 80rem)` 或等价类。
- 480px 以下宽度使用更紧凑的左右留白，但左右 padding 必须基本一致。
- 首页 Hero/ProfileCard、SiteDashboard、最新文章、内容发现入口必须共用同一主容器。
- Grid/Flex 子项必须使用 `min-w-0`，图片和卡片必须 `max-width: 100%`。
- 文章正文比首页聚合区更窄或更聚焦，优先保证阅读舒适。

## Radius And Shadow

- 前台常规卡片圆角建议 `24px-30px`。
- 后台工具卡片圆角可以保留 `24px-30px`，但阴影更克制。
- 阴影用于层级，不用于制造大面积发光噪声。
- 危险操作不要只靠颜色，要有文案和确认。

## Hover And Motion

- hover/transition 控制在 `0.2s-0.3s`。
- hover 位移不超过 `3px`，移动端和无 hover 设备不依赖 hover 表达信息。
- 不允许 hover 导致卡片宽高改变或列表抖动。
- 不引入大型动画库，不做 3D/Three.js。

## Article Reading

- 文章详情标题区、摘要、日期、标签应有清晰层级。
- Markdown 正文必须继续由 `MarkdownRenderer` 渲染并经过 DOMPurify 清洗。
- 代码块和表格允许内部横向滚动，但不能撑爆页面。
- 评论区与正文之间要有明确间距和视觉分隔。
- 分享按钮样式与全站按钮体系一致，不依赖第三方 SDK。

## Mobile

- 390px 宽度必须可读可操作。
- 首页 ProfileCard、SiteDashboard、最新文章必须完整显示，不能靠 `overflow-x: hidden` 裁切。
- 浮动音乐和背景控制不能挡正文、评论区和主要按钮。
- 后台侧边栏在窄屏下可以滚动，但不能挡住主内容。
- 表单按钮可以换行，但不得挤出屏幕。

## Empty And Loading States

- 每个列表页都要有加载、空、错误状态。
- 空状态说明当前没有内容，并提供合理入口或下一步。
- 错误状态必须有可读文案，不只在控制台报错。
- 后台保存、上传、备份、恢复、导入等操作必须有 pending 状态。

## Admin Layout

- 后台不做营销式大 Hero。
- Dashboard 更像控制台：统计、入口、风险提示和状态反馈优先。
- 表单卡片、列表卡片、统计卡片使用统一玻璃和边框风格。
- 高级 JSON 折叠区视觉降级，不抢主流程。
- 审计日志和备份恢复页面保持严肃工具风，避免花哨动效。
- 删除、恢复、导入等高风险按钮使用危险样式和二次确认。

## P2 Acceptance

P2 视觉增强只有在以下检查通过后才可继续提升状态：

- 首页 1440px、1280px、1024px、390px 不裁切、不撑宽、左右边距稳定。
- 文章详情正文不被背景、浮动控件或导航遮挡。
- 搜索、标签、归档、媒体页不因视觉改动白屏或布局破坏。
- 后台 editor/comments/backups/settings 主流程不退化。
- 关闭氛围动效后页面仍可读。
- 构建通过，构建产物 Secret 搜索通过。
