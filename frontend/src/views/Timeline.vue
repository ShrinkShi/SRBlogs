<script setup lang="ts">
import { onMounted, ref } from 'vue'
import MomentTimeline from '@/components/MomentTimeline.vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
const items = ref<ContentItem[]>([])
const loading = ref(true)
const error = ref('')
useSeo({ title: '时间线', description: 'SRBlogs 的公开动态时间线。', path: '/timeline' })
async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await contentApi.list('moments')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '时间线加载失败'
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">时间线</h1>
      <p class="mt-3 text-white/56">按时间查看公开动态。</p>
    </GlassCard>
    <GlassCard v-if="loading"><p class="text-white/60">时间线加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!items.length"><p class="text-white/60">暂无时间线内容。</p></GlassCard>
    <MomentTimeline v-else :items="items" />
  </section>
</template>
