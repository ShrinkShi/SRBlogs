<script setup lang="ts">
import { floatingApps, type FloatingAppIcon, type FloatingAppItem } from '@/config/floatingApps'
import { useFloatingAppWheel } from '@/composables/useFloatingAppWheel'

const emit = defineEmits<{
  action: [app: FloatingAppItem]
}>()

const {
  expanded,
  dragging,
  positionedApps,
  wheelStyle,
  close,
  toggleExpanded,
  onFabPointerDown,
  onWheel
} = useFloatingAppWheel(floatingApps)

function trigger(app: FloatingAppItem) {
  emit('action', app)
  close()
}

function iconPath(icon: FloatingAppIcon) {
  const paths: Record<FloatingAppIcon, string> = {
    settings: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm8.5 3.5a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7.4 7.4 0 0 0-2-1.2L15.7 2h-4l-.4 3.2a7.4 7.4 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5A7 7 0 0 0 6.8 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1c.6.5 1.3.9 2 1.2l.4 3.2h4l.4-3.2c.7-.3 1.4-.7 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z',
    music: 'M9 18V5l11-2v13M9 18a3 3 0 1 1-2-2.8A3 3 0 0 1 9 18Zm11-2a3 3 0 1 1-2-2.8A3 3 0 0 1 20 16Z',
    search: 'M11 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm9 15-4.2-4.2',
    calculator: 'M6 3h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 4h8M8 12h.1M12 12h.1M16 12h.1M8 16h.1M12 16h.1M16 16h.1',
    article: 'M6 4h9l3 3v13H6V4Zm8 0v4h4M9 11h6M9 15h6M9 18h4'
  }
  return paths[icon]
}
</script>

<template>
  <div
    class="floating-app-wheel"
    :class="{ 'floating-app-wheel-open': expanded, 'floating-app-wheel-dragging': dragging }"
    :style="wheelStyle"
    data-floating-app-wheel
    @wheel="onWheel"
  >
    <button
      v-for="item in positionedApps"
      :key="item.app.id"
      type="button"
      class="floating-app-node"
      :class="{ 'floating-app-node-focused': item.focused }"
      :style="item.style"
      :title="item.app.tooltip || item.app.name"
      :aria-label="item.app.name"
      data-clickable="true"
      @click="trigger(item.app)"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path :d="iconPath(item.app.icon)" />
      </svg>
      <span>{{ item.app.name }}</span>
    </button>

    <button
      type="button"
      class="floating-app-fab"
      :aria-expanded="expanded"
      aria-label="打开功能菜单"
      data-clickable="true"
      @pointerdown="onFabPointerDown"
      @click="toggleExpanded"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 12h14M12 5v14" />
      </svg>
    </button>
  </div>
</template>
