<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'

type PageKey = 'home' | 'posts' | 'photos' | 'music' | 'projects' | 'friends' | 'about'
type PageTextKey = PageKey | 'chatters'

interface EditorBlock {
  id: string
  label: string
  type: string
  order: number
  w: number
  h: number
  visible: boolean
  locked?: boolean
  props?: Record<string, unknown>
}

interface AddableBlock {
  type: string
  label: string
  unique?: boolean
  w: number
  h: number
  props?: Record<string, unknown>
}

const route = useRoute()
const router = useRouter()
const pageKeys: PageKey[] = ['home', 'posts', 'photos', 'music', 'projects', 'friends', 'about']
const pageKey = computed<PageKey>(() => {
  const key = String(route.params.page || 'home')
  return pageKeys.includes(key as PageKey) ? key as PageKey : 'home'
})

const pages: Array<{ key: PageKey; label: string; path: string; action: string; actionPath: string }> = [
  { key: 'home', label: '首页', path: '/', action: '编辑首页名片', actionPath: '/pages/home' },
  { key: 'posts', label: '文章', path: '/posts', action: '新增文章', actionPath: '/content/editor' },
  { key: 'photos', label: '图片', path: '/photowall', action: '新增相册', actionPath: '/photos' },
  { key: 'music', label: '音乐', path: '/music', action: '新增歌曲', actionPath: '/music' },
  { key: 'projects', label: '项目', path: '/projects', action: '新增项目', actionPath: '/projects' },
  { key: 'friends', label: '友链', path: '/friends', action: '新增友链', actionPath: '/friends' },
  { key: 'about', label: '关于', path: '/about', action: '编辑关于 Markdown', actionPath: '/about' }
]

const defaultText: Record<PageTextKey, { title: string; subtitle: string }> = {
  home: { title: '首页', subtitle: '名片、音乐、歌词、轮播与状态区。' },
  posts: { title: '文章归档', subtitle: '从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。' },
  chatters: { title: '云端杂谈', subtitle: '长一点的念头，短一点的文章。' },
  photos: { title: '图片', subtitle: '相册记录从后端 JSON 动态读取，点击封面可查看组内照片。' },
  music: { title: '音乐歌单', subtitle: '全局播放器、歌词和歌单共享同一播放状态。' },
  projects: { title: '项目陈列柜', subtitle: '记录正在构建和已经完成的作品。' },
  friends: { title: '星际友链', subtitle: '把值得长期访问的站点放在这里。' },
  about: { title: '关于', subtitle: '关于 SRBlogs 与站点作者。' }
}

const defaultLayouts: Record<PageKey, EditorBlock[]> = {
  home: [
    { id: 'profileCard', label: '名片', type: 'profileCard', order: 1, w: 6, h: 2, visible: true, locked: true },
    { id: 'musicPlayer', label: '音乐播放器', type: 'musicPlayer', order: 2, w: 6, h: 2, visible: true, locked: true },
    { id: 'lyrics', label: '歌词区', type: 'lyrics', order: 3, w: 12, h: 1, visible: true, locked: true },
    { id: 'latestPostsCarousel', label: '最新文章轮播', type: 'latestPostsCarousel', order: 4, w: 4, h: 3, visible: true, locked: true },
    { id: 'photoCarousel', label: '图片轮播', type: 'photoCarousel', order: 5, w: 8, h: 2, visible: true, locked: true },
    { id: 'updatesCarousel', label: '更新内容轮播', type: 'updatesCarousel', order: 6, w: 8, h: 2, visible: true, locked: true },
    { id: 'themeToggle', label: '昼夜切换卡片', type: 'themeToggle', order: 7, w: 4, h: 2, visible: true, locked: true },
    { id: 'statusBar', label: '底部状态区', type: 'statusBar', order: 8, w: 12, h: 1, visible: true, locked: true }
  ],
  posts: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'sectionSwitch', label: '正经 / 杂谈切换', type: 'sectionSwitch', order: 2, w: 12, h: 0.8, visible: true, locked: true },
    { id: 'searchBox', label: '搜索区', type: 'searchBox', order: 3, w: 12, h: 0.8, visible: true, locked: true },
    { id: 'tagFilter', label: '标签筛选区', type: 'tagFilter', order: 4, w: 12, h: 0.8, visible: true, locked: true },
    { id: 'viewModeSwitch', label: '显示模式切换', type: 'viewModeSwitch', order: 5, w: 12, h: 0.8, visible: true, locked: true },
    { id: 'contentList', label: '内容列表区', type: 'contentList', order: 6, w: 12, h: 4, visible: true, locked: true }
  ],
  photos: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'viewModeSwitch', label: '显示模式切换', type: 'viewModeSwitch', order: 2, w: 12, h: 0.8, visible: true, locked: true },
    { id: 'albumList', label: '相册列表区', type: 'albumList', order: 3, w: 12, h: 4, visible: true, locked: true },
    { id: 'messageBoard', label: '留言板区域', type: 'messageBoard', order: 4, w: 12, h: 2, visible: false, locked: true }
  ],
  music: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'playerPanel', label: '音乐播放器面板', type: 'playerPanel', order: 2, w: 5, h: 4, visible: true, locked: true },
    { id: 'lyricsPlaylistPanel', label: '歌词 / 歌单面板', type: 'lyricsPlaylistPanel', order: 3, w: 7, h: 4, visible: true, locked: true },
    { id: 'messageBoard', label: '留言板', type: 'messageBoard', order: 4, w: 12, h: 2, visible: true, locked: true }
  ],
  projects: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'projectList', label: '项目列表区', type: 'projectList', order: 2, w: 12, h: 4, visible: true, locked: true }
  ],
  friends: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'friendList', label: '友链列表区', type: 'friendList', order: 2, w: 12, h: 4, visible: true, locked: true }
  ],
  about: [
    { id: 'pageTitle', label: '页面标题区', type: 'pageTitle', order: 1, w: 12, h: 1.4, visible: true, locked: true },
    { id: 'markdownContent', label: 'Markdown 内容区', type: 'markdownContent', order: 2, w: 12, h: 4, visible: true, locked: true }
  ]
}

const addableMap: Record<PageKey, AddableBlock[]> = {
  home: [
    { type: 'customText', label: '文本块', w: 12, h: 1, props: { text: '新的文本块' } },
    { type: 'customMarkdown', label: 'Markdown 块', w: 12, h: 1.5, props: { text: '### 新的 Markdown 块' } },
    { type: 'imageBlock', label: '图片块', w: 6, h: 2, props: { url: '', title: '图片块' } },
    { type: 'linkButton', label: '链接按钮块', w: 4, h: 1, props: { text: '访问链接', url: '/' } },
    { type: 'divider', label: '分隔区块', w: 12, h: 0.5, props: {} }
  ],
  posts: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '文章页自定义说明' } },
    { type: 'divider', label: '分隔区块', w: 12, h: 0.5, props: {} }
  ],
  photos: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '图片页自定义说明' } }
  ],
  music: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '音乐页自定义说明' } }
  ],
  projects: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '项目页自定义说明' } }
  ],
  friends: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '友链页自定义说明' } }
  ],
  about: [
    { type: 'customText', label: '自定义文本块', w: 12, h: 1, props: { text: '关于页自定义说明' } }
  ]
}

const sizeLimits = {
  w: { min: 1, max: 12, step: 0.1 },
  h: { min: 0.5, max: 8, step: 0.1 }
}

const currentPage = computed(() => pages.find((page) => page.key === pageKey.value) || pages[0])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const dirty = ref(false)
const configSource = ref('尚未加载')
const raw = ref<Record<string, any>>({})
const componentTheme = ref<Record<string, any>>({})
const settingsRaw = ref<Record<string, any>>({})
const themeDirty = ref(false)
const summary = ref('')
const aboutContent = ref('')
const addDialogOpen = ref(false)
const fieldDialogOpen = ref(false)
const selectedBlockId = ref('')

const pageText = reactive<Record<PageTextKey, { title: string; subtitle: string }>>({
  home: { ...defaultText.home },
  posts: { ...defaultText.posts },
  chatters: { ...defaultText.chatters },
  photos: { ...defaultText.photos },
  music: { ...defaultText.music },
  projects: { ...defaultText.projects },
  friends: { ...defaultText.friends },
  about: { ...defaultText.about }
})

const home = reactive({
  author: '',
  avatar: '',
  description: '',
  socialLinks: { github: '', email: '', qq: '', wechat: '' } as Record<string, string>
})

const pageLayouts = reactive<Record<PageKey, EditorBlock[]>>({
  home: [],
  posts: [],
  photos: [],
  music: [],
  projects: [],
  friends: [],
  about: []
})

const blocks = computed(() => pageLayouts[pageKey.value])
const sortedBlocks = computed(() => [...blocks.value].sort((a, b) => a.order - b.order))
const selectedBlock = computed(() => blocks.value.find((block) => block.id === selectedBlockId.value) || null)
const fieldEditLabel = computed(() => `编辑${currentPage.value.label}信息`)

function cloneBlock(block: EditorBlock): EditorBlock {
  return { ...block, props: { ...(block.props || {}) } }
}

function clampPrecision(value: unknown, min: number, max: number, fallback: number) {
  const next = Number(value)
  if (!Number.isFinite(next)) return fallback
  return Math.round(Math.min(max, Math.max(min, next)) * 10) / 10
}

function formatSize(value: number) {
  return clampPrecision(value, 0, 99, 0).toFixed(1)
}

function eventNumber(event: Event) {
  return Number((event.target as HTMLInputElement).value)
}

function savedComponentsFor(key: PageKey, data: Record<string, any>) {
  return data.pageLayouts?.[key]?.components || (key === 'home' ? data.homeLayout?.components || data.home?.components : {}) || {}
}

function hydrateLayouts(data: Record<string, any>) {
  for (const key of pageKeys) {
    const saved = savedComponentsFor(key, data)
    const defaults = defaultLayouts[key]
    const list: EditorBlock[] = defaults.map((block) => {
      const current = saved[block.id] || {}
      return {
        ...block,
        ...current,
        id: block.id,
        label: current.label || block.label,
        type: current.type || block.type,
        order: Math.round(clampPrecision(current.order, 1, 999, block.order)),
        w: clampPrecision(current.w, sizeLimits.w.min, sizeLimits.w.max, block.w),
        h: clampPrecision(current.h, sizeLimits.h.min, sizeLimits.h.max, block.h),
        visible: current.visible !== false,
        locked: current.locked !== false,
        props: { ...(block.props || {}), ...(current.props || {}) }
      }
    })
    for (const [id, current] of Object.entries(saved) as Array<[string, any]>) {
      if (list.some((item) => item.id === id)) continue
      list.push({
        id,
        label: current.label || id,
        type: current.type || 'customText',
        order: Math.round(clampPrecision(current.order, 1, 999, list.length + 1)),
        w: clampPrecision(current.w, sizeLimits.w.min, sizeLimits.w.max, 12),
        h: clampPrecision(current.h, sizeLimits.h.min, sizeLimits.h.max, 1),
        visible: current.visible !== false,
        locked: false,
        props: current.props || {}
      })
    }
    pageLayouts[key] = list.sort((a, b) => a.order - b.order)
  }
}

function hydrate(data: Record<string, any>) {
  const savedText = data.pageText || {}
  ;(Object.keys(defaultText) as PageTextKey[]).forEach((key) => {
    pageText[key].title = savedText[key]?.title || defaultText[key].title
    pageText[key].subtitle = savedText[key]?.subtitle || defaultText[key].subtitle
  })
  const profile = data.homeProfile || {}
  home.author = profile.author || ''
  home.avatar = profile.avatar || ''
  home.description = profile.description || ''
  home.socialLinks = { github: '', email: '', qq: '', wechat: '', ...(profile.socialLinks || {}) }
  hydrateLayouts(data)
}

async function loadSummary(key: PageKey) {
  try {
    if (key === 'posts') {
      const list = await adminApi.list('posts')
      summary.value = `真实文章 ${list.length} 篇，草稿 ${list.filter((item) => item.meta.draft).length} 篇。`
    } else if (key === 'photos') {
      const list = await adminApi.json<any[]>('/photos')
      summary.value = `真实相册 ${Array.isArray(list) ? list.length : 0} 组。`
    } else if (key === 'music') {
      const list = await adminApi.json<any[]>('/music')
      summary.value = `真实歌曲 ${Array.isArray(list) ? list.length : 0} 首。`
    } else if (key === 'projects') {
      const list = await adminApi.json<any[]>('/projects')
      summary.value = `真实项目 ${Array.isArray(list) ? list.length : 0} 个。`
    } else if (key === 'friends') {
      const list = await adminApi.json<any[]>('/friends')
      summary.value = `真实友链 ${Array.isArray(list) ? list.length : 0} 条。`
    } else if (key === 'about') {
      const data = await adminApi.json<{ content: string }>('/about')
      aboutContent.value = data.content || ''
      summary.value = `关于页 Markdown：${aboutContent.value.length} 个字符。`
    } else {
      summary.value = '首页读取页面配置中的名片资料和 8 个真实前台组件布局。'
    }
  } catch (exc) {
    summary.value = exc instanceof Error ? `真实数据摘要读取失败：${exc.message}` : '真实数据摘要读取失败。'
  }
}

async function load() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    raw.value = await adminApi.json<Record<string, any>>('/admin/pages/config')
    try {
      const settings = await adminApi.json<Record<string, any>>('/admin/settings')
      settingsRaw.value = settings
      componentTheme.value = settings.themeConfig?.componentTheme || {}
    } catch {
      settingsRaw.value = {}
      componentTheme.value = {}
    }
    hydrate(raw.value)
    configSource.value = '已加载后端配置'
    await loadSummary(pageKey.value)
    dirty.value = false
  } catch (exc) {
    configSource.value = '加载失败'
    error.value = exc instanceof Error ? exc.message : '页面配置加载失败'
  } finally {
    loading.value = false
  }
}

function serializeLayouts() {
  return Object.fromEntries(pageKeys.map((key) => [
    key,
    {
      layoutVersion: 1,
      components: Object.fromEntries(pageLayouts[key].map((block) => [
        block.id,
        {
          label: block.label,
          type: block.type,
          order: block.order,
          w: clampPrecision(block.w, sizeLimits.w.min, sizeLimits.w.max, block.w),
          h: clampPrecision(block.h, sizeLimits.h.min, sizeLimits.h.max, block.h),
          visible: block.visible !== false,
          locked: block.locked !== false,
          props: { ...(block.props || {}) }
        }
      ]))
    }
  ]))
}

function payload() {
  const pageLayoutsPayload = serializeLayouts()
  return {
    ...raw.value,
    homeProfile: {
      author: home.author,
      avatar: home.avatar,
      description: home.description,
      socialLinks: { ...home.socialLinks }
    },
    pageText: Object.fromEntries((Object.keys(pageText) as PageTextKey[]).map((key) => [key, { ...pageText[key] }])),
    pageLayouts: pageLayoutsPayload,
    homeLayout: pageLayoutsPayload.home,
    home: pageLayoutsPayload.home
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    if (themeDirty.value) {
      const settingsPayload = {
        ...settingsRaw.value,
        themeConfig: {
          ...(settingsRaw.value.themeConfig || {}),
          componentTheme: componentTheme.value
        }
      }
      await adminApi.putJson('/admin/settings', settingsPayload)
      settingsRaw.value = await adminApi.json<Record<string, any>>('/admin/settings')
      componentTheme.value = settingsRaw.value.themeConfig?.componentTheme || componentTheme.value
      themeDirty.value = false
    }
    await adminApi.putJson('/admin/pages/config', payload())
    if (pageKey.value === 'about') await adminApi.putJson('/about', { content: aboutContent.value })
    raw.value = await adminApi.json<Record<string, any>>('/admin/pages/config')
    hydrate(raw.value)
    configSource.value = '已加载后端配置'
    success.value = '页面配置已保存，刷新前台后生效。'
    dirty.value = false
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面配置保存失败'
  } finally {
    saving.value = false
  }
}

function normalizeOrders(list = blocks.value) {
  ;[...list].sort((a, b) => a.order - b.order).forEach((block, index) => { block.order = index + 1 })
}

function moveBlock(id: string, direction: -1 | 1) {
  const list = sortedBlocks.value
  const index = list.findIndex((item) => item.id === id)
  const target = index + direction
  if (index < 0 || target < 0 || target >= list.length) return
  const currentOrder = list[index].order
  list[index].order = list[target].order
  list[target].order = currentOrder
  normalizeOrders()
  dirty.value = true
}

function setBlockOrder(block: EditorBlock, value: number) {
  const target = Math.round(Math.min(blocks.value.length, Math.max(1, value || block.order)))
  const list = sortedBlocks.value.filter((item) => item.id !== block.id)
  list.splice(target - 1, 0, block)
  list.forEach((item, index) => { item.order = index + 1 })
  dirty.value = true
}

function setBlockSize(block: EditorBlock, key: 'w' | 'h', value: number) {
  const limit = sizeLimits[key]
  block[key] = clampPrecision(value, limit.min, limit.max, block[key])
  dirty.value = true
}

const componentThemeKeyMap: Record<string, string> = {
  profileCard: 'homeProfileCard',
  musicPlayer: 'homeMusicPlayer',
  lyrics: 'homeLyrics',
  latestPostsCarousel: 'homeLatestPostsCarousel',
  photoCarousel: 'homePhotoCarousel',
  updatesCarousel: 'homeUpdatesCarousel',
  themeToggle: 'homeThemeToggle',
  statusBar: 'homeStatusBar',
  playerPanel: 'musicPlayerPanel',
  lyricsPlaylistPanel: 'musicLyricsPanel',
  messageBoard: 'messageBoard',
  searchBox: 'searchInput',
  sectionSwitch: 'sectionSwitch',
  viewModeSwitch: 'viewModeSwitch',
  contentList: 'postCard',
  albumList: 'photoAlbumCard'
}

function componentThemeKey(block: EditorBlock) {
  return componentThemeKeyMap[block.id] || componentThemeKeyMap[block.type] || block.type || block.id
}

function ensureComponentTheme(block: EditorBlock) {
  const key = componentThemeKey(block)
  const current = componentTheme.value[key] || {}
  const next = {
    label: current.label || block.label,
    group: current.group || '页面编辑组件',
    day: { ...(current.day || {}) },
    night: { ...(current.night || {}) },
    opacity: current.opacity ?? 0.86,
    size: current.size || 'medium',
    fontFamily: current.fontFamily || '',
    fontSize: current.fontSize ?? 16,
    textColor: current.textColor || current.day?.text || '',
    textAlign: current.textAlign || 'left',
    fontWeight: current.fontWeight || 'normal',
    fontStyle: current.fontStyle || 'normal'
  }
  componentTheme.value[key] = next
  return next
}

function setThemeField(block: EditorBlock, field: string, value: string | number) {
  const item = ensureComponentTheme(block) as Record<string, string | number | Record<string, string>>
  item[field] = value
  themeDirty.value = true
  dirty.value = true
}

function setThemeModeField(block: EditorBlock, mode: 'day' | 'night', field: 'bg' | 'text' | 'accent' | 'border', value: string) {
  const item = ensureComponentTheme(block) as Record<string, any>
  item[mode] = { ...(item[mode] || {}), [field]: value }
  themeDirty.value = true
  dirty.value = true
}

function colorValue(value: unknown) {
  const text = String(value || '').trim()
  return /^#[0-9a-fA-F]{6}$/.test(text) ? text : '#111827'
}

function restoreDefaultLayout() {
  pageLayouts[pageKey.value] = defaultLayouts[pageKey.value].map(cloneBlock)
  dirty.value = true
}

function blockStyle(block: EditorBlock) {
  const span = Math.max(1, Math.min(12, Math.round(clampPrecision(block.w, sizeLimits.w.min, sizeLimits.w.max, 12))))
  const height = clampPrecision(block.h, sizeLimits.h.min, sizeLimits.h.max, 1)
  return {
    order: block.order,
    gridColumn: `span ${span} / span ${span}`,
    minHeight: `${Math.max(4, height * 4.2)}rem`
  }
}

function themeInfo(block: EditorBlock) {
  const item = componentTheme.value[componentThemeKey(block)] || componentTheme.value[block.type] || componentTheme.value[block.id] || {}
  return {
    opacity: item.opacity ?? '默认',
    dayBg: item.day?.bg || '默认',
    nightBg: item.night?.bg || '默认',
    size: item.size || '默认'
  }
}

function addBlock(option: AddableBlock) {
  const id = option.unique ? option.type : `${option.type}-${Date.now()}`
  if (option.unique && blocks.value.some((block) => block.type === option.type)) {
    error.value = '该组件类型只允许添加一个。'
    return
  }
  blocks.value.push({
    id,
    label: option.label,
    type: option.type,
    order: blocks.value.length + 1,
    w: option.w,
    h: option.h,
    visible: true,
    locked: false,
    props: { ...(option.props || {}) }
  })
  normalizeOrders()
  addDialogOpen.value = false
  dirty.value = true
}

function removeBlock(block: EditorBlock) {
  if (block.locked) {
    if (confirm(`核心组件「${block.label}」不会被删除，只会隐藏。确定隐藏吗？`)) {
      block.visible = false
      dirty.value = true
    }
    return
  }
  if (!confirm(`确定删除组件「${block.label}」吗？这不会删除实际内容数据。`)) return
  pageLayouts[pageKey.value] = blocks.value.filter((item) => item.id !== block.id)
  normalizeOrders()
  dirty.value = true
}

function openContentEntry() {
  router.push(currentPage.value.actionPath)
}

watch(pageKey, async () => {
  selectedBlockId.value = ''
  await loadSummary(pageKey.value)
}, { immediate: false })

load()
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-editor-sticky">
      <div class="relative z-[1] flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.28em]">PAGE EDITOR</p>
          <h1 class="mt-2 text-4xl font-black">页面编辑</h1>
          <p class="mt-2 max-w-3xl text-sm text-slate-600">读取真实页面配置；每个页面都支持组件顺序、宽高、显示状态和基础文案编辑。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="admin-btn admin-btn-ghost" @click="fieldDialogOpen = true">{{ fieldEditLabel }}</button>
          <button type="button" class="admin-btn admin-btn-ghost" @click="addDialogOpen = true">添加组件</button>
          <button type="button" class="admin-btn admin-btn-ghost" @click="restoreDefaultLayout">恢复当前页默认布局</button>
          <button type="button" class="admin-btn admin-btn-primary" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
        </div>
      </div>
    </GlassCard>

    <GlassCard class="hidden">
      <div class="relative z-[1] grid gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black">{{ currentPage.label }} / 真实字段</h2>
            <p class="mt-1 text-sm text-slate-600">前台路径：{{ currentPage.path }}。{{ summary }}</p>
          </div>
          <p v-if="dirty" class="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-sm text-amber-700">有未保存修改</p>
        </div>

        <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{{ error }}</p>
        <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{{ success }}</p>
        <p class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">配置来源：{{ configSource }}</p>
        <div v-if="loading" class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-600">正在读取真实页面配置...</div>

        <div v-else class="grid gap-4">
          <div class="grid gap-3 md:grid-cols-2">
            <label class="field">页面标题<input v-model="pageText[pageKey].title" class="admin-input" @input="dirty = true" /></label>
            <label class="field">页面副标题<input v-model="pageText[pageKey].subtitle" class="admin-input" @input="dirty = true" /></label>
          </div>

          <div v-if="pageKey === 'posts'" class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-2">
            <label class="field">杂谈板块标题<input v-model="pageText.chatters.title" class="admin-input" @input="dirty = true" /></label>
            <label class="field">杂谈板块副标题<input v-model="pageText.chatters.subtitle" class="admin-input" @input="dirty = true" /></label>
          </div>

          <div v-if="pageKey === 'home'" class="grid gap-3 md:grid-cols-2">
            <label class="field">首页作者<input v-model="home.author" class="admin-input" @input="dirty = true" /></label>
            <label class="field">头像 URL<input v-model="home.avatar" class="admin-input" @input="dirty = true" /></label>
            <label class="field md:col-span-2">首页简介<textarea v-model="home.description" rows="3" class="admin-input" @input="dirty = true"></textarea></label>
            <label v-for="(_, key) in home.socialLinks" :key="key" class="field">社交链接 {{ key }}<input v-model="home.socialLinks[key]" class="admin-input" @input="dirty = true" /></label>
          </div>

          <label v-if="pageKey === 'about'" class="field">关于页 Markdown
            <textarea v-model="aboutContent" rows="12" class="admin-input font-mono" @input="dirty = true"></textarea>
          </label>
        </div>
      </div>
    </GlassCard>

    <div v-if="fieldDialogOpen" class="fixed inset-0 z-50 grid place-items-center bg-black/35 p-4" @click="fieldDialogOpen = false">
      <div class="max-h-[86vh] w-full max-w-4xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl" @click.stop>
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-200 p-5">
          <div>
            <p class="text-xs font-bold uppercase tracking-[.2em] text-slate-500">PAGE FIELDS</p>
            <h2 class="mt-1 text-2xl font-black text-slate-950">{{ fieldEditLabel }}</h2>
            <p class="mt-1 text-sm text-slate-600">{{ currentPage.path }} · {{ summary }}</p>
          </div>
          <button type="button" class="admin-btn admin-btn-ghost" @click="fieldDialogOpen = false">关闭</button>
        </div>
        <div class="max-h-[calc(86vh-9rem)] overflow-y-auto p-5">
          <p v-if="dirty" class="mb-4 rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-700">有未保存修改，请保存页面配置后刷新前台验证。</p>
          <p v-if="error" class="mb-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{{ error }}</p>
          <p v-if="success" class="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{{ success }}</p>

          <div class="grid gap-4">
            <div class="grid gap-3 md:grid-cols-2">
              <label class="field">页面标题<input v-model="pageText[pageKey].title" class="admin-input" @input="dirty = true" /></label>
              <label class="field">页面副标题<input v-model="pageText[pageKey].subtitle" class="admin-input" @input="dirty = true" /></label>
            </div>

            <div v-if="pageKey === 'posts'" class="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-2">
              <label class="field">杂谈板块标题<input v-model="pageText.chatters.title" class="admin-input" @input="dirty = true" /></label>
              <label class="field">杂谈板块副标题<input v-model="pageText.chatters.subtitle" class="admin-input" @input="dirty = true" /></label>
            </div>

            <div v-if="pageKey === 'home'" class="grid gap-3 md:grid-cols-2">
              <label class="field">首页作者<input v-model="home.author" class="admin-input" @input="dirty = true" /></label>
              <label class="field">头像 URL<input v-model="home.avatar" class="admin-input" @input="dirty = true" /></label>
              <label class="field md:col-span-2">首页简介<textarea v-model="home.description" rows="3" class="admin-input" @input="dirty = true"></textarea></label>
              <label v-for="(_, key) in home.socialLinks" :key="key" class="field">社交链接 {{ key }}<input v-model="home.socialLinks[key]" class="admin-input" @input="dirty = true" /></label>
            </div>

            <label v-if="pageKey === 'about'" class="field">关于页 Markdown
              <textarea v-model="aboutContent" rows="12" class="admin-input font-mono" @input="dirty = true"></textarea>
            </label>
          </div>
        </div>
        <div class="flex flex-wrap justify-end gap-2 border-t border-slate-200 p-5">
          <button type="button" class="admin-btn admin-btn-ghost" @click="fieldDialogOpen = false">关闭</button>
          <button type="button" class="admin-btn admin-btn-primary" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
        </div>
      </div>
    </div>

    <GlassCard>
      <div class="relative z-[1] grid gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black">组件编辑</h2>
            <p class="mt-1 text-sm text-slate-600">使用上移/下移或 order 数值调整顺序；宽高支持滑动条和精确数值输入。详情默认收起。</p>
          </div>
          <button type="button" class="admin-btn admin-btn-ghost" @click="addDialogOpen = true">添加组件</button>
        </div>

        <div class="page-editor-grid">
          <article
            v-for="block in sortedBlocks"
            :key="block.id"
            class="page-editor-block"
            :class="{ 'opacity-55': block.visible === false }"
            :style="blockStyle(block)"
            role="button"
            tabindex="0"
            @click="selectedBlockId = block.id"
            @keydown.enter.prevent="selectedBlockId = block.id"
          >
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div class="min-w-0">
                <b class="block truncate">{{ block.label }}</b>
                <p class="mt-1 truncate font-mono text-xs text-slate-500">{{ block.id }}</p>
              </div>
              <span class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">order {{ block.order }}</span>
            </div>

            <p class="mt-3 text-xs text-slate-500">w {{ formatSize(block.w) }} / h {{ formatSize(block.h) }} / 透明度 {{ themeInfo(block).opacity }} / {{ block.visible ? '显示' : '隐藏' }}</p>

            <div class="mt-3 grid gap-2 page-size-controls">
              <div class="page-size-row">
                <span>宽度</span>
                <input type="range" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="block.w" @input="setBlockSize(block, 'w', eventNumber($event))" />
                <input class="admin-input page-number" type="number" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="block.w" @input="setBlockSize(block, 'w', eventNumber($event))" />
                <button v-for="size in [4, 6, 8, 12]" :key="`w-${size}`" type="button" class="admin-btn admin-btn-ghost page-preset" @click="setBlockSize(block, 'w', size)">{{ size }}</button>
              </div>
              <div class="page-size-row">
                <span>高度</span>
                <input type="range" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="block.h" @input="setBlockSize(block, 'h', eventNumber($event))" />
                <input class="admin-input page-number" type="number" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="block.h" @input="setBlockSize(block, 'h', eventNumber($event))" />
                <button v-for="size in [1, 2, 3, 4]" :key="`h-${size}`" type="button" class="admin-btn admin-btn-ghost page-preset" @click="setBlockSize(block, 'h', size)">{{ size }}</button>
              </div>
            </div>

            <div class="mt-3 flex flex-wrap gap-2 page-inline-actions">
              <button type="button" class="admin-btn admin-btn-ghost page-preset" @click="moveBlock(block.id, -1)">上移</button>
              <button type="button" class="admin-btn admin-btn-ghost page-preset" @click="moveBlock(block.id, 1)">下移</button>
              <input class="admin-input page-number" type="number" min="1" :max="blocks.length" :value="block.order" @change="setBlockOrder(block, eventNumber($event))" />
              <button type="button" class="admin-btn admin-btn-ghost page-preset" @click="block.visible = !block.visible; dirty = true">{{ block.visible ? '隐藏' : '显示' }}</button>
              <button type="button" class="admin-btn admin-btn-danger page-preset" @click="removeBlock(block)">{{ block.locked ? '隐藏' : '删除' }}</button>
            </div>

            <details class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
              <summary class="cursor-pointer font-bold text-slate-800">详情</summary>
              <div class="mt-2 grid gap-1">
                <p>类型：{{ block.type }}</p>
                <p>透明度：{{ themeInfo(block).opacity }}</p>
                <p>日间背景：<span class="inline-block h-3 w-8 rounded border align-middle" :style="{ background: String(themeInfo(block).dayBg) }"></span> {{ themeInfo(block).dayBg }}</p>
                <p>夜间背景：<span class="inline-block h-3 w-8 rounded border align-middle" :style="{ background: String(themeInfo(block).nightBg) }"></span> {{ themeInfo(block).nightBg }}</p>
                <p>大小档位：{{ themeInfo(block).size }}</p>
                <button type="button" class="admin-btn admin-btn-ghost mt-2 w-fit page-preset" @click="router.push('/settings?tab=theme')">打开组件主题设置</button>
              </div>
            </details>
          </article>
        </div>

        <details class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <summary class="cursor-pointer text-sm font-bold text-slate-700">高级：当前页 layout JSON</summary>
          <pre class="mt-4 max-h-80 overflow-auto rounded-xl bg-white p-4 text-xs text-slate-700">{{ JSON.stringify(serializeLayouts()[pageKey], null, 2) }}</pre>
        </details>
      </div>
    </GlassCard>

    <div v-if="selectedBlock" class="fixed inset-0 z-[55] grid place-items-center bg-black/35 p-4" @click="selectedBlockId = ''">
      <div class="flex max-h-[85vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl" @click.stop>
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-200 pb-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-[.2em] text-slate-500">COMPONENT SETTINGS</p>
            <h2 class="mt-1 text-2xl font-black text-slate-950">{{ selectedBlock.label }}</h2>
            <p class="mt-1 font-mono text-xs text-slate-500">{{ selectedBlock.id }} · {{ componentThemeKey(selectedBlock) }} · order {{ selectedBlock.order }}</p>
          </div>
          <button type="button" class="admin-btn admin-btn-ghost" @click="selectedBlockId = ''">关闭</button>
        </div>

        <div class="grid gap-4 overflow-y-auto p-5">
          <details open class="component-setting-section">
            <summary>布局设置</summary>
            <div class="mt-4 grid gap-4">
              <div class="page-size-row-modal">
                <span>宽度</span>
                <input type="range" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="selectedBlock.w" @input="setBlockSize(selectedBlock, 'w', eventNumber($event))" />
                <input class="admin-input page-number" type="number" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="selectedBlock.w" @input="setBlockSize(selectedBlock, 'w', eventNumber($event))" />
                <button v-for="size in [4, 6, 8, 12]" :key="`modal-w-${size}`" type="button" class="admin-btn admin-btn-ghost page-preset" @click="setBlockSize(selectedBlock, 'w', size)">{{ size }}</button>
              </div>
              <div class="page-size-row-modal">
                <span>高度</span>
                <input type="range" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="selectedBlock.h" @input="setBlockSize(selectedBlock, 'h', eventNumber($event))" />
                <input class="admin-input page-number" type="number" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="selectedBlock.h" @input="setBlockSize(selectedBlock, 'h', eventNumber($event))" />
                <button v-for="size in [1, 2, 3, 4]" :key="`modal-h-${size}`" type="button" class="admin-btn admin-btn-ghost page-preset" @click="setBlockSize(selectedBlock, 'h', size)">{{ size }}</button>
              </div>

              <div class="grid gap-3 sm:grid-cols-[auto_auto_6rem_1fr]">
                <button type="button" class="admin-btn admin-btn-ghost" @click="moveBlock(selectedBlock.id, -1)">上移</button>
                <button type="button" class="admin-btn admin-btn-ghost" @click="moveBlock(selectedBlock.id, 1)">下移</button>
                <input class="admin-input page-number" type="number" min="1" :max="blocks.length" :value="selectedBlock.order" @change="setBlockOrder(selectedBlock, eventNumber($event))" />
                <div class="flex flex-wrap gap-2 sm:justify-end">
                  <button type="button" class="admin-btn admin-btn-ghost" @click="selectedBlock.visible = !selectedBlock.visible; dirty = true">{{ selectedBlock.visible ? '隐藏' : '显示' }}</button>
                  <button type="button" class="admin-btn admin-btn-danger" @click="removeBlock(selectedBlock); selectedBlockId = ''">{{ selectedBlock.locked ? '隐藏' : '删除' }}</button>
                </div>
              </div>
            </div>
          </details>

          <details open class="component-setting-section">
            <summary>外观设置</summary>
            <div class="mt-4 grid gap-4">
              <div class="grid gap-3 md:grid-cols-2">
                <label class="field">日间背景色
                  <div class="grid grid-cols-[3rem_minmax(0,1fr)] gap-2">
                    <input class="h-10 w-full rounded border border-slate-300" type="color" :value="colorValue(ensureComponentTheme(selectedBlock).day?.bg)" @input="setThemeModeField(selectedBlock, 'day', 'bg', ($event.target as HTMLInputElement).value)" />
                    <input class="admin-input" :value="ensureComponentTheme(selectedBlock).day?.bg" placeholder="rgba(...) 或 #ffffff" @input="setThemeModeField(selectedBlock, 'day', 'bg', ($event.target as HTMLInputElement).value)" />
                  </div>
                </label>
                <label class="field">夜间背景色
                  <div class="grid grid-cols-[3rem_minmax(0,1fr)] gap-2">
                    <input class="h-10 w-full rounded border border-slate-300" type="color" :value="colorValue(ensureComponentTheme(selectedBlock).night?.bg)" @input="setThemeModeField(selectedBlock, 'night', 'bg', ($event.target as HTMLInputElement).value)" />
                    <input class="admin-input" :value="ensureComponentTheme(selectedBlock).night?.bg" placeholder="rgba(...) 或 #0f172a" @input="setThemeModeField(selectedBlock, 'night', 'bg', ($event.target as HTMLInputElement).value)" />
                  </div>
                </label>
                <label class="field">日间文字色
                  <div class="grid grid-cols-[3rem_minmax(0,1fr)] gap-2">
                    <input class="h-10 w-full rounded border border-slate-300" type="color" :value="colorValue(ensureComponentTheme(selectedBlock).day?.text)" @input="setThemeModeField(selectedBlock, 'day', 'text', ($event.target as HTMLInputElement).value)" />
                    <input class="admin-input" :value="ensureComponentTheme(selectedBlock).day?.text" placeholder="#111827" @input="setThemeModeField(selectedBlock, 'day', 'text', ($event.target as HTMLInputElement).value)" />
                  </div>
                </label>
                <label class="field">夜间文字色
                  <div class="grid grid-cols-[3rem_minmax(0,1fr)] gap-2">
                    <input class="h-10 w-full rounded border border-slate-300" type="color" :value="colorValue(ensureComponentTheme(selectedBlock).night?.text)" @input="setThemeModeField(selectedBlock, 'night', 'text', ($event.target as HTMLInputElement).value)" />
                    <input class="admin-input" :value="ensureComponentTheme(selectedBlock).night?.text" placeholder="#f8fafc" @input="setThemeModeField(selectedBlock, 'night', 'text', ($event.target as HTMLInputElement).value)" />
                  </div>
                </label>
              </div>
              <label class="field">透明度 0-1
                <div class="grid grid-cols-[minmax(0,1fr)_5rem] gap-2">
                  <input type="range" min="0" max="1" step="0.01" :value="ensureComponentTheme(selectedBlock).opacity" @input="setThemeField(selectedBlock, 'opacity', eventNumber($event))" />
                  <input class="admin-input page-number" type="number" min="0" max="1" step="0.01" :value="ensureComponentTheme(selectedBlock).opacity" @input="setThemeField(selectedBlock, 'opacity', eventNumber($event))" />
                </div>
              </label>
              <label class="field">大小档位
                <select class="admin-input" :value="ensureComponentTheme(selectedBlock).size" @change="setThemeField(selectedBlock, 'size', ($event.target as HTMLSelectElement).value)">
                  <option value="small">小</option>
                  <option value="medium">中</option>
                  <option value="large">大</option>
                </select>
              </label>
            </div>
          </details>

          <details open class="component-setting-section">
            <summary>字体设置</summary>
            <div class="mt-4 grid gap-4">
              <label class="field">字体族
                <input class="admin-input" :value="ensureComponentTheme(selectedBlock).fontFamily" placeholder="留空使用默认字体" @input="setThemeField(selectedBlock, 'fontFamily', ($event.target as HTMLInputElement).value)" />
              </label>
              <label class="field">字体大小(px)
                <div class="grid grid-cols-[minmax(0,1fr)_5rem] gap-2">
                  <input type="range" min="10" max="42" step="1" :value="ensureComponentTheme(selectedBlock).fontSize" @input="setThemeField(selectedBlock, 'fontSize', eventNumber($event))" />
                  <input class="admin-input page-number" type="number" min="10" max="42" step="1" :value="ensureComponentTheme(selectedBlock).fontSize" @input="setThemeField(selectedBlock, 'fontSize', eventNumber($event))" />
                </div>
              </label>
              <label class="field">字体颜色
                <div class="grid grid-cols-[3rem_minmax(0,1fr)] gap-2">
                  <input class="h-10 w-full rounded border border-slate-300" type="color" :value="colorValue(ensureComponentTheme(selectedBlock).textColor)" @input="setThemeField(selectedBlock, 'textColor', ($event.target as HTMLInputElement).value)" />
                  <input class="admin-input" :value="ensureComponentTheme(selectedBlock).textColor" placeholder="#111827" @input="setThemeField(selectedBlock, 'textColor', ($event.target as HTMLInputElement).value)" />
                </div>
              </label>
              <label class="field">文本对齐
                <select class="admin-input" :value="ensureComponentTheme(selectedBlock).textAlign" @change="setThemeField(selectedBlock, 'textAlign', ($event.target as HTMLSelectElement).value)">
                  <option value="left">靠左</option>
                  <option value="center">居中</option>
                  <option value="right">靠右</option>
                </select>
              </label>
              <div class="grid gap-2 sm:grid-cols-2">
                <label class="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-bold text-slate-700">
                  <input type="checkbox" :checked="ensureComponentTheme(selectedBlock).fontWeight === '700' || ensureComponentTheme(selectedBlock).fontWeight === 'bold'" @change="setThemeField(selectedBlock, 'fontWeight', ($event.target as HTMLInputElement).checked ? '700' : 'normal')" />
                  加粗
                </label>
                <label class="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-bold text-slate-700">
                  <input type="checkbox" :checked="ensureComponentTheme(selectedBlock).fontStyle === 'italic'" @change="setThemeField(selectedBlock, 'fontStyle', ($event.target as HTMLInputElement).checked ? 'italic' : 'normal')" />
                  斜体
                </label>
              </div>
            </div>
          </details>

          <details class="component-setting-section">
            <summary>显示设置</summary>
            <div class="mt-4 grid gap-3">
              <label class="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-bold text-slate-700">
                <span>当前组件在前台显示</span>
                <input type="checkbox" :checked="selectedBlock.visible !== false" @change="selectedBlock.visible = ($event.target as HTMLInputElement).checked; dirty = true" />
              </label>
              <button type="button" class="admin-btn admin-btn-danger w-fit" @click="removeBlock(selectedBlock); selectedBlockId = ''">{{ selectedBlock.locked ? '隐藏核心组件' : '删除组件引用' }}</button>
              <p class="text-xs text-slate-500">删除或隐藏只影响页面布局引用，不会删除文章、图片、音乐等真实内容数据。</p>
            </div>
          </details>

          <details class="component-setting-section">
            <summary>状态摘要</summary>
            <div class="mt-4 grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
              <p>order：{{ selectedBlock.order }}</p>
              <p>w/h：{{ formatSize(selectedBlock.w) }} / {{ formatSize(selectedBlock.h) }}</p>
              <p>透明度：{{ themeInfo(selectedBlock).opacity }}</p>
              <p>大小档位：{{ themeInfo(selectedBlock).size }}</p>
              <p>日间背景：<span class="inline-block h-3 w-8 rounded border align-middle" :style="{ background: String(themeInfo(selectedBlock).dayBg) }"></span> {{ themeInfo(selectedBlock).dayBg }}</p>
              <p>夜间背景：<span class="inline-block h-3 w-8 rounded border align-middle" :style="{ background: String(themeInfo(selectedBlock).nightBg) }"></span> {{ themeInfo(selectedBlock).nightBg }}</p>
            </div>
          </details>
        </div>
        <div class="flex flex-wrap justify-between gap-2 border-t border-slate-200 bg-white p-5">
          <button type="button" class="admin-btn admin-btn-ghost" @click="selectedBlockId = ''">关闭</button>
          <button type="button" class="admin-btn admin-btn-primary" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
        </div>
      </div>
    </div>

    <div v-if="addDialogOpen" class="fixed inset-0 z-50 grid place-items-center bg-black/35 p-4" @click="addDialogOpen = false">
      <div class="w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-5 shadow-xl" @click.stop>
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-xl font-black">添加组件</h2>
          <button type="button" class="admin-btn admin-btn-ghost" @click="addDialogOpen = false">关闭</button>
        </div>
        <div class="mt-4 grid gap-3 sm:grid-cols-2">
          <button
            v-for="option in addableMap[pageKey]"
            :key="option.type + option.label"
            type="button"
            class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:bg-slate-100"
            @click="addBlock(option)"
          >
            <b>{{ option.label }}</b>
            <p class="mt-1 text-xs text-slate-500">默认宽 {{ option.w }}，高 {{ option.h }}</p>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.page-editor-sticky {
  position: sticky;
  top: .75rem;
  z-index: 30;
}
.page-editor-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: .75rem;
  max-width: 100%;
  overflow: visible;
  align-items: stretch;
}
.page-editor-block {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  border-radius: .8rem;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: .75rem;
  color: #111827;
  overflow: visible;
  cursor: pointer;
  transition: border-color .2s ease, background-color .2s ease;
}
.page-editor-block:hover {
  border-color: #111827;
  background: #f9fafb;
}
.page-editor-block:focus-visible {
  outline: 2px solid #111827;
  outline-offset: 2px;
}
.page-size-controls {
  display: none;
}
.page-inline-actions,
.page-editor-block > details {
  display: none;
}
.page-size-row {
  display: grid;
  grid-template-columns: 2.75rem minmax(0, 1fr) 3.9rem;
  align-items: center;
  gap: .45rem;
  font-size: .78rem;
  color: #4b5563;
  max-width: 100%;
}
.page-size-row-modal {
  display: grid;
  grid-template-columns: 2.75rem minmax(0, 1fr) 4.5rem repeat(4, auto);
  align-items: center;
  gap: .55rem;
  font-size: .85rem;
  color: #374151;
  max-width: 100%;
}
.page-size-row-modal input[type="range"] {
  min-width: 0;
  width: 100%;
  accent-color: #111827;
}
.page-size-row input[type="range"] {
  min-width: 0;
  width: 100%;
  accent-color: #111827;
}
.page-number {
  min-height: 2rem !important;
  padding: .3rem .45rem !important;
  font-size: .75rem !important;
  width: 100%;
  min-width: 0;
}
.page-preset {
  min-height: 2rem !important;
  padding: .3rem .55rem !important;
  font-size: .72rem !important;
}
.component-setting-section {
  border: 1px solid #e5e7eb;
  border-radius: .9rem;
  background: #f9fafb;
  padding: .9rem;
}
.component-setting-section > summary {
  cursor: pointer;
  font-size: .92rem;
  font-weight: 800;
  color: #111827;
}
@media (max-width: 1000px) {
  .page-editor-block {
    grid-column: 1 / -1 !important;
  }
  .page-size-row {
    grid-template-columns: 2.75rem minmax(0, 1fr) 3.9rem;
  }
  .page-size-row-modal {
    grid-template-columns: 2.75rem minmax(0, 1fr) 4.5rem;
  }
}
</style>
