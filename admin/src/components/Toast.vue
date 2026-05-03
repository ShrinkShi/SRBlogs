<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>
<template><Teleport to="body"><Transition name="t"><div v-if="ui.toast" class="toast-shell left-1/2 top-5 z-[10000] max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl border-emerald-300/40 bg-emerald-500/20 px-5 py-3 text-center text-sm font-bold text-emerald-50 shadow-2xl">{{ ui.toast }}</div></Transition></Teleport></template>
<style scoped>.t-enter-active,.t-leave-active{transition:opacity .24s ease,transform .24s ease}.t-enter-from,.t-leave-to{opacity:0;transform:translate(-50%,-14px) scale(.98)}.toast-shell{position:fixed;border:1px solid rgba(110,231,183,.35);backdrop-filter:blur(18px) saturate(140%)}</style>
