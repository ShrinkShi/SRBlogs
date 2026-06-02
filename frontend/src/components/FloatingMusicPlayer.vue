<script setup lang="ts">
import { computed } from 'vue'
import PlayerVolumeControl from '@/components/PlayerVolumeControl.vue'
import { usePlayerStore } from '@/stores/player'

const player = usePlayerStore()
const track = computed(() => player.track)
const progressPercent = computed(() => player.duration ? `${Math.min(100, (player.currentTime / player.duration) * 100)}%` : '0%')
const playModeLabel = computed(() => player.playMode === 'sequence' ? '顺序播放' : player.playMode === 'shuffle' ? '随机播放' : '单曲循环')

function formatTime(seconds: number) {
  if (!seconds || !Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${mins}:${secs}`
}

function seekFromEvent(event: Event) {
  player.seek(Number((event.target as HTMLInputElement).value))
}
</script>

<template>
  <aside class="floating-music-player" aria-label="全局音乐播放器">
    <div class="floating-music-meta">
      <span class="floating-music-kicker">正在播放</span>
      <strong>{{ track?.title || '暂无歌曲' }}</strong>
      <small>{{ track?.artist || '请在后台添加歌曲' }}</small>
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
      <button type="button" class="icon-button" :aria-label="playModeLabel" :title="playModeLabel" @click="player.cyclePlayMode()">
        <svg v-if="player.playMode === 'sequence'" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h12l-3-3 1.4-1.4L20.8 9l-6.4 6.4L13 14l3-3H4V7zm0 10h16v2H4v-2z" /></svg>
        <svg v-else-if="player.playMode === 'shuffle'" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3h5v5h-2V6.4l-4.8 4.8-1.4-1.4L17.6 5H16V3zM4 7h3.5l3.2 3.2-1.4 1.4L6.7 9H4V7zm10.2 5.8 4.8 4.8V16h2v5h-5v-2h1.6l-4.8-4.8 1.4-1.4zM4 17h2.7l10.1-10.1 1.4 1.4L7.5 19H4v-2z" /></svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7h8.6l-2.3-2.3L14.7 3 20 8.3l-5.3 5.3-1.4-1.7 2.3-2.3H7a3 3 0 0 0 0 6h1v2H7A5 5 0 0 1 7 7zm10 10h-4v-2h4a3 3 0 0 0 0-6h-1V7h1a5 5 0 0 1 0 10z" /></svg>
      </button>
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
