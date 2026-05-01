<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { contentApi } from '@/api/content'
import GlassCard from './GlassCard.vue'
import type { CommentItem } from '@/types'

const props = defineProps<{ resource: 'posts' | 'moments' | 'chatters'; slug: string }>()
const comments = ref<CommentItem[]>([])
const loading = ref(false)
const form = reactive({ author: '', email: '', content: '' })

async function load() {
  comments.value = await contentApi.comments(props.resource, props.slug)
}
async function submit() {
  if (!form.author.trim() || !form.content.trim()) return
  loading.value = true
  try {
    const item = await contentApi.createComment(props.resource, props.slug, { ...form })
    comments.value.push(item)
    form.content = ''
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <GlassCard class="mt-8">
    <h3 class="text-xl font-black text-white">评论</h3>
    <div class="mt-4 grid gap-3">
      <div v-for="item in comments" :key="item.id" class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between text-sm"><b>{{ item.author }}</b><span class="text-white/45">{{ item.created_at }}</span></div>
        <p class="mt-2 whitespace-pre-wrap text-white/70">{{ item.content }}</p>
      </div>
      <p v-if="!comments.length" class="text-white/50">暂无评论。</p>
    </div>
    <form class="mt-5 grid gap-3" @submit.prevent="submit">
      <div class="grid gap-3 md:grid-cols-2">
        <input v-model="form.author" required maxlength="40" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="昵称" />
        <input v-model="form.email" maxlength="120" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="邮箱，可选" />
      </div>
      <textarea v-model="form.content" required maxlength="1000" rows="4" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="写下评论，禁止脚本内容"></textarea>
      <button :disabled="loading" class="w-fit rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950 disabled:opacity-50">发表评论</button>
    </form>
  </GlassCard>
</template>
