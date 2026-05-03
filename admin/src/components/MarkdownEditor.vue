<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap } from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { markdown } from '@codemirror/lang-markdown'
import MarkdownPreview from './MarkdownPreview.vue'
import { markdownPreviewSample } from '@/constants/markdownSample'

const model = defineModel<string>({ required: true })
const host = ref<HTMLDivElement | null>(null)
const toolbarOpen = ref(true)
const mobileMode = ref<'edit' | 'preview'>('edit')
const split = ref(50)
const dragging = ref(false)
const colorOpen = ref(false)
const colorValue = ref('#67e8f9')
const colorPresets = ['#67e8f9', '#a78bfa', '#f472b6', '#22c55e', '#facc15', '#fb7185', '#ffffff']
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
  window.addEventListener('keydown', onKeydown)
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
  window.removeEventListener('keydown', onKeydown)
})

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') colorOpen.value = false
}

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

function wrap(prefix: string, suffix = prefix, fallback = '文本') {
  const text = selectedText(fallback)
  replaceSelection(`${prefix}${text}${suffix}`, prefix.length, prefix.length + text.length)
}

function insertBlock(template: string, cursorOffset?: number) {
  replaceSelection(template, cursorOffset)
}

function openColorPanel() {
  colorOpen.value = !colorOpen.value
}

function applyColor(color = colorValue.value) {
  const normalized = color.trim()
  if (!/^#[0-9a-fA-F]{6}$/.test(normalized)) return
  colorValue.value = normalized
  wrap(`<span style="color:${normalized}">`, '</span>', '彩色文字')
  colorOpen.value = false
}

const tools = [
  { label: 'B', title: '加粗', run: () => wrap('**', '**', '加粗文字') },
  { label: 'I', title: '斜体', run: () => wrap('*', '*', '斜体文字') },
  { label: '-', title: '无序列表', run: () => insertBlock(`- ${selectedText('列表项')}\n`) },
  { label: '1.', title: '有序列表', run: () => insertBlock(`1. ${selectedText('列表项')}\n`) },
  { label: '>', title: '引用', run: () => insertBlock(`> ${selectedText('引用内容')}\n`) },
  { label: '<>', title: '行内代码', run: () => wrap('`', '`', 'code') },
  { label: '{ }', title: '代码块', run: () => insertBlock(`\n\`\`\`ts\n${selectedText('console.log("hello")')}\n\`\`\`\n`, 7) },
  { label: '表', title: '表格', run: () => insertBlock('\n| 标题 | 内容 |\n| --- | --- |\n| 示例 | 文本 |\n') },
  { label: '链', title: '链接', run: () => wrap('[', '](https://example.com)', '链接文字') },
  { label: '图', title: '图片', run: () => insertBlock('\n![图片描述](https://example.com/image.png)\n') }
]
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

    <div v-if="toolbarOpen" class="relative flex flex-wrap gap-2 rounded-[24px] border border-white/10 bg-white/[0.055] p-3">
      <button v-for="tool in tools" :key="tool.title" type="button" class="rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm font-bold text-white/76 hover:bg-white/15" :title="tool.title" @click="tool.run">
        {{ tool.label }}
      </button>
      <button type="button" class="rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm font-bold text-white/76 hover:bg-white/15" title="字体颜色" @click="openColorPanel">色</button>
      <div v-if="colorOpen" class="absolute left-3 top-full z-20 mt-2 w-72 rounded-3xl border border-white/12 bg-slate-950/95 p-4 shadow-2xl backdrop-blur-xl">
        <p class="text-sm font-bold text-white">字体颜色</p>
        <div class="mt-3 flex items-center gap-3">
          <input v-model="colorValue" type="color" class="h-11 w-11 rounded-xl border border-white/15 bg-white/10 p-1" />
          <input v-model="colorValue" class="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/10 px-3 py-2 text-sm text-white outline-none" placeholder="#67e8f9" />
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <button v-for="preset in colorPresets" :key="preset" type="button" class="h-8 w-8 rounded-xl border border-white/15" :style="{ backgroundColor: preset }" :aria-label="`选择 ${preset}`" @click="applyColor(preset)"></button>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button type="button" class="rounded-xl border border-white/10 px-3 py-2 text-xs text-white/60" @click="colorOpen = false">取消</button>
          <button type="button" class="rounded-xl bg-cyan-300 px-3 py-2 text-xs font-bold text-slate-950" @click="applyColor()">应用</button>
        </div>
      </div>
    </div>

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
