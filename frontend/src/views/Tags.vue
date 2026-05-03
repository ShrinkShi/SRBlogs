<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { TagItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const tags = ref<TagItem[]>([])
const loading = ref(true)
const error = ref('')
useSeo({ title: '标签', description: '浏览 SRBlogs 的内容标签索引。', path: '/tags' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    tags.value = await contentApi.tags()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '标签加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">tags</p>
      <h1 class="mt-2 text-4xl font-black text-white">标签索引</h1>
      <p class="mt-3 text-white/56">标签合并文章、瞬间、杂谈和项目数据，点击后进入对应内容列表。</p>
    </GlassCard>
    <GlassCard v-if="loading"><p class="text-white/60">标签加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!tags.length"><p class="text-white/60">暂无标签。</p></GlassCard>
    <div v-else class="grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <RouterLink v-for="item in tags" :key="item.tag" :to="`/tags/${encodeURIComponent(item.tag)}`" class="glass glass-hover min-w-0 rounded-[28px] p-5">
        <div class="flex min-w-0 items-start justify-between gap-4">
          <h2 class="break-words text-2xl font-black text-white"># {{ item.tag }}</h2>
          <span class="shrink-0 rounded-full bg-cyan-200/[0.12] px-3 py-1 text-sm text-cyan-100">{{ item.count }}</span>
        </div>
        <p class="mt-3 text-sm text-white/45">{{ item.types.join(' / ') || 'content' }}</p>
        <p v-if="item.latestDate" class="mt-2 text-xs text-white/35">最近：{{ item.latestDate }}</p>
      </RouterLink>
    </div>
  </section>
</template>
