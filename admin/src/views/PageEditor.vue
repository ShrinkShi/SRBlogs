<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'

type PageKey = 'home' | 'posts' | 'photos' | 'music' | 'projects' | 'friends' | 'about'
type PageTextKey = PageKey | 'chatters'
type HomeComponentId =
  | 'profileCard'
  | 'musicPlayer'
  | 'lyrics'
  | 'latestPostsCarousel'
  | 'photoCarousel'
  | 'updatesCarousel'
  | 'themeToggle'
  | 'statusBar'
type HomeBlock = { id: HomeComponentId; label: string; order: number; w: number; h: number; visible: boolean }

const route = useRoute()
const router = useRouter()

const pageKey = computed<PageKey>(() => {
  const key = String(route.params.page || 'home')
  return ['home', 'posts', 'photos', 'music', 'projects', 'friends', 'about'].includes(key) ? key as PageKey : 'home'
})

const pages: Array<{ key: PageKey; label: string; path: string; action: string; actionPath: string }> = [
  { key: 'home', label: '首页', path: '/', action: '编辑首页名片和布局', actionPath: '/pages/home' },
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

const defaultHomeBlocks: HomeBlock[] = [
  { id: 'profileCard', label: '名片', order: 1, w: 6, h: 2, visible: true },
  { id: 'musicPlayer', label: '音乐播放器', order: 2, w: 6, h: 2, visible: true },
  { id: 'lyrics', label: '歌词区', order: 3, w: 12, h: 1, visible: true },
  { id: 'latestPostsCarousel', label: '最新文章轮播', order: 4, w: 4, h: 3, visible: true },
  { id: 'photoCarousel', label: '图片轮播', order: 5, w: 8, h: 2, visible: true },
  { id: 'updatesCarousel', label: '更新内容轮播', order: 6, w: 8, h: 2, visible: true },
  { id: 'themeToggle', label: '昼夜切换卡片', order: 7, w: 4, h: 2, visible: true },
  { id: 'statusBar', label: '底部状态区', order: 8, w: 12, h: 1, visible: true }
]

const sizeLimits = {
  w: { min: 1, max: 12, step: 0.1 },
  h: { min: 0.5, max: 6, step: 0.1 }
}

const homeThemeKey: Record<HomeComponentId, string> = {
  profileCard: 'homeProfileCard',
  musicPlayer: 'homeMusicPlayer',
  lyrics: 'homeLyrics',
  latestPostsCarousel: 'homeLatestPostsCarousel',
  photoCarousel: 'homePhotoCarousel',
  updatesCarousel: 'homeUpdatesCarousel',
  themeToggle: 'homeThemeToggle',
  statusBar: 'homeStatusBar'
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
const summary = ref('')
const aboutContent = ref('')
const draggingId = ref<HomeComponentId | null>(null)

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

const blocks = ref<HomeBlock[]>(defaultHomeBlocks.map((block) => ({ ...block })))
const sortedBlocks = computed(() => [...blocks.value].sort((a, b) => a.order - b.order))

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

function themeInfo(id: HomeComponentId) {
  const item = componentTheme.value[homeThemeKey[id]] || {}
  return {
    opacity: item.opacity ?? '默认',
    dayBg: item.day?.bg || '默认',
    nightBg: item.night?.bg || '默认',
    size: item.size || '默认'
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
  const components = data.homeLayout?.components || data.home?.components || {}
  blocks.value = defaultHomeBlocks.map((block) => {
    const saved = components[block.id] || {}
    return {
      ...block,
      ...saved,
      order: Number(saved.order || block.order),
      w: clampPrecision(saved.w, sizeLimits.w.min, sizeLimits.w.max, block.w),
      h: clampPrecision(saved.h, sizeLimits.h.min, sizeLimits.h.max, block.h),
      visible: saved.visible !== false
    }
  })
}

async function loadSummary(key: PageKey) {
  try {
    if (key === 'posts') {
      const list = await adminApi.list('posts')
      summary.value = `真实文章数据：${list.length} 篇，其中草稿 ${list.filter((item) => item.meta.draft).length} 篇。`
    } else if (key === 'photos') {
      const list = await adminApi.json<any[]>('/photos')
      summary.value = `真实相册数据：${Array.isArray(list) ? list.length : 0} 组。`
    } else if (key === 'music') {
      const list = await adminApi.json<any[]>('/music')
      summary.value = `真实音乐数据：${Array.isArray(list) ? list.length : 0} 首。`
    } else if (key === 'projects') {
      const list = await adminApi.json<any[]>('/projects')
      summary.value = `真实项目数据：${Array.isArray(list) ? list.length : 0} 个。`
    } else if (key === 'friends') {
      const list = await adminApi.json<any[]>('/friends')
      summary.value = `真实友链数据：${Array.isArray(list) ? list.length : 0} 条。`
    } else if (key === 'about') {
      const data = await adminApi.json<{ content: string }>('/about')
      aboutContent.value = data.content || ''
      summary.value = `关于页 Markdown：${aboutContent.value.length} 个字符。`
    } else {
      summary.value = '首页读取页面配置中的名片资料与 8 个真实前台组件布局。'
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
      componentTheme.value = settings.themeConfig?.componentTheme || {}
    } catch {
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

function payload() {
  return {
    ...raw.value,
    homeProfile: {
      author: home.author,
      avatar: home.avatar,
      description: home.description,
      socialLinks: { ...home.socialLinks }
    },
    pageText: Object.fromEntries((Object.keys(pageText) as PageTextKey[]).map((key) => [key, { ...pageText[key] }])),
    homeLayout: {
      layoutVersion: 1,
      components: Object.fromEntries(blocks.value.map((block) => [
        block.id,
        {
          order: block.order,
          w: clampPrecision(block.w, sizeLimits.w.min, sizeLimits.w.max, block.w),
          h: clampPrecision(block.h, sizeLimits.h.min, sizeLimits.h.max, block.h),
          visible: block.visible !== false
        }
      ]))
    }
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
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

function normalizeOrders() {
  sortedBlocks.value.forEach((block, index) => { block.order = index + 1 })
}

function moveBlock(id: HomeComponentId, direction: -1 | 1) {
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

function setBlockOrder(block: HomeBlock, value: number) {
  const target = Math.round(Math.min(blocks.value.length, Math.max(1, value || block.order)))
  const list = sortedBlocks.value.filter((item) => item.id !== block.id)
  list.splice(target - 1, 0, block)
  list.forEach((item, index) => { item.order = index + 1 })
  dirty.value = true
}

function setBlockSize(block: HomeBlock, key: 'w' | 'h', value: number) {
  const limit = sizeLimits[key]
  block[key] = clampPrecision(value, limit.min, limit.max, block[key])
  dirty.value = true
}

function onDragStart(id: HomeComponentId) {
  draggingId.value = id
}

function onDrop(targetId: HomeComponentId) {
  if (!draggingId.value || draggingId.value === targetId) return
  const list = sortedBlocks.value
  const from = list.findIndex((item) => item.id === draggingId.value)
  const to = list.findIndex((item) => item.id === targetId)
  if (from < 0 || to < 0) return
  const [item] = list.splice(from, 1)
  list.splice(to, 0, item)
  list.forEach((block, index) => { block.order = index + 1 })
  draggingId.value = null
  dirty.value = true
}

function restoreDefaultLayout() {
  blocks.value = defaultHomeBlocks.map((block) => ({ ...block }))
  dirty.value = true
}

function blockStyle(block: HomeBlock) {
  const span = Math.max(10, Math.min(120, Math.round(clampPrecision(block.w, sizeLimits.w.min, sizeLimits.w.max, 12) * 10)))
  const height = clampPrecision(block.h, sizeLimits.h.min, sizeLimits.h.max, 1)
  return {
    order: block.order,
    gridColumn: `span ${span} / span ${span}`,
    minHeight: `${Math.max(4.5, height * 5.6)}rem`
  }
}

function openContentEntry() {
  router.push(currentPage.value.actionPath)
}

watch(pageKey, load, { immediate: true })
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1] flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">PAGE EDITOR</p>
          <h1 class="mt-2 text-4xl font-black text-white">页面编辑</h1>
          <p class="mt-2 max-w-3xl text-white/58">读取真实前台配置。首页布局保存到页面配置，前台通过 `/api/pages/config` 读取并应用。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="admin-btn admin-btn-ghost" @click="openContentEntry">{{ currentPage.action }}</button>
          <button type="button" class="admin-btn admin-btn-primary" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
        </div>
      </div>
    </GlassCard>

    <GlassCard>
      <div class="relative z-[1] grid gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black text-white">{{ currentPage.label }} / 真实字段</h2>
            <p class="mt-1 text-sm text-white/50">前台路径：{{ currentPage.path }}。{{ summary }}</p>
          </div>
          <p v-if="dirty" class="rounded-full border border-amber-200/25 bg-amber-200/10 px-3 py-1 text-sm text-amber-100">有未保存修改</p>
        </div>

        <p v-if="error" class="rounded-2xl border border-red-300/20 bg-red-300/10 p-3 text-sm text-red-100">{{ error }}</p>
        <p v-if="success" class="rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm text-emerald-100">{{ success }}</p>
        <p class="rounded-2xl border border-cyan-200/15 bg-cyan-200/[0.08] p-3 text-sm text-cyan-50/72">配置来源：{{ configSource }}</p>
        <div v-if="loading" class="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-white/55">正在读取真实页面配置...</div>

        <div v-else class="grid gap-4">
          <div class="grid gap-3 md:grid-cols-2">
            <label class="field">页面标题<input v-model="pageText[pageKey].title" class="admin-input" @input="dirty = true" /></label>
            <label class="field">页面副标题<input v-model="pageText[pageKey].subtitle" class="admin-input" @input="dirty = true" /></label>
          </div>

          <div v-if="pageKey === 'posts'" class="grid gap-3 rounded-[24px] border border-white/10 bg-white/[0.04] p-4 md:grid-cols-2">
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

    <GlassCard>
      <div class="relative z-[1] grid gap-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black text-white">真实组件预览</h2>
            <p class="mt-1 text-sm text-white/50">首页拆为 8 个真实前台组件。拖动卡片排序，或使用精确顺序、宽度、高度控件；保存后刷新前台生效。</p>
          </div>
          <button v-if="pageKey === 'home'" type="button" class="admin-btn admin-btn-ghost" @click="restoreDefaultLayout">恢复首页默认布局</button>
        </div>

        <div v-if="pageKey === 'home'" class="page-editor-grid">
          <article
            v-for="block in sortedBlocks"
            :key="block.id"
            class="page-editor-block"
            :style="blockStyle(block)"
            draggable="true"
            @dragstart="onDragStart(block.id)"
            @dragover.prevent
            @drop="onDrop(block.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <b class="text-white">{{ block.label }}</b>
                <p class="mt-1 font-mono text-xs text-cyan-100/45">{{ block.id }}</p>
              </div>
              <span class="rounded-full bg-white/10 px-2 py-1 text-xs text-white/55">顺序 {{ block.order }}</span>
            </div>

            <div class="mt-4 grid gap-3">
              <div class="grid gap-2 rounded-2xl border border-white/10 bg-white/[0.05] p-3 text-xs text-white/55">
                <p>顺序：{{ block.order }} · 宽度：{{ formatSize(block.w) }}/12 · 高度：{{ formatSize(block.h) }} · 显示：{{ block.visible === false ? '隐藏' : '显示' }}</p>
                <p>透明度：{{ themeInfo(block.id).opacity }} · 大小：{{ themeInfo(block.id).size }}</p>
                <p class="truncate">日间背景：{{ themeInfo(block.id).dayBg }}</p>
                <p class="truncate">夜间背景：{{ themeInfo(block.id).nightBg }}</p>
                <button type="button" class="admin-btn admin-btn-ghost w-fit text-xs" @click="router.push('/settings?tab=theme')">打开组件主题设置</button>
              </div>

              <div class="flex flex-wrap items-end gap-2">
                <button type="button" class="admin-btn admin-btn-ghost text-xs" @click="moveBlock(block.id, -1)">上移</button>
                <button type="button" class="admin-btn admin-btn-ghost text-xs" @click="moveBlock(block.id, 1)">下移</button>
                <label class="inline-grid min-w-[8rem] gap-1 text-xs text-white/45">
                  精确顺序
                  <input class="admin-input py-2 text-xs" type="number" min="1" :max="blocks.length" step="1" :value="block.order" @change="setBlockOrder(block, eventNumber($event))" />
                </label>
              </div>

              <div class="page-size-control">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-xs text-white/45">宽度 w</span>
                  <b class="font-mono text-xs text-white">{{ formatSize(block.w) }}/12</b>
                </div>
                <div class="grid gap-2 sm:grid-cols-[minmax(0,1fr)_6.5rem]">
                  <input type="range" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="block.w" @input="setBlockSize(block, 'w', eventNumber($event))" />
                  <input class="admin-input py-2 text-xs" type="number" :min="sizeLimits.w.min" :max="sizeLimits.w.max" :step="sizeLimits.w.step" :value="block.w" @input="setBlockSize(block, 'w', eventNumber($event))" />
                </div>
                <div class="flex flex-wrap gap-2">
                  <button v-for="size in [4, 6, 8, 12]" :key="size" type="button" class="admin-btn admin-btn-ghost text-xs" @click="setBlockSize(block, 'w', size)">{{ size }}/12</button>
                </div>
              </div>

              <div class="page-size-control">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-xs text-white/45">高度 h</span>
                  <b class="font-mono text-xs text-white">{{ formatSize(block.h) }}</b>
                </div>
                <div class="grid gap-2 sm:grid-cols-[minmax(0,1fr)_6.5rem]">
                  <input type="range" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="block.h" @input="setBlockSize(block, 'h', eventNumber($event))" />
                  <input class="admin-input py-2 text-xs" type="number" :min="sizeLimits.h.min" :max="sizeLimits.h.max" :step="sizeLimits.h.step" :value="block.h" @input="setBlockSize(block, 'h', eventNumber($event))" />
                </div>
                <div class="flex flex-wrap gap-2">
                  <button v-for="size in [1, 2, 3, 4]" :key="size" type="button" class="admin-btn admin-btn-ghost text-xs" @click="setBlockSize(block, 'h', size)">{{ size }}</button>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="rounded-[28px] border border-white/10 bg-slate-950/45 p-5">
          <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">{{ currentPage.path }}</p>
          <h3 class="mt-3 text-3xl font-black text-white">{{ pageText[pageKey].title }}</h3>
          <p class="mt-2 text-white/58">{{ pageText[pageKey].subtitle }}</p>
          <p class="mt-5 rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-white/62">{{ summary }}</p>
          <p class="mt-3 text-sm text-white/42">第一阶段该页面支持真实文案编辑和内容新增入口；拖拽/缩放布局先集中在首页 8 个核心组件。</p>
        </div>

        <details class="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
          <summary class="cursor-pointer text-sm font-bold text-white/62">高级：当前首页布局 JSON</summary>
          <pre class="mt-4 max-h-80 overflow-auto rounded-2xl bg-slate-950/70 p-4 text-xs text-cyan-50/70">{{ JSON.stringify(payload().homeLayout, null, 2) }}</pre>
        </details>
      </div>
    </GlassCard>
  </section>
</template>

<style scoped>
.page-editor-grid {
  display: grid;
  grid-template-columns: repeat(120, minmax(0, 1fr));
  gap: 1rem;
}
.page-editor-block {
  min-width: 0;
  border-radius: .75rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 1rem;
  cursor: grab;
}
.page-editor-block:active {
  cursor: grabbing;
}
.page-size-control {
  display: grid;
  gap: .65rem;
  border-radius: .75rem;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: .75rem;
}
.page-size-control input[type="range"] {
  width: 100%;
  accent-color: #111827;
}
@media (max-width: 900px) {
  .page-editor-block {
    grid-column: 1 / -1 !important;
  }
}
</style>
