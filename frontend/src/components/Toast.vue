<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<template>
  <Transition name="toast">
    <div
      v-if="ui.toast"
      class="glass fixed left-1/2 top-5 z-[10000] max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl px-5 py-3 text-center text-sm font-bold text-white shadow-2xl md:top-7"
      :class="ui.toastKind === 'success' ? 'toast-success' : ui.toastKind === 'error' ? 'toast-error' : ''"
    >
      {{ ui.toast }}
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,.toast-leave-active{transition:opacity .24s ease, transform .24s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translate(-50%,-14px) scale(.98)}
.toast-success{border-color:rgba(74,222,128,.55);background:linear-gradient(135deg,rgba(22,163,74,.72),rgba(16,185,129,.4));box-shadow:0 18px 48px rgba(34,197,94,.24)}
.toast-error{border-color:rgba(248,113,113,.55);background:linear-gradient(135deg,rgba(185,28,28,.72),rgba(248,113,113,.28));box-shadow:0 18px 48px rgba(248,113,113,.2)}
</style>
