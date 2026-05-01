<script setup lang="ts">
import { onMounted, ref } from 'vue'
import CloudPlayer from '@/components/CloudPlayer.vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { MusicItem, SiteSettings } from '@/types'
const tracks = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
onMounted(async () => { tracks.value = await contentApi.json<MusicItem[]>('/music'); settings.value = await contentApi.json<SiteSettings>('/settings') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-fuchsia-100/45">cloud music</p>
      <h1 class="mt-2 text-4xl font-black text-white">网易云音乐挂件</h1>
      <p class="mt-3 text-white/56">可在后台维护歌单，也可按原项目思路记录网易云歌曲 ID：{{ settings?.cloudMusicIds?.join(' / ') || '未配置' }}</p>
    </GlassCard>
    <CloudPlayer :tracks="tracks" />
  </section>
</template>
