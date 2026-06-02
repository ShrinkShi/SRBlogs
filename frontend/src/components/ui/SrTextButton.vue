<script setup lang="ts">
withDefaults(defineProps<{
  tone?: 'default' | 'danger' | 'success'
  disabled?: boolean
}>(), {
  tone: 'default',
  disabled: false
})
</script>

<template>
  <button type="button" class="sr-text-button" :class="`sr-text-button-${tone}`" :disabled="disabled">
    <slot />
  </button>
</template>

<style scoped>
.sr-text-button {
  display: inline-flex;
  align-items: center;
  gap: .28rem;
  border: 0;
  background: transparent;
  padding: 0;
  color: rgba(255, 255, 255, .62);
  font: inherit;
  font-size: .9rem;
  font-weight: 900;
  line-height: 1.2;
  text-decoration: none;
  transition: color .18s ease, opacity .18s ease;
}
.sr-text-button:hover:not(:disabled) {
  color: white;
}
.sr-text-button-danger {
  color: rgba(252, 165, 165, .86);
}
.sr-text-button-danger:hover:not(:disabled) {
  color: #fecaca;
}
.sr-text-button-success {
  color: rgba(187, 247, 208, .86);
}
.sr-text-button:disabled {
  cursor: wait;
  opacity: .55;
}
</style>
