<script setup lang="ts">
import type { ContentItem, SiteSettings } from '@/types'
import { formatDate } from '@/utils/date'
defineProps<{ items: ContentItem[]; settings?: SiteSettings | null }>()
</script>
<template>
  <section class="min-w-0 max-w-full">
    <div class="mb-4 flex min-w-0 flex-wrap items-end justify-between gap-3">
      <div class="min-w-0"><p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/45">latest posts</p><h2 class="mt-1 text-2xl font-black text-white">最新文章</h2></div>
      <RouterLink to="/posts" class="shrink-0 text-sm text-cyan-100/70 hover:text-cyan-100">查看全部</RouterLink>
    </div>
    <div class="grid min-w-0 max-w-full grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      <RouterLink v-for="item in items" :key="item.slug" :to="`/posts/${item.slug}`" class="glass sr-card sr-card-hover group min-w-0 overflow-hidden rounded-[30px]">
        <div class="h-40 bg-cover bg-center" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.05), rgba(0,0,0,.58)), url(${item.meta.cover || settings?.defaultPostCover || ''})` }"></div>
        <div class="relative z-[1] min-w-0 p-5">
          <p class="text-xs text-cyan-100/55">{{ formatDate(item.meta.date) }}</p>
          <h3 class="mt-2 line-clamp-2 text-xl font-black text-white group-hover:text-cyan-100">{{ item.meta.title }}</h3>
          <p class="mt-3 line-clamp-2 text-sm leading-6 text-white/55">{{ item.meta.summary || item.content.slice(0, 80) }}</p>
          <div class="mt-4 flex flex-wrap gap-2"><span v-for="tag in item.meta.tags?.slice(0,3)" :key="tag" class="sr-chip px-2 py-1 text-[11px]">#{{ tag }}</span></div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>
