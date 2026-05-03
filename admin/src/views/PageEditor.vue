<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'

type Block = { id: string; label: string; x: number; y: number; w: number; h: number }
type PageLayout = { title: string; subtitle: string; note: string; blocks: Block[] }

const route = useRoute()
const router = useRouter()
const pageKey = computed(() => String(route.params.page || 'home'))
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const raw = ref<Record<string, any>>({})
const dragging = ref<{ id: string; mode: 'move' | 'resize'; startX: number; startY: number; origin: Block } | null>(null)

const pages = [
  { key: 'home', label: '首页', path: '/', action: '编辑首页名片和核心模块说明' },
  { key: 'posts', label: '文章', path: '/posts', action: '进入写作和文章管理' },
  { key: 'photos', label: '图片', path: '/photowall', action: '进入相册管理' },
  { key: 'music', label: '音乐', path: '/music', action: '进入歌曲管理' },
  { key: 'projects', label: '项目', path: '/projects', action: '进入项目管理' },
  { key: 'friends', label: '友链', path: '/friends', action: '进入友链管理' },
  { key: 'about', label: '关于', path: '/about', action: '进入关于 Markdown 编辑' }
]

const currentPage = computed(() => pages.find((page) => page.key === pageKey.value) || pages[0])
const draft = reactive<PageLayout>(defaultLayout('home'))

function defaultLayout(key: string): PageLayout {
  const page = pages.find((item) => item.key === key) || pages[0]
  return {
    title: `${page.label}页面`,
    subtitle: `${page.label}页面的标题、副标题和预览布局。`,
    note: page.action,
    blocks: [
      { id: 'hero', label: '标题区域', x: 6, y: 8, w: 88, h: 18 },
      { id: 'main', label: '主体内容', x: 6, y: 32, w: 58, h: 42 },
      { id: 'side', label: '辅助模块', x: 68, y: 32, w: 26, h: 42 }
    ]
  }
}

function applyLayout(layout: Partial<PageLayout> | undefined) {
  const fallback = defaultLayout(pageKey.value)
  draft.title = layout?.title || fallback.title
  draft.subtitle = layout?.subtitle || fallback.subtitle
  draft.note = layout?.note || fallback.note
  draft.blocks = Array.isArray(layout?.blocks) && layout!.blocks.length
    ? layout!.blocks.map((block) => ({ ...block }))
    : fallback.blocks.map((block) => ({ ...block }))
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    raw.value = await adminApi.json<Record<string, any>>('/admin/settings')
    const layouts = raw.value.pageLayouts || {}
    applyLayout(layouts[pageKey.value])
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面配置加载失败'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const payload = {
      ...raw.value,
      pageLayouts: {
        ...(raw.value.pageLayouts || {}),
        [pageKey.value]: {
          title: draft.title,
          subtitle: draft.subtitle,
          note: draft.note,
          blocks: draft.blocks.map((block) => ({ ...block }))
        }
      }
    }
    await adminApi.putJson('/admin/settings', payload)
    raw.value = await adminApi.json<Record<string, any>>('/admin/settings')
    success.value = '页面布局配置已保存。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面布局保存失败'
  } finally {
    saving.value = false
  }
}

function restoreDefault() {
  applyLayout(defaultLayout(pageKey.value))
}

function startDrag(event: PointerEvent, block: Block, mode: 'move' | 'resize') {
  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
  dragging.value = {
    id: block.id,
    mode,
    startX: event.clientX,
    startY: event.clientY,
    origin: { ...block }
  }
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return
  const block = draft.blocks.find((item) => item.id === dragging.value?.id)
  if (!block) return
  const dx = ((event.clientX - dragging.value.startX) / 760) * 100
  const dy = ((event.clientY - dragging.value.startY) / 420) * 100
  if (dragging.value.mode === 'move') {
    block.x = Math.max(0, Math.min(100 - block.w, dragging.value.origin.x + dx))
    block.y = Math.max(0, Math.min(100 - block.h, dragging.value.origin.y + dy))
  } else {
    block.w = Math.max(18, Math.min(100 - block.x, dragging.value.origin.w + dx))
    block.h = Math.max(14, Math.min(100 - block.y, dragging.value.origin.h + dy))
  }
}

function stopDrag() {
  dragging.value = null
}

function actionPath() {
  if (pageKey.value === 'posts') return '/editor/posts'
  if (pageKey.value === 'photos') return '/photos'
  if (pageKey.value === 'music') return '/music'
  if (pageKey.value === 'projects') return '/projects'
  if (pageKey.value === 'friends') return '/friends'
  if (pageKey.value === 'about') return '/about'
  return '/settings?tab=site'
}

watch(pageKey, load, { immediate: true })
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1] flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">page editor</p>
          <h1 class="mt-2 text-4xl font-black text-white">页面编辑</h1>
          <p class="mt-2 max-w-2xl text-white/55">第一阶段只做标题文案和后台预览区布局编辑，不会直接重写前台页面结构。保存后写入安全设置文件，可随时恢复默认。</p>
        </div>
        <button type="button" class="admin-btn admin-btn-ghost" @click="router.push(actionPath())">打开对应管理功能</button>
      </div>
    </GlassCard>

    <div class="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
      <GlassCard>
        <div class="relative z-[1] grid gap-2">
          <RouterLink
            v-for="page in pages"
            :key="page.key"
            :to="`/pages/${page.key}`"
            class="rounded-2xl border px-4 py-3 text-sm transition"
            :class="page.key === pageKey ? 'border-cyan-200/35 bg-cyan-200/12 text-cyan-100' : 'border-white/10 bg-white/[0.04] text-white/62 hover:bg-white/[0.08]'"
          >
            {{ page.label }}
          </RouterLink>
        </div>
      </GlassCard>

      <div class="grid gap-4">
        <GlassCard>
          <div class="relative z-[1] grid gap-4">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 class="text-2xl font-black text-white">{{ currentPage.label }}配置</h2>
                <p class="mt-1 text-sm text-white/48">前台路径：{{ currentPage.path }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <button type="button" class="admin-btn admin-btn-ghost" @click="restoreDefault">恢复默认布局</button>
                <button type="button" class="admin-btn" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存页面配置' }}</button>
              </div>
            </div>
            <p v-if="error" class="rounded-2xl border border-red-300/20 bg-red-300/10 p-3 text-sm text-red-100">{{ error }}</p>
            <p v-if="success" class="rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm text-emerald-100">{{ success }}</p>
            <div v-if="loading" class="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-white/55">加载页面配置中...</div>
            <div v-else class="grid gap-3 md:grid-cols-2">
              <label class="field">页面标题<input v-model="draft.title" class="admin-input" /></label>
              <label class="field">副标题<input v-model="draft.subtitle" class="admin-input" /></label>
              <label class="field md:col-span-2">说明文案<textarea v-model="draft.note" class="admin-input min-h-24"></textarea></label>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div class="relative z-[1] grid gap-4">
            <div>
              <h2 class="text-2xl font-black text-white">可视化预览雏形</h2>
              <p class="mt-1 text-sm text-white/48">拖动模块可改变位置，拖动右下角手柄可改变大小。当前仅在后台预览区生效。</p>
            </div>
            <div
              class="relative min-h-[420px] overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/55"
              @pointermove="onPointerMove"
              @pointerup="stopDrag"
              @pointerleave="stopDrag"
            >
              <div class="absolute inset-x-6 top-5">
                <h3 class="truncate text-3xl font-black text-white">{{ draft.title }}</h3>
                <p class="mt-1 truncate text-white/50">{{ draft.subtitle }}</p>
              </div>
              <div
                v-for="block in draft.blocks"
                :key="block.id"
                class="absolute grid place-items-center rounded-[24px] border border-cyan-200/20 bg-cyan-200/[0.08] text-center text-sm font-bold text-cyan-100 shadow-inner shadow-white/5"
                :style="{ left: `${block.x}%`, top: `${block.y}%`, width: `${block.w}%`, height: `${block.h}%` }"
                @pointerdown="startDrag($event, block, 'move')"
              >
                <span>{{ block.label }}</span>
                <button
                  type="button"
                  class="absolute bottom-2 right-2 h-5 w-5 rounded-md border border-white/20 bg-white/15 text-[10px] text-white/70"
                  aria-label="调整大小"
                  @pointerdown.stop="startDrag($event, block, 'resize')"
                >
                  ↘
                </button>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  </section>
</template>
