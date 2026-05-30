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
  resource: CommentIndexItem['resource']
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
const createLabel = computed(() => props.section === 'chatters' ? '杂谈' : props.section === 'moments' ? '说说' : '文章')

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

function commentCountFor(resource: CommentIndexItem['resource'], slug: string) {
  return commentIndex.value.find((item) => item.resource === resource && item.slug === slug)?.count || 0
}

function commentResource() {
  return props.section as CommentIndexItem['resource']
}

function openComments(item: ContentItem) {
  const resource = commentResource()
  activeCommentTarget.value = {
    resource,
    slug: item.slug,
    title: item.meta.title || item.slug,
    typeLabel: props.section === 'chatters' ? '杂谈' : props.section === 'moments' ? '说说' : '文章'
  }
}

function numberFrom(item: ContentItem, keys: string[]) {
  const record = item as unknown as Record<string, unknown>
  const meta = item.meta as unknown as Record<string, unknown>
  for (const key of keys) {
    const value = record[key] ?? meta[key]
    const numberValue = Number(value)
    if (Number.isFinite(numberValue)) return Math.max(0, numberValue)
  }
  return 0
}

function statsFor(item: ContentItem) {
  const resource = commentResource()
  return {
    views: numberFrom(item, ['view_count', 'views', 'viewCount', 'visits', 'readCount']),
    likes: numberFrom(item, ['like_count', 'likes', 'likeCount']),
    comments: commentCountFor(resource, item.slug),
    shares: numberFrom(item, ['share_count', 'shares', 'shareCount', 'forwards'])
  }
}

function tagsFor(item: ContentItem) {
  return Array.isArray(item.meta.tags) ? item.meta.tags : []
}

function coverFor(item: ContentItem) {
  return item.meta.cover || item.meta.images?.[0] || ''
}

function descriptionFor(item: ContentItem) {
  if (props.section === 'moments') return item.content || item.meta.summary || '未填写说说内容'
  return item.meta.summary || '未填写卡片简介'
}

function metaChipsFor(item: ContentItem) {
  if (props.section === 'moments') {
    return [item.meta.location ? `定位：${item.meta.location}` : '', item.meta.draft ? '草稿' : '已发布'].filter(Boolean)
  }
  return tagsFor(item).length ? tagsFor(item).map((tag) => `# ${tag}`) : ['无标签']
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
          <RouterLink :to="`/editor/${section}`" class="admin-btn admin-btn-primary">新增{{ createLabel }}</RouterLink>
        </div>
      </div>
      <input v-model="query" class="admin-input mt-5" placeholder="搜索标题、简介、标签或 slug" />
      <p v-if="error" class="mt-3 text-sm font-bold text-red-700">{{ error }}</p>
    </div>

    <div class="admin-table-card">
      <p v-if="loading" class="p-6 text-slate-500">加载中...</p>
      <p v-else-if="!filteredItems.length" class="p-6 text-slate-500">当前条件下暂无内容。</p>
      <div v-else>
        <article v-for="item in filteredItems" :key="item.slug" class="admin-list-row admin-manage-row">
          <div class="admin-manage-item">
            <div class="admin-manage-cover">
              <img v-if="coverFor(item)" :src="coverFor(item)" alt="" class="h-full w-full object-cover" loading="lazy" />
              <div v-else class="grid h-full place-items-center text-xs font-bold text-slate-400">默认封面</div>
            </div>
            <div class="admin-manage-info">
              <div class="admin-manage-title-line">
                <h3>{{ item.meta.title || item.slug }}</h3>
                <span v-if="item.meta.draft" class="rounded-full bg-amber-50 px-2 py-1 text-xs font-bold text-amber-700">草稿</span>
                <span v-else class="rounded-full bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700">已发布</span>
              </div>
              <p class="admin-manage-time">{{ item.meta.date || item.updatedAt || '无日期' }}</p>
              <p class="admin-manage-desc">{{ descriptionFor(item) }}</p>
              <div class="admin-manage-tags">
                <span v-for="chip in metaChipsFor(item)" :key="chip">{{ chip }}</span>
              </div>
              <div class="admin-manage-stats">
                <span title="浏览" aria-label="浏览">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="3" /></svg>
                  {{ statsFor(item).views }}
                </span>
                <span title="点赞" aria-label="点赞">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3m0 11V10l5-8 1 1a4 4 0 0 1 .8 4.1L13 10h5.6a2 2 0 0 1 2 2.3l-1.4 7.5a2 2 0 0 1-2 1.7H7Z" /></svg>
                  {{ statsFor(item).likes }}
                </span>
                <span title="评论" aria-label="评论">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4V5Z" /></svg>
                  {{ statsFor(item).comments }}
                </span>
                <span title="转发" aria-label="转发">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" /><path d="M5 5h5M5 5v5M19 19h-5M19 19v-5" /></svg>
                  {{ statsFor(item).shares }}
                </span>
              </div>
            </div>
            <div class="admin-manage-actions">
              <RouterLink :to="`/editor/${section}/${item.slug}`" class="admin-btn admin-btn-ghost text-sm">✏️ 编辑</RouterLink>
              <button :disabled="actionBusy === item.slug" class="admin-btn admin-btn-danger text-sm" type="button" @click="remove(item)">❌ 删除</button>
              <button class="admin-btn admin-btn-ghost text-sm" type="button" @click="openComments(item)">
                🗨︎ 评论管理
              </button>
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
