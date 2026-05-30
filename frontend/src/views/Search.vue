<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import StateBlock from '@/components/StateBlock.vue'
import DiscoveryResultCard from '@/components/DiscoveryResultCard.vue'
import { contentApi } from '@/api/content'
import type { DiscoveryType, SearchResponse, TagItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const route = useRoute()
const router = useRouter()
const q = ref(String(route.query.q || ''))
const type = ref<DiscoveryType>((route.query.type as DiscoveryType) || 'all')
const tag = ref(String(route.query.tag || ''))
const result = ref<SearchResponse>({ items: [], total: 0, limit: 20, offset: 0 })
const tags = ref<TagItem[]>([])
const loading = ref(false)
const error = ref('')

const typeOptions: { label: string; value: DiscoveryType }[] = [
  { label: '全部', value: 'all' },
  { label: '文章', value: 'posts' },
  { label: '说说', value: 'moments' },
  { label: '杂谈', value: 'chatters' },
  { label: '项目', value: 'projects' },
  { label: '相册', value: 'photos' },
  { label: '友链', value: 'friends' },
  { label: '音乐', value: 'music' }
]

useSeo({ title: () => q.value ? `搜索：${q.value}` : '全站搜索', description: '搜索 SRBlogs 的文章、说说、杂谈、项目、相册、友链和音乐。', path: () => `/search${window.location.search}` })

const activeQuery = computed(() => ({ q: q.value.trim(), type: type.value, tag: tag.value.trim() }))

function syncQuery() {
  router.replace({
    path: '/search',
    query: {
      ...(q.value.trim() ? { q: q.value.trim() } : {}),
      ...(type.value !== 'all' ? { type: type.value } : {}),
      ...(tag.value.trim() ? { tag: tag.value.trim() } : {})
    }
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    result.value = await contentApi.search({ ...activeQuery.value, limit: 40 })
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '搜索失败'
  } finally {
    loading.value = false
  }
}

function chooseTag(nextTag: string) {
  tag.value = tag.value === nextTag ? '' : nextTag
  syncQuery()
  load()
}

watch(() => route.query, () => {
  q.value = String(route.query.q || '')
  type.value = (route.query.type as DiscoveryType) || 'all'
  tag.value = String(route.query.tag || '')
  load()
})

onMounted(async () => {
  load()
  try {
    tags.value = await contentApi.tags()
  } catch {
    tags.value = []
  }
})
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">全站搜索</h1>
      <form class="search-input-theme mx-auto mt-5 flex w-full max-w-5xl items-center gap-2 rounded-[22px] border px-3 py-2 shadow-inner shadow-white/[0.04] transition md:w-[82%]" @submit.prevent="syncQuery(); load()">
        <input v-model="q" aria-label="搜索关键词" class="min-w-0 flex-1 bg-transparent text-sm outline-none" placeholder="搜索文章、说说、项目、音乐..." />
        <button type="submit" class="search-button-theme grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950/88 shadow-[0_8px_18px_rgba(0,0,0,.22)] transition hover:scale-105" aria-label="搜索">
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.6-3.6" />
          </svg>
        </button>
      </form>
      <div class="mt-4 flex flex-wrap gap-2">
        <button v-for="option in typeOptions" :key="option.value" class="filter-chip" :class="type === option.value ? 'filter-chip-active' : ''" @click="type = option.value; syncQuery(); load()">{{ option.label }}</button>
      </div>
      <div v-if="tags.length" class="mt-4 flex flex-wrap gap-2">
        <button v-for="item in tags.slice(0, 12)" :key="item.tag" class="filter-chip text-xs" :class="tag === item.tag ? 'filter-chip-active' : ''" @click="chooseTag(item.tag)"># {{ item.tag }} · {{ item.count }}</button>
      </div>
    </GlassCard>

    <StateBlock v-if="loading" message="搜索中..." />
    <StateBlock v-else-if="error" title="搜索失败" :message="error" @retry="load" />
    <GlassCard v-else-if="!result.items.length">
      <h2 class="text-xl font-black text-white">没有匹配内容</h2>
      <p class="mt-2 text-white/58">换一个关键词、类型或标签再试试。</p>
    </GlassCard>
    <div v-else class="grid min-w-0 gap-5 md:grid-cols-2">
      <DiscoveryResultCard v-for="item in result.items" :key="`${item.type}-${item.slug}-${item.title}`" :item="item" />
    </div>
  </section>
</template>
