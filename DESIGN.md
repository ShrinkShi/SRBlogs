# SRBlogs Design Guide

本文档是 SRBlogs 项目的 UI 设计约束文件。  
所有涉及 UI、布局、样式、组件视觉、交互状态、后台页面重构的修改，都必须优先阅读并遵守本文档。

本设计规范主要面向：

```text
admin/ 后台管理端
frontend/ 前台页面中需要统一视觉语言的管理型组件
后续所有与 UI 相关的 Codex / AI 修改任务
```

本项目可以参考「异次元发卡网」一类后台的视觉语言，但**不是照搬**。SRBlogs 需要保留自己的品牌特征，尤其是：

```text
SRBlogs 的重点色是红色
背景图必须可配置
不固定为二次元少女
不照搬参考项目的图标、文案、布局细节、业务结构
```

---

## 1. 设计目标

SRBlogs Admin 的 UI 目标是：

> 浅色、干净、柔和、轻量、有玻璃质感、有个人博客气质，同时保留 SRBlogs 的红色品牌重点色。

关键词：

```text
Light Admin
Soft Glassmorphism
Red Accent
Customizable Background
Large Whitespace
Low Contrast
Rounded Cards
Soft Shadow
Readable Forms
Calm Dashboard
Personal Blog System
```

中文解释：

```text
浅色后台
轻玻璃拟态
红色重点色
可定制背景
大面积留白
低对比
圆角卡片
柔和阴影
清晰表单
克制的后台仪表盘
个人博客系统气质
```

---

## 2. 与参考项目的关系

可以学习参考项目的这些特点：

```text
浅色主基调
左侧固定 Sidebar
顶部轻量 Topbar
内容区域居中
半透明卡片
宽松表单
柔和背景图
低对比输入框
轻阴影
圆角按钮
```

不能照搬这些内容：

```text
不能照搬参考项目名称、logo、图标、菜单文案
不能固定使用二次元少女背景
不能把 SRBlogs 改成发卡网后台
不能把业务结构改成电商/发卡系统结构
不能抛弃 SRBlogs 原有红色品牌重点色
不能为了相似外观破坏现有功能
```

SRBlogs 要做的是：

```text
学习它的“轻、白、透、柔、松”的视觉方法
保留 SRBlogs 的红色点缀、个人博客属性、内容管理属性
```

---

## 3. 总体风格定义

SRBlogs Admin 的推荐风格名称：

```text
轻红玻璃后台
```

也可以理解为：

```text
Light Red Glass Admin
```

核心描述：

```text
以白色和浅灰作为页面基底，以低饱和红色作为品牌重点色，通过半透明卡片、柔和阴影、宽松间距和可定制背景图，形成清爽但具有个性化的后台管理界面。
```

不是以下风格：

```text
不是暗黑科技风
不是黑红赛博风
不是高饱和红色警告风
不是纯二次元主题站后台
不是传统 Bootstrap 默认后台
不是企业 ERP 密集表格风
不是花哨粒子特效风
不是粗暴堆 Tailwind class 的临时页面
```

---

## 4. 色彩规范

### 4.1 基础色

后台整体以白色、浅灰为主。

推荐 CSS 变量：

```css
:root {
  --admin-bg: #f8fafc;
  --admin-bg-soft: #fafafa;
  --admin-surface: rgba(255, 255, 255, 0.84);
  --admin-surface-strong: rgba(255, 255, 255, 0.94);
  --admin-surface-muted: rgba(248, 250, 252, 0.78);

  --admin-text-primary: #0f172a;
  --admin-text-secondary: #64748b;
  --admin-text-muted: #94a3b8;

  --admin-border: rgba(148, 163, 184, 0.18);
  --admin-border-soft: rgba(148, 163, 184, 0.12);
}
```

### 4.2 SRBlogs 品牌重点色：红色

SRBlogs 的重点色必须保留为红色，但要使用**低饱和、柔和、克制**的红色，不要使用刺眼大红。

推荐：

```css
:root {
  --admin-primary: #ef4444;
  --admin-primary-strong: #dc2626;
  --admin-primary-soft: rgba(239, 68, 68, 0.10);
  --admin-primary-softer: rgba(239, 68, 68, 0.06);
  --admin-primary-border: rgba(239, 68, 68, 0.22);
  --admin-primary-shadow: rgba(239, 68, 68, 0.18);
}
```

使用原则：

```text
红色用于：主按钮、当前菜单项、关键状态、当前 Tab、重要操作提示
红色不用于：大面积背景、整页渐变、长文本背景、普通表格行背景
```

### 4.3 辅助色

辅助色只能少量使用，用于状态区分。

```css
:root {
  --admin-success: #22c55e;
  --admin-success-soft: rgba(34, 197, 94, 0.10);

  --admin-warning: #f59e0b;
  --admin-warning-soft: rgba(245, 158, 11, 0.12);

  --admin-info: #60a5fa;
  --admin-info-soft: rgba(96, 165, 250, 0.12);

  --admin-danger: #ef4444;
  --admin-danger-soft: rgba(239, 68, 68, 0.10);
}
```

注意：蓝色可以保留为信息色，但不能成为主品牌色。主重点色仍然是红色。

### 4.4 色彩比例

推荐比例：

```text
80% 白色 / 浅灰
10% 红色品牌重点色
5% 信息蓝
5% 状态色
```

禁止：

```text
大面积纯黑
大面积高饱和红
大量霓虹色
多个渐变色同时出现
背景和卡片对比过强
按钮颜色体系混乱
```

---

## 5. 页面布局

后台采用经典三段式结构：

```text
左侧 Sidebar
顶部 Topbar
右侧 Main Content
```

推荐尺寸：

```text
Sidebar 宽度：220px - 240px
Topbar 高度：56px - 64px
主内容左右 padding：32px - 48px
内容最大宽度：1200px - 1380px
```

主内容不要贴边。  
表单、表格、编辑区都应放入卡片或清晰的 section 中。

推荐结构：

```text
AdminLayout
├── Sidebar
├── Topbar
└── MainContent
    └── PageCard / PageSection / DataPanel
```

禁止：

```text
内容贴着浏览器边缘
左侧栏和主内容没有分隔
页面信息密度过高
所有模块挤在一屏
顶部栏放太多按钮
```

---

## 6. 背景图规范

SRBlogs 允许使用背景图，但背景图必须**可配置**。

背景图可以是：

```text
抽象图形
柔和插画
个人博客风格背景
渐变光影图
站点自定义背景
轻量二次元图
自然风景
城市/设备/代码氛围图
```

背景图不能固定为：

```text
固定二次元少女
固定某张图片
固定外部 URL
固定参考项目同款图
```

### 6.1 背景图配置原则

后台背景图应从配置或 CSS 变量读取。

推荐变量：

```css
:root {
  --admin-bg-image: none;
  --admin-bg-image-opacity: 0.12;
  --admin-bg-overlay: rgba(255, 255, 255, 0.72);
}
```

可通过站点设置扩展：

```text
adminBackgroundImage
adminBackgroundOpacity
adminBackgroundBlur
```

### 6.2 背景实现建议

```css
.admin-main {
  position: relative;
  background: var(--admin-bg);
}

.admin-main::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image: var(--admin-bg-image);
  background-position: center top;
  background-size: contain;
  background-repeat: no-repeat;
  opacity: var(--admin-bg-image-opacity, 0.12);
  pointer-events: none;
  z-index: 0;
}

.admin-main::after {
  content: "";
  position: fixed;
  inset: 0;
  background: var(--admin-bg-overlay, rgba(255, 255, 255, 0.72));
  backdrop-filter: blur(2px);
  pointer-events: none;
  z-index: 0;
}

.admin-content {
  position: relative;
  z-index: 1;
}
```

### 6.3 背景图限制

必须遵守：

```text
透明度建议：0.06 - 0.18
必须保证文字可读
必须加白色或浅色遮罩
不能干扰表单输入
不能抢占主体视觉
不能依赖背景图传递关键信息
```

如果背景图质量不够，宁可使用纯浅灰背景。

---

## 7. Sidebar 设计约束

Sidebar 必须轻量、稳定、清晰。

推荐：

```css
.admin-sidebar {
  width: 220px;
  background: rgba(255, 255, 255, 0.92);
  border-right: 1px solid rgba(148, 163, 184, 0.14);
  backdrop-filter: blur(12px);
}
```

菜单分组建议：

```text
MAIN
  控制台

CONTENT
  文章管理
  分类管理
  标签管理
  评论管理

MEDIA
  音乐管理
  相册管理

SYSTEM
  网站设置
  备份管理
  审计日志
```

分组标题：

```css
.sidebar-group-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #94a3b8;
  text-transform: uppercase;
}
```

菜单项：

```css
.sidebar-link {
  height: 38px;
  border-radius: 10px;
  color: #4b5563;
  font-size: 14px;
}

.sidebar-link:hover {
  background: var(--admin-primary-softer);
  color: var(--admin-primary-strong);
}

.sidebar-link.active {
  background: var(--admin-primary-soft);
  color: var(--admin-primary-strong);
}
```

禁止：

```text
纯黑 Sidebar
大面积深红 Sidebar
选中项使用刺眼红色块
菜单项高度过低
菜单分组不清晰
图标过粗过大
```

---

## 8. Topbar 设计约束

Topbar 应该轻，不应该抢主体。

推荐：

```css
.admin-topbar {
  height: 60px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}
```

Topbar 可以包含：

```text
当前页面标题
面包屑
环境标识
当前登录用户
退出按钮
少量快捷操作
```

胶囊标签：

```css
.admin-pill {
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.14);
  color: #64748b;
}

.admin-pill.primary {
  background: var(--admin-primary-soft);
  border-color: var(--admin-primary-border);
  color: var(--admin-primary-strong);
}
```

禁止：

```text
Topbar 过高
顶部堆满操作按钮
顶部使用强阴影
顶部使用大面积纯红背景
```

---

## 9. 卡片设计约束

后台主要内容应放入卡片中。

推荐：

```css
.admin-card {
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.68);
  border-radius: 22px;
  box-shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
}
```

卡片头部：

```css
.admin-card-header {
  min-height: 60px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.admin-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}
```

卡片内容：

```css
.admin-card-body {
  padding: 32px 40px;
}
```

禁止：

```text
卡片边框太黑
阴影太重
卡片内部拥挤
多个卡片之间间距过小
卡片圆角不统一
透明度太高导致文字看不清
```

---

## 10. 表单设计约束

后台设置类页面优先使用「左 label，右控件」的双列布局。

推荐结构：

```text
FormRow
├── Label
└── Control
```

推荐尺寸：

```text
label 宽度：220px - 280px
input 高度：42px - 46px
行间距：22px - 28px
```

推荐：

```css
.admin-form-row {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 32px;
  align-items: center;
  margin-bottom: 24px;
}

.admin-label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.admin-required {
  color: var(--admin-primary);
}
```

输入框：

```css
.admin-input {
  height: 44px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(248, 250, 252, 0.78);
  color: #334155;
  padding: 0 16px;
  outline: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.admin-input::placeholder {
  color: #94a3b8;
}

.admin-input:focus {
  border-color: rgba(239, 68, 68, 0.48);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.12);
}
```

Textarea：

```css
.admin-textarea {
  min-height: 120px;
  resize: vertical;
  border-radius: 12px;
}
```

禁止：

```text
label 和 input 挤在一起
input 高度不统一
input 边框过黑
placeholder 颜色过深
focus 状态没有反馈
必填星号使用刺眼红
表单横向过宽导致阅读困难
```

---

## 11. 按钮设计约束

按钮应柔和、圆润、低饱和。

主按钮使用 SRBlogs 红色：

```css
.admin-btn-primary {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.22);
}
```

次按钮：

```css
.admin-btn-secondary {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.88);
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.18);
}
```

危险按钮：

```css
.admin-btn-danger {
  background: rgba(239, 68, 68, 0.10);
  color: #dc2626;
}
```

交互：

```css
.admin-btn {
  transition: all 0.18s ease;
}

.admin-btn:hover {
  transform: translateY(-1px);
}

.admin-btn:active {
  transform: translateY(0);
}
```

禁止：

```text
主按钮使用蓝色替代红色
按钮阴影过重
按钮高度不统一
同一页面出现多套按钮风格
所有按钮都使用高饱和红
```

---

## 12. 表格设计约束

表格不应像传统 ERP 一样密集。

推荐：

```text
表头浅灰
行高 48px - 56px
行 hover 使用浅红背景
边框极淡
操作按钮使用文字按钮或浅色胶囊按钮
```

推荐：

```css
.admin-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.admin-table th {
  height: 44px;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  background: rgba(248, 250, 252, 0.72);
}

.admin-table td {
  height: 52px;
  color: #334155;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.admin-table tr:hover td {
  background: rgba(239, 68, 68, 0.04);
}
```

禁止：

```text
表格线过重
行高过低
操作按钮堆叠
表格内容贴边
hover 使用强红背景
```

---

## 13. Tab 与页面分区

后台设置页、内容管理页允许使用轻量 Tab。

推荐：

```css
.admin-tabs {
  display: flex;
  gap: 8px;
  align-items: center;
}

.admin-tab {
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  color: #64748b;
  background: transparent;
}

.admin-tab.active {
  color: var(--admin-primary-strong);
  background: var(--admin-primary-soft);
}
```

Tab 数量过多时应分组，不要挤成一排。

---

## 14. 空状态、加载态、错误态

所有管理页面必须有明确状态。

### 14.1 空状态

```text
图标
简短标题
一句说明
可选操作按钮
```

推荐：

```css
.admin-empty {
  padding: 48px 24px;
  text-align: center;
  color: #94a3b8;
}
```

### 14.2 加载态

使用骨架屏或轻量 spinner。  
不能整页白屏。

### 14.3 错误态

错误信息应说明：

```text
发生了什么
可能原因
用户可以怎么做
```

禁止：

```text
加载时白屏
请求失败只在 console 报错
空数据时显示 undefined/null
错误态使用浏览器默认 alert
```

---

## 15. 字体规范

使用系统字体，不额外引入复杂字体。

```css
font-family:
  Inter,
  ui-sans-serif,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  "Microsoft YaHei",
  sans-serif;
```

字号建议：

```text
页面标题：20px - 24px / 700
卡片标题：18px - 20px / 700
表单 label：14px - 15px / 500
输入框文字：14px - 15px
辅助说明：12px - 13px
菜单分组：11px - 12px / 700 / letter-spacing
菜单项：14px
```

禁止：

```text
正文字号过大
混用过多字体
字重层级混乱
英文和中文基线不协调
```

---

## 16. 动效规范

后台动效必须克制。

允许：

```text
hover 轻微上浮
菜单背景淡入
卡片轻微阴影变化
modal 淡入
loading skeleton
```

推荐：

```css
transition: all 0.18s ease;
```

禁止：

```text
大幅缩放
大面积闪烁
复杂粒子
强烈弹跳动画
页面切换时整页大动画
```

---

## 17. 响应式约束

后台至少支持：

```text
桌面端：>= 1280px
中等宽度：1024px - 1279px
窄屏：<= 768px 基本可用
```

窄屏规则：

```text
Sidebar 可折叠
表单双列改为单列
主内容 padding 缩小到 16px - 20px
卡片圆角和阴影适当减弱
Topbar 不堆叠过多操作
```

移动端不是后台核心场景，但不能完全崩。

---

## 18. SRBlogs Admin 修改范围约束

涉及后台 UI 的第一阶段修改，优先集中在：

```text
admin/src/components/AdminLayout.vue
admin/src/views/Login.vue
admin/src/components/LoginForm.vue
admin/src/views/ContentHub.vue
admin/src/views/Settings.vue
admin/src/styles.css
```

允许新增通用 UI 组件：

```text
admin/src/components/ui/AdminCard.vue
admin/src/components/ui/AdminButton.vue
admin/src/components/ui/AdminInput.vue
admin/src/components/ui/AdminSection.vue
admin/src/components/ui/AdminTabs.vue
admin/src/components/ui/AdminTable.vue
admin/src/components/ui/AdminEmpty.vue
```

原则：

```text
UI 组件负责视觉和基础交互
页面负责布局和数据组织
api 目录负责请求
stores 目录负责状态
router 目录负责路由
```

禁止在 UI 重构中随意修改：

```text
admin/src/api/*
admin/src/stores/*
admin/src/router/*
admin/src/types.ts
backend/*
```

除非本轮任务明确要求。

---

## 19. 与业务逻辑的边界

UI 重构不得破坏现有功能。

禁止：

```text
擅自修改 API 契约
擅自删除现有字段
擅自改变登录流程
擅自改变 JWT 存储方式
擅自改变路由守卫
擅自改变后端接口
为了视觉效果牺牲功能可用性
```

如果接口字段与 UI mock 字段不一致，应写 adapter，而不是强行改 UI 结构或后端接口。

---

## 20. 页面优先级

后台 UI 重构按以下顺序进行。

### 第一阶段

```text
AdminLayout
Login
Settings
Dashboard / ContentHub
```

目标：建立整体视觉语言。

### 第二阶段

```text
文章管理
分类 / 标签
评论管理
项目管理
友链管理
```

目标：统一列表、表格、表单、空状态。

### 第三阶段

```text
音乐管理
相册管理
备份管理
审计日志
```

目标：处理复杂管理页面。

### 第四阶段

```text
Markdown 编辑器
复杂弹窗
批量上传
大型表单
```

目标：单独设计高密度操作页，不强行套用大留白卡片。

---

## 21. Codex / AI 修改 UI 时必须遵守的规则

每次让 Codex 或其他 AI 修改 UI 时，必须明确要求：

```text
请先阅读 DESIGN.md，并严格遵守其中的 UI 风格和修改边界。
```

AI 修改 UI 的硬性要求：

```text
1. 不允许引入新的 UI 框架。
2. 不允许改后端。
3. 不允许改 API 契约。
4. 不允许破坏登录、权限、路由守卫。
5. 不允许把后台改成深色主题。
6. 不允许把 SRBlogs 改成异次元发卡网。
7. 不允许固定使用二次元少女背景。
8. 不允许移除 SRBlogs 的红色重点色。
9. 不允许大面积使用强渐变和霓虹效果。
10. 不允许用随机 class 堆出一次性页面。
11. 不允许删除现有功能入口。
12. 修改后必须保证 admin 构建通过。
```

推荐 Codex 执行流程：

```text
1. 阅读 DESIGN.md
2. 扫描当前 admin 结构
3. 说明本轮准备修改的文件
4. 只修改本轮需要的 UI 文件
5. 不碰 api/stores/router/backend
6. 运行 cd admin && npm run build
7. 汇总变更和验收点
```

---

## 22. 验收标准

任意 UI 修改必须满足：

```text
1. cd admin && npm run build 通过
2. /admin/login 正常显示
3. 登录后后台不白屏
4. Sidebar、Topbar、主内容卡片风格统一
5. 重点色为 SRBlogs 红色，而不是蓝色或粉色
6. 背景图可配置，不固定为某张二次元图
7. 没有资源 404
8. 没有 console error
9. 没有明显布局溢出
10. 表单可读性良好
11. 按钮、输入框、卡片样式统一
12. 原有功能入口不丢失
```

涉及部署后的后台页面，还必须验证：

```text
http://服务器IP/admin/login
```

并检查浏览器控制台：

```text
无 /admin/assets/*.js 404
无 /admin/assets/*.css 404
无 MIME type error
无白屏
```

---

## 23. 反例

以下修改不符合本设计规范：

```text
把后台改成黑红科技风
把 Sidebar 做成纯黑大色块
主按钮大量使用鲜红色
把重点色改成蓝色或粉色
固定使用二次元少女背景
背景图透明度过高导致文字看不清
表单行距过小
卡片阴影过重
所有页面都挤满小组件
为了视觉效果删除已有功能
为了 UI 重构改 API
用 alert 展示错误
加载时整页白屏
照搬异次元发卡网的菜单、logo、业务文案
```

---

## 24. 简短版提示词

当需要快速要求 AI 按本规范修改 UI 时，可以使用：

```text
请先阅读项目根目录 DESIGN.md。本轮只做 SRBlogs Admin UI 修改，必须遵守 DESIGN.md 中的“轻红玻璃后台”风格：浅色主基调、SRBlogs 红色重点色、半透明玻璃卡片、大留白、柔和阴影、白色 Sidebar、半透明 Topbar、表单卡片化布局、背景图可配置。可以参考异次元发卡网的轻量后台视觉，但不能照搬，不能固定二次元少女背景，不能把重点色改成蓝色或粉色。不要改后端、不要改 API、不要改登录和路由守卫、不要引入 UI 框架。修改后必须保证 cd admin && npm run build 通过。
```

---

## 25. 设计原则总结

SRBlogs Admin 的 UI 不追求炫耀，而追求长期使用的舒适感。

最终效果应当是：

```text
第一眼干净
第二眼柔和
长期使用不累
功能入口清楚
表单和数据可读
保留 SRBlogs 红色识别
背景可以个性化配置
视觉统一而不喧宾夺主
```
