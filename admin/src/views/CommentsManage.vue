<script setup lang="ts">
import { ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { CommentItem } from '@/types'

const ui = useUiStore()
const resource = ref<'posts' | 'moments' | 'chatters'>('posts')
const slug = ref('vue-fastapi-blog')
const comments = ref<CommentItem[]>([])
const loading = ref(false)
const deleting = ref('')
const error = ref('')

async function load() {
  error.value = ''
  comments.value = []
  if (!slug.value.trim()) {
    error.value = 'slug 不能为空。'
    return
  }
  loading.value = true
  try {
    comments.value = await adminApi.comments(resource.value, slug.value.trim())
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论加载失败'
  } finally {
    loading.value = false
  }
}

async function remove(item: CommentItem) {
  error.value = ''
  deleting.value = item.id
  try {
    await adminApi.deleteComment(resource.value, slug.value.trim(), item.id)
    comments.value = comments.value.filter((comment) => comment.id !== item.id)
    ui.show('评论已删除')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论删除失败'
  } finally {
    deleting.value = ''
  }
}
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-sm font-bold uppercase tracking-[.32em] text-cyan-100/45">comments</p>
      <h1 class="mt-2 text-4xl font-black text-white">评论管理</h1>
      <p class="mt-3 text-white/56">本地评论管理最小版。当前支持按 resource/slug 查看和删除评论；隐藏/恢复后续再做。</p>
      <div class="mt-5 grid gap-3 md:grid-cols-[180px_1fr_auto]">
        <select v-model="resource" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none">
          <option value="posts">posts</option>
          <option value="moments">moments</option>
          <option value="chatters">chatters</option>
        </select>
        <input v-model="slug" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="slug" @keyup.enter="load" />
        <button :disabled="loading" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="load">{{ loading ? '加载中...' : '加载评论' }}</button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-200/80">{{ error }}</p>
    </GlassCard>

    <GlassCard v-if="loading"><p class="text-white/60">评论加载中...</p></GlassCard>
    <GlassCard v-else-if="!comments.length"><p class="text-white/60">暂无评论。</p></GlassCard>
    <div v-else class="grid gap-3">
      <GlassCard v-for="item in comments" :key="item.id">
        <div class="relative z-[1] flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex flex-wrap items-center gap-2 text-sm">
              <b class="text-white">{{ item.author }}</b>
              <span v-if="item.email" class="text-white/40">{{ item.email }}</span>
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
  </section>
</template>
