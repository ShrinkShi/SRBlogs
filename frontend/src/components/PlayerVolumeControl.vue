<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { usePlayerStore } from '@/stores/player'

const player = usePlayerStore()
const open = ref(false)
const dragging = ref(false)
const trackRef = ref<HTMLElement | null>(null)
let hideTimer = 0

const level = computed(() => Math.max(0, Math.min(1, player.muted ? 0 : player.volume)))
const levelPercent = computed(() => `${level.value * 100}%`)

function show() {
  if (hideTimer) window.clearTimeout(hideTimer)
  open.value = true
}

function hideSoon() {
  if (hideTimer) window.clearTimeout(hideTimer)
  hideTimer = window.setTimeout(() => {
    if (!dragging.value) open.value = false
  }, 500)
}

function setFromPointer(event: PointerEvent) {
  const rect = trackRef.value?.getBoundingClientRect()
  if (!rect) return
  const next = 1 - ((event.clientY - rect.top) / rect.height)
  player.setVolume(Math.max(0, Math.min(1, next)))
}

function onPointerDown(event: PointerEvent) {
  show()
  dragging.value = true
  ;(event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId)
  setFromPointer(event)
}

function onPointerMove(event: PointerEvent) {
  if (dragging.value) setFromPointer(event)
}

function onPointerUp(event: PointerEvent) {
  dragging.value = false
  ;(event.currentTarget as HTMLElement).releasePointerCapture?.(event.pointerId)
  hideSoon()
}

function onKeydown(event: KeyboardEvent) {
  const step = event.shiftKey ? 0.1 : 0.05
  if (event.key === 'ArrowUp' || event.key === 'ArrowRight') {
    event.preventDefault()
    player.setVolume(level.value + step)
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowLeft') {
    event.preventDefault()
    player.setVolume(level.value - step)
  }
}

onBeforeUnmount(() => {
  if (hideTimer) window.clearTimeout(hideTimer)
})
</script>

<template>
  <div
    class="volume-control"
    :class="{ 'volume-open': open }"
    @mouseenter="show"
    @mouseleave="hideSoon"
    @focusin="show"
    @focusout="hideSoon"
  >
    <button type="button" class="icon-button h-9 w-9" :aria-label="player.muted ? '取消静音' : '静音'" @click="player.toggleMuted()">
      <svg v-if="player.muted || player.volume <= 0" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.8 3 2.6-2.6-1.4-1.4-2.6 2.6-2.6-2.6-1.4 1.4L14 12l-2.6 2.6 1.4 1.4 2.6-2.6 2.6 2.6 1.4-1.4L16.8 12z" /></svg>
      <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zm-2.5-9.2v2.1a7.5 7.5 0 0 1 0 14.2v2.1a9.5 9.5 0 0 0 0-18.4z" /></svg>
    </button>
    <div class="volume-slider-panel" @mouseenter="show" @mouseleave="hideSoon">
      <div
        ref="trackRef"
        class="volume-track"
        role="slider"
        tabindex="0"
        aria-label="音量"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-valuenow="Math.round(level * 100)"
        @keydown="onKeydown"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
      >
        <div class="volume-track-fill" :style="{ height: levelPercent }"></div>
        <div class="volume-thumb" :style="{ bottom: levelPercent }"></div>
      </div>
    </div>
  </div>
</template>
