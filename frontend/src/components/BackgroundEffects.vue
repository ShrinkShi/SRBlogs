<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()
const bgImage = computed(() => props.settings?.bgImages?.[ui.bgIndex % (props.settings?.bgImages?.length || 1)])
const cls = computed(() => {
  if (ui.theme === 'sakura') return 'from-rose-950 via-fuchsia-950 to-slate-950'
  if (ui.theme === 'aurora') return 'from-emerald-950 via-slate-950 to-cyan-950'
  if (ui.theme === 'cyber') return 'from-slate-950 via-violet-950 to-black'
  return 'from-slate-950 via-indigo-950 to-black'
})
</script>

<template>
  <div class="fixed inset-0 -z-10 bg-gradient-to-br" :class="cls"></div>
  <div v-if="bgImage" class="fixed inset-0 -z-10 bg-cover bg-center opacity-[0.34] blur-[1px] scale-[1.02]" :style="{ backgroundImage: `url(${bgImage})` }"></div>
  <div class="pointer-events-none fixed inset-0 -z-10 bg-cyber-radial opacity-95"></div>
  <div class="pointer-events-none fixed left-[8%] top-[16%] -z-10 hidden h-40 w-40 rounded-full bg-fuchsia-400/16 blur-3xl md:block" style="animation: float-slow 8s ease-in-out infinite"></div>
  <div class="pointer-events-none fixed bottom-[6%] right-[10%] -z-10 hidden h-52 w-52 rounded-full bg-emerald-300/10 blur-3xl md:block" style="animation: float-slow 11s ease-in-out infinite reverse"></div>
</template>
