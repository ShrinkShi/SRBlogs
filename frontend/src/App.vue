<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import AppNav from '@/components/AppNav.vue'
import BackgroundEffects from '@/components/BackgroundEffects.vue'
import ClickEffect from '@/components/ClickEffect.vue'
import CyberCat from '@/components/CyberCat.vue'
import Toast from '@/components/Toast.vue'
import Toolbox from '@/components/Toolbox.vue'
import DanmakuBackground from '@/components/DanmakuBackground.vue'
import Sakura from '@/components/Sakura.vue'
import Fireflies from '@/components/Fireflies.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, SiteSettings } from '@/types'
import { useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'

const settings = ref<SiteSettings | null>(null)
const ui = useUiStore()
const player = usePlayerStore()

function applyTheme() {
  const root = document.documentElement
  const config = settings.value?.themeConfig || {}
  const mode = ui.colorMode || config.mode || 'night'
  const tokens = mode === 'day' ? config.day : config.night
  root.dataset.colorMode = mode
  const preferredScale = ui.fontScale || config.fontScale
  root.dataset.fontScale = preferredScale || 'medium'
  if (config.fontFamily) root.style.setProperty('--app-font-family', config.fontFamily)
  const map: Record<string, string | undefined> = {
    '--bg-page': tokens?.bgPage,
    '--bg-card': tokens?.bgCard,
    '--bg-card-elevated': tokens?.bgCardElevated,
    '--border-glass': tokens?.borderGlass,
    '--text-primary': tokens?.textPrimary,
    '--text-secondary': tokens?.textSecondary,
    '--accent': tokens?.accent,
    '--accent-soft': tokens?.accentSoft,
    '--nav-bg': tokens?.navBg,
    '--home-panel-bg': tokens?.homePanelBg,
    '--shadow-glow': tokens?.shadowGlow
  }
  Object.entries(map).forEach(([key, value]) => {
    if (value) root.style.setProperty(key, value)
    else root.style.removeProperty(key)
  })
  const opacityDefaults: Record<string, number> = {
    toolboxSettingsPanel: 0.92,
    toolboxSearchPanel: 0.92,
    toolboxCalculatorPanel: 0.90,
    homeCard: 0.82,
    homeCarousel: 0.82,
    contentCard: 0.82,
    photoCard: 0.82,
    musicPanel: 0.88,
    messageBoard: 0.86,
    navBar: 0.72
  }
  const opacity = (config.opacity || {}) as Record<string, number>
  Object.entries(opacityDefaults).forEach(([key, fallback]) => {
    const raw = Number(opacity[key] ?? fallback)
    const value = Math.min(1, Math.max(0, Number.isFinite(raw) ? raw : fallback))
    root.style.setProperty(`--opacity-${key.replace(/[A-Z]/g, (char) => `-${char.toLowerCase()}`)}`, String(value))
  })
  const sizeScale: Record<string, number> = { small: 0.92, medium: 1, large: 1.08 }
  const componentTheme = config.componentTheme || {}
  Object.entries(componentTheme).forEach(([key, item]) => {
    const cssKey = key.replace(/[A-Z]/g, (char) => `-${char.toLowerCase()}`)
    const modeTokens = mode === 'day' ? item.day : item.night
    const opacityValue = Number(item.opacity ?? 0.86)
    root.style.setProperty(`--ct-${cssKey}-opacity`, String(Math.min(1, Math.max(0, Number.isFinite(opacityValue) ? opacityValue : 0.86))))
    root.style.setProperty(`--ct-${cssKey}-size`, String(sizeScale[item.size || 'medium'] ?? 1))
    if (modeTokens?.bg) root.style.setProperty(`--ct-${cssKey}-bg`, modeTokens.bg)
    if (modeTokens?.text) root.style.setProperty(`--ct-${cssKey}-text`, modeTokens.text)
    if (modeTokens?.accent) root.style.setProperty(`--ct-${cssKey}-accent`, modeTokens.accent)
    if (modeTokens?.border) root.style.setProperty(`--ct-${cssKey}-border`, modeTokens.border)
  })
}

onMounted(async () => {
  try { settings.value = await contentApi.json<SiteSettings>('/settings/public') } catch { settings.value = null }
  ui.applyInteraction(settings.value?.interaction)
  try { player.setTracks(await contentApi.json<MusicItem[]>('/music')) } catch { player.setTracks([]) }
  applyTheme()
})
watch([settings, () => ui.colorMode, () => ui.fontScale], () => {
  ui.applyInteraction(settings.value?.interaction)
  applyTheme()
})
</script>

<template>
  <BackgroundEffects :settings="settings" />
  <DanmakuBackground :list="settings?.danmakuList" />
  <Sakura />
  <Fireflies />
  <ClickEffect />
  <div class="relative z-10 min-h-screen">
    <AppNav />
    <Toolbox :settings="settings" />
    <CyberCat />
    <main class="sr-page-shell pb-28 pt-32 md:pt-36">
      <RouterView v-slot="{ Component }">
        <Transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <Toast />
  </div>
</template>

<style scoped>
.fade-slide-enter-active,.fade-slide-leave-active { transition: all .24s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
