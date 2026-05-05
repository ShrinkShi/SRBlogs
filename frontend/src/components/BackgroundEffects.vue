<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()
const modeTokens = computed(() => {
  const config = props.settings?.themeConfig
  const activeTheme = config?.activeTheme || props.settings?.theme || 'shrink-red-glass'
  const activePackage = config?.themePackages?.[activeTheme]
  const localTokens = ui.colorMode === 'day' ? config?.day : config?.night
  const packageTokens = ui.colorMode === 'day' ? activePackage?.modes?.day : activePackage?.modes?.night
  return { ...(localTokens || {}), ...(packageTokens || {}) }
})
const bgImage = computed(() => modeTokens.value.bgImage || props.settings?.bgImages?.[ui.bgIndex % (props.settings?.bgImages?.length || 1)])
const overlayStyle = computed(() => ({
  backgroundColor: modeTokens.value.overlayColor || (ui.colorMode === 'day' ? '#ffffff' : '#000000'),
  opacity: String(Math.min(1, Math.max(0, Number(modeTokens.value.overlayOpacity ?? (ui.colorMode === 'day' ? 0.66 : 0.68)))))
}))
</script>

<template>
  <div class="fixed inset-0 -z-10 bg-[var(--bg-page)]"></div>
  <div v-if="bgImage" class="fixed inset-0 -z-10 bg-cover bg-center opacity-[0.34] blur-[1px] scale-[1.02]" :style="{ backgroundImage: `url(${bgImage})` }"></div>
  <div class="pointer-events-none fixed inset-0 -z-10" :style="overlayStyle"></div>
  <div class="pointer-events-none fixed inset-0 -z-10 bg-cyber-radial opacity-80"></div>
  <div class="pointer-events-none fixed left-[8%] top-[16%] -z-10 hidden h-40 w-40 rounded-full bg-rose-500/12 blur-3xl md:block" style="animation: float-slow 8s ease-in-out infinite"></div>
  <div class="pointer-events-none fixed bottom-[6%] right-[10%] -z-10 hidden h-52 w-52 rounded-full bg-zinc-100/8 blur-3xl md:block" style="animation: float-slow 11s ease-in-out infinite reverse"></div>
</template>
