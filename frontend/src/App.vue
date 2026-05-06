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
  const activeTheme = config.activeTheme || settings.value?.theme || 'shrink-red-glass'
  const activePackage = config.themePackages?.[activeTheme]
  const packageTokens = mode === 'day' ? activePackage?.modes?.day : activePackage?.modes?.night
  const tokens = { ...(mode === 'day' ? config.day : config.night), ...(packageTokens || {}) }
  root.dataset.colorMode = mode
  const preferredScale = ui.fontScale || config.fontScale
  root.dataset.fontScale = preferredScale || 'medium'
  if (config.fontFamily) root.style.setProperty('--app-font-family', config.fontFamily)
  const map: Record<string, string | undefined> = {
    '--bg-page': tokens?.bgPage || tokens?.pageBg,
    '--bg-card': tokens?.bgCard || tokens?.cardBg,
    '--bg-card-elevated': tokens?.bgCardElevated || tokens?.cardBg,
    '--border-glass': tokens?.borderGlass || tokens?.border,
    '--text-primary': tokens?.textPrimary,
    '--text-secondary': tokens?.textSecondary,
    '--accent': tokens?.accent,
    '--accent-hover': tokens?.accentHover,
    '--accent-soft': tokens?.accentSoft,
    '--nav-bg': tokens?.navBg,
    '--home-panel-bg': tokens?.homePanelBg,
    '--shadow-glow': tokens?.shadowGlow || tokens?.shadow,
    '--bg-overlay-color': tokens?.overlayColor,
    '--glass-radius': tokens?.radius ? `${tokens.radius}px` : undefined,
    '--glass-blur': tokens?.blur ? `${tokens.blur}px` : undefined
  }
  Object.entries(map).forEach(([key, value]) => {
    if (value) root.style.setProperty(key, value)
    else root.style.removeProperty(key)
  })
  if (tokens?.overlayOpacity !== undefined) {
    root.style.setProperty('--bg-overlay-opacity', String(Math.min(1, Math.max(0, Number(tokens.overlayOpacity)))))
  } else {
    root.style.removeProperty('--bg-overlay-opacity')
  }
  if (tokens?.fontFamily || config.fontFamily) root.style.setProperty('--app-font-family', tokens?.fontFamily || config.fontFamily || '')
  if (tokens?.fontSizeBase) root.style.setProperty('--theme-font-size-base', `${tokens.fontSizeBase}px`)
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
  // componentTheme is kept as legacy configuration only. Frontend layout and visual
  // structure now use fixed Vue/CSS plus global theme tokens, not per-component
  // low-code overrides.
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
    <main class="site-page-container pb-28 pt-32 md:pt-36">
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
