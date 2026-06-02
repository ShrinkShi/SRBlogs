import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { FloatingAppItem } from '@/config/floatingApps'

type WheelPosition = { left: number; top: number }

const STORAGE_KEY = 'sr-floating-app-wheel-position'
const FAB_SIZE = 58
const DRAG_THRESHOLD = 6
const WHEEL_THROTTLE_MS = 180

function clampPosition(next: WheelPosition): WheelPosition {
  if (typeof window === 'undefined') return next
  const margin = 14
  return {
    left: Math.min(Math.max(margin, next.left), Math.max(margin, window.innerWidth - FAB_SIZE - margin)),
    top: Math.min(Math.max(margin, next.top), Math.max(margin, window.innerHeight - FAB_SIZE - margin))
  }
}

function defaultPosition(): WheelPosition {
  if (typeof window === 'undefined') return { left: 20, top: 560 }
  return clampPosition({ left: 22, top: window.innerHeight - FAB_SIZE - 22 })
}

export function useFloatingAppWheel(apps: FloatingAppItem[]) {
  const expanded = ref(false)
  const focusedIndex = ref(0)
  const position = ref<WheelPosition>(defaultPosition())
  const dragging = ref(false)
  const dragMoved = ref(false)
  let dragStart: { x: number; y: number; left: number; top: number } | null = null
  let lastWheelAt = 0
  let suppressClickUntil = 0

  const enabledApps = computed(() =>
    apps
      .filter((app) => app.enabled !== false)
      .sort((a, b) => Number(a.order ?? 0) - Number(b.order ?? 0))
  )

  const wheelStyle = computed(() => ({
    left: `${position.value.left}px`,
    top: `${position.value.top}px`
  }))

  const positionedApps = computed(() => {
    const list = enabledApps.value
    const count = list.length
    if (!count) return []
    const radius = count > 6 ? 118 : 106
    const startAngle = 20
    const endAngle = count > 6 ? 170 : 138
    const step = count > 1 ? (endAngle - startAngle) / (count - 1) : 0
    return list.map((app, index) => {
      const slot = (index - focusedIndex.value + count) % count
      const angle = (startAngle + slot * step) * Math.PI / 180
      return {
        app,
        focused: index === focusedIndex.value,
        style: {
          '--wheel-x': `${Math.cos(angle) * radius}px`,
          '--wheel-y': `${-Math.sin(angle) * radius}px`,
          '--wheel-delay': `${Math.min(slot, 6) * 24}ms`
        } as Record<string, string>
      }
    })
  })

  function loadPosition() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
      if (parsed && Number.isFinite(parsed.left) && Number.isFinite(parsed.top)) {
        position.value = clampPosition(parsed)
      }
    } catch {
      position.value = defaultPosition()
    }
  }

  function savePosition() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(position.value))
  }

  function toggleExpanded() {
    if (Date.now() < suppressClickUntil) return
    expanded.value = !expanded.value
  }

  function close() {
    expanded.value = false
  }

  function onFabPointerDown(event: PointerEvent) {
    dragStart = {
      x: event.clientX,
      y: event.clientY,
      left: position.value.left,
      top: position.value.top
    }
    dragging.value = true
    dragMoved.value = false
    ;(event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId)
  }

  function onPointerMove(event: PointerEvent) {
    if (!dragStart) return
    const dx = event.clientX - dragStart.x
    const dy = event.clientY - dragStart.y
    if (Math.hypot(dx, dy) > DRAG_THRESHOLD) dragMoved.value = true
    if (!dragMoved.value) return
    position.value = clampPosition({
      left: dragStart.left + dx,
      top: dragStart.top + dy
    })
  }

  function onPointerUp() {
    if (!dragStart) return
    dragStart = null
    dragging.value = false
    if (dragMoved.value) {
      suppressClickUntil = Date.now() + 220
      savePosition()
    }
  }

  function rotate(delta: number) {
    const count = enabledApps.value.length
    if (!count) return
    focusedIndex.value = (focusedIndex.value + delta + count) % count
  }

  function onWheel(event: WheelEvent) {
    if (!expanded.value) return
    event.preventDefault()
    const now = Date.now()
    if (now - lastWheelAt < WHEEL_THROTTLE_MS) return
    lastWheelAt = now
    rotate(event.deltaY > 0 ? 1 : -1)
  }

  function onResize() {
    position.value = clampPosition(position.value)
    savePosition()
  }

  onMounted(() => {
    loadPosition()
    window.addEventListener('pointermove', onPointerMove)
    window.addEventListener('pointerup', onPointerUp)
    window.addEventListener('resize', onResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', onPointerUp)
    window.removeEventListener('resize', onResize)
  })

  return {
    expanded,
    focusedIndex,
    dragging,
    enabledApps,
    positionedApps,
    wheelStyle,
    close,
    rotate,
    toggleExpanded,
    onFabPointerDown,
    onWheel
  }
}
