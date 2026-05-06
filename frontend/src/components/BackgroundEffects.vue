<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
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
const bgImages = computed(() => {
  const modeImages = Array.isArray(modeTokens.value.bgImages) ? modeTokens.value.bgImages : []
  const enabled = modeImages
    .map((item: unknown) => typeof item === 'string' ? { url: item } : item as { url?: string; enabled?: boolean })
    .filter((item) => item?.url && item.enabled !== false)
    .map((item) => item.url as string)
  if (enabled.length) return enabled
  const legacy = Array.isArray(props.settings?.bgImages) ? props.settings?.bgImages || [] : []
  return [modeTokens.value.bgImage, ...legacy].filter(Boolean) as string[]
})
const activeBgIndex = ref(0)
let bgTimer = 0
const siteSlideshowEnabled = computed(() => props.settings?.themeConfig?.backgroundSlideshowEnabled !== false)
const slideshowEnabled = computed(() => siteSlideshowEnabled.value && ui.bgSlideshow && bgImages.value.length > 1)
const bgImage = computed(() => bgImages.value[activeBgIndex.value % Math.max(1, bgImages.value.length)])

function stopBgTimer() {
  if (bgTimer) window.clearInterval(bgTimer)
  bgTimer = 0
}

function startBgTimer() {
  stopBgTimer()
  if (!slideshowEnabled.value) return
  bgTimer = window.setInterval(() => {
    activeBgIndex.value = (activeBgIndex.value + 1) % bgImages.value.length
  }, 8500)
}

watch([bgImages, () => modeTokens.value.activeBgIndex, () => ui.bgIndex], () => {
  const next = Number(modeTokens.value.activeBgIndex ?? ui.bgIndex)
  activeBgIndex.value = Math.max(0, Number.isFinite(next) ? next : 0) % Math.max(1, bgImages.value.length)
}, { immediate: true })
watch(slideshowEnabled, startBgTimer, { immediate: true })
onBeforeUnmount(stopBgTimer)
const overlayStyle = computed(() => ({
  backgroundColor: modeTokens.value.overlayColor || (ui.colorMode === 'day' ? '#ffffff' : '#000000'),
  opacity: String(Math.min(1, Math.max(0, Number(modeTokens.value.overlayOpacity ?? (ui.colorMode === 'day' ? 0.66 : 0.68)))))
}))
</script>

<template>
  <div class="fixed inset-0 -z-10 bg-[var(--bg-page)]"></div>
  <Transition name="bg-fade" mode="out-in">
    <div v-if="bgImage" :key="bgImage" class="fixed inset-0 -z-10 bg-cover bg-center opacity-[0.34] blur-[1px] scale-[1.02]" :style="{ backgroundImage: `url(${bgImage})` }"></div>
  </Transition>
  <div class="pointer-events-none fixed inset-0 -z-10" :style="overlayStyle"></div>
  <div class="pointer-events-none fixed inset-0 -z-10 bg-cyber-radial opacity-80"></div>
  <div class="pointer-events-none fixed left-[8%] top-[16%] -z-10 hidden h-40 w-40 rounded-full bg-rose-500/12 blur-3xl md:block" style="animation: float-slow 8s ease-in-out infinite"></div>
  <div class="pointer-events-none fixed bottom-[6%] right-[10%] -z-10 hidden h-52 w-52 rounded-full bg-zinc-100/8 blur-3xl md:block" style="animation: float-slow 11s ease-in-out infinite reverse"></div>
</template>
