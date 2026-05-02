<script setup lang="ts">
defineProps<{ as?: string; hover?: boolean; dense?: boolean }>()
</script>

<template>
  <component
    :is="as || 'div'"
    class="glass sr-card overflow-hidden rounded-[30px] transition duration-300"
    :class="[hover ? 'sr-card-hover' : '', dense ? 'p-4' : 'p-5 md:p-6']"
  >
    <div class="relative z-[1]"><slot /></div>
  </component>
</template>
