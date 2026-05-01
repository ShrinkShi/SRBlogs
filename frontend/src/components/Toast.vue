<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<template>
  <Transition name="toast">
    <div v-if="ui.toast" class="glass fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-2xl px-5 py-3 text-sm text-white">
      {{ ui.toast }}
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,.toast-leave-active{transition:.2s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translate(-50%,10px)}
</style>
