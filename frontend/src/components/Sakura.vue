<script setup lang="ts">
const petals = Array.from({ length: 20 }, (_, i) => i)
</script>
<template>
  <div class="pointer-events-none fixed inset-0 z-[1] overflow-hidden">
    <span v-for="i in petals" :key="i" class="absolute top-[-8vh] h-2 w-3 rounded-full bg-pink-200/50 blur-[.2px]" :style="{ left: `${(i * 41) % 100}%`, animation: `fall ${12 + (i % 7)}s linear ${-(i * 1.3)}s infinite` }"></span>
  </div>
</template>
