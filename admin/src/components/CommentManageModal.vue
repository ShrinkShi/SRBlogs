<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { CommentIndexItem, CommentItem } from '@/types'

type CommentResource = CommentIndexItem['resource']
type CommentWithLegacyReply = CommentItem & Record<string, unknown>

const props = defineProps<{
  modelValue: boolean
  resource: CommentResource
  slug: string
  title: string
  typeLabel: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'count-updated': [payload: { resource: CommentResource; slug: string; count: number; title: string }]
}>()

const ui = useUiStore()
const comments = ref<CommentWithLegacyReply[]>([])
const loading = ref(false)
const deletingId = ref('')
const error = ref('')

const sortedComments = computed(() => {
  return [...comments.value].sort((left, right) => {
    return new Date(left.created_at || '').getTime() - new Date(right.created_at || '').getTime()
  })
})

function close() {
  emit('update:modelValue', false)
}

function displayName(comment: CommentWithLegacyReply) {
  return String(comment.author || comment.githubLogin || comment.providerId || '匿名访客')
}

function githubProfile(comment: CommentWithLegacyReply) {
  const login = String(comment.githubLogin || comment.providerId || '')
  return comment.provider === 'github' && login ? `https://github.com/${login}` : ''
}

function identityLine(comment: CommentWithLegacyReply) {
  if (comment.provider === 'github') {
    return `GitHub ${comment.githubLogin ? `@${comment.githubLogin}` : comment.providerId || '用户'}`
  }
  if (comment.provider === 'qq') {
    return `QQ ${comment.providerId ? `openid ${comment.providerId}` : '用户'}`
  }
  return `游客 / 本地评论 · ${comment.email ? '已留邮箱' : '未留邮箱'}`
}

function initials(comment: CommentWithLegacyReply) {
  return displayName(comment).slice(0, 1).toUpperCase()
}

function replyTarget(comment: CommentWithLegacyReply) {
  // TODO: backend CommentItem has no standardized reply fields yet; show legacy fields only when present.
  return String(comment.parentId || comment.parent_id || comment.replyTo || comment.replyToId || comment.reply_to || '')
}

function replyAuthor(comment: CommentWithLegacyReply) {
  return String(comment.replyAuthor || comment.replyToAuthor || comment.reply_to_author || replyTarget(comment))
}

function formatTime(value: string) {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadComments() {
  if (!props.modelValue || !props.resource || !props.slug) return
  loading.value = true
  error.value = ''
  try {
    comments.value = await adminApi.comments(props.resource, props.slug) as CommentWithLegacyReply[]
    emit('count-updated', {
      resource: props.resource,
      slug: props.slug,
      count: comments.value.length,
      title: props.title
    })
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论加载失败'
  } finally {
    loading.value = false
  }
}

async function deleteComment(comment: CommentWithLegacyReply) {
  if (!confirm(`确认删除 ${displayName(comment)} 的这条评论？`)) return
  deletingId.value = comment.id
  error.value = ''
  try {
    await adminApi.deleteComment(props.resource, props.slug, comment.id)
    ui.show('评论已删除')
    await loadComments()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '删除评论失败'
  } finally {
    deletingId.value = ''
  }
}

watch(() => [props.modelValue, props.resource, props.slug], loadComments, { immediate: true })
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="admin-modal-backdrop" role="dialog" aria-modal="true" aria-label="评论管理" @click.self="close">
      <div class="admin-modal comment-modal">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="text-xs font-bold uppercase tracking-[.24em] text-slate-500">comments</p>
            <h2 class="mt-2 break-words text-2xl font-black text-slate-950">评论管理</h2>
            <div class="mt-3 grid gap-2 text-sm text-slate-600">
              <p><b class="text-slate-950">内容：</b>{{ title || '-' }}</p>
              <p><b class="text-slate-950">类型：</b>{{ typeLabel }} / {{ resource }}</p>
              <p class="break-all"><b class="text-slate-950">Slug：</b>{{ slug }}</p>
            </div>
          </div>
          <button type="button" class="admin-btn admin-btn-ghost" @click="close">关闭</button>
        </div>

        <p v-if="error" class="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{{ error }}</p>
        <p v-if="loading" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-8 text-center text-slate-500">评论加载中...</p>

        <div v-else class="mt-5 grid gap-3">
          <p v-if="!sortedComments.length" class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-8 text-center text-slate-500">当前内容暂无评论。</p>
          <article
            v-for="comment in sortedComments"
            :key="comment.id"
            class="comment-item"
            :class="replyTarget(comment) ? 'comment-item-reply' : ''"
          >
            <div class="flex gap-3">
              <img v-if="comment.avatar" :src="comment.avatar" alt="" class="h-10 w-10 rounded-full border border-slate-200 object-cover" loading="lazy" />
              <span v-else class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-slate-950 text-sm font-black text-white">{{ initials(comment) }}</span>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <a v-if="githubProfile(comment)" :href="githubProfile(comment)" target="_blank" rel="noreferrer" class="font-black text-slate-950 underline-offset-4 hover:underline">
                    {{ displayName(comment) }}
                  </a>
                  <b v-else class="text-slate-950">{{ displayName(comment) }}</b>
                  <span class="text-xs font-bold text-slate-500">{{ identityLine(comment) }}</span>
                </div>
                <p v-if="replyTarget(comment)" class="mt-1 text-xs font-bold text-slate-500">回复 @{{ replyAuthor(comment) }}</p>
                <p class="mt-2 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">{{ comment.content }}</p>
                <div class="mt-3 flex flex-wrap items-center justify-between gap-2">
                  <span class="text-xs font-bold text-slate-500">{{ formatTime(comment.created_at) }}</span>
                  <button
                    type="button"
                    class="admin-btn admin-btn-danger px-3 py-1.5 text-xs"
                    :disabled="deletingId === comment.id"
                    @click="deleteComment(comment)"
                  >
                    {{ deletingId === comment.id ? '删除中...' : '删除' }}
                  </button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </Teleport>
</template>
