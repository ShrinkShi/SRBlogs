# UI Style Guide
## 2026-05-07 背景蒙层透明度规范

- 壁纸是前台背景的主要视觉来源，昼夜蒙层只负责统一色调，默认不应超过 `0.28`。
- 当前红白黑玻璃主题建议：日间蒙层约 `0.08`，夜间蒙层约 `0.24`；如导入主题给出更高值，前台需要做安全上限以避免壁纸被压成纯色。
- 径向装饰层应保持很低透明度，只做氛围补充，不得覆盖壁纸细节。
## 2026-05-07 前台壁纸轮播背景规范

- 前台背景必须优先保持壁纸氛围，不得把主题背景误处理成纯色页面背景。
- 背景图来源顺序为：当前昼夜模式壁纸组、单张模式壁纸、旧版全站壁纸列表；当前模式未配置壁纸时必须回退旧版壁纸列表。
- 白天/夜间蒙层只用于统一红白黑玻璃主题色调，不能遮蔽到看不出壁纸。
- 背景切换继续使用淡入淡出动画；游客工具箱里的背景选择数量应按当前有效壁纸列表计算。

## 2026-05-06 前台可读性与分段控件规范

- 前台普通内容文字必须走主题 token：白天使用 `--text-primary` / `--text-secondary`，夜间使用对应浅色 token；不要在非图片背景正文里固定 `text-white`。
- 以图片为背景的卡片、轮播和封面继续使用图片明暗判断：深图白字、浅图黑字，并配合轻微遮罩和 text-shadow 保证可读。
- “正经 / 杂谈”“矩阵网格 / 中枢链路”“歌词 / 歌单”等切换控件统一使用分段按钮样式：文字水平垂直居中，active 使用红色 `--accent` 和高对比文字，inactive 读取主题文字色。
- 搜索框输入文字、placeholder 和搜索按钮必须读取主题 token，白天模式不得出现不可读白字。
- 音乐页固定布局需保持左侧播放器、右侧歌词/歌单面板、下方留言板完整显示；面板不得使用过小高度或 `overflow:hidden` 裁切核心内容。

## 2026-05-05 1100px 内容框与音量控件规范

- 前台主要页面不再依赖“继续增大左右边距”来收窄内容，统一使用 `--page-content-width: 1100px` 作为桌面端主内容最大宽度。
- 2026-05-06 起，前台布局回归 Vue/CSS 固定实现：后台不再控制组件宽度、高度、跨行、排序、添加或删除。`pageLayouts` 只作为 legacy compatibility 字段保留，不再参与前台实际布局。
- 首页固定布局：首行名片 + 音乐播放器各半且约 290px 高；歌词区全宽居中；轮播区使用固定 mosaic CSS Grid；390px 移动端单列。
- 主题包只管理昼夜配色、背景壁纸组、蒙层、毛玻璃强度、全局字体、全局字号、强调色和背景轮播，不再承载页面布局。
- 页面编辑组件使用 12 栅格映射：`w=12` 约为 `1100px`，`w=6` 约为半宽，`w=4` 约为三分之一宽。页面安全边距只保护内容不贴浏览器边缘，不参与组件宽高和 grid 计算。
- `.site-page-container` 只提供基础安全 padding；实际内容宽度由其直接子级居中限制到 `--page-content-width`。
- 音量控件必须是独立的自定义垂直滑杆浮层：一个轨道、一个填充层、一个 thumb，不得与播放进度条共用轨道，也不得叠加第二条幽灵轨道。
- 音量浮层锚定音量按钮向上弹出，白天/夜间都使用主题 token；轨道居中，thumb 始终位于轨道中心线上，上下保留内边距。
- 背景图轮播使用轻量淡入淡出过渡，后台站点级开关优先，游客工具箱开关只在站点允许时生效。
- 首页名片和首页音乐播放器默认高度约 `290px`；高度来自页面编辑 `h` 映射，不能通过裁切内容来强行压缩。

## 2026-05-05 页面边距作用域修复

- 前台主体内容使用统一 `1100px` 内容宽度基准，路由根内容应通过 `--page-content-width` 居中限制到该宽度。
- 页面编辑组件宽度按 12 栅格计算：`w=12` 约为 `1100px`，`w=6` 约为半宽，`w=4` 约为三分之一。
- 前台页面左右边距只作为浏览器边缘安全留白，不再作为主要内容收窄方案。
- 页面边距配置不得参与首页 grid、组件 `w/h`、`rowSpan`、组件内部 padding、播放器宽高或歌词区高度计算。
- `.sr-section` 不再叠加页面边距，避免主内容容器和页面段落双重收窄。
- 页面编辑的组件高度配置在前台应作为 `min-height` 或安全高度映射使用，不得用固定 `height` 裁切名片、播放器、歌词或轮播内容。
- 顶部导航和左下角工具箱固定位置不跟随页面边距变化。
- 后台不再提供页面边距作为主内容宽度控制入口；旧主题包中的 `pagePadding` 只作为兼容字段处理。

## 2026-05-05 UI/UX skill 与音量控件规范

- 前端 UI/UX 修改应先参考本地 `ui-ux-pro-max` skill 的可读性、交互反馈和控件一致性建议。
- 音量浮层只允许出现一个垂直滑杆；当前实现使用“毛玻璃面板 + 单个旋转 range”，必须通过自定义 track/thumb 收敛为单轨，不得再叠加额外 div 轨道。
- 音量滑杆白天/夜间都使用主题 token，轨道底色为灰阶，填充和 thumb 使用红色 accent。

## 2026-05-05 主题边距、背景组与播放器细节

- 前台内容区宽度由 `--page-content-width: 1100px` 控制；`themeConfig.layout.pagePadding` 继续作为旧主题包兼容字段保留，但不应替代 1100px 内容宽度模型。
- 主题包需要同时包含 day/night 背景壁纸组。日间模式读取 `modes.day.bgImages`，夜间模式读取 `modes.night.bgImages`，切换昼夜时背景和蒙层同步切换。
- 音量浮层应保持毛玻璃风格，但上下必须留出内边距；鼠标离开按钮和浮层后约 0.5 秒隐藏，拖动时不得消失。
- 音乐播放进度条必须可点击和拖动，进度高亮使用当前主题 accent，拖动后歌词状态立即跟随当前播放时间。
- 播放器控制按钮应保持同一行，喜欢图标和喜欢数水平排列，不得掉到下一行。
- 页面编辑高度 `h` 支持小数，前台应通过更细粒度的 grid row 或明确高度计算真实应用，不得把 `h` 强制取整。

## 前台红白黑主题收口

- 前台内容容器统一使用 `sr-page-shell` / `site-page-container` 的安全留白与 `1100px` 内容框；不要再通过继续加大页面边距来收窄主内容。
- 白天模式文字必须使用深色主题 token，夜间模式文字使用浅色主题 token；文章详情、关于页和 Markdown 正文不得固定写死白色。
- 播放器图标按钮使用 `--text-primary` / `--text-secondary`，hover、进度条、已喜欢和轮播激活点使用 `--accent` 红色重点色。
- 首页歌词区只展示当前播放时间对应的单句歌词；长句允许缩小字体但不展示完整歌词列表。

## 2026-05-05 页面编辑组件设置弹窗规范

- 组件卡片默认保持简洁，只展示组件名称、key、`order`、`w`、`h`、透明度和显示状态。
- 点击组件后打开统一的“组件详细设置”弹窗，不在卡片中铺开大量控制项。
- 组件设置弹窗必须包含四个中文分组：布局设置、外观设置、字体设置、显示设置。
- 布局设置包含 `order`、宽度 `w`、高度 `h`、显示/隐藏；宽高使用滑动条和数值输入同步编辑。
- 外观设置包含日间/夜间背景色、日间/夜间文字色、透明度 `0-1`、大小档位。
- 字体设置包含字体族、字号、字体颜色、文本左/中/右对齐、加粗和斜体。
- 显示设置包含可见状态和删除/隐藏入口；删除布局引用不得删除真实内容数据。
- 弹窗主体必须允许滚动，最大高度建议 `80vh-85vh`；保存和关闭按钮必须始终可访问。
- 保存任一分组都必须与其他分组合并，不能用局部 payload 覆盖完整组件配置。

## 2026-05-05 页面编辑弹窗与组件字体规范

- 页面编辑主界面只保留页面状态、关键操作按钮和组件布局编辑区；真实字段编辑必须通过“编辑当前页面信息”弹窗进入。
- 页面编辑顶部操作栏应使用后台黑白灰平面风，并在内容区滚动时保持 sticky，避免保存、添加组件、恢复默认布局按钮离开视野。
- 组件详细设置放在点击组件后的弹窗中，弹窗可滚动，表单分组建议为“布局 / 外观 / 字体 / 显示”。
- 组件字体设置归入组件主题配置，不另造独立配置体系。每个组件可配置字体族、字号、文字颜色、文本对齐、加粗和斜体。
- 组件独立字体设置优先级高于全站游客字体大小设置；缺失字段必须回退默认字体和默认组件文字色。
- 留言板不得显示开发调试 target；调试信息如需保留，只能放在开发控制台。
- 音乐播放器喜欢按钮和喜欢数必须水平排列，数量不得掉到按钮下方。

## 2026-05-04 页面编辑器边界约束

- 后台页面编辑器不再使用真实 120 栅格作为组件卡片容器，避免小组件卡片被滑块和输入框撑破。
- 页面编辑组件卡片使用受控 `auto-fit` 网格，卡片必须 `max-width: 100%`、`min-width: 0`。
- 宽度和高度滑块必须被限制在卡片内部，数值输入和预设按钮在空间不足时换行。
- 组件排序暂时不使用拖拽，避免与滑动条操作冲突；排序统一通过“上移 / 下移 / order 数值”完成。
- 前台首页可以应用后台保存的高度配置，但高度映射必须克制，不能因为后台调试值导致首页组件异常撑满屏幕。

## 2026-05-04 后台设置可读性与多页面编辑规范

后台管理端继续采用黑白灰平面化工具风，前台玻璃风不受影响。后台样式必须限定在 admin 应用内，不得污染 frontend 的主题变量。

后台设置中心可读性：

- 白底或浅灰底上的主文字使用深灰或黑色。
- 说明文字可以使用中灰，但不能接近不可见。
- `input`、`textarea`、`select` 使用白底、浅灰边框和深色文字。
- placeholder 允许较浅，但必须能辨认。
- checkbox、radio、range 的选中和禁用状态必须清楚。
- 折叠区标题、组件主题配置标题、高级 JSON 区标题必须清楚可读。
- 禁止后台设置页继续使用前台浅色玻璃文字变量。

页面编辑卡片：

- 默认只显示组件名称、组件 key、`order`、`w`、`h`、`visible`。
- 宽度和高度控制应压缩在一行内：标签、滑块、数值输入、快捷预设按钮。
- 透明度、日间/夜间背景色、大小档位等详细状态默认折叠或悬浮显示，不挤占卡片布局。
- 自定义组件可以删除；核心组件优先隐藏，不能删除真实内容数据。
- 添加组件必须使用弹窗或轻量面板，不能把所有候选组件常驻铺开。

多页面布局：

- `home/posts/photos/music/projects/friends/about` 都使用同一套 `pageLayouts` 结构。
- 桌面端应应用组件 `order/w/h/visible`。
- 移动端可以退化为单列，但不能横向溢出。
- 缺失配置时使用默认布局兜底。

## 2026-05-04 后台黑白灰平面化与页面编辑精细尺寸

- 本轮后台管理端采用黑白灰平面简约风，前台玻璃风格保持不变。
- 后台根容器使用 `admin-flat` 作用域，所有黑白灰覆盖必须限定在 admin 应用内，不能污染 frontend。
- 后台主背景使用白色或近白色，卡片使用白底或浅灰底，边框使用浅灰，主文字使用黑色或深灰。
- 后台主按钮使用黑底白字，次按钮使用白底灰边框，危险按钮可保留红色但必须平面化。
- 后台输入框、textarea、select 使用白底、浅灰边框和清晰 focus 状态。
- 后台弹窗使用白色或近白色面板、浅灰边框和简洁遮罩，不使用大面积毛玻璃、强渐变和发光阴影。
- 后台左侧导航使用平面层级结构，当前项通过浅灰底、黑色左边线或深色文字表达，不使用胶囊式毛玻璃。
- 高级 JSON 编辑区使用浅灰背景和等宽字体，视觉层级低于表单主流程。

页面编辑规范：

- 首页组件尺寸使用滑动条 + 数值输入，不再只依赖大/中/小或固定宽度档位。
- `w` 使用 `1-12` 范围，步进 `0.1`；前台桌面端映射到 120 子列 grid。
- `h` 使用 `0.5-6` 范围，步进 `0.1`；前台映射为组件最小高度。
- 组件状态摘要必须以中文展示组件名称、key、order、w、h、visible、透明度、大小、日间/夜间背景色。
- 移动端可退化为单列布局，避免精细桌面布局造成横向溢出。

## 2026-05-04 Component Theme DIY

- Component opacity ranges from `0` to `1`. `0` is allowed for full transparency, but the UI should warn that the component may become visually invisible.
- Component theme tokens are grouped by component key. Each key has a Chinese label, day/night color values, opacity, and a size token.
- First-stage component keys include top navigation, toolbox, toolbox panels, toast, home profile/music/lyrics/carousels/theme/status cards, content switch buttons, post/chatter/photo cards, music panels, message board, search input/button, and tag buttons.
- Component color settings must use both `input[type=color]` and text input so users can choose quickly or paste exact values.
- Font size settings and component size settings are separate: font size only changes text; component size may adjust padding or minimum height for that component only.
- Frontend components should read CSS variables generated from `themeConfig.componentTheme` and fall back to defaults when config is missing.
- Page Editor home cards should show component state summaries: order, width, height, visible state, opacity, day/night background, and size.
- Music controls use icon-only buttons for play mode and like state. Play modes are sequence, shuffle, and repeat-one. Like counts are public content metadata and should stay visually compact.

## 2026-05-04 可配置透明度

- 前台主要玻璃面板透明度不再通过改代码调节，后台“主题与背景 > 前台透明度设置”提供 0.60-1.00 的滑块和数字输入。
- 工具箱设置弹窗、全局搜索弹窗、计算器弹窗分别读取 `themeConfig.opacity.toolboxSettingsPanel`、`toolboxSearchPanel`、`toolboxCalculatorPanel`。
- 首页卡片、首页轮播、内容卡片、图片卡片、音乐卡片、留言板和顶部导航读取对应透明度 CSS 变量。
- 透明度可以保留轻微玻璃感，但最低值必须保证文字、输入框和按钮清晰可读；不要只调整遮罩层或 blur。
- 点击音效识别应覆盖 `button`、`a`、`role=button`、`data-clickable=true`、工具箱按钮和菜单项；视觉点击特效可以任意点击触发，但空白点击不播放音效。

## 2026-05-03 首页布局编辑硬修规范

- 工具箱“设置 / 全局搜索”弹窗主体背景必须明确设置高不透明度，夜间建议 `rgba(12,16,32,.90~.94)`，日间建议 `rgba(245,248,255,.90~.94)`；不得只依赖遮罩或 blur。
- 点击视觉特效响应页面任意点击；点击音效只响应交互元素。空白点击可有视觉效果，但不得播放声音。
- 字体大小设置只能改变文本字号，禁止使用 `zoom`、页面/组件 `transform: scale()` 或修改 `html font-size` 来整体缩放布局。
- 字体大小通过文本类和 CSS 变量覆盖 `font-size`；卡片宽高、图片尺寸、播放器唱片尺寸、弹窗宽高、grid 列宽、gap、padding 不应跟随字体档位等比例变化。
- 首页页面编辑第一阶段固定 8 个组件：名片、音乐播放器、歌词区、最新文章轮播、图片轮播、更新内容轮播、昼夜切换、底部状态区。
- 前台首页桌面端必须应用 `homeLayout.components` 的 `order/w/h/visible`；移动端可以退化为单列，但不能忽略桌面保存配置。
- 后台页面编辑可使用拖拽排序，也必须提供上移/下移、宽度档位、高度档位作为可靠兜底。

## 2026-05-03 页面编辑与交互规则修订

- 工具箱“设置”和“全局搜索”弹窗背景应接近不透明，建议主体 `rgba(..., 0.94~0.98)`，遮罩更深；保留轻微玻璃质感但优先保证阅读。
- 点击视觉特效和点击音效使用不同触发规则：视觉特效响应页面内任意点击，音效只响应按钮、链接、导航、表单控件等有效交互元素。
- 后台关闭点击音效或点击特效时，游客设置中对应项必须隐藏或显示不可用说明，不能通过 localStorage 覆盖站点级禁用。
- 字体大小三档不得通过根字号或 `zoom` 缩放布局；应只通过文本字号变量同步影响导航、标题、Markdown 正文、卡片、按钮、标签、输入框、留言板和工具箱弹窗。
- 中枢链路的纵向间距应明显大于普通列表，本阶段目标为原先间距约 2.5 倍；移动端单列也保持更宽松间距。
- 后台页面编辑第一阶段必须展示真实字段和真实数据摘要；不能用与前台无关的静态假数据冒充预览。
- 首页布局拖拽/缩放未保存前只影响后台预览区；保存后通过公开 `homeLayout.components` 应用到前台首页。
- 作者、头像、首页简介和社交链接属于首页页面内容，主编辑入口在“页面编辑 > 首页”；设置中心只保留兼容折叠区。

## 2026-05-03 工具箱与后台信息架构补充

- 工具箱“设置”和“全局搜索”弹窗应使用高不透明度玻璃面板，保留模糊质感但优先保证文字、输入框和按钮可读。
- 工具箱计算器使用小浮窗，不使用全屏遮罩，不阻塞页面滚动和其他交互；Esc 可关闭。
- 鼠标点击视觉特效响应页面任意点击，包括空白区域；点击音效才只响应交互元素。特效必须轻量，不能遮挡内容，也不能替代点击音效。
- 后台可通过公开设置关闭点击特效；关闭后游客设置中不得强行开启。
- 游客字体大小使用小/中/大三档，必须明显影响导航、卡片、按钮、留言板和工具箱弹窗等前台文字。
- 中枢链路视图的上下卡片间距应比矩阵列表更疏朗，保持左右交替和贴近中心线。
- 后台一级导航固定为：页面编辑、内容管理、评论管理、后台设置、日志备份。旧路由可保留兼容，但主导航不得重新散落为旧分类。
- 操作暂存区默认完全隐藏；显示时用抽屉或浮层，不预留主内容宽度。
- 页面编辑第一阶段只在后台预览区提供拖拽/缩放雏形，未保存前不得影响前台真实页面；必须保留恢复默认布局。

## 2026-05-03 导航、内容列表与工具箱规范

- 前台顶部导航固定为：首页、文章、图片、音乐、项目、友链、关于；搜索、杂谈、归档只保留路由能力，不作为顶部主导航。
- `/posts` 是统一内容列表页，板块切换使用清晰的“正经 / 杂谈”分段控件；显示模式切换使用“矩阵网格 / 中枢链路”分段控件。
- 矩阵网格卡片保持上图下文，内容区使用 flex column，标签区使用 `margin-top:auto` 靠底。
- 中枢链路卡片保持左右交替、贴近中心线；移动端退化为单列。
- 图片页相册卡片同样遵循上图下文和标签沉底规则，点击封面打开相册弹窗。
- 左下角工具箱悬浮球使用玻璃风格、固定定位和合理 z-index；展开菜单包含计算器、全局搜索、设置。
- 工具箱弹窗必须居中、可 Esc 关闭、移动端不横向溢出；弹窗不应压住确认类关键弹窗。
- 游客设置弹窗只管理浏览器本地偏好，包括昼夜、主题、背景、氛围、弹幕、点击音效、音乐音量和字体大小；不得展示后台私密配置。
- 首页右侧旧分散控制按钮不再显示，避免与工具箱重复。

## 2026-05-03 多平台留言与搜索框收口规范

- 前台留言板所有访客可见文案必须使用中文。GitHub/QQ 未配置时，只显示“站点暂未开启 GitHub/QQ 留言，请稍后再试或联系站点管理员。”，不得出现后端、Secret、`.env` 等开发者文案。
- GitHub 与 QQ 登录入口必须独立判断：一个平台未配置时，只禁用或提示该平台，不能影响另一个已配置平台。
- 后台留言设置使用中文主标签：是否开启留言板、GitHub 登录留言、QQ 登录留言、客户端 ID、应用 ID、密钥已配置状态等；内部字段名可以保持英文。
- 搜索区域外层保持轻量、无厚重边框和背景；搜索输入框本体保留清晰输入框样式，背景更不透明，高度更紧凑，右侧使用深色搜索图标按钮。
- 留言板、搜索框、标题区在 390px 下不得产生严重横向溢出。

## 2026-05-03 列表页与播放器收口补充

- 非首页页面标题区使用轻量化容器，标题和副标题保持居中，但外层不得再使用厚重毛玻璃卡片、明显边框或大背景填充；主体内容卡片不受此规则影响。
- 搜索区域的大容器要轻量透明；搜索输入框本身仍应保持可识别的输入框样式、focus 状态和 placeholder。
- 内容卡片应使用 `flex` 纵向布局，标签区靠近卡片底部，避免摘要长度不同造成标签高度跳动。
- 文章“中枢链路”模式在桌面端使用中轴线与左右交替卡片，单卡片宽度约为内容区三分之一；移动端退化为单列。
- 播放器音量控制是全局播放体验的一部分：首页和 `/music` 必须共享音量、静音状态，并持久化到 localStorage。
- 前台 GitHub 留言未配置提示必须面向访客，不出现后端配置、Secret、`.env` 等开发者词汇。
- 管理端相册编辑弹窗内容区必须可滚动，头部和操作区不能被大量缩略图挤出视口。
## 2026-05-03 P1/P2 收口补充

- Toast 必须使用全局顶层浮层，建议顶部居中或右上角，使用 `Teleport`/fixed 层级，不得出现在页面底部或挤占布局。
- 后台主导航固定在最左侧并铺满视口高度，父子/三级目录都应在主侧栏内完成；设置页主体不再放突兀的独立导航卡片。
- Markdown 近全屏编辑器桌面端为左右贴合分栏，中间分隔条可拖动；移动端切换编辑/预览。
- 字体颜色使用自定义 popover，包含颜色选择器、输入框和预设色；禁止使用浏览器原生 prompt。
- 名片统计和联系方式采用无边框、无填充的轻量文字/图标按钮；hover 只做克制缩放或透明度变化。
- 名片统计 hover 缩放应明显但不夸张，建议 `scale(1.06)` 到 `scale(1.1)`；联系方式 hover 需要图标变色并显示不挤占布局的 tooltip。
- 首页轮播分页点支持 hover 预选切换；移动端保留点击切换。
- 照片墙前台以相册封面为主视觉，进入相册后展示缩略图列表和当前大图。
- 首页音乐播放器应与名片高度接近，唱片在左、歌曲信息和进度条在右；歌词卡片保持紧凑高度并居中单行显示。
- 首页音乐播放器右半部分的歌名、歌手、进度条和控制按钮应整体居中；歌词区不显示额外英文标签，仅保留当前歌词或歌曲信息。
- `/music` 页面采用工具型双栏布局：左侧为主播放器，右侧为“歌词 / 歌单”页签；移动端改为上下布局。

## 2026-05-03 P2 交互细节补充规范

- Toast 必须作为全局顶层浮层显示在顶部居中或右上角，不得挤占页面布局；成功为绿色，失败为红色或警告色。
- 后台设置页可以有轻量顶部标签或锚点，但不得再出现抢占主区域的独立左侧二级导航卡片。
- 主题 token 表单必须展示中文名称、内部 key、颜色预览块、颜色选择器和文本输入框；日间/夜间分组清晰。
- 结构化内容新增/编辑使用居中弹窗，列表页默认只展示内容列表和新增按钮；高级 JSON 仍保持折叠兜底。
- Markdown 编辑器使用近全屏弹窗，桌面左右分栏，移动端编辑/预览切换；工具栏可收起。
- Markdown 快捷工具栏只插入安全 Markdown 或受控 HTML span，字体颜色仅允许 `#RRGGBB` 格式，渲染仍必须通过 DOMPurify。
- 鼠标跟随大型光晕默认移除；点击音效只绑定交互元素，不响应空白区域点击。
- 首页已有主音乐播放器时，不再显示右下角悬浮播放器，避免重复入口和遮挡内容。

## 2026-05-03 P2 第三阶段补充规范

- 首页轮播区使用固定不对称布局：左侧三分之一为文章轮播，右侧三分之二上层为照片墙轮播，右侧下层为更新轮播和独立昼夜切换卡片。
- 昼夜切换卡片是独立静态卡片，不进入轮播数据，不显示轮播分页点。
- 有图轮播必须让图片铺满卡片，标题、摘要、日期和分页点放在图片内部，并通过遮罩保证白天/夜间模式均可读。
- 有图组件 hover 只放大图片层；无图组件 hover 轻微缩放组件本体，比例控制在 `1.015` 到 `1.03`，不再以上移作为主要效果。
- 名片、歌词区、唱片播放器、昼夜切换卡片、底部状态区均属于无图组件，hover 使用同一缩放规则。
- 歌词区必须单行居中；长句允许按长度降低字号，但不得换行撑高布局。
- 后台左侧导航采用垂直平铺父子目录结构，不再使用胶囊堆叠作为主导航形态。
- 后台右侧 pendingOperations 暂存区必须可以完全隐藏；隐藏后主内容区扩宽，且必须提供恢复入口。
- 设置中心主题 token UI 展示使用中文名称，同时保留内部 token 键；颜色值同时提供颜色选择器和文本输入框。
- 本地上传入口可用于图片、音频和视频字段；上传后回填 URL，仍必须遵守后端扩展名、MIME 和大小限制。

## 2026-05-03 P2 首页轮播与播放器补充规范

- 首页只保留新结构：名片 + 唱片式音乐播放器、居中歌词区、三组轮播卡片、底部状态区；旧首页内容发现、站点仪表盘、旧最新文章、旧云端杂谈、旧最近瞬间不再作为首页主结构展示。
- 文章列表和杂谈列表统一为居中页头、无外边框搜索栏、大屏三列图片卡片；小屏自动降列，不允许横向撑宽。
- 文章页提供“矩阵网格 / 中枢链路”双显示模式。中枢链路在桌面端使用中轴线和左右交替卡片，移动端退化为单列。
- 大搜索栏使用轻量透明样式，不使用厚外框或明显背景填充；搜索图标/标识、placeholder 和输入态必须清晰。
- 内容卡片标签区应靠近卡片底部，使用 `flex` 布局和 `margin-top:auto` 维持多卡片视觉齐平。
- 除首页外，页面标题和副标题默认居中显示；正文、表格、时间线等内容区保持自身可读布局，不强行居中正文。
- 三组轮播必须是真实轮播区域：最新文章、最新更新内容、主题模式。至少提供自动切换或分页点切换，本轮两者均支持。
- 有图片的轮播卡片 hover 时只放大图片层，卡片本体不明显缩放，避免布局抖动。
- 无图片卡片 hover 时组件本体可以轻微缩放，建议 `scale(1.015)` 到 `scale(1.035)`，不再以上移作为主效果。
- 首页唱片播放器采用唱片、歌名、歌手、进度条和上一首/播放暂停/下一首图标按钮结构；无 URL 时必须给出可读提示，不得报错。
- 歌词区文字应水平居中并在视觉上垂直居中；无歌词时展示当前歌曲信息或占位文案。
- 顶部导航滚动隐藏/显示动画建议 450ms-650ms，本轮使用约 560ms cubic-bezier 曲线。

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

- 前台顶部导航采用铺满式顶栏，不再使用悬浮胶囊作为主结构。
- 顶栏保持毛玻璃/半透明质感，内部内容仍使用 `sr-page-shell` 与页面主体对齐。
- 顶栏向下滚动时隐藏，向上滚动或鼠标移到页面顶部时显示；动画必须平滑。
- sticky 导航不得遮挡正文标题。
- 中窄屏下导航按钮不得超出视口。
- 后台侧边栏 active 状态必须明确，当前页应有边框、底色或左侧强调线。

## Page Width

- 前台主要页面使用 `width: min(calc(100% - 3rem), 80rem)` 或等价类。
- 480px 以下宽度使用更紧凑的左右留白，但左右 padding 必须基本一致。
- 首页 Hero/ProfileCard、SiteDashboard、最新文章、内容发现入口必须共用同一主容器。
- Grid/Flex 子项必须使用 `min-w-0`，图片和卡片必须 `max-width: 100%`。
- 文章正文比首页聚合区更窄或更聚焦，优先保证阅读舒适。

## Home Structure

首页 P2 第二阶段采用固定结构顺序：

1. 第一排：左侧个人名片，右侧首页音乐播放器卡片。
2. 第二排：全宽歌词/播放状态区，与音乐播放器形成一组。
3. 第三排：不对称内容模块，至少包含最新文章、最新更新内容和昼夜模式切换卡片。
4. 内容发现入口：搜索、标签、归档保持可见。
5. 底部状态区：北京时间、网站运行时间、技术栈。

最新更新内容优先复用公开 posts/moments/chatters 聚合数据，draft 内容不得出现。

## Day/Night Theme

昼夜主题使用 CSS 变量，不做两套组件：

- `--bg-page`
- `--bg-card`
- `--bg-card-elevated`
- `--border-glass`
- `--text-primary`
- `--text-secondary`
- `--accent`
- `--accent-soft`
- `--nav-bg`
- `--home-panel-bg`
- `--shadow-glow`

后台设置中心可以配置核心 token、字体族和字号档位。前台通过 `themeConfig` 读取公开 token，切换模式时写入浏览器本地偏好。

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
- 评论区统一命名为“留言板”。留言板应有访客视角标题、副标题、头像区、输入区、登录状态/登录按钮和下方操作反馈；GitHub 未配置提示不得出现后台配置口吻。
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
## 2026-05-03 列表页细节补充

- 文章、杂谈、搜索结果等内容卡片的标签区必须靠近卡片底部，避免摘要长短导致标签上下跳动。
- 文章页“中枢链路”模式应让左右卡片贴靠中心线，桌面端单卡片约为内容区三分之一宽，移动端退化为单列。
- 搜索框本体保留清晰输入框样式；搜索区和页面标题区外层保持轻量，不使用厚重边框和大面积毛玻璃背景。
- 搜索框不使用额外文字标签，右侧使用深色图标按钮；桌面端宽度应接近内容区 80%，移动端占满可用宽度。
- 后台弹窗类编辑器应限制在视口内，头尾操作区可见，中间内容滚动，避免相册缩略图被裁切。
## 2026-05-03 Admin Album Modal Rule

- Admin create/edit modals that contain media grids should use one viewport-constrained shell, one scrollable body, and a reachable footer action row.
- Media grid sections must grow naturally. Do not put fixed-height clipping containers around album photo previews.
- Album thumbnails should use stable preview dimensions and `object-fit: cover`; large source images must not stretch the modal.
- Scrolling should happen at the modal body level, not inside each small photo section.

## 2026-05-03 Message Board and Search Polish

Message boards use the same glass surface as article comments, music, and photowall album dialogs. Login buttons should be clear platform choices, with disabled states still readable. Search inputs should be compact, more opaque than the surrounding lightweight search area, and keep an icon-only dark search button.
## 2026-05-05 前台红色重点色与跨行布局规范

### 页面容器

- 前台主内容容器桌面端左右留白扩大到上一轮的约 150%，统一通过页面 shell/section 变量或公共类控制。
- 移动端不得照搬桌面大留白，窄屏继续使用紧凑安全边距，避免内容过窄。
- 顶部导航和左下角工具箱固定位置不参与主内容宽度计算。

### 色彩方向

- 白天模式：白色、浅灰、深灰文字为主，红色只作为重点色。
- 夜间模式：黑色、深灰、浅灰文字为主，红色只作为重点色。
- 红色重点色用于 active、hover、链接重点态、轮播当前点、导航品牌中的 `<`、`/`、`>` 等小面积强调。
- 保持前台毛玻璃质感，不改成后台黑白灰平面风。

### 首页布局

- 首页核心模块使用 12 栅格 CSS Grid。
- 支持 `rowSpan`，不再强制同一行组件等高。
- 默认四组件区域建议为：左侧 4/12 宽并跨两行，右上 8/12 宽，右下两个 4/12 小组件并排。
- 后台页面编辑保存的 `w/h/rowSpan/order/visible` 必须在桌面端前台真实应用；移动端可退化为单列。

### 轮播与播放器

- 轮播分页指示器统一放在卡片底部内侧，当前项使用红色重点色，非当前项半透明。
- 首页和音乐页播放器控制顺序为：播放模式、音量、上一首、播放/暂停、下一首、喜欢。
- 音量默认只显示图标，hover/focus 时显示垂直悬浮滑杆，不挤占布局。

### 全局主题预设

- 后台提供“白昼红白主题”和“夜幕红黑主题”一键应用。
- 预设应更新全局 token 和默认组件主题；组件单独设置继续拥有覆盖能力。
- 组件级自定义仍通过颜色、透明度、大小和字体字段微调，不得散落硬编码颜色。
## 2026-05-05 Red/White/Black Glass Theme Rules

Frontend visual direction:

- Keep the frontend glass style. Do not flatten it into the admin black/white/gray tool style.
- Default theme is `Shrink 红白黑玻璃主题`.
- Day mode uses white, light gray, dark text, and red as the only accent.
- Night mode uses black, dark gray, light text, and red as the only accent.
- Red accent is used for active states, hover emphasis, links, current carousel dot, progress highlights, important button accents, and the `<`, `/`, `>` symbols in `<Shrink/>`.
- Red must stay an accent, not a large surface color.

Layout and spacing:

- Main frontend page containers use shared side padding variables and are visually more centered than previous rounds.
- Desktop side margin is about 150% of the previous page shell spacing.
- Tablet and mobile use reduced padding so content remains readable.
- Fixed elements such as the top navigation and toolbox do not participate in the page content width calculation.

Theme package:

- Theme packages contain day/night tokens, component theme defaults, and optional page layout data.
- Component overrides remain supported and take priority over global token defaults.
- Admin theme preset actions should update global tokens first; they should not remove the ability to fine-tune individual components.

Player and carousel:

- Home and music player controls are ordered as playback mode, volume, previous, play/pause, next, like.
- The volume slider is vertical, floating, and remains visible while hovered or dragged.
- Carousel indicators are placed at the bottom inside the card. The active indicator uses the red accent.

## 2026-05-06 前台卡片文字与音乐页布局规则

- 图片明暗自适应只用于压在图片上的标题、摘要和轮播覆盖文案。
- 文章卡片、杂谈卡片、相册卡片的图片下方正文必须跟随主题文字 token：白天深色，夜间浅色。
- 内容卡片标签使用透明背景、边框和主题文字色，不使用红色实心填充。
- 分段切换控件统一使用居中对齐、红色 active 背景和高对比文字。
- 音乐页保持固定两栏：左播放器、右歌词/歌单面板；面板不得塌陷或裁切内容。

## 2026-05-07 工具箱与背景层规则

- 游客工具箱必须显式区分日间和夜间状态：日间使用浅色玻璃面板、深色文字和深色表单控件文字；夜间使用深色玻璃面板、浅色文字。
- 左下角工具箱悬浮球和展开菜单也要随昼夜模式切换背景、边框和文字色，不允许日间仍保留深色菜单加白字造成风格断层。
- 前台背景不是纯色背景。主题应使用“壁纸图层 + 昼夜蒙层 + 毛玻璃内容”的结构，壁纸图层必须保持可辨识，只由蒙层负责统一白/灰/红或黑/灰/红氛围。
## About Page Visual Direction

- `/about` uses the existing site wallpaper/background-effect layer. Do not replace the root page background with a hard-coded pure white block.
- The page is organized as four vertical portfolio sections: Hero, About Me, GitHub Activity, and Contact.
- Day mode uses dark text on white/light glass cards with red as the only strong accent.
- Night mode uses light text on dark glass cards with the same red accent.
- Decorative lines, orbits, triangles, and particles are local to the About page and must not obstruct text or form fields.
- Contact form controls must keep strong contrast in both modes and show loading/error/success states.
# 后台管理界面收口规范（2026-05-09）

- 后台保持黑白灰平面简约风，定位为高密度管理工具，不使用前台毛玻璃视觉。
- 一级导航仅保留：内容管理、设置、审计日志、备份恢复。
- 不再提供低代码式组件宽高、拖拽、添加、删除等页面布局编辑入口。
- 内容管理页面使用清晰的列表、表单、弹窗和分段开关；文章区分“正经 / 杂谈”，图片以相册组管理，音乐以歌单/歌曲管理。
- 设置页仅保留四个 Frame：站点信息设置、我的信息设置、主题设置、留言设置。
- 旧 `pageLayouts` 和旧页面编辑能力仅作为兼容数据存在，不作为 UI 主流程展示。
