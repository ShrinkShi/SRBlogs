<script setup lang="ts">
import type { ContentItem } from '@/types'
import GlassCard from './GlassCard.vue'
import { formatDate } from '@/utils/date'
defineProps<{ items: ContentItem[]; base: string }>()
</script>
<template>
  <div class="grid gap-5 md:grid-cols-2">
    <RouterLink v-for="item in items" :key="item.slug" :to="`${base}/${item.slug}`" class="block">
      <GlassCard hover class="h-full">
        <div class="flex h-full flex-col gap-4">
          <div v-if="item.meta.cover" class="h-44 rounded-[24px] bg-cover bg-center" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.08), rgba(0,0,0,.45)), url(${item.meta.cover})` }"></div>
          <div class="flex items-center justify-between gap-3 text-xs text-white/45"><span>{{ formatDate(item.meta.date) }}</span><span>{{ item.content.length }} chars</span></div>
          <h2 class="line-clamp-2 text-2xl font-black text-white">{{ item.meta.title }}</h2>
          <p class="line-clamp-3 flex-1 text-sm leading-7 text-white/58">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
          <div class="flex flex-wrap gap-2"><span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/15 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/65"># {{ tag }}</span></div>
        </div>
      </GlassCard>
    </RouterLink>
    <GlassCard v-if="!items.length"><p class="text-white/55">没有匹配内容。</p></GlassCard>
  </div>
</template>
