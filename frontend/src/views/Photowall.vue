<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { PhotoItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const photos = ref<PhotoItem[]>([])
const active = ref<PhotoItem | null>(null)
const loading = ref(false)
const error = ref('')
useSeo({ title: '照片墙', description: 'SRBlogs 的照片墙、图片记录和预览。', path: '/photowall' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    photos.value = await contentApi.json<PhotoItem[]>('/photos')
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
    <GlassCard>
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
    <GlassCard v-else-if="!photos.length">
      <p class="text-white/60">暂无照片。</p>
    </GlassCard>

    <div v-else class="columns-1 gap-5 md:columns-2 xl:columns-3">
      <button
        v-for="item in photos"
        :key="item.url"
        type="button"
        class="glass glass-hover mb-5 block w-full break-inside-avoid overflow-hidden rounded-[30px] text-left"
        :aria-label="`预览照片：${item.title || item.url}`"
        @click="active = item"
      >
        <SafeImage :src="item.url" :alt="item.title || 'photo'" img-class="relative z-[1] w-full object-cover" />
        <div class="relative z-[1] p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h3 class="break-words font-bold text-white">{{ item.title || '未命名照片' }}</h3>
            <span v-if="item.date" class="text-xs text-white/42">{{ item.date }}</span>
          </div>
          <p v-if="item.description" class="mt-1 break-words text-sm leading-6 text-white/55">{{ item.description }}</p>
          <div v-if="item.tags?.length" class="mt-3 flex flex-wrap gap-2">
            <span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-2 py-1 text-[11px] text-white/50">#{{ tag }}</span>
          </div>
        </div>
      </button>
    </div>

    <div
      v-if="active"
      class="fixed inset-0 z-50 grid place-items-center bg-black/75 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      @click="active = null"
      @keydown.esc.window="active = null"
    >
      <div class="relative max-w-5xl" @click.stop>
        <button
          type="button"
          class="absolute right-3 top-3 z-10 rounded-full border border-white/15 bg-black/45 px-3 py-2 text-sm text-white hover:bg-black/70"
          aria-label="关闭照片预览"
          @click="active = null"
        >
          关闭
        </button>
        <SafeImage :src="active.url" :alt="active.title || 'photo'" img-class="max-h-[82vh] max-w-[92vw] rounded-3xl border border-white/15 object-contain" />
        <p class="mt-3 text-center text-white/70">{{ active.title }}</p>
      </div>
    </div>
  </section>
</template>
