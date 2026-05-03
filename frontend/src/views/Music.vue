<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import CommentBox from '@/components/CommentBox.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { usePlayerStore } from '@/stores/player'

const tracks = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref<'lyrics' | 'playlist'>('lyrics')
const lyricText = ref('')
const player = usePlayerStore()

const pageTitle = computed(() => settings.value?.pageText?.music?.title || '音乐歌单')
const pageSubtitle = computed(() => settings.value?.pageText?.music?.subtitle || '左侧控制播放，右侧查看歌词和歌单。')
useSeo({ title: () => pageTitle.value, description: () => pageSubtitle.value, path: '/music' })

const sortedTracks = computed(() => [...tracks.value].sort((a, b) => Number(a.sort ?? 0) - Number(b.sort ?? 0)))
const currentTrack = computed(() => player.track || sortedTracks.value[0])
const progressPercent = computed(() => {
  if (!player.duration) return '0%'
  return `${Math.min(100, Math.max(0, (player.currentTime / player.duration) * 100))}%`
})
const recordStyle = computed(() => ({
  '--record-cover': currentTrack.value?.cover ? `url(${currentTrack.value.cover})` : 'linear-gradient(135deg, rgba(103,232,249,.38), rgba(192,132,252,.38))'
}))
const displayLyrics = computed(() => {
  const inline = currentTrack.value?.lyrics?.trim()
  const remote = lyricText.value.trim()
  const source = remote || inline
  if (!source) return '暂无歌词，播放时会显示当前歌曲信息。'
  return source
    .split('\n')
    .map((line) => line.replace(/^\[[^\]]+\]/, '').trim())
    .filter(Boolean)
    .join('\n')
})

function formatTime(value: number) {
  if (!Number.isFinite(value) || value <= 0) return '0:00'
  const minutes = Math.floor(value / 60)
  const seconds = Math.floor(value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
}

function setVolumeFromEvent(event: Event) {
  player.setVolume(Number((event.target as HTMLInputElement).value))
}

async function togglePlay() {
  await player.toggle()
}

function selectTrack(index: number, autoplay = true) {
  player.current = index
  player.currentTime = 0
  player.duration = 0
  player.syncAudio(autoplay && player.playing)
  if (autoplay && !player.playing) player.play()
}

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
    player.setTracks(music)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '歌单加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => currentTrack.value?.lyricUrl, async (url) => {
  lyricText.value = ''
  if (!url) return
  try {
    const response = await fetch(url)
    if (response.ok) lyricText.value = await response.text()
  } catch {
    lyricText.value = ''
  }
}, { immediate: true })

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block">
      <div class="mx-auto max-w-3xl text-center">
        <p class="text-xs font-bold uppercase tracking-[.32em] text-fuchsia-100/45">music</p>
        <h1 class="mt-2 text-4xl font-black text-white">{{ pageTitle }}</h1>
        <p class="mt-3 text-white/56">{{ pageSubtitle }} 公开音乐配置：{{ settings?.cloudMusicIds?.join(' / ') || '未配置' }}</p>
      </div>
    </GlassCard>

    <GlassCard v-if="loading">
      <p class="text-center text-white/60">歌单加载中...</p>
    </GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-center text-red-200/85">{{ error }}</p>
      <div class="mt-4 text-center">
        <button class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
      </div>
    </GlassCard>
    <GlassCard v-else-if="!sortedTracks.length">
      <p class="text-center text-white/60">暂无歌曲。</p>
    </GlassCard>

    <div v-else class="music-page-grid">
      <GlassCard hover class="min-w-0">
        <div class="grid justify-items-center gap-5 text-center">
          <div class="record-disc music-page-record rounded-full" :class="{ playing: player.playing }" :style="recordStyle" aria-hidden="true"></div>
          <div class="min-w-0">
            <h2 class="break-words text-3xl font-black text-white">{{ currentTrack?.title }}</h2>
            <p class="mt-2 text-sm text-white/58">{{ currentTrack?.artist }}</p>
          </div>
          <div class="w-full max-w-md">
            <div class="mb-2 flex items-center justify-between text-xs text-white/48">
              <span>{{ formatTime(player.currentTime) }}</span>
              <span>{{ formatTime(player.duration) }}</span>
            </div>
            <button type="button" class="block h-2 w-full overflow-hidden rounded-full border border-white/10 bg-white/10 text-left" aria-label="播放进度">
              <span class="block h-full rounded-full bg-gradient-to-r from-cyan-300 to-fuchsia-300 transition-all duration-300" :style="{ width: progressPercent }"></span>
            </button>
          </div>
          <div class="flex items-center justify-center gap-3">
            <button type="button" class="icon-button" aria-label="previous track" @click="player.prev()">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 6h2v12H7zM18 6v12l-8.5-6z" /></svg>
            </button>
            <button type="button" class="icon-button icon-button-main" :aria-label="player.playing ? '暂停' : '播放'" @click="togglePlay">
              <svg v-if="player.playing" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" /></svg>
            </button>
            <button type="button" class="icon-button" aria-label="next track" @click="player.next()">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6h2v12h-2zM6 6l8.5 6L6 18z" /></svg>
            </button>
          </div>
          <div class="volume-control">
            <button type="button" class="icon-button h-9 w-9" :aria-label="player.muted ? 'unmute' : 'mute'" @click="player.toggleMuted()">
              <svg v-if="player.muted || player.volume <= 0" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.8 3 2.6-2.6-1.4-1.4-2.6 2.6-2.6-2.6-1.4 1.4L14 12l-2.6 2.6 1.4 1.4 2.6-2.6 2.6 2.6 1.4-1.4L16.8 12z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zm-2.5-9.2v2.1a7.5 7.5 0 0 1 0 14.2v2.1a9.5 9.5 0 0 0 0-18.4z" /></svg>
            </button>
            <input class="volume-slider" type="range" min="0" max="1" step="0.01" :value="player.muted ? 0 : player.volume" aria-label="volume" @input="setVolumeFromEvent" />
          </div>
          <p v-if="currentTrack && !currentTrack.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅展示信息。</p>
        </div>
      </GlassCard>

      <GlassCard hover class="min-w-0">
        <div class="flex flex-wrap gap-2">
          <button class="rounded-full px-4 py-2 text-sm font-bold transition" :class="activeTab === 'lyrics' ? 'bg-cyan-300 text-slate-950' : 'bg-white/[0.08] text-white/62 hover:bg-white/[0.12]'" @click="activeTab = 'lyrics'">歌词</button>
          <button class="rounded-full px-4 py-2 text-sm font-bold transition" :class="activeTab === 'playlist' ? 'bg-cyan-300 text-slate-950' : 'bg-white/[0.08] text-white/62 hover:bg-white/[0.12]'" @click="activeTab = 'playlist'">歌单</button>
        </div>

        <div v-if="activeTab === 'lyrics'" class="mt-5 max-h-[32rem] overflow-auto whitespace-pre-line rounded-[24px] bg-white/[0.05] p-5 text-center text-sm leading-8 text-white/68">
          {{ displayLyrics }}
        </div>

        <div v-else class="mt-5 grid gap-3">
          <button
            v-for="(item, index) in sortedTracks"
            :key="`${item.id || item.url}-${item.title}`"
            type="button"
            class="flex min-w-0 items-center gap-4 rounded-[24px] bg-white/[0.055] p-3 text-left transition hover:scale-[1.015] hover:bg-white/[0.08]"
            :class="player.current === index ? 'ring-1 ring-cyan-200/40' : ''"
            @click="selectTrack(index)"
          >
            <div class="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-2xl bg-white/10">
              <SafeImage v-if="item.cover" :src="item.cover" :alt="item.title" img-class="h-full w-full object-cover" />
              <span v-else class="text-white/50">Music</span>
            </div>
            <div class="min-w-0">
              <h3 class="truncate text-lg font-black text-white">{{ item.title }}</h3>
              <p class="truncate text-sm text-white/55">{{ item.artist }}</p>
              <p class="mt-1 truncate text-xs text-white/38">{{ item.id || item.url || '未配置 ID 或 URL' }}</p>
            </div>
          </button>
        </div>
      </GlassCard>
    </div>

    <CommentBox resource="music" slug="global" />
  </section>
</template>
