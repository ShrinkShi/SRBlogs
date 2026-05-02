<script setup lang="ts">
import type { ContentItem } from '@/types'
import GlassCard from './GlassCard.vue'
import SafeImage from './SafeImage.vue'
import { formatDate } from '@/utils/date'

withDefaults(defineProps<{ items: ContentItem[]; base: string; emptyText?: string }>(), {
  emptyText: '没有匹配内容。'
})

const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'
</script>
<template>
  <div class="grid gap-5 md:grid-cols-2">
    <RouterLink v-for="item in items" :key="item.slug" :to="`${base}/${item.slug}`" class="block">
      <GlassCard hover class="h-full">
        <div class="flex h-full flex-col gap-4">
          <div class="relative h-44 overflow-hidden rounded-[24px] bg-slate-900/60">
            <SafeImage :src="item.meta.cover" :fallback="fallbackCover" :alt="item.meta.title" img-class="h-full w-full object-cover opacity-85" />
            <div class="absolute inset-0 bg-gradient-to-b from-black/5 to-black/50"></div>
          </div>
          <div class="flex items-center justify-between gap-3 text-xs text-white/45"><span>{{ formatDate(item.meta.date) }}</span><span>{{ item.content.length }} chars</span></div>
          <h2 class="line-clamp-2 text-2xl font-black text-white">{{ item.meta.title }}</h2>
          <p class="line-clamp-3 flex-1 text-sm leading-7 text-white/58">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
          <div class="flex flex-wrap gap-2"><span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/15 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/65"># {{ tag }}</span></div>
        </div>
      </GlassCard>
    </RouterLink>
    <GlassCard v-if="!items.length"><p class="text-white/55">{{ emptyText }}</p></GlassCard>
  </div>
</template>
