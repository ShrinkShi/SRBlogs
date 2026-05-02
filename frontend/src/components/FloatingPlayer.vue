<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MusicItem } from '@/types'

const props = defineProps<{ tracks?: MusicItem[] }>()
const index = ref(0)
const open = ref(false)
const track = computed(() => props.tracks?.[index.value])

function next() {
  if (props.tracks?.length) index.value = (index.value + 1) % props.tracks.length
}
</script>

<template>
  <div v-if="tracks?.length" class="fixed bottom-4 right-4 z-40 md:bottom-5 md:right-5">
    <div v-if="open" class="glass mb-3 w-[min(290px,calc(100vw-2rem))] rounded-[28px] p-4">
      <div class="flex items-center gap-3">
        <div
          class="h-12 w-12 rounded-2xl bg-white/10 bg-cover bg-center"
          :style="{ backgroundImage: track?.cover ? `url(${track.cover})` : '' }"
          role="img"
          :aria-label="track?.title || '当前歌曲封面'"
        ></div>
        <div class="min-w-0">
          <p class="truncate font-bold text-white">{{ track?.title }}</p>
          <p class="truncate text-xs text-white/48">{{ track?.artist }}</p>
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button type="button" class="rounded-2xl bg-white/10 px-3 py-2 text-xs text-white/70" aria-label="播放当前歌曲">播放</button>
        <button type="button" class="rounded-2xl bg-cyan-300/20 px-3 py-2 text-xs text-cyan-100" aria-label="切换到下一首" @click="next">下一首</button>
        <RouterLink to="/music" class="rounded-2xl border border-white/10 px-3 py-2 text-xs text-white/60">歌单</RouterLink>
      </div>
    </div>
    <button
      type="button"
      class="glass grid h-14 w-14 place-items-center rounded-2xl text-white"
      style="animation: pulse-ring 2.6s infinite"
      :aria-label="open ? '收起音乐播放器' : '展开音乐播放器'"
      @click="open = !open"
    >
      ♪
    </button>
  </div>
</template>
