<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'

type PageKey = 'home' | 'posts' | 'photos' | 'music' | 'projects' | 'friends' | 'about'
type Block = { id: string; label: string; x: number; y: number; w: number; h: number }

const route = useRoute()
const router = useRouter()
const pageKey = computed<PageKey>(() => {
  const key = String(route.params.page || 'home')
  return ['home', 'posts', 'photos', 'music', 'projects', 'friends', 'about'].includes(key) ? key as PageKey : 'home'
})

const pages: Array<{ key: PageKey; label: string; path: string; action: string; actionPath: string }> = [
  { key: 'home', label: '首页', path: '/', action: '编辑首页名片、简介、社交链接和核心模块布局', actionPath: '/settings' },
  { key: 'posts', label: '文章', path: '/posts', action: '复用写作编辑器新增文章', actionPath: '/content/editor' },
  { key: 'photos', label: '图片', path: '/photowall', action: '复用相册管理新增相册', actionPath: '/content/media/photos' },
  { key: 'music', label: '音乐', path: '/music', action: '复用歌曲管理新增歌曲', actionPath: '/content/media/music' },
  { key: 'projects', label: '项目', path: '/projects', action: '复用项目管理新增项目', actionPath: '/content/media/projects' },
  { key: 'friends', label: '友链', path: '/friends', action: '复用友链管理新增友链', actionPath: '/content/media/friends' },
  { key: 'about', label: '关于', path: '/about', action: '编辑关于页 Markdown 内容', actionPath: '/about' }
]

const defaultText: Record<PageKey, { title: string; subtitle: string }> = {
  home: { title: '首页', subtitle: '名片、音乐、歌词、轮播与状态区。' },
  posts: { title: '文章归档', subtitle: '从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。' },
  photos: { title: '图片', subtitle: '相册记录从后端 JSON 动态读取，点击封面可查看组内照片。' },
  music: { title: '音乐歌单', subtitle: '全局播放器、歌词和歌单共享同一播放状态。' },
  projects: { title: '项目', subtitle: '记录正在构建和已经完成的作品。' },
  friends: { title: '友链', subtitle: '把值得长期访问的站点放在这里。' },
  about: { title: '关于', subtitle: '关于 SRBlogs 与站点作者。' }
}

const defaultHomeBlocks: Block[] = [
  { id: 'profile', label: '名片', x: 4, y: 6, w: 42, h: 24 },
  { id: 'music', label: '音乐播放器', x: 50, y: 6, w: 46, h: 24 },
  { id: 'lyrics', label: '歌词区', x: 4, y: 34, w: 92, h: 14 },
  { id: 'carousel', label: '轮播区', x: 4, y: 52, w: 92, h: 30 },
  { id: 'status', label: '底部状态', x: 4, y: 86, w: 92, h: 10 }
]

const currentPage = computed(() => pages.find((page) => page.key === pageKey.value) || pages[0])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const dirty = ref(false)
const raw = ref<Record<string, any>>({})
const summary = ref('')
const aboutContent = ref('')
const dragging = ref<{ id: string; mode: 'move' | 'resize'; startX: number; startY: number; origin: Block } | null>(null)

const pageText = reactive<Record<PageKey, { title: string; subtitle: string }>>({
  home: { ...defaultText.home },
  posts: { ...defaultText.posts },
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

const blocks = ref<Block[]>(defaultHomeBlocks.map((block) => ({ ...block })))

function hydrateSettings(data: Record<string, any>) {
  const savedText = data.pageText || {}
  ;(Object.keys(defaultText) as PageKey[]).forEach((key) => {
    pageText[key].title = savedText[key]?.title || defaultText[key].title
    pageText[key].subtitle = savedText[key]?.subtitle || defaultText[key].subtitle
  })
  home.author = data.author || data.authorName || ''
  home.avatar = data.avatar || data.avatarUrl || ''
  home.description = data.description || data.bio || ''
  home.socialLinks = { github: '', email: '', qq: '', wechat: '', ...(data.socialLinks || data.social || {}) }
  const savedBlocks = data.pageLayouts?.home?.blocks
  blocks.value = Array.isArray(savedBlocks) && savedBlocks.length
    ? savedBlocks.map((block: Block) => ({ ...block }))
    : defaultHomeBlocks.map((block) => ({ ...block }))
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
      summary.value = '首页读取 settings 中的作者、头像、简介、社交链接和布局配置。'
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
    raw.value = await adminApi.json<Record<string, any>>('/admin/settings')
    hydrateSettings(raw.value)
    await loadSummary(pageKey.value)
    dirty.value = false
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面编辑配置加载失败'
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  return {
    ...raw.value,
    author: home.author,
    avatar: home.avatar,
    description: home.description,
    socialLinks: { ...home.socialLinks },
    pageText: {
      ...(raw.value.pageText || {}),
      home: { ...pageText.home },
      posts: { ...pageText.posts },
      photos: { ...pageText.photos },
      music: { ...pageText.music },
      projects: { ...pageText.projects },
      friends: { ...pageText.friends },
      about: { ...pageText.about }
    },
    pageLayouts: {
      ...(raw.value.pageLayouts || {}),
      home: {
        ...(raw.value.pageLayouts?.home || {}),
        blocks: blocks.value.map((block) => ({ ...block }))
      }
    }
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const payload = buildPayload()
    await adminApi.putJson('/admin/settings', payload)
    if (pageKey.value === 'about') {
      await adminApi.putJson('/about', { content: aboutContent.value })
    }
    raw.value = await adminApi.json<Record<string, any>>('/admin/settings')
    hydrateSettings(raw.value)
    success.value = '页面配置已保存，刷新前台后生效。'
    dirty.value = false
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面配置保存失败'
  } finally {
    saving.value = false
  }
}

function restoreDefaultLayout() {
  blocks.value = defaultHomeBlocks.map((block) => ({ ...block }))
  dirty.value = true
}

function startDrag(event: PointerEvent, block: Block, mode: 'move' | 'resize') {
  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
  dragging.value = { id: block.id, mode, startX: event.clientX, startY: event.clientY, origin: { ...block } }
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return
  const block = blocks.value.find((item) => item.id === dragging.value?.id)
  if (!block) return
  const dx = ((event.clientX - dragging.value.startX) / 760) * 100
  const dy = ((event.clientY - dragging.value.startY) / 440) * 100
  if (dragging.value.mode === 'move') {
    block.x = Math.max(0, Math.min(100 - block.w, dragging.value.origin.x + dx))
    block.y = Math.max(0, Math.min(100 - block.h, dragging.value.origin.y + dy))
  } else {
    block.w = Math.max(18, Math.min(100 - block.x, dragging.value.origin.w + dx))
    block.h = Math.max(8, Math.min(100 - block.y, dragging.value.origin.h + dy))
  }
  dirty.value = true
}

function stopDrag() {
  dragging.value = null
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
          <p class="mt-2 max-w-3xl text-white/58">第一阶段绑定真实前台字段：文案直接保存到 settings/about，首页布局保存为独立布局配置，不覆盖文章、相册、音乐等业务数据。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="admin-btn admin-btn-ghost" @click="openContentEntry">{{ currentPage.action }}</button>
          <button type="button" class="admin-btn" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
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
        <div v-if="loading" class="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-white/55">正在读取真实页面配置...</div>

        <div v-else class="grid gap-4">
          <div class="grid gap-3 md:grid-cols-2">
            <label class="field">页面标题<input v-model="pageText[pageKey].title" class="admin-input" @input="dirty = true" /></label>
            <label class="field">页面副标题<input v-model="pageText[pageKey].subtitle" class="admin-input" @input="dirty = true" /></label>
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
            <h2 class="text-2xl font-black text-white">真实预览摘要</h2>
            <p class="mt-1 text-sm text-white/50">预览使用当前表单字段和真实数据摘要，不再使用静态假数据。</p>
          </div>
          <button v-if="pageKey === 'home'" type="button" class="admin-btn admin-btn-ghost" @click="restoreDefaultLayout">恢复首页默认布局</button>
        </div>

        <div
          v-if="pageKey === 'home'"
          class="relative min-h-[460px] overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/55"
          @pointermove="onPointerMove"
          @pointerup="stopDrag"
          @pointerleave="stopDrag"
        >
          <div
            v-for="block in blocks"
            :key="block.id"
            class="absolute grid place-items-center rounded-[24px] border border-cyan-200/25 bg-cyan-200/[0.09] p-3 text-center text-sm font-bold text-cyan-100 shadow-inner shadow-white/5"
            :style="{ left: `${block.x}%`, top: `${block.y}%`, width: `${block.w}%`, height: `${block.h}%` }"
            @pointerdown="startDrag($event, block, 'move')"
          >
            <span>{{ block.label }}</span>
            <small v-if="block.id === 'profile'" class="mt-1 text-white/60">{{ home.author || '未设置作者' }} / {{ home.description || '未设置简介' }}</small>
            <button
              type="button"
              class="absolute bottom-2 right-2 h-6 w-6 rounded-md border border-white/20 bg-white/15 text-xs text-white/70"
              aria-label="调整大小"
              @pointerdown.stop="startDrag($event, block, 'resize')"
            >
              ↘
            </button>
          </div>
        </div>

        <div v-else class="rounded-[28px] border border-white/10 bg-slate-950/45 p-5">
          <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">{{ currentPage.path }}</p>
          <h3 class="mt-3 text-3xl font-black text-white">{{ pageText[pageKey].title }}</h3>
          <p class="mt-2 text-white/58">{{ pageText[pageKey].subtitle }}</p>
          <p class="mt-5 rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-white/62">{{ summary }}</p>
          <p class="mt-3 text-sm text-white/42">第一阶段该页面支持真实文案编辑和内容新增入口；拖拽/缩放布局先集中在首页核心组件。</p>
        </div>
      </div>
    </GlassCard>
  </section>
</template>
