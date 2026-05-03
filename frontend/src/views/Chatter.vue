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
const loading = ref(true)
const error = ref('')

useSeo({ title: '杂谈', description: '长一点的念头，短一点的文章。', path: '/chatters' })

const filtered = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) => [item.meta.title, item.meta.summary, item.content, ...(item.meta.tags || [])].join(' ').toLowerCase().includes(q))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await contentApi.list('chatters')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '杂谈加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block">
      <div class="mx-auto max-w-3xl text-center">
        <p class="text-xs font-bold uppercase tracking-[.32em] text-fuchsia-100/45">chatters</p>
        <h1 class="mt-2 text-4xl font-black text-white">杂谈</h1>
        <p class="mt-3 text-white/56">长一点的念头，短一点的文章。</p>
        <div class="mx-auto mt-5 w-full max-w-4xl md:w-[65%]"><SearchBar v-model="keyword" /></div>
      </div>
    </GlassCard>
    <StateBlock v-if="loading" message="杂谈加载中..." />
    <StateBlock v-else-if="error" title="杂谈加载失败" :message="error" @retry="load" />
    <PostList v-else :items="filtered" base="/chatters" empty-text="暂无杂谈。" />
  </section>
</template>
