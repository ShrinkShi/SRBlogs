<script setup lang="ts">
import GlassCard from './GlassCard.vue'
import type { SearchResultItem } from '@/types'

defineProps<{ item: SearchResultItem }>()

const typeLabels: Record<string, string> = {
  posts: '文章',
  moments: '瞬间',
  chatters: '杂谈',
  projects: '项目',
  photos: '照片',
  friends: '友链',
  music: '音乐'
}
</script>

<template>
  <RouterLink :to="item.url" class="block min-w-0">
    <GlassCard hover class="flex h-full flex-col">
      <div class="flex min-w-0 flex-wrap items-center gap-2">
        <span class="rounded-full border border-cyan-200/20 bg-cyan-200/[0.1] px-3 py-1 text-xs font-bold text-cyan-100">{{ typeLabels[item.type] || item.type }}</span>
        <span v-if="item.date" class="text-xs text-white/42">{{ item.date }}</span>
      </div>
      <h2 class="mt-3 break-words text-2xl font-black text-white">{{ item.title }}</h2>
      <p v-if="item.summary" class="mt-3 line-clamp-3 break-words text-sm leading-7 text-white/58">{{ item.summary }}</p>
      <div v-if="item.tags?.length" class="mt-auto flex flex-wrap gap-2 pt-4">
        <span
          v-for="tag in item.tags"
          :key="tag"
          class="rounded-full border border-white/10 px-3 py-1 text-xs text-white/56"
        >
          # {{ tag }}
        </span>
      </div>
    </GlassCard>
  </RouterLink>
</template>
