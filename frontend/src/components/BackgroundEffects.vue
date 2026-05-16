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
  // 后台“白天/夜晚壁纸”是当前主题的直接编辑结果，必须覆盖主题包默认值。
  return { ...(packageTokens || {}), ...(localTokens || {}) }
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
const modeSlideshowEnabled = computed(() => modeTokens.value.slideshowEnabled !== false)
const slideshowEnabled = computed(() => siteSlideshowEnabled.value && modeSlideshowEnabled.value && ui.bgSlideshow && bgImages.value.length > 1)
const slideshowIntervalMs = computed(() => {
  const seconds = Number(modeTokens.value.slideshowInterval ?? 8.5)
  const safeSeconds = Number.isFinite(seconds) ? Math.min(60, Math.max(3, seconds)) : 8.5
  return safeSeconds * 1000
})
const transitionName = computed(() => {
  const effect = String(modeTokens.value.slideshowEffect || 'fade')
  if (effect === 'soft-blur') return 'bg-soft-blur'
  if (effect === 'none') return 'bg-none'
  return 'bg-fade'
})
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
  }, slideshowIntervalMs.value)
}

watch([bgImages, () => modeTokens.value.activeBgIndex], () => {
  const next = Number(modeTokens.value.activeBgIndex ?? 0)
  activeBgIndex.value = Math.max(0, Number.isFinite(next) ? next : 0) % Math.max(1, bgImages.value.length)
}, { immediate: true })
watch(() => ui.bgIndex, () => {
  const next = Number(ui.bgIndex)
  if (Number.isFinite(next)) {
    activeBgIndex.value = Math.max(0, next) % Math.max(1, bgImages.value.length)
  }
})
watch(() => ui.colorMode, () => {
  window.setTimeout(() => {
    if (bgImages.value.length > 1) {
      activeBgIndex.value = (activeBgIndex.value + 1) % bgImages.value.length
    }
  })
})
watch([slideshowEnabled, slideshowIntervalMs], startBgTimer, { immediate: true })
onBeforeUnmount(stopBgTimer)

const overlayStyle = computed(() => ({
  backgroundColor: modeTokens.value.overlayColor || (ui.colorMode === 'day' ? '#ffffff' : '#000000'),
  opacity: String(ui.colorMode === 'day' ? 0 : Math.min(1, Math.max(0, Number(modeTokens.value.overlayOpacity ?? 0.58))))
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
    <Transition :name="transitionName" mode="out-in">
      <div
        v-if="bgImage"
        :key="`${ui.colorMode}-${bgImage}`"
        class="absolute inset-0 scale-[1.02] bg-cover bg-center blur-[1px]"
        :style="bgLayerStyle"
      ></div>
    </Transition>
    <div class="absolute inset-0" :style="overlayStyle"></div>
    <div class="bg-painterly-wash absolute inset-0"></div>
    <div class="absolute inset-0 bg-cyber-radial" :style="radialStyle"></div>
    <div class="absolute left-[8%] top-[16%] hidden h-40 w-40 rounded-full bg-rose-500/12 blur-3xl md:block" style="animation: float-slow 8s ease-in-out infinite"></div>
    <div class="absolute bottom-[6%] right-[10%] hidden h-52 w-52 rounded-full bg-zinc-100/8 blur-3xl md:block" style="animation: float-slow 11s ease-in-out infinite reverse"></div>
  </div>
</template>
