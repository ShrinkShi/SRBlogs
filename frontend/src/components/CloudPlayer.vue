<script setup lang="ts">
import { computed, ref } from 'vue'
import GlassCard from './GlassCard.vue'
import type { MusicItem } from '@/types'
const props = defineProps<{ tracks: MusicItem[] }>()
const current = ref(0)
const playing = ref(false)
const track = computed(() => props.tracks[current.value])
function next() { current.value = (current.value + 1) % Math.max(1, props.tracks.length) }
function prev() { current.value = (current.value - 1 + props.tracks.length) % Math.max(1, props.tracks.length) }
</script>

<template>
  <GlassCard>
    <div v-if="track" class="flex flex-col gap-5 md:flex-row md:items-center">
      <div class="h-24 w-24 rounded-3xl border border-white/15 bg-white/10 bg-cover bg-center" :style="{ backgroundImage: track.cover ? `url(${track.cover})` : '' }"></div>
      <div class="flex-1">
        <h3 class="text-2xl font-black text-white">{{ track.title }}</h3>
        <p class="mt-1 text-white/60">{{ track.artist }}</p>
        <div class="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div class="h-full w-1/3 rounded-full bg-cyan-300/80"></div>
        </div>
      </div>
      <div class="flex gap-3">
        <button class="rounded-2xl bg-white/10 px-4 py-2" @click="prev">上一首</button>
        <button class="rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950" @click="playing = !playing">{{ playing ? '暂停' : '播放' }}</button>
        <button class="rounded-2xl bg-white/10 px-4 py-2" @click="next">下一首</button>
      </div>
    </div>
    <p v-else class="text-white/60">暂无歌单。</p>
  </GlassCard>
</template>
