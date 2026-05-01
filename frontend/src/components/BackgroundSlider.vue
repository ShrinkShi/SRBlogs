<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore, themes } from '@/stores/ui'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()
const count = computed(() => Math.max(props.settings?.bgImages?.length || 0, themes.length))
</script>
<template>
  <div class="fixed right-4 top-24 z-30 hidden gap-2 md:grid">
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.nextTheme">主题 {{ ui.theme }}</button>
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.setBgIndex((ui.bgIndex + 1) % count)">背景 {{ ui.bgIndex + 1 }}</button>
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.toggleDanmaku">弹幕 {{ ui.danmaku ? '开' : '关' }}</button>
  </div>
</template>
