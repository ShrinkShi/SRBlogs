<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>
<template><Transition name="t"><div v-if="ui.toast" class="glass fixed left-1/2 top-5 z-[10000] max-w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl border-emerald-300/40 bg-emerald-500/20 px-5 py-3 text-center text-sm font-bold text-emerald-50 shadow-2xl">{{ ui.toast }}</div></Transition></template>
<style scoped>.t-enter-active,.t-leave-active{transition:opacity .24s ease,transform .24s ease}.t-enter-from,.t-leave-to{opacity:0;transform:translate(-50%,-14px) scale(.98)}</style>
