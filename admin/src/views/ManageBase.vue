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
  if (!confirm(`确认${label}「${item.meta.title}」？`)) return
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
    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-2xl font-black text-slate-950">{{ title }}</h2>
          <p class="mt-2 text-sm leading-6 text-slate-600">正文 Markdown 和卡片简介分开维护；封面缺失时前台会使用设置里的默认封面。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
          <RouterLink :to="`/editor/${section}`" class="admin-btn admin-btn-primary">新增</RouterLink>
        </div>
      </div>
      <div class="mt-5 flex flex-wrap items-center gap-2">
        <input v-model="query" class="admin-input max-w-md" placeholder="搜索标题、简介或 slug" />
        <button
          v-for="option in filterOptions"
          :key="option.value"
          type="button"
          class="admin-btn"
          :class="filter === option.value ? 'admin-btn-primary' : 'admin-btn-ghost'"
          @click="filter = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-700">{{ error }}</p>
    </div>

    <div class="admin-card">
      <p v-if="loading" class="text-slate-500">加载中...</p>
      <p v-else-if="!filteredItems.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-500">当前筛选下暂无内容。</p>
      <div v-else class="grid gap-3">
        <div v-for="item in filteredItems" :key="item.slug" class="rounded-xl border border-slate-200 bg-white p-4">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="break-words text-lg font-black text-slate-950">{{ item.meta.title }}</h3>
                <span v-if="item.meta.draft" class="rounded-full bg-amber-50 px-2 py-1 text-xs font-bold text-amber-700">草稿</span>
                <span v-else class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700">已发布</span>
              </div>
              <p class="mt-1 break-all font-mono text-xs text-slate-500">{{ item.slug }}</p>
              <p class="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">{{ item.meta.summary || '未填写卡片简介' }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span>{{ item.meta.date || '无日期' }}</span>
                <span>{{ item.meta.tags?.length || 0 }} 个标签</span>
                <span>{{ item.content?.length || 0 }} 字符正文</span>
              </div>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <RouterLink :to="`/editor/${section}/${item.slug}`" class="admin-btn admin-btn-ghost text-sm">编辑</RouterLink>
              <a v-if="!item.meta.draft" :href="publicPath(item)" target="_blank" class="admin-btn admin-btn-ghost text-sm">前台预览</a>
              <button v-if="item.meta.draft" :disabled="actionBusy === item.slug" class="admin-btn admin-btn-primary text-sm" type="button" @click="toggleDraft(item, false)">发布</button>
              <button v-else :disabled="actionBusy === item.slug" class="admin-btn admin-btn-ghost text-sm" type="button" @click="toggleDraft(item, true)">设为草稿</button>
              <button :disabled="actionBusy === item.slug" class="admin-btn admin-btn-danger text-sm" type="button" @click="remove(item.slug)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
