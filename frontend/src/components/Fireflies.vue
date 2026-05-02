<script setup lang="ts">
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const dots = Array.from({ length: 18 }, (_, i) => i)
</script>
<template>
  <div v-if="ui.ambience" class="pointer-events-none fixed inset-0 z-[1] hidden overflow-hidden opacity-75 md:block">
    <span v-for="i in dots" :key="i" class="absolute h-1 w-1 rounded-full bg-cyan-200/60 shadow-[0_0_18px_rgba(103,232,249,.8)]" :style="{ left: `${(i * 29) % 100}%`, top: `${(i * 47) % 100}%`, animation: `float-slow ${5 + (i % 6)}s ease-in-out ${-(i % 5)}s infinite` }"></span>
  </div>
</template>
