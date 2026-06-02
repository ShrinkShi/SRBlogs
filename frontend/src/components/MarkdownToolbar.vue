<script setup lang="ts">
import { ref } from 'vue'
import {
  markdownColorPresets,
  markdownToolbarItems,
  normalizeMarkdownColor,
  type MarkdownToolbarCommand,
  type MarkdownToolbarCommandType
} from '@/utils/markdownTools'

const props = withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })
const emit = defineEmits<{ command: [command: MarkdownToolbarCommand] }>()
const colorOpen = ref(false)
const colorValue = ref('#fb7185')

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
  <div class="front-md-toolbar" role="toolbar" aria-label="Markdown 快捷工具">
    <button
      v-for="tool in markdownToolbarItems"
      :key="tool.type"
      type="button"
      :disabled="disabled"
      :title="tool.title"
      :aria-label="tool.title"
      @mousedown.prevent
      @click="run(tool.type)"
    >
      {{ tool.label }}
    </button>
    <div v-if="colorOpen" class="front-md-color-popover">
      <p>字体颜色</p>
      <div class="front-md-color-inputs">
        <input v-model="colorValue" type="color" aria-label="选择字体颜色" />
        <input v-model="colorValue" type="text" aria-label="十六进制颜色值" placeholder="#fb7185" />
      </div>
      <div class="front-md-color-presets">
        <button
          v-for="preset in markdownColorPresets"
          :key="preset"
          type="button"
          :style="{ backgroundColor: preset }"
          :title="preset"
          @click="applyColor(preset)"
        ></button>
      </div>
      <div class="front-md-color-actions">
        <button type="button" @click="colorOpen = false">取消</button>
        <button type="button" @click="applyColor()">应用</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.front-md-toolbar {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
  min-width: 0;
}
.front-md-toolbar > button {
  min-width: 2.1rem;
  min-height: 2.1rem;
  border-radius: 999px;
  background: white;
  color: black;
  font-size: .8rem;
  font-weight: 900;
}
.front-md-toolbar > button:hover:not(:disabled) {
  border-color: rgba(248, 113, 113, .46);
  color: #fecaca;
}
.front-md-color-popover {
  position: absolute;
  left: 0;
  top: calc(100% + .5rem);
  z-index: 10;
  display: grid;
  width: min(17rem, 86vw);
  gap: .6rem;
  border: 1px solid rgba(255, 255, 255, .14);
  border-radius: 1rem;
  background: #191A1B;
  padding: .8rem;
  box-shadow: 0 18px 48px rgba(0, 0, 0, .5);
}
.front-md-color-popover p {
  color: rgba(255, 255, 255, .66);
  font-size: .8rem;
  font-weight: 900;
}
.front-md-color-inputs {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: .45rem;
}
.front-md-color-inputs input[type='text'] {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 999px;
  background: #202123;
  padding: .45rem .55rem;
  color: white;
}
.front-md-color-presets {
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
}
.front-md-color-presets button {
  width: 1.4rem;
  height: 1.4rem;
  border: 1px solid rgba(255, 255, 255, .24);
  border-radius: 999px;
}
.front-md-color-actions {
  display: flex;
  justify-content: flex-end;
  gap: .45rem;
}
.front-md-color-actions button {
  border-radius: 999px;
  background: white;
  padding: .4rem .65rem;
  color: black;
  font-weight: 900;
}
</style>
