<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { contentApi } from '@/api/content'
import GlassCard from './GlassCard.vue'
import type { CommentItem } from '@/types'

const props = defineProps<{ resource: 'posts' | 'moments' | 'chatters'; slug: string }>()
const comments = ref<CommentItem[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ author: '', email: '', content: '' })
const showDebug = import.meta.env.DEV

async function load() {
  loading.value = true
  error.value = ''
  try {
    comments.value = await contentApi.comments(props.resource, props.slug)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论加载失败'
  } finally {
    loading.value = false
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  if (!form.author.trim() || !form.content.trim()) {
    error.value = '昵称和评论内容不能为空。'
    return
  }
  if (form.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    error.value = '邮箱格式不正确。'
    return
  }
  submitting.value = true
  try {
    const item = await contentApi.createComment(props.resource, props.slug, { ...form })
    comments.value.push(item)
    form.content = ''
    success.value = '评论已提交。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论提交失败'
  } finally {
    submitting.value = false
  }
}

onMounted(load)
watch(() => props.slug, load)
</script>

<template>
  <GlassCard class="mt-8">
    <div class="flex items-center justify-between gap-3">
      <h3 class="text-xl font-black text-white">评论</h3>
      <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/50">{{ comments.length }} 条</span>
    </div>
    <p v-if="showDebug" class="mt-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-cyan-100/55">
      DEV comments target: {{ props.resource }}/{{ props.slug }}
    </p>
    <p v-if="loading" class="mt-4 text-white/50">评论加载中...</p>
    <div v-else class="mt-4 grid gap-3">
      <div v-for="item in comments" :key="item.id" class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between gap-3 text-sm"><b>{{ item.author }}</b><span class="text-white/45">{{ item.created_at }}</span></div>
        <p class="mt-2 whitespace-pre-wrap break-words text-white/70">{{ item.content }}</p>
      </div>
      <p v-if="!comments.length" class="text-white/50">暂无评论。</p>
    </div>
    <form class="mt-5 grid gap-3" @submit.prevent="submit">
      <div class="grid gap-3 md:grid-cols-2">
        <input v-model="form.author" required maxlength="40" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="昵称" />
        <input v-model="form.email" maxlength="120" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="邮箱，可选" />
      </div>
      <textarea v-model="form.content" required maxlength="1000" rows="4" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="写下评论，HTML 会被后端清洗"></textarea>
      <div class="flex flex-wrap items-center gap-3">
        <button :disabled="submitting" class="w-fit rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950 disabled:opacity-50">{{ submitting ? '提交中...' : '发表评论' }}</button>
        <span v-if="success" class="text-sm text-emerald-200/80">{{ success }}</span>
        <span v-if="error" class="text-sm text-red-200/80">{{ error }}</span>
      </div>
    </form>
  </GlassCard>
</template>
