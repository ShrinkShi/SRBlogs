<script setup lang="ts">
import { computed, watch } from 'vue'
import GlassCard from './GlassCard.vue'
import SafeImage from './SafeImage.vue'
import type { MusicItem } from '@/types'
import { usePlayerStore } from '@/stores/player'

const props = defineProps<{ tracks: MusicItem[] }>()
const player = usePlayerStore()
const track = computed(() => player.track)

function next() {
  player.next()
}

function prev() {
  player.prev()
}

async function toggle() {
  await player.toggle()
}

watch(() => props.tracks, (items) => player.setTracks(items), { immediate: true })
</script>

<template>
  <GlassCard>
    <div v-if="track" class="flex flex-col gap-5 md:flex-row md:items-center">
      <div class="h-24 w-24 shrink-0 overflow-hidden rounded-3xl border border-white/15 bg-white/10">
        <SafeImage v-if="track.cover" :src="track.cover" :alt="track.title" img-class="h-full w-full object-cover" />
      </div>
      <div class="min-w-0 flex-1">
        <h3 class="break-words text-2xl font-black text-white">{{ track.title }}</h3>
        <p class="mt-1 text-white/60">{{ track.artist }}</p>
        <p class="mt-2 break-all text-xs text-white/38">{{ track.id || track.url || '未配置歌曲 ID 或 URL' }}</p>
        <div class="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div class="h-full w-1/3 rounded-full bg-cyan-300/80"></div>
        </div>
      </div>
      <div class="flex flex-wrap gap-3">
        <button type="button" class="rounded-2xl bg-white/10 px-4 py-2" @click="prev">上一首</button>
        <button type="button" class="rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950" @click="toggle">{{ player.playing ? '暂停' : '播放' }}</button>
        <button type="button" class="rounded-2xl bg-white/10 px-4 py-2" @click="next">下一首</button>
      </div>
    </div>
    <p v-else class="text-white/60">暂无歌单。</p>
  </GlassCard>
</template>
