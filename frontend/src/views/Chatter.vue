<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PostList from '@/components/PostList.vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
const items = ref<ContentItem[]>([])
const loading = ref(true)
const error = ref('')
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
    <GlassCard>
      <h1 class="text-4xl font-black text-white">碎碎念</h1>
      <p class="mt-3 text-white/56">长一点的念头，短一点的文章。</p>
    </GlassCard>
    <GlassCard v-if="loading"><p class="text-white/60">杂谈加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <PostList v-else :items="items" base="/chatters" empty-text="暂无杂谈。" />
  </section>
</template>
