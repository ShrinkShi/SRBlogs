<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { PhotoAlbum, PhotoItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const rawPhotos = ref<Array<PhotoItem | PhotoAlbum>>([])
const activeAlbum = ref<PhotoAlbum | null>(null)
const active = ref<PhotoItem | null>(null)
const loading = ref(false)
const error = ref('')
useSeo({ title: '照片墙', description: 'SRBlogs 的照片墙、图片记录和预览。', path: '/photowall' })

function normalizeAlbum(item: PhotoItem | PhotoAlbum, index: number): PhotoAlbum {
  if ('photos' in item && Array.isArray(item.photos)) {
    const photos = item.photos.slice(0, 50)
    return {
      ...item,
      title: item.title || `相册 ${index + 1}`,
      cover: item.cover || photos[0]?.url || '',
      photos
    }
  }
  const photo = item as PhotoItem
  return {
    title: photo.title || `相册 ${index + 1}`,
    description: photo.description,
    cover: photo.url,
    date: photo.date,
    tags: photo.tags,
    photos: [photo]
  }
}

const albums = computed(() => rawPhotos.value.map(normalizeAlbum).filter((album) => album.photos.length || album.cover))

async function load() {
  loading.value = true
  error.value = ''
  try {
    rawPhotos.value = await contentApi.json<Array<PhotoItem | PhotoAlbum>>('/photos')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '照片加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-pink-100/45">photowall</p>
      <h1 class="mt-2 text-4xl font-black text-white">照片墙</h1>
      <p class="mt-3 text-white/56">图片记录从后端 JSON 动态读取，点击图片可放大预览。</p>
    </GlassCard>

    <GlassCard v-if="loading">
      <p class="text-white/60">照片加载中...</p>
    </GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!albums.length">
      <p class="text-white/60">暂无相册。</p>
    </GlassCard>

    <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <button
        v-for="album in albums"
        :key="album.title + album.cover"
        type="button"
        class="glass glass-hover block w-full overflow-hidden rounded-[30px] text-left"
        :aria-label="`打开相册：${album.title}`"
        @click="activeAlbum = album; active = album.photos[0] || null"
      >
        <SafeImage :src="album.cover || album.photos[0]?.url" :alt="album.title || 'album'" img-class="relative z-[1] aspect-[4/3] w-full object-cover" />
        <div class="relative z-[1] p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h3 class="break-words font-bold text-white">{{ album.title || '未命名相册' }}</h3>
            <span v-if="album.date" class="text-xs text-white/42">{{ album.date }}</span>
          </div>
          <p class="mt-1 text-xs text-white/42">{{ album.photos.length }} 张照片</p>
          <p v-if="album.description" class="mt-1 break-words text-sm leading-6 text-white/55">{{ album.description }}</p>
          <div v-if="album.tags?.length" class="mt-3 flex flex-wrap gap-2">
            <span v-for="tag in album.tags" :key="tag" class="rounded-full border border-white/10 px-2 py-1 text-[11px] text-white/50">#{{ tag }}</span>
          </div>
        </div>
      </button>
    </div>

    <div
      v-if="activeAlbum"
      class="fixed inset-0 z-50 grid place-items-center bg-black/75 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      @click="activeAlbum = null; active = null"
      @keydown.esc.window="activeAlbum = null; active = null"
    >
      <div class="relative grid max-h-[92vh] w-full max-w-6xl gap-4 overflow-auto rounded-[32px] border border-white/15 bg-slate-950/82 p-4" @click.stop>
        <button
          type="button"
          class="absolute right-4 top-4 z-10 rounded-full border border-white/15 bg-black/45 px-3 py-2 text-sm text-white hover:bg-black/70"
          aria-label="关闭相册预览"
          @click="activeAlbum = null; active = null"
        >
          关闭
        </button>
        <div class="pr-16">
          <h2 class="text-2xl font-black text-white">{{ activeAlbum.title }}</h2>
          <p class="mt-1 text-sm text-white/50">{{ activeAlbum.description }}</p>
        </div>
        <SafeImage v-if="active" :src="active.url" :alt="active.title || activeAlbum.title" img-class="mx-auto max-h-[60vh] max-w-full rounded-3xl border border-white/15 object-contain" />
        <div class="grid grid-cols-3 gap-2 sm:grid-cols-5 md:grid-cols-8">
          <button v-for="photo in activeAlbum.photos" :key="photo.url" type="button" class="overflow-hidden rounded-2xl border border-white/10" :class="active?.url === photo.url ? 'ring-2 ring-cyan-300' : ''" @click="active = photo">
            <SafeImage :src="photo.url" :alt="photo.title || 'photo'" img-class="aspect-square w-full object-cover" />
          </button>
        </div>
        <p class="text-center text-white/70">{{ active?.title }}</p>
      </div>
    </div>
  </section>
</template>
