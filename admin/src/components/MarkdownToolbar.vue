<script setup lang="ts">
import { ref } from 'vue'
import {
  markdownColorPresets,
  markdownToolbarItems,
  normalizeMarkdownColor,
  type MarkdownToolbarCommand,
  type MarkdownToolbarCommandType
} from '@/utils/markdownTools'

const props = withDefaults(defineProps<{
  disabled?: boolean
  tone?: 'light' | 'dark'
  compact?: boolean
}>(), {
  disabled: false,
  tone: 'light',
  compact: false
})

const emit = defineEmits<{
  command: [command: MarkdownToolbarCommand]
}>()

const colorOpen = ref(false)
const colorValue = ref('#67e8f9')

function run(type: MarkdownToolbarCommandType) {
  if (props.disabled) return
  if (type === 'color') {
    colorOpen.value = !colorOpen.value
    return
  }
  emit('command', { type } as MarkdownToolbarCommand)
}

function applyColor(color = colorValue.value) {
  if (props.disabled) return
  const normalized = normalizeMarkdownColor(color)
  if (!normalized) return
  colorValue.value = normalized
  colorOpen.value = false
  emit('command', { type: 'color', color: normalized })
}
</script>

<template>
  <div
    class="markdown-toolbar"
    :class="[
      `markdown-toolbar-${tone}`,
      compact ? 'markdown-toolbar-compact' : '',
      disabled ? 'markdown-toolbar-disabled' : ''
    ]"
    role="toolbar"
    aria-label="Markdown 快捷工具"
  >
    <button
      v-for="tool in markdownToolbarItems"
      :key="tool.type"
      type="button"
      class="markdown-toolbar-button"
      :disabled="disabled"
      :title="tool.title"
      :aria-label="tool.title"
      @mousedown.prevent
      @click="run(tool.type)"
    >
      {{ tool.label }}
    </button>

    <div v-if="colorOpen" class="markdown-color-popover">
      <p>字体颜色</p>
      <div class="markdown-color-inputs">
        <input v-model="colorValue" type="color" aria-label="选择字体颜色" />
        <input v-model="colorValue" type="text" aria-label="十六进制颜色值" placeholder="#67e8f9" />
      </div>
      <div class="markdown-color-presets">
        <button
          v-for="preset in markdownColorPresets"
          :key="preset"
          type="button"
          class="markdown-color-swatch"
          :style="{ backgroundColor: preset }"
          :aria-label="`选择 ${preset}`"
          :title="`选择 ${preset}`"
          @click="applyColor(preset)"
        ></button>
      </div>
      <div class="markdown-color-actions">
        <button type="button" class="markdown-color-cancel" @click="colorOpen = false">取消</button>
        <button type="button" class="markdown-color-apply" @click="applyColor()">应用</button>
      </div>
    </div>
  </div>
</template>
