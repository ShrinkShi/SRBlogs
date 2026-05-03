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
  { label: '瞬间', value: 'moments' },
  { label: '杂谈', value: 'chatters' },
  { label: '项目', value: 'projects' },
  { label: '照片', value: 'photos' },
  { label: '友链', value: 'friends' },
  { label: '音乐', value: 'music' }
]

useSeo({ title: () => q.value ? `搜索：${q.value}` : '全站搜索', description: '搜索 SRBlogs 的文章、瞬间、杂谈、项目、照片、友链和音乐。', path: () => `/search${window.location.search}` })

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
    <GlassCard class="text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">search</p>
      <h1 class="mt-2 text-4xl font-black text-white">全站搜索</h1>
      <form class="mt-5 grid gap-3 lg:grid-cols-[1fr_auto]" @submit.prevent="syncQuery(); load()">
        <input v-model="q" aria-label="搜索关键词" class="min-w-0 rounded-2xl border border-white/10 bg-white/[0.08] px-4 py-3 text-white outline-none placeholder:text-white/35" placeholder="搜索文章、瞬间、项目、音乐..." />
        <button type="submit" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950">搜索</button>
      </form>
      <div class="mt-4 flex flex-wrap gap-2">
        <button v-for="option in typeOptions" :key="option.value" class="rounded-full border px-3 py-1 text-sm" :class="type === option.value ? 'border-cyan-200/50 bg-cyan-200/[0.16] text-cyan-100' : 'border-white/10 text-white/55 hover:bg-white/10'" @click="type = option.value; syncQuery(); load()">{{ option.label }}</button>
      </div>
      <div v-if="tags.length" class="mt-4 flex flex-wrap gap-2">
        <button v-for="item in tags.slice(0, 12)" :key="item.tag" class="rounded-full border px-3 py-1 text-xs" :class="tag === item.tag ? 'border-fuchsia-200/50 bg-fuchsia-200/[0.16] text-fuchsia-100' : 'border-white/10 text-white/50 hover:bg-white/10'" @click="chooseTag(item.tag)"># {{ item.tag }} · {{ item.count }}</button>
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
