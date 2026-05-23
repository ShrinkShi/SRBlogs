<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
const error = ref('')
const resource = ref<CommentIndexItem['resource']>('posts')
const slug = ref('')

async function loadIndex(keepSelection = true) {
  error.value = ''
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
    await selectItem(current || next[0])
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言索引加载失败'
  } finally {
    loadingIndex.value = false
  }
}

async function loadComments(target: CommentIndexItem) {
  comments.value = []
  loadingComments.value = true
  try {
    comments.value = await adminApi.comments(target.resource, target.slug)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言加载失败'
  } finally {
    loadingComments.value = false
  }
}

async function selectItem(item: CommentIndexItem) {
  selected.value = item
  resource.value = item.resource
  slug.value = item.slug
  await loadComments(item)
}

async function manualLoad() {
  const value = slug.value.trim()
  if (!value) {
    error.value = 'slug 不能为空'
    return
  }
  await selectItem({ resource: resource.value, slug: value, count: 0, updatedAt: '', title: value })
}

async function remove(item: CommentItem) {
  if (!selected.value) return
  if (!confirm(`确认删除 ${item.author || '访客'} 的这条留言？`)) return
  deleting.value = item.id
  error.value = ''
  try {
    await adminApi.deleteComment(selected.value.resource, selected.value.slug, item.id)
    await loadComments(selected.value)
    await loadIndex(true)
    ui.show('留言已删除')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言删除失败'
  } finally {
    deleting.value = ''
  }
}

onMounted(() => loadIndex(false))
</script>

<template>
  <section class="grid gap-5">
    <div class="admin-card">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 class="text-2xl font-black text-slate-950">留言管理</h2>
        </div>
        <button :disabled="loadingIndex" class="admin-btn admin-btn-primary" type="button" @click="loadIndex(true)">
          {{ loadingIndex ? '刷新中...' : '刷新索引' }}
        </button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-700">{{ error }}</p>
    </div>

    <div class="grid gap-5 xl:grid-cols-[360px_1fr]">
      <div class="admin-card">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-lg font-black text-slate-950">有留言的内容</h3>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{{ indexItems.length }} 项</span>
        </div>
        <p v-if="loadingIndex" class="mt-5 text-slate-500">留言索引加载中...</p>
        <p v-else-if="!indexItems.length" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-500">暂无留言。</p>
        <div v-else class="mt-5 grid gap-2">
          <button
            v-for="item in indexItems"
            :key="`${item.resource}/${item.slug}`"
            type="button"
            class="rounded-xl border p-3 text-left transition"
            :class="selected?.resource === item.resource && selected?.slug === item.slug ? 'admin-active-option border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-400'"
            @click="selectItem(item)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <b class="block truncate">{{ item.title || item.slug }}</b>
                <p class="mt-1 truncate font-mono text-xs opacity-70">{{ item.resource }}/{{ item.slug }}</p>
              </div>
              <span class="rounded-full bg-white/15 px-2 py-1 text-xs font-bold">{{ item.count }}</span>
            </div>
          </button>
        </div>
      </div>

      <div class="grid gap-4">
        <div class="admin-card">
          <div class="grid gap-3 md:grid-cols-[160px_1fr_auto]">
            <select v-model="resource" class="admin-input">
              <option value="posts">posts</option>
              <option value="moments">moments</option>
              <option value="chatters">chatters</option>
              <option value="music">music</option>
              <option value="photos">photos</option>
            </select>
            <input v-model="slug" class="admin-input" placeholder="手动输入 slug 加载留言" @keyup.enter="manualLoad" />
            <button :disabled="loadingComments" class="admin-btn admin-btn-ghost" type="button" @click="manualLoad">加载</button>
          </div>
        </div>

        <div class="admin-card">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-lg font-black text-slate-950">留言列表</h3>
              <p v-if="selected" class="mt-1 font-mono text-xs text-slate-500">{{ selected.resource }}/{{ selected.slug }}</p>
            </div>
            <span v-if="selected" class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{{ comments.length }} 条</span>
          </div>

          <p v-if="loadingComments" class="mt-5 text-slate-500">留言加载中...</p>
          <p v-else-if="selected && !comments.length" class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-500">该内容暂无留言。</p>
          <div v-else-if="comments.length" class="mt-5 grid gap-3">
            <article v-for="item in comments" :key="item.id" class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2 text-sm">
                    <b class="text-slate-950">{{ item.author || '访客' }}</b>
                    <span class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{{ item.provider || 'legacy' }}</span>
                    <span class="text-slate-500">{{ item.created_at }}</span>
                  </div>
                  <p class="mt-3 whitespace-pre-wrap break-words text-slate-700">{{ item.content }}</p>
                </div>
                <button :disabled="deleting === item.id" class="admin-btn admin-btn-danger text-sm" type="button" @click="remove(item)">
                  {{ deleting === item.id ? '删除中...' : '删除' }}
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
