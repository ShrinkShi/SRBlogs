<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="ui.toast"
        class="toast-shell left-1/2 top-5 z-[10000] max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl px-5 py-3 text-center text-sm font-bold text-white shadow-2xl md:top-7"
        :class="ui.toastKind === 'success' ? 'toast-success' : ui.toastKind === 'error' ? 'toast-error' : ''"
      >
        {{ ui.toast }}
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,.toast-leave-active{transition:opacity .24s ease, transform .24s ease}
.toast-enter-from,.toast-leave-to{opacity:0;transform:translate(-50%,-14px) scale(.98)}
.toast-shell{position:fixed;border:1px solid var(--ct-toast-border, var(--border-glass));background:var(--ct-toast-bg,var(--bg-card-elevated));color:var(--ct-toast-text,var(--text-primary));box-shadow:0 18px 48px color-mix(in srgb,#000 18%,transparent);backdrop-filter:none;-webkit-backdrop-filter:none}
.toast-success{border-color:rgba(22,163,74,.65);background:rgb(240 253 244);color:rgb(22 101 52);box-shadow:0 18px 48px rgba(34,197,94,.18)}
.toast-error{border-color:rgba(220,38,38,.62);background:rgb(254 242 242);color:rgb(127 29 29);box-shadow:0 18px 48px rgba(248,113,113,.18)}
:global(:root[data-color-mode='night']) .toast-success{background:rgb(20 83 45);color:rgb(220 252 231)}
:global(:root[data-color-mode='night']) .toast-error{background:rgb(127 29 29);color:rgb(254 226 226)}
</style>
