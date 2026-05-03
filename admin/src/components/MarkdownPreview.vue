<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
const props = defineProps<{ content: string }>()

marked.use({
  gfm: true,
  breaks: true,
  async: false,
  highlight(code: string, lang: string) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  }
} as any)

const html = computed(() => {
  const raw = marked.parse(props.content || '') as string
  return DOMPurify.sanitize(raw, {
    USE_PROFILES: { html: true },
    ADD_ATTR: ['target', 'rel', 'style']
  }).replace(/style="([^"]*)"/g, (_match, style) => {
    const color = String(style).match(/color\s*:\s*(#[0-9a-fA-F]{6})/)
    return color ? `style="color:${color[1]}"` : ''
  })
})
</script>

<template>
  <article class="prose-sr prose-sr-admin max-w-none" v-html="html"></article>
</template>
