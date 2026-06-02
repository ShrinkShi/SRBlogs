<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import AppNav from '@/components/AppNav.vue'
import BackgroundEffects from '@/components/BackgroundEffects.vue'
import ClickEffect from '@/components/ClickEffect.vue'
import Toast from '@/components/Toast.vue'
import Toolbox from '@/components/Toolbox.vue'
import FloatingAppSidebar from '@/components/FloatingAppSidebar.vue'
import FloatingMusicPlayer from '@/components/FloatingMusicPlayer.vue'
import DanmakuBackground from '@/components/DanmakuBackground.vue'
import Sakura from '@/components/Sakura.vue'
import Fireflies from '@/components/Fireflies.vue'
import { contentApi } from '@/api/content'
import type { FloatingAppItem } from '@/config/floatingApps'
import type { MusicItem, SiteSettings } from '@/types'
import { useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'
import { useRoute, useRouter } from 'vue-router'

const settings = ref<SiteSettings | null>(null)
const ui = useUiStore()
const player = usePlayerStore()
const route = useRoute()
const router = useRouter()
const installRoute = computed(() => route.path === '/install')
type ToolPanel = 'calculator' | 'search' | 'settings'
const toolboxPanel = ref<ToolPanel | null>(null)
const floatingMusicVisible = ref(localStorage.getItem('sr-floating-music-visible') !== 'off')
const showFloatingPlayer = computed(() => !installRoute.value && !route.path.startsWith('/music') && floatingMusicVisible.value)

function setFloatingMusicVisible(visible: boolean) {
  floatingMusicVisible.value = visible
  localStorage.setItem('sr-floating-music-visible', visible ? 'on' : 'off')
}

function resolveExternalUrl(action: string) {
  if (action.startsWith('/admin') && ['5173', '5175'].includes(window.location.port)) {
    return `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:5174${action}`
  }
  return action
}

function handleFloatingAppAction(app: FloatingAppItem) {
  if (app.actionType === 'modal') {
    if (['calculator', 'search', 'settings'].includes(app.action)) {
      toolboxPanel.value = app.action as ToolPanel
    }
    return
  }
  if (app.actionType === 'route') {
    router.push(app.action)
    return
  }
  if (app.actionType === 'external') {
    window.open(resolveExternalUrl(app.action), '_blank', 'noopener,noreferrer')
    return
  }
  if (app.actionType === 'toggle' && app.action === 'floatingMusicPlayer') {
    setFloatingMusicVisible(!floatingMusicVisible.value)
  }
}

function solidColor(value: string | undefined, fallback: string) {
  if (!value) return fallback
  const rgba = value.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i)
  if (rgba) return `rgb(${Number(rgba[1])} ${Number(rgba[2])} ${Number(rgba[3])})`
  return value
}

function applyTheme() {
  const root = document.documentElement
  const config = settings.value?.themeConfig || {}
  const mode = 'night'
  const activeTheme = config.activeTheme || settings.value?.theme || 'shrink-red-glass'
  const activePackage = config.themePackages?.[activeTheme]
  const packageTokens = activePackage?.modes?.night
  const localTokens = config.night
  const tokens = { ...(packageTokens || {}), ...(localTokens || {}) }
  root.dataset.colorMode = mode
  const preferredScale = ui.fontScale || config.fontScale
  root.dataset.fontScale = preferredScale || 'medium'
  root.style.setProperty('--app-font-family', '"Consolas-with-Yahei", Consolas, "Microsoft YaHei", "微软雅黑", "Courier New", monospace')
  const solidCard = solidColor(tokens?.bgCard || tokens?.cardBg, '#191A1B')
  const solidElevated = solidColor(tokens?.bgCardElevated || tokens?.cardBg, '#202123')
  const solidNav = solidColor(tokens?.navBg, '#101112')
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
    const overlayOpacity = Math.min(1, Math.max(0, Number(tokens.overlayOpacity)))
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

async function reloadSettings() {
  try {
    settings.value = await contentApi.publicSettings<SiteSettings>()
  } catch {
    settings.value = null
  }
  ui.applyInteraction(settings.value?.interaction)
  applyTheme()
}

onMounted(async () => {
  await reloadSettings()
  try { player.setTracks(await contentApi.json<MusicItem[]>('/music')) } catch { player.setTracks([]) }
})
watch([settings, () => ui.fontScale], () => {
  ui.applyInteraction(settings.value?.interaction)
  applyTheme()
})
</script>

<template>
  <BackgroundEffects v-if="!installRoute" :settings="settings" />
  <DanmakuBackground v-if="!installRoute" :list="settings?.danmakuList" />
  <Sakura v-if="!installRoute" />
  <Fireflies v-if="!installRoute" />
  <ClickEffect v-if="!installRoute" />
  <div class="relative z-10 min-h-screen">
    <AppNav v-if="!installRoute" />
    <Toolbox v-if="!installRoute" v-model:active-panel="toolboxPanel" :settings="settings" @settings-saved="reloadSettings" />
    <FloatingAppSidebar v-if="!installRoute" @action="handleFloatingAppAction" />
    <FloatingMusicPlayer v-if="showFloatingPlayer" />
    <main :class="installRoute ? 'min-h-screen' : 'site-page-container pb-28 pt-32 md:pt-36'">
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
