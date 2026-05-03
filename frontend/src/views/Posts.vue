<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PostList from '@/components/PostList.vue'
import SearchBar from '@/components/SearchBar.vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import StateBlock from '@/components/StateBlock.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { formatDate } from '@/utils/date'

const items = ref<ContentItem[]>([])
const keyword = ref('')
const activeTag = ref('全部')
const displayMode = ref<'grid' | 'link'>('grid')
const loading = ref(true)
const error = ref('')
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'

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
        <div class="mt-5 inline-flex rounded-full bg-white/[0.05] p-1">
          <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="displayMode === 'grid' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="displayMode = 'grid'">矩阵网格</button>
          <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="displayMode === 'link' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="displayMode = 'link'">中枢链路</button>
        </div>
      </div>
    </GlassCard>
    <StateBlock v-if="loading" message="文章加载中..." />
    <StateBlock v-else-if="error" title="文章加载失败" :message="error" @retry="load" />
    <PostList v-else-if="displayMode === 'grid'" :items="filtered" base="/posts" empty-text="暂无公开文章。" />
    <div v-else class="article-link-mode">
      <RouterLink
        v-for="(item, index) in filtered"
        :key="item.slug"
        :to="`/posts/${item.slug}`"
        class="article-link-node"
        :class="index % 2 === 0 ? 'article-link-left' : 'article-link-right'"
      >
        <GlassCard hover class="h-full overflow-hidden !p-0">
          <article class="grid min-w-0 gap-4 md:grid-cols-[11rem_minmax(0,1fr)]">
            <div class="relative h-44 overflow-hidden md:h-full">
              <SafeImage :src="item.meta.cover" :fallback="fallbackCover" :alt="item.meta.title" img-class="h-full w-full object-cover transition duration-300 hover:scale-[1.035]" />
              <div class="absolute inset-0 bg-gradient-to-b from-black/0 to-black/45"></div>
            </div>
            <div class="flex min-h-[12rem] flex-col gap-3 p-5">
              <div class="flex flex-wrap items-center gap-2 text-xs text-white/45">
                <span>{{ formatDate(item.meta.date) }}</span>
                <span>{{ item.content.length }} chars</span>
              </div>
              <h2 class="line-clamp-2 text-2xl font-black text-white">{{ item.meta.title }}</h2>
              <p class="line-clamp-3 text-sm leading-7 text-white/58">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
              <div class="mt-auto flex flex-wrap gap-2 pt-3">
                <span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/15 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/65"># {{ tag }}</span>
              </div>
            </div>
          </article>
        </GlassCard>
      </RouterLink>
      <GlassCard v-if="!filtered.length"><p class="text-center text-white/55">暂无公开文章。</p></GlassCard>
    </div>
  </section>
</template>
