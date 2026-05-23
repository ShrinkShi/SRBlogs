<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap } from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { markdown } from '@codemirror/lang-markdown'
import MarkdownToolbar from './MarkdownToolbar.vue'
import MarkdownPreview from './MarkdownPreview.vue'
import { markdownPreviewSample } from '@/constants/markdownSample'
import { buildMarkdownInsertion, type MarkdownToolbarCommand } from '@/utils/markdownTools'

const model = defineModel<string>({ required: true })
const host = ref<HTMLDivElement | null>(null)
const toolbarOpen = ref(true)
const mobileMode = ref<'edit' | 'preview'>('edit')
const split = ref(50)
const dragging = ref(false)
let view: EditorView | null = null
let internal = false

const splitStyle = computed(() => ({
  gridTemplateColumns: `${split.value}% 10px minmax(0, 1fr)`
}))

onMounted(() => {
  view = new EditorView({
    parent: host.value!,
    state: EditorState.create({
      doc: model.value,
      extensions: [
        history(),
        markdown(),
        keymap.of([...defaultKeymap, ...historyKeymap]),
        EditorView.lineWrapping,
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            internal = true
            model.value = update.state.doc.toString()
            internal = false
          }
        })
      ]
    })
  })
  window.addEventListener('pointermove', onDrag)
  window.addEventListener('pointerup', stopDrag)
})

watch(model, (value) => {
  if (!view || internal) return
  const current = view.state.doc.toString()
  if (value !== current) view.dispatch({ changes: { from: 0, to: current.length, insert: value } })
})

onBeforeUnmount(() => {
  view?.destroy()
  window.removeEventListener('pointermove', onDrag)
  window.removeEventListener('pointerup', stopDrag)
})

function startDrag(event: PointerEvent) {
  dragging.value = true
  ;(event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId)
}

function onDrag(event: PointerEvent) {
  if (!dragging.value) return
  const target = host.value?.parentElement?.parentElement
  if (!target) return
  const rect = target.getBoundingClientRect()
  const percent = ((event.clientX - rect.left) / rect.width) * 100
  split.value = Math.min(70, Math.max(30, percent))
}

function stopDrag() {
  dragging.value = false
}

function insertSample() {
  model.value = markdownPreviewSample
}

function replaceSelection(insert: string, selectFrom?: number, selectTo?: number) {
  if (!view) {
    model.value += insert
    return
  }
  const range = view.state.selection.main
  view.dispatch({
    changes: { from: range.from, to: range.to, insert },
    selection: { anchor: range.from + (selectFrom ?? insert.length), head: range.from + (selectTo ?? (selectFrom ?? insert.length)) },
    scrollIntoView: true
  })
  view.focus()
}

function selectedText(fallback: string) {
  if (!view) return fallback
  const range = view.state.selection.main
  return view.state.sliceDoc(range.from, range.to) || fallback
}

function applyToolbarCommand(command: MarkdownToolbarCommand) {
  const insertion = buildMarkdownInsertion(command, selectedText)
  if (!insertion) return
  replaceSelection(insertion.text, insertion.selectFrom, insertion.selectTo)
}
</script>

<template>
  <div class="grid gap-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-bold uppercase tracking-[.24em] text-cyan-100/45">Markdown</p>
        <p class="mt-1 text-sm text-white/52">右侧预览继续经过 DOMPurify 清洗，字体颜色只允许安全的十六进制颜色。</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="rounded-2xl border border-white/12 bg-white/8 px-4 py-2 text-sm font-bold text-white/72 hover:bg-white/12" type="button" @click="toolbarOpen = !toolbarOpen">
          {{ toolbarOpen ? '收起工具栏' : '展开工具栏' }}
        </button>
        <button class="rounded-2xl border border-white/12 bg-white/8 px-4 py-2 text-sm font-bold text-white/72 hover:bg-white/12" type="button" @click="insertSample">
          插入测试样例
        </button>
      </div>
    </div>

    <MarkdownToolbar v-if="toolbarOpen" class="markdown-toolbar-panel" @command="applyToolbarCommand" />

    <div class="flex gap-2 sm:hidden">
      <button type="button" class="flex-1 rounded-2xl px-3 py-2 text-sm" :class="mobileMode === 'edit' ? 'bg-cyan-300 text-slate-950' : 'bg-white/10 text-white/70'" @click="mobileMode = 'edit'">编辑</button>
      <button type="button" class="flex-1 rounded-2xl px-3 py-2 text-sm" :class="mobileMode === 'preview' ? 'bg-cyan-300 text-slate-950' : 'bg-white/10 text-white/70'" @click="mobileMode = 'preview'">预览</button>
    </div>

    <div class="min-h-[520px] overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.04] sm:grid" :style="splitStyle">
      <div class="min-w-0 overflow-hidden p-2" :class="mobileMode === 'preview' ? 'hidden sm:block' : ''"><div ref="host"></div></div>
      <div class="resizer hidden sm:block" role="separator" aria-label="拖动调整编辑和预览宽度" @pointerdown="startDrag"></div>
      <div class="min-w-0 max-h-[calc(100vh-15rem)] overflow-auto p-6" :class="mobileMode === 'edit' ? 'hidden sm:block' : ''"><MarkdownPreview :content="model" /></div>
    </div>
  </div>
</template>

<style scoped>
.resizer {
  cursor: col-resize;
  background: linear-gradient(to bottom, transparent, rgba(103, 232, 249, .4), transparent);
  transition: background .2s ease;
}
.resizer:hover {
  background: rgba(103, 232, 249, .28);
}
</style>
