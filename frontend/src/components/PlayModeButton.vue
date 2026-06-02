<script setup lang="ts">
import playInOrderIcon from '../../../assets/playinorder.png'
import repeatSingleIcon from '../../../assets/repeatsingle.png'
import shufflePlayIcon from '../../../assets/shuffleplay.png'
import type { PlayMode } from '@/stores/player'

const props = defineProps<{
  mode: PlayMode
  label: string
}>()

const iconMap: Record<PlayMode, string> = {
  sequence: playInOrderIcon,
  shuffle: shufflePlayIcon,
  'repeat-one': repeatSingleIcon
}
</script>

<template>
  <button type="button" class="icon-button play-mode-button" :aria-label="label" :title="label">
    <img :src="iconMap[props.mode]" :alt="label" draggable="false" />
  </button>
</template>
