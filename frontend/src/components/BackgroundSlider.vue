<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore, themes } from '@/stores/ui'
import type { SiteSettings } from '@/types'

const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()
const count = computed(() => Math.max(props.settings?.bgImages?.length || 0, themes.length))
</script>

<template>
  <div class="fixed bottom-5 left-1/2 z-30 hidden max-w-[calc(100vw-3rem)] -translate-x-1/2 grid-flow-col gap-2 md:grid 2xl:bottom-auto 2xl:left-auto 2xl:right-[max(1.5rem,calc((100vw-80rem)/2-6rem))] 2xl:top-24 2xl:max-w-none 2xl:translate-x-0 2xl:grid-flow-row">
    <button type="button" class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" aria-label="切换主题" @click="ui.nextTheme">
      主题 {{ ui.theme }}
    </button>
    <button type="button" class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" aria-label="切换背景图" @click="ui.setBgIndex((ui.bgIndex + 1) % count)">
      背景 {{ ui.bgIndex + 1 }}
    </button>
    <button type="button" class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" aria-label="切换弹幕背景" @click="ui.toggleDanmaku">
      弹幕 {{ ui.danmaku ? '开' : '关' }}
    </button>
    <button type="button" class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" aria-label="切换氛围动效" @click="ui.toggleAmbience">
      氛围 {{ ui.ambience ? '开' : '关' }}
    </button>
    <button type="button" class="glass rounded-2xl px-3 py-2 text-xs font-bold text-white/72 hover:text-white" aria-label="切换点击音效" @click="ui.toggleClickSound">
      点击音 {{ ui.clickSound ? '开' : '关' }}
    </button>
  </div>
</template>
