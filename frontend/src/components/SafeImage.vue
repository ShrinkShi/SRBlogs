<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  src?: string
  fallback?: string
  alt: string
  eager?: boolean
  imgClass?: string
}>(), {
  src: '',
  fallback: '',
  eager: false,
  imgClass: ''
})

const failed = ref(false)
const fallbackUrl = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'
const currentSrc = computed(() => failed.value ? (props.fallback || fallbackUrl) : (props.src || props.fallback || fallbackUrl))

watch(() => props.src, () => { failed.value = false })
</script>

<template>
  <img
    :src="currentSrc"
    :alt="alt"
    :loading="eager ? 'eager' : 'lazy'"
    draggable="false"
    decoding="async"
    :class="imgClass"
    @error="failed = true"
    @dragstart.prevent
  />
</template>
