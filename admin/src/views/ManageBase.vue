<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import AdminConfirmDialog from '@/components/AdminConfirmDialog.vue'
import CommentManageModal from '@/components/CommentManageModal.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useUiStore } from '@/stores/ui'
import type { CommentIndexItem, ContentItem } from '@/types'

const props = defineProps<{ section: 'posts' | 'moments' | 'chatters'; title: string }>()

const ui = useUiStore()
const confirmDialog = useConfirmDialog()
const router = useRouter()
const items = ref<ContentItem[]>([])
const filter = ref<'all' | 'published' | 'draft'>('all')
const query = ref('')
const loading = ref(false)
const error = ref('')
const actionBusy = ref('')
const commentIndex = ref<CommentIndexItem[]>([])
const activeCommentTarget = ref<{
  resource: 'posts' | 'chatters'
  slug: string
  title: string
  typeLabel: string
} | null>(null)

const filterOptions: { value: 'all' | 'published' | 'draft'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'published', label: '已发布' },
  { value: 'draft', label: '草稿' }
]

const showArticleKindSwitch = computed(() => props.section === 'posts' || props.section === 'chatters')
const articleKind = computed<'posts' | 'chatters'>(() => props.section === 'chatters' ? 'chatters' : 'posts')

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

function publicPath(item: ContentItem) {
  if (props.section === 'chatters') return `/chatters/${item.slug}`
  if (props.section === 'moments') return `/moments/${item.slug}`
  return `/posts/${item.slug}`
}

function setArticleKind(kind: 'posts' | 'chatters') {
  router.replace({ path: '/content/articles', query: kind === 'chatters' ? { kind } : {} })
}

async function load() {
  error.value = ''
  loading.value = true
  try {
    const [content, comments] = await Promise.all([
      adminApi.list(props.section),
      adminApi.commentsIndex().catch(() => [])
    ])
    items.value = content
    commentIndex.value = comments
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '内容列表加载失败'
  } finally {
    loading.value = false
  }
}

function commentCountFor(resource: 'posts' | 'chatters', slug: string) {
  return commentIndex.value.find((item) => item.resource === resource && item.slug === slug)?.count || 0
}

function openComments(item: ContentItem) {
  if (!showArticleKindSwitch.value) return
  const resource = props.section === 'chatters' ? 'chatters' : 'posts'
  activeCommentTarget.value = {
    resource,
    slug: item.slug,
    title: item.meta.title,
    typeLabel: props.section === 'chatters' ? '杂谈' : '文章'
  }
}

function updateCommentCount(payload: { resource: CommentIndexItem['resource']; slug: string; count: number; title: string }) {
  const index = commentIndex.value.findIndex((item) => item.resource === payload.resource && item.slug === payload.slug)
  const nextItem: CommentIndexItem = {
    resource: payload.resource,
    slug: payload.slug,
    count: payload.count,
    title: payload.title,
    updatedAt: new Date().toISOString()
  }
  if (index >= 0) commentIndex.value.splice(index, 1, nextItem)
  else commentIndex.value.push(nextItem)
}

async function remove(item: ContentItem) {
  const label = item.meta.title || item.slug
  const ok = await confirmDialog.ask({
    title: '确认删除',
    message: `删除后会生成备份，确定删除「${label}」吗？`,
    cancelText: '取消',
    confirmText: '确认删除',
    variant: 'danger'
  })
  if (!ok) return
  error.value = ''
  actionBusy.value = item.slug
  try {
    await adminApi.remove(props.section, item.slug)
    ui.show('已删除')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '删除失败'
    ui.error('删除失败，请重试')
  } finally {
    actionBusy.value = ''
  }
}

async function toggleDraft(item: ContentItem, draft: boolean) {
  const label = draft ? '设为草稿' : '发布'
  const ok = await confirmDialog.ask({
    title: `确认${label}`,
    message: `确定${label}「${item.meta.title || item.slug}」吗？`,
    cancelText: '取消',
    confirmText: `确认${label}`,
    variant: draft ? 'default' : 'danger'
  })
  if (!ok) return
  error.value = ''
  actionBusy.value = item.slug
  try {
    const payload: ContentItem = { ...item, meta: { ...item.meta, draft } }
    await adminApi.save(props.section, payload, item.slug)
    ui.show(draft ? '已设为草稿' : '已发布')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : `${label}失败`
    ui.error(`${label}失败，请重试`)
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
        <h2 class="text-2xl font-black text-slate-950">{{ title }}</h2>
        <div class="flex flex-wrap items-center gap-2">
          <div v-if="showArticleKindSwitch" class="admin-segment" aria-label="文章类型">
            <button type="button" :class="articleKind === 'posts' ? 'admin-segment-active' : ''" @click="setArticleKind('posts')">正经</button>
            <button type="button" :class="articleKind === 'chatters' ? 'admin-segment-active' : ''" @click="setArticleKind('chatters')">杂谈</button>
          </div>
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
          <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
          <RouterLink :to="`/editor/${section}`" class="admin-btn admin-btn-primary">新增{{ props.section === 'chatters' ? '杂谈' : '文章' }}</RouterLink>
        </div>
      </div>
      <input v-model="query" class="admin-input mt-5" placeholder="搜索标题、简介、标签或 slug" />
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
              <button v-if="showArticleKindSwitch" class="admin-btn admin-btn-ghost text-sm" type="button" @click="openComments(item)">
                评论({{ commentCountFor(props.section === 'chatters' ? 'chatters' : 'posts', item.slug) }})
              </button>
              <RouterLink :to="`/editor/${section}/${item.slug}`" class="admin-btn admin-btn-ghost text-sm">编辑</RouterLink>
              <a v-if="!item.meta.draft" :href="publicPath(item)" target="_blank" class="admin-btn admin-btn-ghost text-sm">预览</a>
              <button v-if="item.meta.draft" :disabled="actionBusy === item.slug" class="admin-btn admin-btn-primary text-sm" type="button" @click="toggleDraft(item, false)">发布</button>
              <button v-else :disabled="actionBusy === item.slug" class="admin-btn admin-btn-ghost text-sm" type="button" @click="toggleDraft(item, true)">设为草稿</button>
              <button :disabled="actionBusy === item.slug" class="admin-btn admin-btn-danger text-sm" type="button" @click="remove(item)">删除</button>
            </div>
          </div>
        </article>
      </div>
    </div>

    <CommentManageModal
      v-if="activeCommentTarget"
      :model-value="Boolean(activeCommentTarget)"
      :resource="activeCommentTarget.resource"
      :slug="activeCommentTarget.slug"
      :title="activeCommentTarget.title"
      :type-label="activeCommentTarget.typeLabel"
      @update:model-value="(value) => { if (!value) activeCommentTarget = null }"
      @count-updated="updateCommentCount"
    />

    <AdminConfirmDialog
      v-bind="confirmDialog.state"
      @confirm="confirmDialog.confirm"
      @cancel="confirmDialog.cancel"
    />
  </section>
</template>
