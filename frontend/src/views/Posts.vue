<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PostList from '@/components/PostList.vue'
import SearchBar from '@/components/SearchBar.vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import StateBlock from '@/components/StateBlock.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, PageConfig } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { formatDate } from '@/utils/date'
import { detectImageTone, type ImageTone } from '@/utils/imageTone'

type SectionKey = 'posts' | 'chatters'

const route = useRoute()
const router = useRouter()
const items = ref<ContentItem[]>([])
const keyword = ref('')
const activeTag = ref('全部')
const displayMode = ref<'grid' | 'link'>('grid')
const section = ref<SectionKey>(route.query.section === 'chatters' ? 'chatters' : 'posts')
const loading = ref(true)
const error = ref('')
const pageConfig = ref<PageConfig | null>(null)
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'
const toneMap = reactive<Record<string, ImageTone>>({})

const sectionConfig = computed(() => section.value === 'chatters'
  ? {
      title: pageConfig.value?.pageText?.chatters?.title || '云端杂谈',
      eyebrow: 'chatters',
      subtitle: pageConfig.value?.pageText?.chatters?.subtitle || '长一点的念头，短一点的文章。',
      base: '/chatters',
      empty: '暂无杂谈。'
    }
  : {
      title: pageConfig.value?.pageText?.posts?.title || '文章归档',
      eyebrow: 'archive',
      subtitle: pageConfig.value?.pageText?.posts?.subtitle || '从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。',
      base: '/posts',
      empty: '暂无公开文章。'
    })

useSeo({
  title: () => sectionConfig.value.title,
  description: () => sectionConfig.value.subtitle,
  path: () => `/posts?section=${section.value}`
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

watch(filtered, (list) => {
  list.forEach(async (item) => {
    toneMap[item.slug] = await detectImageTone(item.meta.cover || fallbackCover, 'dark')
  })
}, { immediate: true })

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await contentApi.list(section.value)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : `${sectionConfig.value.title}加载失败`
  } finally {
    loading.value = false
  }
}

function switchSection(next: SectionKey) {
  if (section.value === next) return
  section.value = next
  activeTag.value = '全部'
  keyword.value = ''
  router.replace({ path: '/posts', query: { section: next, mode: displayMode.value } })
}

function switchMode(next: 'grid' | 'link') {
  displayMode.value = next
  router.replace({ path: '/posts', query: { ...route.query, section: section.value, mode: next } })
}

watch(() => route.query.section, (value) => {
  const next = value === 'chatters' ? 'chatters' : 'posts'
  if (next !== section.value) section.value = next
})

watch(() => route.query.mode, (value) => {
  if (value === 'grid' || value === 'link') displayMode.value = value
})

watch(section, load)

onMounted(() => {
  if (route.query.mode === 'grid' || route.query.mode === 'link') displayMode.value = route.query.mode
  contentApi.json<PageConfig>('/pages/config').then((data) => { pageConfig.value = data }).catch(() => {})
  load()
})
</script>

<template>
  <section class="page-layout-grid">
    <GlassCard class="page-title-block">
      <div class="mx-auto max-w-5xl text-center">
        <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">{{ sectionConfig.eyebrow }}</p>
        <h1 class="mt-2 text-4xl font-black text-white">{{ sectionConfig.title }}</h1>
        <p class="mx-auto mt-3 max-w-2xl text-white/56">{{ sectionConfig.subtitle }}</p>
      </div>
    </GlassCard>

    <div class="flex justify-center">
      <div class="inline-flex shrink-0 rounded-full bg-white/[0.06] p-1">
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="section === 'posts' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="switchSection('posts')">正经</button>
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="section === 'chatters' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="switchSection('chatters')">杂谈</button>
      </div>
    </div>

    <div class="mx-auto w-full max-w-5xl md:w-[86%]">
      <SearchBar v-model="keyword" />
    </div>

    <div class="flex flex-wrap justify-center gap-2">
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

    <div class="flex justify-center">
      <div class="inline-flex rounded-full bg-white/[0.05] p-1">
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="displayMode === 'grid' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="switchMode('grid')">矩阵网格</button>
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="displayMode === 'link' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="switchMode('link')">中枢链路</button>
      </div>
    </div>

    <div>
      <StateBlock v-if="loading" :message="`${sectionConfig.title}加载中...`" />
      <StateBlock v-else-if="error" :title="`${sectionConfig.title}加载失败`" :message="error" @retry="load" />
      <PostList v-else-if="displayMode === 'grid'" :items="filtered" :base="sectionConfig.base" :empty-text="sectionConfig.empty" />
      <div v-else class="article-link-mode">
        <RouterLink
          v-for="(item, index) in filtered"
          :key="item.slug"
          :to="`${sectionConfig.base}/${item.slug}`"
          class="article-link-node"
          :class="index % 2 === 0 ? 'article-link-left' : 'article-link-right'"
        >
          <GlassCard hover class="post-card-theme h-full overflow-hidden !p-0" :class="toneMap[item.slug] === 'light' ? 'image-tone-light' : 'image-tone-dark'">
            <article class="flex h-full min-w-0 flex-col">
              <div class="relative h-48 overflow-hidden">
                <SafeImage :src="item.meta.cover" :fallback="fallbackCover" :alt="item.meta.title" img-class="h-full w-full object-cover transition duration-300 hover:scale-[1.035]" />
                <div class="image-contrast-overlay absolute inset-0"></div>
              </div>
              <div class="flex min-h-[16rem] flex-1 flex-col gap-3 p-5">
                <div class="flex flex-wrap items-center gap-2 text-xs text-white/45">
                  <span>{{ formatDate(item.meta.date) }}</span>
                  <span>{{ item.content.length }} chars</span>
                </div>
                <h2 class="line-clamp-2 text-xl font-black text-white">{{ item.meta.title }}</h2>
                <p class="line-clamp-3 text-sm leading-7 text-white/58">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
                <div class="mt-auto flex flex-wrap gap-2 pt-3">
                  <span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/15 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/65"># {{ tag }}</span>
                </div>
              </div>
            </article>
          </GlassCard>
        </RouterLink>
        <GlassCard v-if="!filtered.length"><p class="text-center text-white/55">{{ sectionConfig.empty }}</p></GlassCard>
      </div>
    </div>
  </section>
</template>
