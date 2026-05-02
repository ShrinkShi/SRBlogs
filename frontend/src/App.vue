<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import BackgroundEffects from '@/components/BackgroundEffects.vue'
import BackgroundSlider from '@/components/BackgroundSlider.vue'
import ClickEffect from '@/components/ClickEffect.vue'
import CyberCat from '@/components/CyberCat.vue'
import Toast from '@/components/Toast.vue'
import DanmakuBackground from '@/components/DanmakuBackground.vue'
import Sakura from '@/components/Sakura.vue'
import Fireflies from '@/components/Fireflies.vue'
import FloatingPlayer from '@/components/FloatingPlayer.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, SiteSettings } from '@/types'

const settings = ref<SiteSettings | null>(null)
const tracks = ref<MusicItem[]>([])
onMounted(async () => {
  try { settings.value = await contentApi.json<SiteSettings>('/settings/public') } catch { settings.value = null }
  try { tracks.value = await contentApi.json<MusicItem[]>('/music') } catch { tracks.value = [] }
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
    <BackgroundSlider :settings="settings" />
    <CyberCat />
    <main class="mx-auto w-full max-w-7xl px-4 pb-24 pt-32 md:px-6 md:pt-36">
      <RouterView v-slot="{ Component }">
        <Transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <FloatingPlayer :tracks="tracks" />
    <Toast />
  </div>
</template>

<style scoped>
.fade-slide-enter-active,.fade-slide-leave-active { transition: all .24s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
