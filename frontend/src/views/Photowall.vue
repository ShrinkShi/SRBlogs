<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { PhotoItem } from '@/types'
const photos = ref<PhotoItem[]>([])
const active = ref<PhotoItem | null>(null)
onMounted(async () => { photos.value = await contentApi.json<PhotoItem[]>('/photos') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-pink-100/45">photowall</p>
      <h1 class="mt-2 text-4xl font-black text-white">照片墙</h1>
      <p class="mt-3 text-white/56">瀑布流预览 + 点击灯箱。图片 URL 可由后台上传后写入 JSON。</p>
    </GlassCard>
    <div class="columns-1 gap-5 md:columns-2 lg:columns-3">
      <button v-for="item in photos" :key="item.url" class="glass glass-hover mb-5 block w-full break-inside-avoid overflow-hidden rounded-[30px] text-left" @click="active = item">
        <img :src="item.url" loading="lazy" class="relative z-[1] w-full object-cover" />
        <div class="relative z-[1] p-4"><h3 class="font-bold text-white">{{ item.title }}</h3><p class="mt-1 text-sm text-white/55">{{ item.description }}</p></div>
      </button>
    </div>
    <div v-if="active" class="fixed inset-0 z-50 grid place-items-center bg-black/75 p-4 backdrop-blur-sm" @click="active = null">
      <div class="max-w-5xl"><img :src="active.url" class="max-h-[82vh] max-w-[92vw] rounded-3xl border border-white/15 object-contain" /><p class="mt-3 text-center text-white/70">{{ active.title }}</p></div>
    </div>
  </section>
</template>
