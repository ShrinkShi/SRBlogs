<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PostList from '@/components/PostList.vue'
import SearchBar from '@/components/SearchBar.vue'
import GlassCard from '@/components/GlassCard.vue'
import StateBlock from '@/components/StateBlock.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const items = ref<ContentItem[]>([])
const keyword = ref('')
const activeTag = ref('全部')
const loading = ref(true)
const error = ref('')

useSeo({
  title: '文章归档',
  description: '从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。',
  path: '/posts'
})

const tags = computed(() => ['全部', ...Array.from(new Set(items.value.flatMap((i) => i.meta.tags || [])))])
const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return items.value.filter((item) => {
    const tagOk = activeTag.value === '全部' || item.meta.tags?.includes(activeTag.value)
    const qOk = !q || [item.meta.title, item.meta.summary, item.content, ...(item.meta.tags || [])].join(' ').toLowerCase().includes(q)
    return tagOk && qOk
  })
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await contentApi.list('posts')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '文章加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="mx-auto max-w-3xl text-center">
        <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">archive</p>
        <h1 class="mt-2 text-4xl font-black text-white">文章归档</h1>
        <p class="mt-3 text-white/56">从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。</p>
        <div class="mx-auto mt-5 max-w-2xl"><SearchBar v-model="keyword" /></div>
        <div class="mt-4 flex flex-wrap justify-center gap-2">
          <button
            v-for="tag in tags"
            :key="tag"
            class="rounded-full border px-3 py-1 text-sm transition"
            :class="activeTag === tag ? 'border-cyan-200/40 bg-cyan-200/[0.15] text-cyan-100' : 'border-white/10 bg-white/[0.06] text-white/54 hover:bg-white/10'"
            @click="activeTag = tag"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </GlassCard>
    <StateBlock v-if="loading" message="文章加载中..." />
    <StateBlock v-else-if="error" title="文章加载失败" :message="error" @retry="load" />
    <PostList v-else :items="filtered" base="/posts" empty-text="暂无公开文章。" />
  </section>
</template>
