<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
let lastSound = 0
let customAudio: HTMLAudioElement | null = null

function isInteractive(target: EventTarget | null) {
  const el = target instanceof Element ? target : null
  return Boolean(el?.closest([
    'button',
    'a',
    '[role="button"]',
    'input[type="button"]',
    'input[type="submit"]',
    'input[type="reset"]',
    'label',
    '[data-clickable="true"]',
    '.clickable',
    '.btn',
    '.button',
    '[aria-label]',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',')))
}

function playClickSound() {
  if (!ui.clickSoundAllowed || !ui.clickSound) return
  const now = performance.now()
  if (now - lastSound < 90) return
  lastSound = now
  try {
    if (ui.clickSoundUrl) {
      if (!customAudio || customAudio.src !== new URL(ui.clickSoundUrl, window.location.href).href) {
        customAudio = new Audio(ui.clickSoundUrl)
      }
      customAudio.currentTime = 0
      customAudio.volume = Math.max(0, Math.min(1, ui.clickSoundVolume))
      customAudio.play().catch(() => {})
      return
    }
    const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext
    const ctx = new AudioCtx()
    const gain = ctx.createGain()
    const osc = ctx.createOscillator()
    osc.type = 'square'
    osc.frequency.value = 1250
    gain.gain.setValueAtTime(0.0001, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(Math.max(0.005, Math.min(0.12, ui.clickSoundVolume)), ctx.currentTime + 0.004)
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
  if (isInteractive(e.target)) playClickSound()
  if (ui.clickEffectAllowed && ui.clickEffect) {
    const node = document.createElement('span')
    node.className = 'click-spark'
    node.style.left = `${e.clientX}px`
    node.style.top = `${e.clientY}px`
    document.body.appendChild(node)
    window.setTimeout(() => node.remove(), 650)
  }
}

onMounted(() => window.addEventListener('click', click, true))
onBeforeUnmount(() => window.removeEventListener('click', click, true))
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
