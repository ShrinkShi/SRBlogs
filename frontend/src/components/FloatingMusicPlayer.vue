<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PlayerVolumeControl from '@/components/PlayerVolumeControl.vue'
import PlayModeButton from '@/components/PlayModeButton.vue'
import { usePlayerStore } from '@/stores/player'

type LyricEntry = { time: number; text: string }
type FloatingPosition = { left: number; top: number }

const player = usePlayerStore()
const track = computed(() => player.track)
const progressPercent = computed(() => player.duration ? `${Math.min(100, (player.currentTime / player.duration) * 100)}%` : '0%')
const playModeLabel = computed(() => player.playMode === 'sequence' ? '顺序播放' : player.playMode === 'shuffle' ? '随机播放' : '单曲循环')
const remoteLyrics = ref('')
const animatedLyricLine = ref('')
const position = ref<FloatingPosition | null>(null)
const dragging = ref(false)
let lyricAnimationTimer = 0
let lyricAnimationToken = 0
let dragStart: { x: number; y: number; left: number; top: number; width: number; height: number } | null = null

const floatingStyle = computed(() => {
  if (!position.value) return {}
  return {
    left: `${position.value.left}px`,
    top: `${position.value.top}px`,
    right: 'auto',
    bottom: 'auto'
  }
})

const lyricEntries = computed(() => parseLrc(remoteLyrics.value || track.value?.lyrics || ''))
const activeLyricLine = computed(() => {
  const entries = lyricEntries.value
  if (!track.value) return '暂无歌曲'
  if (!entries.length) {
    if (track.value.lyricUrl || track.value.lyrics) return '暂无歌词'
    return '暂无歌词'
  }
  const current = Math.max(0, player.currentTime || 0)
  if (current < entries[0].time) return '等待歌词'
  let active = entries[0]
  for (const entry of entries) {
    if (entry.time <= current) active = entry
    else break
  }
  return active.text || '暂无歌词'
})

function formatTime(seconds: number) {
  if (!seconds || !Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${mins}:${secs}`
}

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
  const plainLines: string[] = []
  source.split('\n').forEach((rawLine) => {
    const line = rawLine.trim()
    if (!line) return
    const tags = [...line.matchAll(/\[([0-9:.]+)\]/g)]
    const text = line.replace(/\[[^\]]+\]/g, '').trim()
    if (!tags.length) {
      if (text) plainLines.push(text)
      return
    }
    tags.forEach((tag) => {
      const time = parseTimeTag(tag[1])
      if (time !== null && text) entries.push({ time, text })
    })
  })
  if (!entries.length && plainLines.length) return [{ time: 0, text: plainLines[0] }]
  return entries.sort((a, b) => a.time - b.time)
}

function clearLyricAnimationTimer() {
  if (lyricAnimationTimer) {
    window.clearTimeout(lyricAnimationTimer)
    lyricAnimationTimer = 0
  }
}

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
}

function animateLyricTo(next: string) {
  const target = next || ' '
  const token = ++lyricAnimationToken
  clearLyricAnimationTimer()
  if (prefersReducedMotion()) {
    animatedLyricLine.value = target
    return
  }

  const deleteStep = () => {
    if (token !== lyricAnimationToken) return
    if (animatedLyricLine.value.length > 0) {
      animatedLyricLine.value = animatedLyricLine.value.slice(0, -1)
      lyricAnimationTimer = window.setTimeout(deleteStep, 12)
      return
    }
    let index = 0
    const inputStep = () => {
      if (token !== lyricAnimationToken) return
      if (index >= target.length) return
      index += 1
      animatedLyricLine.value = target.slice(0, index)
      lyricAnimationTimer = window.setTimeout(inputStep, 24)
    }
    inputStep()
  }
  deleteStep()
}

function seekFromEvent(event: Event) {
  player.seek(Number((event.target as HTMLInputElement).value))
}

function clampPosition(next: FloatingPosition, width = 384, height = 178): FloatingPosition {
  const margin = 12
  const maxLeft = Math.max(margin, window.innerWidth - width - margin)
  const maxTop = Math.max(margin, window.innerHeight - height - margin)
  return {
    left: Math.min(maxLeft, Math.max(margin, next.left)),
    top: Math.min(maxTop, Math.max(margin, next.top))
  }
}

function persistPosition() {
  if (!position.value) return
  localStorage.setItem('sr-floating-player-position', JSON.stringify(position.value))
}

function loadPosition() {
  try {
    const parsed = JSON.parse(localStorage.getItem('sr-floating-player-position') || 'null')
    if (parsed && Number.isFinite(parsed.left) && Number.isFinite(parsed.top)) {
      position.value = clampPosition(parsed)
    }
  } catch {
    position.value = null
  }
}

function startDrag(event: PointerEvent) {
  const root = (event.currentTarget as HTMLElement).closest('.floating-music-player') as HTMLElement | null
  if (!root) return
  const rect = root.getBoundingClientRect()
  dragStart = {
    x: event.clientX,
    y: event.clientY,
    left: rect.left,
    top: rect.top,
    width: rect.width,
    height: rect.height
  }
  dragging.value = true
  root.setPointerCapture?.(event.pointerId)
  event.preventDefault()
}

function onPointerMove(event: PointerEvent) {
  if (!dragStart) return
  position.value = clampPosition({
    left: dragStart.left + event.clientX - dragStart.x,
    top: dragStart.top + event.clientY - dragStart.y
  }, dragStart.width, dragStart.height)
}

function stopDrag() {
  if (!dragStart) return
  dragStart = null
  dragging.value = false
  persistPosition()
}

function onResize() {
  if (position.value) {
    position.value = clampPosition(position.value)
    persistPosition()
  }
}

watch(() => track.value?.lyricUrl, async (url) => {
  remoteLyrics.value = ''
  if (!url) return
  try {
    const response = await fetch(url)
    if (response.ok) remoteLyrics.value = await response.text()
  } catch {
    remoteLyrics.value = ''
  }
}, { immediate: true })

watch(activeLyricLine, (line, oldLine) => {
  if (line === oldLine) return
  animateLyricTo(line)
}, { immediate: true })

onMounted(() => {
  loadPosition()
  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('pointerup', stopDrag)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  ++lyricAnimationToken
  clearLyricAnimationTimer()
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', stopDrag)
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <aside class="floating-music-player" :class="{ 'floating-music-player-dragging': dragging }" :style="floatingStyle" aria-label="全局音乐播放器">
    <div class="floating-music-drag-head" @pointerdown="startDrag">
      <span class="floating-music-kicker">正在播放</span>
      <span class="floating-music-drag-hint">拖动调整位置</span>
    </div>

    <div class="floating-music-meta">
      <strong>{{ track?.title || '暂无歌曲' }}</strong>
      <small>{{ track?.artist || '请在后台添加歌曲' }}</small>
      <p class="floating-music-lyric" aria-live="polite">
        <span class="floating-music-lyric-text">{{ animatedLyricLine || '\u00a0' }}</span>
        <span class="floating-music-lyric-cursor" aria-hidden="true"></span>
      </p>
    </div>

    <div class="floating-music-progress">
      <span>{{ formatTime(player.currentTime) }}</span>
      <input
        class="progress-slider"
        type="range"
        min="0"
        :max="player.duration || 0"
        step="0.1"
        :value="player.currentTime"
        aria-label="播放进度"
        :style="{ '--progress': progressPercent }"
        @input="seekFromEvent"
      />
      <span>{{ formatTime(player.duration) }}</span>
    </div>

    <div class="floating-music-controls">
      <PlayModeButton :mode="player.playMode" :label="playModeLabel" @click="player.cyclePlayMode()" />
      <button type="button" class="icon-button" aria-label="上一首" @click="player.prev()">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 6h2v12H7zM18 6v12l-8.5-6z" /></svg>
      </button>
      <button type="button" class="icon-button icon-button-main" :aria-label="player.playing ? '暂停' : '播放'" @click="player.toggle()">
        <svg v-if="player.playing" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" /></svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" /></svg>
      </button>
      <button type="button" class="icon-button" aria-label="下一首" @click="player.next()">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6h2v12h-2zM6 6l8.5 6L6 18z" /></svg>
      </button>
      <PlayerVolumeControl />
    </div>
  </aside>
</template>
