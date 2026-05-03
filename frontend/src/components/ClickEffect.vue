<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
let lastSound = 0

function isInteractive(target: EventTarget | null) {
  const el = target instanceof Element ? target : null
  return Boolean(el?.closest('button,a,input,select,textarea,label,[role="button"],[tabindex]:not([tabindex="-1"])'))
}

function playClickSound() {
  if (!ui.clickSound) return
  const now = performance.now()
  if (now - lastSound < 90) return
  lastSound = now
  try {
    const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext
    const ctx = new AudioCtx()
    const gain = ctx.createGain()
    const osc = ctx.createOscillator()
    osc.type = 'square'
    osc.frequency.value = 1250
    gain.gain.setValueAtTime(0.0001, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.055, ctx.currentTime + 0.004)
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.045)
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.start()
    osc.stop(ctx.currentTime + 0.05)
    window.setTimeout(() => ctx.close(), 90)
  } catch {
    // Browser audio policy or unavailable AudioContext: ignore gracefully.
  }
}

function click(e: MouseEvent) {
  if (!isInteractive(e.target)) return
  playClickSound()
  if (ui.ambience) {
    const node = document.createElement('span')
    node.className = 'click-spark'
    node.style.left = `${e.clientX}px`
    node.style.top = `${e.clientY}px`
    document.body.appendChild(node)
    window.setTimeout(() => node.remove(), 650)
  }
}

onMounted(() => window.addEventListener('click', click))
onBeforeUnmount(() => window.removeEventListener('click', click))
</script>

<template><span /></template>

<style>
.click-spark {
  position: fixed;
  z-index: 9999;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  pointer-events: none;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(103, 232, 249, .9);
  animation: spark .65s ease-out forwards;
}
@keyframes spark {
  to { width: 72px; height: 72px; opacity: 0; }
}
</style>
