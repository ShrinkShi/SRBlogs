<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import DiscoveryResultCard from '@/components/DiscoveryResultCard.vue'
import { contentApi } from '@/api/content'
import type { DiscoveryType, SearchResponse } from '@/types'
import { useSeo } from '@/composables/useSeo'

const route = useRoute()
const router = useRouter()
const tagName = computed(() => decodeURIComponent(String(route.params.tag || '')))
const type = ref<DiscoveryType>((route.query.type as DiscoveryType) || 'all')
const result = ref<SearchResponse>({ items: [], total: 0, limit: 50, offset: 0 })
const loading = ref(true)
const error = ref('')
const typeOptions: { label: string; value: DiscoveryType }[] = [
  { label: '全部', value: 'all' },
  { label: '文章', value: 'posts' },
  { label: '瞬间', value: 'moments' },
  { label: '杂谈', value: 'chatters' },
  { label: '项目', value: 'projects' }
]

useSeo({ title: () => `标签：${tagName.value}`, description: () => `浏览标签 ${tagName.value} 下的公开内容。`, path: () => `/tags/${encodeURIComponent(tagName.value)}` })

async function load() {
  loading.value = true
  error.value = ''
  try {
    result.value = await contentApi.search({ tag: tagName.value, type: type.value, limit: 50 })
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '标签内容加载失败'
  } finally {
    loading.value = false
  }
}

function chooseType(nextType: DiscoveryType) {
  type.value = nextType
  router.replace({ path: `/tags/${encodeURIComponent(tagName.value)}`, query: nextType === 'all' ? {} : { type: nextType } })
  load()
}

watch(() => route.params.tag, load)
onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block text-center">
      <RouterLink to="/tags" class="text-sm text-cyan-100/70 hover:text-cyan-100">返回标签索引</RouterLink>
      <h1 class="mt-3 break-words text-4xl font-black text-white"># {{ tagName }}</h1>
      <div class="mt-4 flex flex-wrap justify-center gap-2">
        <button v-for="option in typeOptions" :key="option.value" class="rounded-full border px-3 py-1 text-sm" :class="type === option.value ? 'border-cyan-200/50 bg-cyan-200/[0.16] text-cyan-100' : 'border-white/10 text-white/55 hover:bg-white/10'" @click="chooseType(option.value)">{{ option.label }}</button>
      </div>
    </GlassCard>
    <GlassCard v-if="loading"><p class="text-white/60">标签内容加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!result.items.length">
      <h2 class="text-xl font-black text-white">没有匹配内容</h2>
      <p class="mt-2 text-white/58">这个标签暂时没有公开内容。</p>
    </GlassCard>
    <div v-else class="grid min-w-0 gap-5 md:grid-cols-2">
      <DiscoveryResultCard v-for="item in result.items" :key="`${item.type}-${item.slug}-${item.title}`" :item="item" />
    </div>
  </section>
</template>
