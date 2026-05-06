<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { ContentItem } from '@/types'
import GlassCard from './GlassCard.vue'
import SafeImage from './SafeImage.vue'
import { formatDate } from '@/utils/date'
import { detectImageTone, type ImageTone } from '@/utils/imageTone'

const props = withDefaults(defineProps<{ items: ContentItem[]; base: string; emptyText?: string }>(), {
  emptyText: '没有匹配内容。'
})

const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'
const toneMap = reactive<Record<string, ImageTone>>({})

watch(() => props.items, (items) => {
  items.forEach(async (item) => {
    toneMap[item.slug] = await detectImageTone(item.meta.cover || fallbackCover, 'dark')
  })
}, { immediate: true, deep: true })
</script>

<template>
  <div class="grid min-w-0 gap-5 sm:grid-cols-2 xl:grid-cols-3">
    <RouterLink v-for="item in items" :key="item.slug" :to="`${base}/${item.slug}`" class="block min-w-0">
      <GlassCard hover class="post-card-theme h-full overflow-hidden !p-0" :class="toneMap[item.slug] === 'light' ? 'image-tone-light' : 'image-tone-dark'">
        <article class="flex h-full min-w-0 flex-col">
          <div class="relative h-48 overflow-hidden bg-slate-900/60">
            <SafeImage
              :src="item.meta.cover"
              :fallback="fallbackCover"
              :alt="item.meta.title"
              img-class="h-full w-full object-cover opacity-90 transition duration-300 hover:scale-[1.035]"
            />
            <div class="image-contrast-overlay absolute inset-0"></div>
          </div>
          <div class="flex min-h-[16rem] flex-1 flex-col gap-3 p-5">
            <div class="flex items-center justify-between gap-3 text-xs text-white/45">
              <span>{{ formatDate(item.meta.date) }}</span>
              <span>{{ item.content.length }} chars</span>
            </div>
            <h2 class="line-clamp-2 text-xl font-black text-white">{{ item.meta.title }}</h2>
            <p class="line-clamp-3 text-sm leading-7 text-white/58">{{ item.meta.summary || item.content.slice(0, 120) }}</p>
            <div class="mt-auto flex flex-wrap gap-2 pt-3">
              <span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/15 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/65"># {{ tag }}</span>
            </div>
          </div>
        </article>
      </GlassCard>
    </RouterLink>
    <GlassCard v-if="!items.length" class="sm:col-span-2 xl:col-span-3">
      <p class="text-center text-white/55">{{ emptyText }}</p>
    </GlassCard>
  </div>
</template>
