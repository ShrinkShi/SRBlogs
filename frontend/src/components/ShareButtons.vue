<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
async function copyLink() {
  await navigator.clipboard.writeText(location.href)
  ui.showToast('链接已复制')
}
</script>
<template>
  <div class="mt-8 flex flex-wrap gap-3 border-t border-white/10 pt-5">
    <button class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/80 hover:bg-white/[0.15]" @click="copyLink">复制链接</button>
    <a class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/80 hover:bg-white/[0.15]" :href="`https://twitter.com/intent/tweet?url=${encodeURIComponent(location.href)}`" target="_blank">分享到 X</a>
  </div>
</template>
