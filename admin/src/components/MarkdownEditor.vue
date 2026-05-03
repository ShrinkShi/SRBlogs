<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
let view: EditorView | null = null
let internal = false

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
})

watch(model, (value) => {
  if (!view || internal) return
  const current = view.state.doc.toString()
  if (value !== current) view.dispatch({ changes: { from: 0, to: current.length, insert: value } })
})

onBeforeUnmount(() => view?.destroy())

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
  const text = view.state.sliceDoc(range.from, range.to)
  return text || fallback
}

function wrap(prefix: string, suffix = prefix, fallback = '文本') {
  const text = selectedText(fallback)
  replaceSelection(`${prefix}${text}${suffix}`, prefix.length, prefix.length + text.length)
}

function insertBlock(template: string, cursorOffset?: number) {
  replaceSelection(template, cursorOffset)
}

function setColor() {
  const color = window.prompt('输入字体颜色，例如 #67e8f9', '#67e8f9')
  if (!color || !/^#[0-9a-fA-F]{6}$/.test(color.trim())) return
  wrap(`<span style="color:${color.trim()}">`, '</span>', '彩色文字')
}

const tools = [
  { label: 'B', title: '加粗', run: () => wrap('**', '**', '加粗文字') },
  { label: 'I', title: '斜体', run: () => wrap('*', '*', '斜体文字') },
  { label: '•', title: '无序列表', run: () => insertBlock(`- ${selectedText('列表项')}\n`) },
  { label: '1.', title: '有序列表', run: () => insertBlock(`1. ${selectedText('列表项')}\n`) },
  { label: '❝', title: '引用', run: () => insertBlock(`> ${selectedText('引用内容')}\n`) },
  { label: '<>', title: '行内代码', run: () => wrap('`', '`', 'code') },
  { label: '{ }', title: '代码块', run: () => insertBlock(`\n\`\`\`ts\n${selectedText('console.log("hello")')}\n\`\`\`\n`, 7) },
  { label: '表', title: '表格', run: () => insertBlock('\n| 标题 | 内容 |\n| --- | --- |\n| 示例 | 文本 |\n') },
  { label: '🔗', title: '链接', run: () => wrap('[', '](https://example.com)', '链接文字') },
  { label: '图', title: '图片', run: () => insertBlock('\n![图片描述](https://example.com/image.png)\n') },
  { label: '色', title: '字体颜色', run: setColor }
]
</script>

<template>
  <div class="grid gap-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-bold uppercase tracking-[.24em] text-cyan-100/45">Markdown</p>
        <p class="mt-1 text-sm text-white/52">右侧预览会经过 DOMPurify 清洗，样式与前台文章详情保持一致但更紧凑。</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="rounded-2xl border border-white/12 bg-white/8 px-4 py-2 text-sm font-bold text-white/72 hover:bg-white/12" type="button" @click="toolbarOpen = !toolbarOpen">
          {{ toolbarOpen ? '收起工具栏' : '展开工具栏' }}
        </button>
        <button class="rounded-2xl border border-white/12 bg-white/8 px-4 py-2 text-sm font-bold text-white/72 hover:bg-white/12" type="button" @click="insertSample">
          插入预览测试样例
        </button>
      </div>
    </div>
    <div v-if="toolbarOpen" class="flex flex-wrap gap-2 rounded-[24px] border border-white/10 bg-white/[0.055] p-3">
      <button v-for="tool in tools" :key="tool.title" type="button" class="rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-sm font-bold text-white/76 hover:bg-white/15" :title="tool.title" @click="tool.run">
        {{ tool.label }}
      </button>
    </div>
    <div class="flex gap-2 sm:hidden">
      <button type="button" class="flex-1 rounded-2xl px-3 py-2 text-sm" :class="mobileMode === 'edit' ? 'bg-cyan-300 text-slate-950' : 'bg-white/10 text-white/70'" @click="mobileMode = 'edit'">编辑</button>
      <button type="button" class="flex-1 rounded-2xl px-3 py-2 text-sm" :class="mobileMode === 'preview' ? 'bg-cyan-300 text-slate-950' : 'bg-white/10 text-white/70'" @click="mobileMode = 'preview'">预览</button>
    </div>
    <div class="grid gap-4 xl:grid-cols-2">
      <div class="glass min-w-0 overflow-hidden rounded-[28px] p-2" :class="mobileMode === 'preview' ? 'hidden sm:block' : ''"><div ref="host"></div></div>
      <div class="glass min-w-0 max-h-[calc(100vh-15rem)] overflow-auto rounded-[28px] p-6" :class="mobileMode === 'edit' ? 'hidden sm:block' : ''"><MarkdownPreview :content="model" /></div>
    </div>
  </div>
</template>
