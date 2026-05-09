<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useUiStore } from '@/stores/ui'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null }>()
const ui = useUiStore()

function normalizeBackgroundList(value: unknown): string[] {
  const list = Array.isArray(value) ? value : value ? [value] : []
  return list
    .map((item: unknown) => {
      if (typeof item === 'string') return { url: item, enabled: true }
      if (item && typeof item === 'object') {
        const entry = item as { url?: string; enabled?: boolean }
        return {
          url: typeof entry.url === 'string' ? entry.url : '',
          enabled: entry.enabled !== false
        }
      }
      return { url: '', enabled: false }
    })
    .filter((item) => item.enabled && item.url.trim())
    .map((item) => item.url.trim())
}

function uniqueBackgrounds(list: string[]) {
  return Array.from(new Set(list))
}

const modeTokens = computed(() => {
  const config = props.settings?.themeConfig
  const activeTheme = config?.activeTheme || props.settings?.theme || 'shrink-red-glass'
  const activePackage = config?.themePackages?.[activeTheme]
  const localTokens = ui.colorMode === 'day' ? config?.day : config?.night
  const packageTokens = ui.colorMode === 'day' ? activePackage?.modes?.day : activePackage?.modes?.night
  return { ...(localTokens || {}), ...(packageTokens || {}) }
})
const bgImages = computed(() => {
  const modeList = uniqueBackgrounds([
    ...normalizeBackgroundList(modeTokens.value.bgImages),
    ...normalizeBackgroundList(modeTokens.value.bgImage)
  ])
  return modeList.length ? modeList : uniqueBackgrounds(normalizeBackgroundList(props.settings?.bgImages))
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
  const next = Number.isFinite(Number(ui.bgIndex))
    ? Number(ui.bgIndex)
    : Number(modeTokens.value.activeBgIndex ?? 0)
  activeBgIndex.value = Math.max(0, Number.isFinite(next) ? next : 0) % Math.max(1, bgImages.value.length)
}, { immediate: true })
watch(slideshowEnabled, startBgTimer, { immediate: true })
onBeforeUnmount(stopBgTimer)

const overlayStyle = computed(() => ({
  backgroundColor: ui.colorMode === 'day' ? '#ffffff' : (modeTokens.value.overlayColor || '#000000'),
  opacity: ui.colorMode === 'day' ? '0.72' : '0.58'
}))
const bgLayerStyle = computed(() => ({
  backgroundImage: bgImage.value ? `url(${bgImage.value})` : '',
  opacity: String(ui.colorMode === 'day' ? 0.9 : 0.86),
  filter: ui.colorMode === 'day' ? 'saturate(1.04) contrast(0.98)' : 'saturate(1.02) contrast(1.05)'
}))
const radialStyle = computed(() => ({
  opacity: String(ui.colorMode === 'day' ? 0.04 : 0.08)
}))
</script>

<template>
  <div class="pointer-events-none fixed inset-0 z-0 overflow-hidden">
    <div class="absolute inset-0 bg-[var(--bg-page)]"></div>
    <Transition name="bg-fade" mode="out-in">
      <div
        v-if="bgImage"
        :key="bgImage"
        class="absolute inset-0 scale-[1.02] bg-cover bg-center blur-[1px]"
        :style="bgLayerStyle"
      ></div>
    </Transition>
    <div class="absolute inset-0" :style="overlayStyle"></div>
    <div class="absolute inset-0 bg-cyber-radial" :style="radialStyle"></div>
    <div class="absolute left-[8%] top-[16%] hidden h-40 w-40 rounded-full bg-rose-500/12 blur-3xl md:block" style="animation: float-slow 8s ease-in-out infinite"></div>
    <div class="absolute bottom-[6%] right-[10%] hidden h-52 w-52 rounded-full bg-zinc-100/8 blur-3xl md:block" style="animation: float-slow 11s ease-in-out infinite reverse"></div>
  </div>
</template>
