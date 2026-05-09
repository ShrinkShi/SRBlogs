<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'

const props = defineProps<{ section: 'posts' | 'moments' | 'chatters'; title: string }>()

const ui = useUiStore()
const items = ref<ContentItem[]>([])
const filter = ref<'all' | 'published' | 'draft'>('all')
const query = ref('')
const loading = ref(false)
const error = ref('')
const actionBusy = ref('')

const filterOptions: { value: 'all' | 'published' | 'draft'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'published', label: '已发布' },
  { value: 'draft', label: '草稿' }
]

const filteredItems = computed(() => items.value.filter((item) => {
  if (filter.value === 'published') return !item.meta.draft
  if (filter.value === 'draft') return item.meta.draft
  return true
}).filter((item) => {
  const q = query.value.trim().toLowerCase()
  if (!q) return true
  return item.meta.title.toLowerCase().includes(q)
    || item.slug.toLowerCase().includes(q)
    || (item.meta.summary || '').toLowerCase().includes(q)
    || item.meta.tags?.some((tag) => tag.toLowerCase().includes(q))
}))

const stats = computed(() => ({
  total: items.value.length,
  published: items.value.filter((item) => !item.meta.draft).length,
  draft: items.value.filter((item) => item.meta.draft).length
}))

function publicPath(item: ContentItem) {
  if (props.section === 'chatters') return `/chatters/${item.slug}`
  if (props.section === 'moments') return `/moments/${item.slug}`
  return `/posts/${item.slug}`
}

async function load() {
  error.value = ''
  loading.value = true
  try {
    items.value = await adminApi.list(props.section)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '内容列表加载失败'
  } finally {
    loading.value = false
  }
}

async function remove(slug: string) {
  if (!confirm(`确认删除 ${slug}？删除前后端会生成备份。`)) return
  error.value = ''
  actionBusy.value = slug
  try {
    await adminApi.remove(props.section, slug)
    ui.show('内容已删除')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '删除失败'
  } finally {
    actionBusy.value = ''
  }
}

async function toggleDraft(item: ContentItem, draft: boolean) {
  const label = draft ? '设为草稿' : '发布'
  if (!confirm(`确认${label}《${item.meta.title}》？`)) return
  error.value = ''
  actionBusy.value = item.slug
  try {
    const payload: ContentItem = { ...item, meta: { ...item.meta, draft } }
    await adminApi.save(props.section, payload, item.slug)
    ui.show(draft ? '已设为草稿' : '已发布')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : `${label}失败`
  } finally {
    actionBusy.value = ''
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <div class="grid gap-3 md:grid-cols-3">
      <div class="admin-card">
        <p class="admin-section-title">TOTAL</p>
        <strong class="mt-2 block text-3xl text-slate-950">{{ stats.total }}</strong>
        <span class="admin-meta">总内容</span>
      </div>
      <div class="admin-card">
        <p class="admin-section-title">PUBLISHED</p>
        <strong class="mt-2 block text-3xl text-slate-950">{{ stats.published }}</strong>
        <span class="admin-meta">公开显示</span>
      </div>
      <div class="admin-card">
        <p class="admin-section-title">DRAFT</p>
        <strong class="mt-2 block text-3xl text-slate-950">{{ stats.draft }}</strong>
        <span class="admin-meta">草稿隐藏</span>
      </div>
    </div>

    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-2xl font-black text-slate-950">{{ title }}</h2>
          <p class="mt-2 text-sm leading-6 text-slate-600">
            Markdown 正文用于详情页，卡片简介单独维护；简介建议控制字数，避免前台卡片溢出。封面为空时前台使用默认封面。
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
          <RouterLink :to="`/editor/${section}`" class="admin-btn admin-btn-primary">新增{{ props.section === 'chatters' ? '杂谈' : '文章' }}</RouterLink>
        </div>
      </div>
      <div class="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]">
        <input v-model="query" class="admin-input" placeholder="搜索标题、简介、标签或 slug" />
        <div class="admin-segment">
          <button
            v-for="option in filterOptions"
            :key="option.value"
            type="button"
            :class="filter === option.value ? 'admin-segment-active' : ''"
            @click="filter = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
      <p v-if="error" class="mt-3 text-sm font-bold text-red-700">{{ error }}</p>
    </div>

    <div class="admin-table-card">
      <p v-if="loading" class="p-6 text-slate-500">加载中...</p>
      <p v-else-if="!filteredItems.length" class="p-6 text-slate-500">当前条件下暂无内容。</p>
      <div v-else>
        <article v-for="item in filteredItems" :key="item.slug" class="admin-list-row">
          <div class="grid gap-4 lg:grid-cols-[8rem_minmax(0,1fr)_auto] lg:items-center">
            <div class="h-24 overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
              <img v-if="item.meta.cover" :src="item.meta.cover" alt="" class="h-full w-full object-cover" loading="lazy" />
              <div v-else class="grid h-full place-items-center text-xs font-bold text-slate-400">默认封面</div>
            </div>
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="break-words text-lg font-black text-slate-950">{{ item.meta.title }}</h3>
                <span v-if="item.meta.draft" class="rounded-full bg-amber-50 px-2 py-1 text-xs font-bold text-amber-700">草稿</span>
                <span v-else class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700">已发布</span>
              </div>
              <p class="mt-1 break-all font-mono text-xs text-slate-500">{{ item.slug }}</p>
              <p class="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">{{ item.meta.summary || '未填写卡片简介' }}</p>
              <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span>{{ item.meta.date || '无日期' }}</span>
                <span>{{ item.meta.tags?.length || 0 }} 个标签</span>
                <span>{{ item.meta.summary?.length || 0 }} 字简介</span>
                <span>{{ item.content?.length || 0 }} 字正文</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 lg:justify-end">
              <RouterLink :to="`/editor/${section}/${item.slug}`" class="admin-btn admin-btn-ghost text-sm">编辑</RouterLink>
              <a v-if="!item.meta.draft" :href="publicPath(item)" target="_blank" class="admin-btn admin-btn-ghost text-sm">预览</a>
              <button v-if="item.meta.draft" :disabled="actionBusy === item.slug" class="admin-btn admin-btn-primary text-sm" type="button" @click="toggleDraft(item, false)">发布</button>
              <button v-else :disabled="actionBusy === item.slug" class="admin-btn admin-btn-ghost text-sm" type="button" @click="toggleDraft(item, true)">设为草稿</button>
              <button :disabled="actionBusy === item.slug" class="admin-btn admin-btn-danger text-sm" type="button" @click="remove(item.slug)">删除</button>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
