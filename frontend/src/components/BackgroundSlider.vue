<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore, themes } from '@/stores/ui'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()
const count = computed(() => Math.max(props.settings?.bgImages?.length || 0, themes.length))
</script>
<template>
  <div class="fixed bottom-5 left-6 z-30 hidden max-w-[calc(100vw-8rem)] grid-flow-col gap-2 md:grid 2xl:bottom-auto 2xl:left-auto 2xl:right-[max(1.5rem,calc((100vw-80rem)/2-6rem))] 2xl:top-24 2xl:max-w-none 2xl:grid-flow-row">
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.nextTheme">主题 {{ ui.theme }}</button>
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.setBgIndex((ui.bgIndex + 1) % count)">背景 {{ ui.bgIndex + 1 }}</button>
    <button class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" @click="ui.toggleDanmaku">弹幕 {{ ui.danmaku ? '开' : '关' }}</button>
  </div>
</template>
