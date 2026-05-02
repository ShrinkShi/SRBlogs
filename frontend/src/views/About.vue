<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { contentApi } from '@/api/content'
const content = ref('')
const loading = ref(true)
const error = ref('')
async function load() {
  loading.value = true
  error.value = ''
  try {
    content.value = (await contentApi.about()).content
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '关于页面加载失败'
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
<template>
  <section>
    <GlassCard v-if="loading"><p class="text-white/60">关于页面加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!content"><p class="text-white/60">暂无关于内容。</p></GlassCard>
    <GlassCard v-else>
      <MarkdownRenderer :content="content" />
    </GlassCard>
  </section>
</template>
