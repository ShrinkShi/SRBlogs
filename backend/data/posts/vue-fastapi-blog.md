---
title: "用 Vue3 和 FastAPI 重构个人博客"
date: "2026-05-01 18:30"
tags:
  - Vue3
  - FastAPI
  - 博客系统
draft: false
cover: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop"
summary: "把原本偏静态的个人博客升级成前后端分离系统：前台展示、后台管理、Markdown 文件存储。"
---

## 为什么要前后端分离

个人博客如果只追求展示，静态站点够用。但一旦加入后台写作、图床配置、AI 助手和内容管理，纯静态方案会开始变形。

SRBlogs 的处理方式是：

- Vue3 负责前台和后台两个 SPA。
- FastAPI 负责统一 REST API。
- Markdown 文件继续作为文章主存储。
- JSON 文件保存友链、项目、音乐和照片墙。

## 当前设计

```ts
const stack = ['Vue3', 'Vite', 'TypeScript', 'Pinia', 'FastAPI']
console.log(stack.join(' + '))
```

## 不要过度迷信视觉

毛玻璃、动态背景、弹幕和音乐挂件只能提升第一印象。真正决定项目能不能长期用的是：内容模型、后台写作效率、部署稳定性和备份机制。
