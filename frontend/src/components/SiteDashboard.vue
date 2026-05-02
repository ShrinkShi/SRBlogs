<script setup lang="ts">
import { computed } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null; posts: number; moments: number; chatters: number; projects: number }>()
const days = computed(() => {
  const start = props.settings?.buildDate ? new Date(props.settings.buildDate) : new Date()
  return Math.max(1, Math.ceil((Date.now() - start.getTime()) / 86400000))
})
</script>
<template>
  <GlassCard class="min-w-0">
    <div class="flex min-w-0 flex-wrap items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/50">site dashboard</p>
        <h2 class="mt-2 text-2xl font-black text-white">站点仪表盘</h2>
      </div>
      <span class="shrink-0 rounded-full border border-cyan-200/20 bg-cyan-200/10 px-3 py-1 text-xs text-cyan-100">运行 {{ days }} 天</span>
    </div>
    <div class="home-stats-grid mt-5">
      <div class="min-w-0 rounded-3xl bg-white/[0.08] p-4"><b class="block break-words text-3xl text-white">{{ posts }}</b><span class="text-xs text-white/45">文章</span></div>
      <div class="min-w-0 rounded-3xl bg-white/[0.08] p-4"><b class="block break-words text-3xl text-white">{{ moments }}</b><span class="text-xs text-white/45">瞬间</span></div>
      <div class="min-w-0 rounded-3xl bg-white/[0.08] p-4"><b class="block break-words text-3xl text-white">{{ chatters }}</b><span class="text-xs text-white/45">杂谈</span></div>
      <div class="min-w-0 rounded-3xl bg-white/[0.08] p-4"><b class="block break-words text-3xl text-white">{{ projects }}</b><span class="text-xs text-white/45">项目</span></div>
      <div class="min-w-0 rounded-3xl bg-white/[0.08] p-4"><b class="block break-words text-3xl text-white">{{ settings?.counts?.photos || 0 }}</b><span class="text-xs text-white/45">照片</span></div>
    </div>
  </GlassCard>
</template>
