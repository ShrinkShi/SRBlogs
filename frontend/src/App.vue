<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import AppNav from '@/components/AppNav.vue'
import BackgroundEffects from '@/components/BackgroundEffects.vue'
import ClickEffect from '@/components/ClickEffect.vue'
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

function solidColor(value: string | undefined, fallback: string) {
  if (!value) return fallback
  const rgba = value.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i)
  if (rgba) return `rgb(${Number(rgba[1])} ${Number(rgba[2])} ${Number(rgba[3])})`
  return value
}

function applyTheme() {
  const root = document.documentElement
  const config = settings.value?.themeConfig || {}
  const mode = ui.colorMode || config.mode || 'night'
  const activeTheme = config.activeTheme || settings.value?.theme || 'shrink-red-glass'
  const activePackage = config.themePackages?.[activeTheme]
  const packageTokens = mode === 'day' ? activePackage?.modes?.day : activePackage?.modes?.night
  const localTokens = mode === 'day' ? config.day : config.night
  const tokens = { ...(packageTokens || {}), ...(localTokens || {}) }
  root.dataset.colorMode = mode
  const preferredScale = ui.fontScale || config.fontScale
  root.dataset.fontScale = preferredScale || 'medium'
  root.style.setProperty('--app-font-family', '"Consolas-with-Yahei", Consolas, "Microsoft YaHei", "微软雅黑", "Courier New", monospace')
  const solidCard = solidColor(tokens?.bgCard || tokens?.cardBg, mode === 'day' ? '#ffffff' : '#141416')
  const solidElevated = solidColor(tokens?.bgCardElevated || tokens?.cardBg, mode === 'day' ? '#ffffff' : '#202023')
  const solidNav = solidColor(tokens?.navBg, mode === 'day' ? '#f8fafc' : '#08080a')
  const map: Record<string, string | undefined> = {
    '--bg-page': tokens?.bgPage || tokens?.pageBg,
    '--bg-card': solidCard,
    '--bg-card-elevated': solidElevated,
    '--border-glass': tokens?.borderGlass || tokens?.border,
    '--text-primary': tokens?.textPrimary,
    '--text-secondary': tokens?.textSecondary,
    '--accent': tokens?.accent,
    '--accent-hover': tokens?.accentHover,
    '--accent-soft': tokens?.accentSoft,
    '--nav-bg': solidNav,
    '--home-panel-bg': solidColor(tokens?.homePanelBg, solidCard),
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
    const overlayOpacity = mode === 'day' ? 0 : Math.min(1, Math.max(0, Number(tokens.overlayOpacity)))
    root.style.setProperty('--bg-overlay-opacity', String(overlayOpacity))
  } else {
    root.style.removeProperty('--bg-overlay-opacity')
  }
  if (tokens?.fontSizeBase) root.style.setProperty('--theme-font-size-base', `${tokens.fontSizeBase}px`)
  const opacityDefaults: Record<string, number> = {
    toolboxSettingsPanel: 1,
    toolboxSearchPanel: 1,
    toolboxCalculatorPanel: 1,
    homeCard: 1,
    homeCarousel: 1,
    contentCard: 1,
    photoCard: 1,
    musicPanel: 1,
    messageBoard: 1,
    navBar: 1
  }
  Object.entries(opacityDefaults).forEach(([key, fallback]) => {
    const value = Math.min(1, Math.max(0, fallback))
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
