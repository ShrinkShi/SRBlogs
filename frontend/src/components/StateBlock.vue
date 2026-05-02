<script setup lang="ts">
import GlassCard from './GlassCard.vue'

withDefaults(defineProps<{
  title?: string
  message: string
  retryLabel?: string
}>(), {
  title: '',
  retryLabel: '重试'
})

defineEmits<{ retry: [] }>()
</script>

<template>
  <GlassCard>
    <p v-if="title" class="text-xl font-black text-white">{{ title }}</p>
    <p class="text-white/68" :class="title ? 'mt-2' : ''" role="status" aria-live="polite">{{ message }}</p>
    <button
      v-if="$attrs.onRetry"
      class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/72 hover:bg-white/10"
      type="button"
      @click="$emit('retry')"
    >
      {{ retryLabel }}
    </button>
  </GlassCard>
</template>
