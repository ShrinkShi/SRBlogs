<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap } from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { markdown } from '@codemirror/lang-markdown'
import MarkdownPreview from './MarkdownPreview.vue'

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
</script>

<template>
  <div class="grid gap-4 xl:grid-cols-2">
    <div class="glass overflow-hidden rounded-[28px] p-2"><div ref="host"></div></div>
    <div class="glass max-h-[620px] overflow-auto rounded-[28px] p-6"><MarkdownPreview :content="model" /></div>
  </div>
</template>
