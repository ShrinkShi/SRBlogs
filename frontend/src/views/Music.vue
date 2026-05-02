<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import CloudPlayer from '@/components/CloudPlayer.vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, SiteSettings } from '@/types'

const tracks = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const loading = ref(false)
const error = ref('')

const sortedTracks = computed(() => [...tracks.value].sort((a, b) => Number(a.sort ?? 0) - Number(b.sort ?? 0)))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [music, publicSettings] = await Promise.all([
      contentApi.json<MusicItem[]>('/music'),
      contentApi.json<SiteSettings>('/settings/public')
    ])
    tracks.value = music
    settings.value = publicSettings
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '歌单加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-fuchsia-100/45">music</p>
      <h1 class="mt-2 text-4xl font-black text-white">音乐歌单</h1>
      <p class="mt-3 text-white/56">后台维护的歌单会提供给页面播放器和悬浮播放器读取。公开设置中的云音乐 ID：{{ settings?.cloudMusicIds?.join(' / ') || '未配置' }}</p>
    </GlassCard>

    <GlassCard v-if="loading">
      <p class="text-white/60">歌单加载中...</p>
    </GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!sortedTracks.length">
      <p class="text-white/60">暂无歌曲。</p>
    </GlassCard>
    <template v-else>
      <CloudPlayer :tracks="sortedTracks" />
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <GlassCard v-for="item in sortedTracks" :key="`${item.id || item.url}-${item.title}`">
          <div class="flex min-w-0 gap-4">
            <div class="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-2xl bg-white/10">
              <img v-if="item.cover" :src="item.cover" :alt="item.title" loading="lazy" class="h-full w-full object-cover" />
              <span v-else class="text-white/50">♪</span>
            </div>
            <div class="min-w-0">
              <h2 class="truncate text-lg font-black text-white">{{ item.title }}</h2>
              <p class="truncate text-sm text-white/55">{{ item.artist }}</p>
              <p class="mt-1 break-all text-xs text-white/40">{{ item.id || item.url || '未配置 ID 或 URL' }}</p>
            </div>
          </div>
        </GlassCard>
      </div>
    </template>
  </section>
</template>
