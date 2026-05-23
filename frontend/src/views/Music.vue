<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import CommentBox from '@/components/CommentBox.vue'
import PlayerVolumeControl from '@/components/PlayerVolumeControl.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, PageConfig, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { usePlayerStore } from '@/stores/player'
import { useUiStore } from '@/stores/ui'

const tracks = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const pageConfig = ref<PageConfig | null>(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref<'lyrics' | 'playlist'>('lyrics')
const lyricText = ref('')
const player = usePlayerStore()
const ui = useUiStore()

const pageTitle = computed(() => pageConfig.value?.pageText?.music?.title || '音乐歌单')
const pageSubtitle = computed(() => pageConfig.value?.pageText?.music?.subtitle || '左侧控制播放，右侧查看歌词和歌单。')
useSeo({ title: () => pageTitle.value, description: () => pageSubtitle.value, path: '/music' })

const sortedTracks = computed(() => player.tracks.length ? player.tracks : [...tracks.value].sort((a, b) => Number(b.likes || 0) - Number(a.likes || 0) || Number(a.sort ?? 0) - Number(b.sort ?? 0)))
const currentTrack = computed(() => player.track || sortedTracks.value[0])
const progressPercent = computed(() => {
  if (!player.duration) return '0%'
  return `${Math.min(100, Math.max(0, (player.currentTime / player.duration) * 100))}%`
})
const recordStyle = computed(() => ({
  '--record-cover': currentTrack.value?.cover ? `url(${currentTrack.value.cover})` : 'linear-gradient(135deg, rgba(239,68,68,.34), rgba(17,24,39,.42))'
}))
const currentSongId = computed(() => player.songKey(currentTrack.value))
const likedCurrent = computed(() => currentSongId.value ? player.isLiked(currentSongId.value) : false)
const currentLikes = computed(() => Math.max(0, Number(currentTrack.value?.likes || 0)))
const playModeLabel = computed(() => player.playMode === 'sequence' ? '顺序播放' : player.playMode === 'shuffle' ? '随机播放' : '单曲循环')
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

function seekFromEvent(event: Event) {
  player.seek(Number((event.target as HTMLInputElement).value))
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

async function toggleLike() {
  const id = currentSongId.value
  if (!id) {
    ui.showToast('当前歌曲缺少稳定 ID，无法喜欢', 'error')
    return
  }
  const nextLiked = !likedCurrent.value
  const previousLikes = currentLikes.value
  const nextLikes = Math.max(0, previousLikes + (nextLiked ? 1 : -1))
  player.setLikedLocal(id, nextLiked)
  player.updateTrackLikes(id, nextLikes)
  tracks.value = tracks.value.map((item) => player.songKey(item) === id ? { ...item, likes: nextLikes } : item)
  try {
    const result = await contentApi.updateMusicLike(id, nextLiked)
    player.updateTrackLikes(id, result.likes)
    tracks.value = tracks.value.map((item) => player.songKey(item) === id ? { ...item, likes: result.likes } : item)
  } catch (exc) {
    player.setLikedLocal(id, !nextLiked)
    player.updateTrackLikes(id, previousLikes)
    tracks.value = tracks.value.map((item) => player.songKey(item) === id ? { ...item, likes: previousLikes } : item)
    ui.showToast(exc instanceof Error ? exc.message : '喜欢状态保存失败', 'error')
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [music, publicSettings, config] = await Promise.all([
      contentApi.json<MusicItem[]>('/music'),
      contentApi.publicSettings<SiteSettings>(),
      contentApi.json<PageConfig>('/pages/config')
    ])
    tracks.value = music
    settings.value = publicSettings
    pageConfig.value = config
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
  <section class="page-layout-grid">
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
      <GlassCard hover class="music-player-panel min-w-0">
        <div class="music-player-core">
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
            <input class="progress-slider" type="range" min="0" :max="player.duration || 0" step="0.1" :value="player.currentTime" aria-label="播放进度" :style="{ '--progress': progressPercent }" @input="seekFromEvent" />
          </div>
          <div class="flex items-center justify-center gap-2 whitespace-nowrap">
            <button type="button" class="icon-button" :aria-label="playModeLabel" :title="playModeLabel" @click="player.cyclePlayMode()">
              <svg v-if="player.playMode === 'sequence'" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h12l-3-3 1.4-1.4L20.8 9l-6.4 6.4L13 14l3-3H4V7zm0 10h16v2H4v-2z" /></svg>
              <svg v-else-if="player.playMode === 'shuffle'" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3h5v5h-2V6.4l-4.8 4.8-1.4-1.4L17.6 5H16V3zM4 7h3.5l3.2 3.2-1.4 1.4L6.7 9H4V7zm10.2 5.8 4.8 4.8V16h2v5h-5v-2h1.6l-4.8-4.8 1.4-1.4zM4 17h2.7l10.1-10.1 1.4 1.4L7.5 19H4v-2z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7h8.6l-2.3-2.3L14.7 3 20 8.3l-5.3 5.3-1.4-1.7 2.3-2.3H7a3 3 0 0 0 0 6h1v2H7A5 5 0 0 1 7 7zm10 10h-4v-2h4a3 3 0 0 0 0-6h-1V7h1a5 5 0 0 1 0 10z" /></svg>
            </button>
            <PlayerVolumeControl />
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
            <button type="button" class="icon-button like-button-inline min-w-[4rem] gap-1 text-sm" :aria-label="likedCurrent ? '取消喜欢' : '喜欢当前歌曲'" @click="toggleLike">
              <svg viewBox="0 0 24 24" aria-hidden="true" :class="likedCurrent ? 'text-rose-300' : ''"><path d="M12 21s-7-4.4-9.4-8.6C.8 9.2 2.7 5.5 6.2 5.1c2-.2 3.6.7 4.7 2.1 1.1-1.4 2.8-2.3 4.7-2.1 3.5.4 5.4 4.1 3.6 7.3C19 16.6 12 21 12 21z" /></svg>
              <span>{{ currentLikes }}</span>
            </button>
          </div>
          <p v-if="currentTrack && !currentTrack.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅展示信息。</p>
        </div>
      </GlassCard>

      <GlassCard hover class="music-lyrics-panel min-w-0">
        <div class="music-tab-header flex flex-wrap gap-2">
          <button class="rounded-full px-4 py-2 text-sm font-bold transition" :class="activeTab === 'lyrics' ? 'bg-[var(--accent)] text-white' : 'bg-white/[0.08] text-white/62 hover:bg-white/[0.12]'" @click="activeTab = 'lyrics'">歌词</button>
          <button class="rounded-full px-4 py-2 text-sm font-bold transition" :class="activeTab === 'playlist' ? 'bg-[var(--accent)] text-white' : 'bg-white/[0.08] text-white/62 hover:bg-white/[0.12]'" @click="activeTab = 'playlist'">歌单</button>
        </div>

        <div v-if="activeTab === 'lyrics'" class="music-tab-content mt-5 max-h-[32rem] overflow-auto whitespace-pre-line rounded-[24px] p-5 text-center text-sm leading-8">
          {{ displayLyrics }}
        </div>

        <div v-else class="music-tab-content mt-5 grid max-h-[32rem] gap-3 overflow-auto rounded-[24px] p-3">
          <button
            v-for="(item, index) in sortedTracks"
            :key="`${item.id || item.url}-${item.title}`"
            type="button"
            class="music-playlist-item flex min-w-0 items-center gap-4 rounded-[24px] p-3 text-left transition hover:scale-[1.015]"
            :class="player.current === index ? 'music-playlist-item-active' : ''"
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
              <p class="mt-1 text-xs text-rose-100/70">喜欢 {{ item.likes || 0 }}</p>
            </div>
          </button>
        </div>
      </GlassCard>
    </div>

    <CommentBox class="music-page-comments" resource="music" slug="global" />
  </section>
</template>
