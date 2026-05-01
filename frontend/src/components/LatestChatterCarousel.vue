<script setup lang="ts">
import type { ContentItem } from '@/types'
const props = defineProps<{ items: ContentItem[]; title?: string; description?: string }>()
</script>
<template>
  <section>
    <div class="mb-4 flex items-end justify-between gap-3">
      <div><p class="text-xs font-bold uppercase tracking-[.3em] text-fuchsia-100/45">cloud chatter</p><h2 class="mt-1 text-2xl font-black text-white">{{ props.title || '云端杂谈' }}</h2><p class="mt-1 text-sm text-white/48">{{ props.description || '长一点的念头，短一点的文章。' }}</p></div>
      <RouterLink to="/chatter" class="text-sm text-cyan-100/70 hover:text-cyan-100">进入杂谈</RouterLink>
    </div>
    <div class="grid gap-4 md:grid-cols-3">
      <RouterLink v-for="item in items" :key="item.slug" :to="`/chatter/${item.slug}`" class="glass glass-hover rounded-[30px] p-5">
        <p class="text-xs text-white/42">{{ item.meta.date }}</p>
        <h3 class="mt-2 line-clamp-2 text-xl font-black text-white">{{ item.meta.title }}</h3>
        <p class="mt-3 line-clamp-3 text-sm leading-6 text-white/56">{{ item.meta.summary || item.content.slice(0, 100) }}</p>
      </RouterLink>
    </div>
  </section>
</template>
