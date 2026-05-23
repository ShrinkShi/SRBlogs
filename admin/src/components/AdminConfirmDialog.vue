<script setup lang="ts">
import type { ConfirmDialogVariant } from '@/composables/useConfirmDialog'

defineProps<{
  open: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  variant: ConfirmDialogVariant
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="admin-confirm-backdrop" role="dialog" aria-modal="true" :aria-label="title" @click.self="emit('cancel')">
      <div class="admin-confirm-dialog">
        <h3>{{ title }}</h3>
        <p>{{ message }}</p>
        <div class="admin-confirm-actions">
          <button type="button" class="admin-btn admin-btn-ghost" @click="emit('cancel')">{{ cancelText }}</button>
          <button
            type="button"
            class="admin-btn"
            :class="variant === 'danger' ? 'admin-btn-danger' : 'admin-btn-primary'"
            @click="emit('confirm')"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
