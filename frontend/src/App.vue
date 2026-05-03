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
  const scale = preferredScale === 'small' ? '15px' : preferredScale === 'large' ? '17px' : '16px'
  root.style.setProperty('--app-font-size', scale)
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
