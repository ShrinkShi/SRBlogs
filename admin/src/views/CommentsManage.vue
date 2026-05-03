<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { CommentIndexItem, CommentItem } from '@/types'

const ui = useUiStore()
const indexItems = ref<CommentIndexItem[]>([])
const selected = ref<CommentIndexItem | null>(null)
const comments = ref<CommentItem[]>([])
const loadingIndex = ref(false)
const loadingComments = ref(false)
const deleting = ref('')
const indexError = ref('')
const commentsError = ref('')
const advancedResource = ref<'posts' | 'moments' | 'chatters' | 'music' | 'photos'>('posts')
const advancedSlug = ref('')

function readableError(exc: unknown, fallback: string) {
  const message = exc instanceof Error ? exc.message : fallback
  if (/not found/i.test(message) || message.includes('404')) {
    return `${message}。请确认后端已重启到最新代码，并且 /api/admin/comments/index 已出现在 /docs。`
  }
  return message
}

async function loadIndex(keepSelection = true) {
  indexError.value = ''
  loadingIndex.value = true
  try {
    const next = await adminApi.commentsIndex()
    indexItems.value = next
    if (!next.length) {
      selected.value = null
      comments.value = []
      return
    }

    const current = keepSelection && selected.value
      ? next.find((item) => item.resource === selected.value?.resource && item.slug === selected.value?.slug)
      : null
    if (current) {
      selected.value = current
    } else if (!selected.value) {
      await selectItem(next[0])
    } else {
      selected.value = null
      comments.value = []
    }
  } catch (exc) {
    indexError.value = readableError(exc, '评论索引加载失败')
  } finally {
    loadingIndex.value = false
  }
}

async function loadComments(resource: 'posts' | 'moments' | 'chatters' | 'music' | 'photos', slug: string) {
  commentsError.value = ''
  comments.value = []
  loadingComments.value = true
  try {
    comments.value = await adminApi.comments(resource, slug)
  } catch (exc) {
    commentsError.value = readableError(exc, '评论加载失败')
  } finally {
    loadingComments.value = false
  }
}

async function selectItem(item: CommentIndexItem) {
  selected.value = item
  advancedResource.value = item.resource
  advancedSlug.value = item.slug
  await loadComments(item.resource, item.slug)
}

async function advancedLoad() {
  const slug = advancedSlug.value.trim()
  if (!slug) {
    commentsError.value = 'slug 不能为空。'
    return
  }
  const item: CommentIndexItem = {
    resource: advancedResource.value,
    slug,
    count: 0,
    updatedAt: '',
    title: slug
  }
  selected.value = item
  await loadComments(item.resource, item.slug)
}

async function remove(item: CommentItem) {
  if (!selected.value) return
  if (!window.confirm(`确认删除 ${item.author} 的这条评论？删除会立即写回后端评论文件，并在覆盖前生成备份。`)) return

  commentsError.value = ''
  deleting.value = item.id
  const target = selected.value
  try {
    await adminApi.deleteComment(target.resource, target.slug, item.id)
    await loadComments(target.resource, target.slug)
    await loadIndex(true)
    ui.show('评论已删除，索引和列表已刷新')
  } catch (exc) {
    commentsError.value = readableError(exc, '评论删除失败')
  } finally {
    deleting.value = ''
  }
}

async function deleteMissingForCheck() {
  if (!selected.value) {
    commentsError.value = '请先选择一个评论目标。'
    return
  }
  commentsError.value = ''
  try {
    await adminApi.deleteComment(selected.value.resource, selected.value.slug, 'missing-comment-id')
  } catch (exc) {
    commentsError.value = readableError(exc, '评论删除失败')
  }
}

onMounted(() => loadIndex(false))
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1] flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-sm font-bold uppercase tracking-[.32em] text-cyan-100/45">comments</p>
          <h1 class="mt-2 text-4xl font-black text-white">评论管理</h1>
          <p class="mt-3 max-w-3xl text-white/56">默认展示已有评论的内容索引。评论管理暂不进入 pendingOperations，删除会直接写回后端 JSON 并在覆盖前备份。</p>
        </div>
        <button :disabled="loadingIndex" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="loadIndex(true)">
          {{ loadingIndex ? '刷新中...' : '刷新索引' }}
        </button>
      </div>
      <p v-if="indexError" class="relative z-[1] mt-3 text-sm text-red-200/80">{{ indexError }}</p>
    </GlassCard>

    <div class="grid gap-5 xl:grid-cols-[380px_1fr]">
      <GlassCard class="min-w-0">
        <div class="relative z-[1] flex items-center justify-between gap-3">
          <h2 class="text-lg font-black text-white">有评论的内容</h2>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/50">{{ indexItems.length }} 项</span>
        </div>

        <p v-if="loadingIndex" class="relative z-[1] mt-5 text-white/55">评论索引加载中...</p>
        <p v-else-if="!indexItems.length" class="relative z-[1] mt-5 rounded-2xl border border-white/10 bg-white/5 p-4 text-white/55">暂无任何评论。</p>
        <div v-else class="relative z-[1] mt-5 grid gap-3">
          <button
            v-for="item in indexItems"
            :key="`${item.resource}/${item.slug}`"
            type="button"
            class="rounded-2xl border p-4 text-left transition"
            :class="selected?.resource === item.resource && selected?.slug === item.slug ? 'border-cyan-200/55 bg-cyan-300/12' : 'border-white/10 bg-white/5 hover:border-white/22 hover:bg-white/8'"
            @click="selectItem(item)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate font-bold text-white">{{ item.title || item.slug }}</p>
                <p class="mt-1 truncate font-mono text-xs text-cyan-100/50">{{ item.resource }}/{{ item.slug }}</p>
              </div>
              <span class="shrink-0 rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-white/68">{{ item.count }}</span>
            </div>
            <p class="mt-3 text-xs text-white/42">最近更新：{{ item.updatedAt || '未知' }}</p>
          </button>
        </div>
      </GlassCard>

      <div class="grid min-w-0 gap-4">
        <GlassCard>
          <div class="relative z-[1] flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-black text-white">评论列表</h2>
            <p v-if="selected" class="mt-2 font-mono text-xs text-cyan-100/55">当前请求：{{ selected.resource }}/{{ selected.slug }}</p>
            <p v-else class="mt-2 text-sm text-white/52">请从左侧选择一项。</p>
          </div>
        </div>
          <p v-if="commentsError" class="relative z-[1] mt-3 text-sm text-red-200/80">{{ commentsError }}</p>

          <details class="relative z-[1] mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
            <summary class="cursor-pointer text-sm font-bold text-white/68">高级加载</summary>
            <div class="mt-4 grid gap-3 md:grid-cols-[160px_1fr_auto]">
              <select v-model="advancedResource" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none">
                <option value="posts">posts</option>
                <option value="moments">moments</option>
                <option value="chatters">chatters</option>
                <option value="music">music</option>
                <option value="photos">photos</option>
              </select>
              <input v-model="advancedSlug" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="slug" @keyup.enter="advancedLoad" />
              <button :disabled="loadingComments" class="rounded-2xl border border-white/12 px-5 py-3 font-bold text-white/72 disabled:opacity-50" @click="advancedLoad">
                {{ loadingComments ? '加载中...' : '加载' }}
              </button>
            </div>
            <button v-if="selected" class="mt-3 rounded-2xl border border-white/12 px-4 py-2 text-sm font-bold text-white/68 hover:bg-white/8" type="button" @click="deleteMissingForCheck">
              验证删除不存在评论的错误提示
            </button>
          </details>
        </GlassCard>

        <GlassCard v-if="loadingComments"><p class="relative z-[1] text-white/60">评论加载中...</p></GlassCard>
        <GlassCard v-else-if="selected && !comments.length"><p class="relative z-[1] text-white/60">该内容当前没有评论。</p></GlassCard>
        <div v-else-if="comments.length" class="grid gap-3">
          <GlassCard v-for="item in comments" :key="item.id">
            <div class="relative z-[1] flex flex-wrap items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <b class="text-white">{{ item.author }}</b>
                  <span v-if="item.email" class="break-all text-white/40">{{ item.email }}</span>
                  <span class="text-white/40">{{ item.created_at }}</span>
                </div>
                <p class="mt-3 whitespace-pre-wrap break-words text-white/70">{{ item.content }}</p>
              </div>
              <button :disabled="deleting === item.id" class="rounded-2xl border border-red-200/25 px-4 py-2 text-sm text-red-100 hover:bg-red-300/10 disabled:opacity-50" @click="remove(item)">
                {{ deleting === item.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  </section>
</template>
