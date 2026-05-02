<script setup lang="ts">
import GlassCard from './GlassCard.vue'
import { formatDate } from '@/utils/date'
import type { ContentItem } from '@/types'
defineProps<{ items: ContentItem[] }>()
</script>

<template>
  <div class="relative ml-3 min-w-0 max-w-full border-l border-cyan-200/20 pl-7">
    <article v-for="item in items" :key="item.slug" class="relative mb-6 min-w-0">
      <span class="absolute -left-[37px] top-5 h-4 w-4 rounded-full border border-cyan-200/70 bg-cyan-300 shadow-[0_0_18px_rgba(34,211,238,.8)]"></span>
      <GlassCard hover>
        <RouterLink :to="`/moments/${item.slug}`">
          <p class="text-xs text-cyan-100/70">{{ formatDate(item.meta.date) }}</p>
          <h3 class="mt-2 text-xl font-black text-white">{{ item.meta.title }}</h3>
          <p class="mt-2 text-white/68">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
        </RouterLink>
      </GlassCard>
    </article>
  </div>
</template>
