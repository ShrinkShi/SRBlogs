<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PostList from '@/components/PostList.vue'
import SearchBar from '@/components/SearchBar.vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
const items = ref<ContentItem[]>([])
const keyword = ref('')
const activeTag = ref('全部')
const tags = computed(() => ['全部', ...Array.from(new Set(items.value.flatMap((i) => i.meta.tags || [])))])
const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return items.value.filter((i) => {
    const tagOk = activeTag.value === '全部' || i.meta.tags?.includes(activeTag.value)
    const qOk = !q || [i.meta.title, i.meta.summary, i.content, ...(i.meta.tags || [])].join(' ').toLowerCase().includes(q)
    return tagOk && qOk
  })
})
onMounted(async () => { items.value = await contentApi.list('posts') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">archive</p>
      <h1 class="mt-2 text-4xl font-black text-white">文章归档</h1>
      <p class="mt-3 text-white/56">按标题、标签、正文检索。这里保持 Vue3 SPA 架构，数据仍由 FastAPI 读取 Markdown 文件。</p>
      <div class="mt-5"><SearchBar v-model="keyword" /></div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button v-for="tag in tags" :key="tag" class="rounded-full border px-3 py-1 text-sm transition" :class="activeTag === tag ? 'border-cyan-200/40 bg-cyan-200/[0.15] text-cyan-100' : 'border-white/10 bg-white/[0.06] text-white/54 hover:bg-white/10'" @click="activeTag = tag">{{ tag }}</button>
      </div>
    </GlassCard>
    <PostList :items="filtered" base="/posts" />
  </section>
</template>
