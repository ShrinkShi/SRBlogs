<script setup lang="ts">
defineProps<{ dense?: boolean }>()
</script>
<template>
  <div class="glass overflow-hidden rounded-[30px]" :class="dense ? 'p-4' : 'p-5 md:p-6'"><div class="relative z-[1]"><slot /></div></div>
</template>
