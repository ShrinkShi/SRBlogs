<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<template>
  <Transition name="toast">
    <div
      v-if="ui.toast"
      class="glass fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-2xl px-5 py-3 text-sm text-white"
      :class="ui.toastKind === 'success' ? 'toast-success' : ui.toastKind === 'error' ? 'toast-error' : ''"
    >
      {{ ui.toast }}
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,.toast-leave-active{transition:.2s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translate(-50%,10px)}
.toast-success{border-color:rgba(74,222,128,.55);background:linear-gradient(135deg,rgba(22,163,74,.72),rgba(16,185,129,.4));box-shadow:0 18px 48px rgba(34,197,94,.24)}
.toast-error{border-color:rgba(248,113,113,.55);background:linear-gradient(135deg,rgba(185,28,28,.72),rgba(248,113,113,.28));box-shadow:0 18px 48px rgba(248,113,113,.2)}
</style>
