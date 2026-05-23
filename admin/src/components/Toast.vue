<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>
<template>
  <Teleport to="body">
    <Transition name="t">
      <div
        v-if="ui.toast"
        class="toast-shell left-1/2 top-5 z-[10000] max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl px-5 py-3 text-center text-sm font-bold shadow-2xl"
        :class="ui.toastType === 'error' ? 'toast-shell-error' : 'toast-shell-success'"
      >
        {{ ui.toast }}
      </div>
    </Transition>
  </Teleport>
</template>
<style scoped>
.t-enter-active,.t-leave-active{transition:opacity .24s ease,transform .24s ease}
.t-enter-from,.t-leave-to{opacity:0;transform:translate(-50%,-14px) scale(.98)}
.toast-shell{position:fixed;border:1px solid transparent;backdrop-filter:blur(18px) saturate(140%)}
.toast-shell-success{border-color:#bbf7d0;background:#f0fdf4;color:#166534}
.toast-shell-error{border-color:#fecaca;background:#fef2f2;color:#b91c1c}
</style>
