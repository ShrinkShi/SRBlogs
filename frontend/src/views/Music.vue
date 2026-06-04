<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import CommentBox from '@/components/CommentBox.vue'
import FrontJsonItemEditorModal from '@/components/FrontJsonItemEditorModal.vue'
import PlayerVolumeControl from '@/components/PlayerVolumeControl.vue'
import PlayModeButton from '@/components/PlayModeButton.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, PageConfig } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { usePlayerStore } from '@/stores/player'
import { useUiStore } from '@/stores/ui'
import { useSessionStore } from '@/stores/session'

type LyricEntry = { time: number; text: string }
type LyricLine = { key: string; text: string; active: boolean }

const tracks = ref<MusicItem[]>([])
const pageConfig = ref<PageConfig | null>(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref<'lyrics' | 'playlist'>('lyrics')
const lyricText = ref('')
const activeLyricNode = ref<HTMLElement | null>(null)
const player = usePlayerStore()
const ui = useUiStore()
const session = useSessionStore()
const editorOpen = ref(false)
const editingTrack = ref<MusicItem | null>(null)
const editingIndex = ref(-1)
const batchDeleteArmed = ref(false)
const batchMode = ref(false)
const selectedTrackKeys = ref<Set<string>>(new Set())
const uploadInput = ref<HTMLInputElement | null>(null)
const uploadingTrack = ref(false)

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
const selectedTracks = computed(() => sortedTracks.value.filter((item) => selectedTrackKeys.value.has(trackKey(item))))
const lyricSource = computed(() => lyricText.value.trim() || currentTrack.value?.lyrics?.trim() || '')
const lyricEntries = computed(() => parseLrc(lyricSource.value))
const activeLyricIndex = computed(() => {
  const entries = lyricEntries.value
  if (!entries.length) return -1
  const current = Math.max(0, player.currentTime || 0)
  if (current < entries[0].time) return -1
  let activeIndex = 0
  entries.forEach((entry, index) => {
    if (entry.time <= current) activeIndex = index
  })
  return activeIndex
})
const lyricLines = computed<LyricLine[]>(() => {
  const entries = lyricEntries.value
  if (entries.length) {
    return entries.map((entry, index) => ({
      key: `${entry.time}-${index}`,
      text: entry.text,
      active: index === activeLyricIndex.value
    }))
  }
  const source = lyricSource.value
  if (source) {
    const lines = source
      .split('\n')
      .map((line) => line.replace(/^\[[^\]]+\]/, '').trim())
      .filter(Boolean)
    if (lines.length) {
      return lines.map((line, index) => ({
        key: `plain-${index}`,
        text: line,
        active: false
      }))
    }
  }
  const fallback = currentTrack.value
    ? `${currentTrack.value.title} - ${currentTrack.value.artist} / ${player.playing ? '正在播放' : '等待播放'}`
    : '暂无歌词，播放时会显示当前歌曲信息。'
  return [{ key: 'fallback', text: fallback, active: false }]
})

function parseTimeTag(tag: string) {
  const match = tag.match(/^(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?$/)
  if (!match) return null
  const minutes = Number(match[1])
  const seconds = Number(match[2])
  const fraction = match[3] ? Number(`0.${match[3].padEnd(3, '0').slice(0, 3)}`) : 0
  return minutes * 60 + seconds + fraction
}

function parseLrc(source: string): LyricEntry[] {
  const entries: LyricEntry[] = []
  source.split('\n').forEach((rawLine) => {
    const line = rawLine.trim()
    if (!line) return
    const tags = [...line.matchAll(/\[([0-9:.]+)\]/g)]
    if (!tags.length) return
    const text = line.replace(/\[[^\]]+\]/g, '').trim()
    tags.forEach((tag) => {
      const time = parseTimeTag(tag[1])
      if (time !== null && text) entries.push({ time, text })
    })
  })
  return entries.sort((a, b) => a.time - b.time)
}

function setActiveLyricNode(el: unknown) {
  activeLyricNode.value = el instanceof HTMLElement ? el : null
}

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
}

watch([activeLyricIndex, activeTab], async () => {
  if (activeTab.value !== 'lyrics' || activeLyricIndex.value < 0) return
  await nextTick()
  activeLyricNode.value?.scrollIntoView({
    block: 'center',
    behavior: prefersReducedMotion() ? 'auto' : 'smooth'
  })
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

function trackKey(item: MusicItem) {
  return player.songKey(item) || item.url || item.title
}

function safeFileName(value: string) {
  return value.replace(/[\\/:*?"<>|]+/g, '-').replace(/\s+/g, ' ').trim() || 'srblogs-music'
}

function trackDuration(item: MusicItem) {
  const stored = Number((item as MusicItem & { duration?: number }).duration || 0)
  if (stored > 0) return formatTime(stored)
  if (trackKey(item) === currentSongId.value && player.duration) return formatTime(player.duration)
  return '0:00'
}

function rawTrackIndex(item: MusicItem) {
  const key = trackKey(item)
  return tracks.value.findIndex((track) => trackKey(track) === key)
}

function openTrackEditor(item: MusicItem | null = null) {
  editingTrack.value = item
  editingIndex.value = item ? rawTrackIndex(item) : -1
  editorOpen.value = true
}

function isTrackSelected(item: MusicItem) {
  return selectedTrackKeys.value.has(trackKey(item))
}

function toggleTrackSelection(item: MusicItem) {
  const key = trackKey(item)
  if (!key) return
  const next = new Set(selectedTrackKeys.value)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  selectedTrackKeys.value = next
}

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  batchDeleteArmed.value = false
  if (!batchMode.value) selectedTrackKeys.value = new Set()
}

function downloadTrack(item: MusicItem) {
  if (!item.url) {
    ui.showToast(`《${item.title || '未命名'}》缺少音频 URL`, 'error')
    return
  }
  const anchor = document.createElement('a')
  anchor.href = item.url
  anchor.download = safeFileName(`${item.title || '未命名'}-${item.artist || '未知歌手'}`)
  anchor.target = '_blank'
  anchor.rel = 'noopener'
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
}

function downloadSelectedTracks() {
  if (!selectedTracks.value.length) {
    ui.showToast('请先在批量模式中选择歌曲', 'info')
    return
  }
  selectedTracks.value.forEach(downloadTrack)
}

async function deleteSelectedTracks() {
  if (!selectedTracks.value.length) {
    ui.showToast('请先选择要删除的歌曲', 'info')
    return
  }
  if (!batchDeleteArmed.value) {
    batchDeleteArmed.value = true
    ui.showToast('再次点击删除选中以确认', 'info')
    window.setTimeout(() => { batchDeleteArmed.value = false }, 3000)
    return
  }
  try {
    const keys = new Set(selectedTrackKeys.value)
    await contentApi.adminPutJson('/music', tracks.value.filter((track) => !keys.has(trackKey(track))))
    ui.showToast('已删除选中歌曲', 'success')
    batchDeleteArmed.value = false
    selectedTrackKeys.value = new Set()
    await load()
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '批量删除失败', 'error')
  }
}

async function uploadTrackFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploadingTrack.value = true
  try {
    const result = await contentApi.upload(file)
    const baseName = file.name.replace(/\.[^.]+$/, '').trim() || '未命名歌曲'
    const nextItem: MusicItem = {
      title: baseName,
      artist: '未知歌手',
      url: result.url,
      id: `song-${Date.now()}`,
      sort: tracks.value.length,
      likes: 0
    }
    await contentApi.adminPutJson('/music', [nextItem, ...tracks.value])
    ui.showToast('歌曲已上传', 'success')
    activeTab.value = 'playlist'
    await load()
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '歌曲上传失败', 'error')
  } finally {
    uploadingTrack.value = false
    input.value = ''
  }
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
    const [music, config] = await Promise.all([
      contentApi.json<MusicItem[]>('/music'),
      contentApi.json<PageConfig>('/pages/config')
    ])
    tracks.value = music
    pageConfig.value = config
    player.setTracks(music)
    selectedTrackKeys.value = new Set([...selectedTrackKeys.value].filter((key) => music.some((item) => trackKey(item) === key)))
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
        <h1 class="text-4xl font-black text-white">{{ pageTitle }}</h1>
      </div>
    </GlassCard>

    <div v-if="session.isAdmin" class="flex justify-end">
      <button type="button" class="frontend-admin-create-btn" @click="openTrackEditor()">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        新增歌曲
      </button>
    </div>

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
            <PlayModeButton :mode="player.playMode" :label="playModeLabel" @click="player.cyclePlayMode()" />
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
        <div v-if="session.isAdmin && activeTab === 'playlist'" class="music-batch-toolbar">
          <input ref="uploadInput" type="file" class="hidden" accept="audio/*,.mp3,.flac,.wav,.ogg,.m4a" @change="uploadTrackFile" />
          <button type="button" :disabled="uploadingTrack" @click="uploadInput?.click()">{{ uploadingTrack ? '上传中' : '上传' }}</button>
          <button type="button" :disabled="!selectedTracks.length" @click="downloadSelectedTracks">下载选中</button>
          <button type="button" @click="toggleBatchMode">{{ batchMode ? '退出批量' : '批量操作' }}</button>
          <button v-if="batchMode" type="button" class="danger" :disabled="!selectedTracks.length" @click="deleteSelectedTracks">
            {{ batchDeleteArmed ? '确认删除' : '删除选中' }}
          </button>
        </div>

        <div v-if="activeTab === 'lyrics'" class="music-tab-content music-lyrics-reader mt-5 max-h-[32rem] overflow-auto rounded-[24px] p-5 text-center text-sm leading-8">
          <p
            v-for="line in lyricLines"
            :key="line.key"
            :ref="line.active ? setActiveLyricNode : undefined"
            class="music-lyric-line"
            :class="{ 'music-lyric-line-active': line.active }"
          >
            {{ line.text }}
          </p>
        </div>

        <div v-else class="music-tab-content music-playlist-table mt-5 max-h-[32rem] overflow-auto rounded-[24px]">
          <div class="music-playlist-head" :class="{ 'with-select': batchMode }">
            <span v-if="batchMode"></span>
            <span>#</span>
            <span>歌名</span>
            <span>歌手</span>
            <span>喜欢</span>
            <span>时长</span>
          </div>
          <article
            v-for="(item, index) in sortedTracks"
            :key="`${item.id || item.url}-${item.title}`"
            class="music-playlist-item"
            :class="[
              player.current === index ? 'music-playlist-item-active' : '',
              batchMode ? 'music-playlist-item-batch' : ''
            ]"
          >
            <label v-if="batchMode" class="music-track-check" @click.stop>
              <input type="checkbox" :checked="isTrackSelected(item)" @change="toggleTrackSelection(item)" />
            </label>
            <button type="button" class="music-playlist-pick" :class="{ 'with-select': batchMode }" @click="batchMode ? toggleTrackSelection(item) : selectTrack(index)">
              <span class="music-track-index">{{ index + 1 }}</span>
              <span class="music-track-title">{{ item.title || '未命名' }}</span>
              <span class="music-track-artist">{{ item.artist || '未知歌手' }}</span>
              <span class="music-track-like">{{ Number(item.likes || 0) }}</span>
              <span class="music-track-duration">{{ trackDuration(item) }}</span>
            </button>
            <div v-if="session.isAdmin" class="music-admin-actions">
              <button type="button" @click="openTrackEditor(item)">编辑</button>
            </div>
          </article>
        </div>
      </GlassCard>
    </div>

    <CommentBox class="music-page-comments" resource="music" slug="global" />
    <FrontJsonItemEditorModal v-model="editorOpen" kind="music" :item="editingTrack" :index="editingIndex" @saved="load" />
  </section>
</template>

<style scoped>
.music-batch-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: .55rem;
  margin-top: 1rem;
}
.music-batch-toolbar button {
  border-radius: 999px;
  background: white;
  padding: .55rem .95rem;
  color: black;
  font-size: .86rem;
  font-weight: 900;
  transition: opacity .18s ease, transform .18s ease;
}
.music-batch-toolbar button:hover:not(:disabled) {
  transform: translateY(-1px);
}
.music-batch-toolbar button:disabled {
  cursor: not-allowed;
  opacity: .42;
}
.music-batch-toolbar .danger {
  background: #ef4444;
  color: white;
}
.music-playlist-table {
  display: grid;
  align-content: start;
  gap: 0;
  padding: .35rem 0;
}
.music-playlist-head,
.music-playlist-pick {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1.65fr) minmax(0, 1fr) 5rem 5rem;
  min-width: 0;
  width: 100%;
  align-items: center;
  gap: .85rem;
  text-align: left;
}
.music-playlist-head.with-select {
  grid-template-columns: 2.25rem 3rem minmax(0, 1.65fr) minmax(0, 1fr) 5rem 5rem;
}
.music-playlist-head {
  padding: .35rem .9rem .6rem;
  color: rgba(255, 255, 255, .38);
  font-size: .72rem;
  font-weight: 900;
  letter-spacing: .08em;
}
.music-playlist-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-items: start;
  gap: .35rem;
  border-bottom: 1px solid rgba(255, 255, 255, .08);
  padding: .72rem .9rem;
  text-align: left;
  transition: background .18s ease;
}
.music-playlist-item:last-child {
  border-bottom: 0;
}
.music-playlist-item:hover {
  background: rgba(255, 255, 255, .045) !important;
}
.music-playlist-item-active {
  background: rgba(255, 255, 255, .06) !important;
  box-shadow: none !important;
}
.music-playlist-item-batch {
  grid-template-columns: 2.25rem minmax(0, 1fr);
}
.music-track-check {
  grid-column: 1;
  grid-row: 1;
  display: grid;
  width: 1.4rem;
  height: 1.4rem;
  place-items: center;
  align-self: center;
}
.music-track-check input {
  width: 1rem;
  height: 1rem;
  accent-color: var(--accent);
}
.music-playlist-pick {
  grid-column: 1 / -1;
  grid-row: 1;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: left;
}
.music-playlist-pick.with-select {
  grid-column: 2;
}
.music-track-index,
.music-track-like,
.music-track-duration {
  color: rgba(255, 255, 255, .46);
  font-size: .82rem;
  font-weight: 800;
}
.music-track-title,
.music-track-artist {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.music-track-title {
  color: white;
  font-weight: 950;
}
.music-track-artist {
  color: rgba(255, 255, 255, .58);
  font-size: .9rem;
}
.music-admin-actions {
  display: flex;
  grid-column: 1 / -1;
  justify-content: flex-end;
  gap: .65rem;
  padding-top: .1rem;
}
.music-admin-actions button {
  color: rgba(255, 255, 255, .68);
  font-weight: 900;
}
.music-admin-actions button:hover {
  color: white;
}
.music-admin-actions .danger {
  color: #fecaca;
}
@media (max-width: 640px) {
  .music-playlist-head {
    display: none;
  }
  .music-playlist-pick,
  .music-playlist-pick.with-select {
    grid-template-columns: 2.25rem minmax(0, 1fr);
    grid-template-areas:
      "index title"
      "index artist"
      "index meta";
    gap: .25rem .65rem;
  }
  .music-track-index { grid-area: index; }
  .music-track-title { grid-area: title; }
  .music-track-artist { grid-area: artist; }
  .music-track-like {
    grid-area: meta;
  }
  .music-track-duration {
    grid-area: meta;
    justify-self: end;
  }
  .music-admin-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
