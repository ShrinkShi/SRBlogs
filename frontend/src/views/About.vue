<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { contentApi } from '@/api/content'
import { useSeo } from '@/composables/useSeo'
import type { PageConfig } from '@/types'
const content = ref('')
const loading = ref(true)
const error = ref('')
const pageConfig = ref<PageConfig | null>(null)
const pageTitle = computed(() => pageConfig.value?.pageText?.about?.title || '关于')
const pageSubtitle = computed(() => pageConfig.value?.pageText?.about?.subtitle || '关于 SRBlogs 与站点作者。')
useSeo({ title: () => pageTitle.value, description: () => pageSubtitle.value, path: '/about' })
async function load() {
  loading.value = true
  error.value = ''
  try {
    const [aboutData, publicSettings] = await Promise.all([
      contentApi.about(),
      contentApi.json<PageConfig>('/pages/config')
    ])
    content.value = aboutData.content
    pageConfig.value = publicSettings
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '关于页面加载失败'
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
<template>
  <section class="page-layout-grid">
    <GlassCard class="page-title-block text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">about</p>
      <h1 class="mt-2 text-4xl font-black text-white">{{ pageTitle }}</h1>
      <p class="mt-3 text-white/56">{{ pageSubtitle }}</p>
    </GlassCard>
    <div>
      <GlassCard v-if="loading"><p class="text-white/60">关于页面加载中...</p></GlassCard>
      <GlassCard v-else-if="error">
        <p class="text-red-200/85">{{ error }}</p>
        <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
      </GlassCard>
      <GlassCard v-else-if="!content"><p class="text-white/60">暂无关于内容。</p></GlassCard>
      <GlassCard v-else>
        <div class="mb-5 flex flex-wrap gap-3">
          <a href="/api/rss.xml" target="_blank" rel="noopener noreferrer" class="rounded-2xl border border-orange-200/20 bg-orange-300/[0.1] px-4 py-2 text-sm font-bold text-orange-100 hover:bg-orange-300/[0.16]">RSS 订阅</a>
          <a href="/api/sitemap.xml" target="_blank" rel="noopener noreferrer" class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/68 hover:bg-white/10">Sitemap</a>
        </div>
        <MarkdownRenderer :content="content" />
      </GlassCard>
    </div>
  </section>
</template>
