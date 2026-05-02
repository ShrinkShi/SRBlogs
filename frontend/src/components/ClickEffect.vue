<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

function click(e: MouseEvent) {
  if (!ui.ambience) return
  const node = document.createElement('span')
  node.className = 'click-spark'
  node.style.left = `${e.clientX}px`
  node.style.top = `${e.clientY}px`
  document.body.appendChild(node)
  window.setTimeout(() => node.remove(), 650)
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
