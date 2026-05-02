<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const currentHref = computed(() => window.location.href)

async function copyLink() {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(currentHref.value)
    } else {
      const input = document.createElement('input')
      input.value = currentHref.value
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
    }
    ui.showToast('链接已复制')
  } catch {
    ui.showToast('复制失败，请手动复制地址栏链接')
  }
}
</script>
<template>
  <div class="mt-8 flex flex-wrap gap-3 border-t border-white/10 pt-5">
    <button class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/80 hover:bg-white/[0.15]" @click="copyLink">复制链接</button>
    <a class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/80 hover:bg-white/[0.15]" :href="`https://twitter.com/intent/tweet?url=${encodeURIComponent(currentHref)}`" target="_blank" rel="noopener noreferrer">分享到 X</a>
  </div>
</template>
