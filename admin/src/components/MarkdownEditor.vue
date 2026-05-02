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
</script>

<template>
  <div class="grid gap-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm font-bold uppercase tracking-[.24em] text-cyan-100/45">Markdown</p>
        <p class="mt-1 text-sm text-white/52">右侧预览会经过 DOMPurify 清洗，样式与前台文章详情保持一致但更紧凑。</p>
      </div>
      <button class="rounded-2xl border border-white/12 bg-white/8 px-4 py-2 text-sm font-bold text-white/72 hover:bg-white/12" type="button" @click="insertSample">
        插入预览测试样例
      </button>
    </div>
    <div class="grid gap-4 xl:grid-cols-2">
      <div class="glass min-w-0 overflow-hidden rounded-[28px] p-2"><div ref="host"></div></div>
      <div class="glass min-w-0 max-h-[620px] overflow-auto rounded-[28px] p-6"><MarkdownPreview :content="model" /></div>
    </div>
  </div>
</template>
