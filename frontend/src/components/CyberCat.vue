<script setup lang="ts">
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
</script>

<template>
  <div v-if="ui.ambience" class="pointer-events-none fixed bottom-24 right-6 z-20 hidden opacity-55 lg:block 2xl:right-[max(1.5rem,calc((100vw-80rem)/2-7rem))]">
    <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
      <path d="M24 36 16 18l22 10h20l22-10-8 18 8 20c4 20-12 30-32 30S12 76 16 56l8-20Z" fill="rgba(255,255,255,.09)" stroke="rgba(125,249,255,.85)" stroke-width="3"/>
      <circle cx="36" cy="54" r="4" fill="#67e8f9"/>
      <circle cx="60" cy="54" r="4" fill="#c084fc"/>
      <path d="M42 66h12M48 60v10" stroke="white" stroke-width="3" stroke-linecap="round"/>
    </svg>
  </div>
</template>
