<script setup lang="ts">
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const petals = Array.from({ length: 14 }, (_, i) => i)
</script>
<template>
  <div v-if="ui.ambience" class="pointer-events-none fixed inset-0 z-[1] hidden overflow-hidden opacity-80 md:block">
    <span v-for="i in petals" :key="i" class="absolute top-[-8vh] h-2 w-3 rounded-full bg-pink-200/50 blur-[.2px]" :style="{ left: `${(i * 41) % 100}%`, animation: `fall ${12 + (i % 7)}s linear ${-(i * 1.3)}s infinite` }"></span>
  </div>
</template>
