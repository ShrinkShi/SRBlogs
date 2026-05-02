<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'

const props = defineProps<{ list?: string[] }>()
const ui = useUiStore()
const fallback = ['代码是星河的注脚', '今天也要写文章', 'Markdown 保存宇宙碎片', 'Vue3 正在运行']
const items = computed(() => (props.list?.length ? props.list : fallback).slice(0, ui.ambience ? 10 : 4))
</script>

<template>
  <div v-if="ui.danmaku" class="pointer-events-none fixed inset-0 -z-[1] overflow-hidden opacity-20 md:opacity-25">
    <span
      v-for="(text, i) in items"
      :key="text + i"
      class="absolute whitespace-nowrap rounded-full border border-white/10 bg-white/[0.08] px-4 py-1 text-xs text-white/38 backdrop-blur-md"
      :style="{ top: `${8 + (i * 7) % 70}%`, animation: `drift ${18 + i * 1.7}s linear ${-i * 2.1}s infinite` }"
    >
      {{ text }}
    </span>
  </div>
</template>
