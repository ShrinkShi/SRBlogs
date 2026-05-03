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
  renderer: new marked.Renderer(),
  highlight(code: string, lang: string) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  }
} as any)

const headings = computed(() => {
  return props.content
    .split('\n')
    .filter((line) => /^#{2,3}\s+/.test(line))
    .map((line) => {
      const text = line.replace(/^#{2,3}\s+/, '').trim()
      const id = text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-')
      return { text, id }
    })
})

const html = computed(() => {
  const raw = marked.parse(props.content) as string
  const withIds = raw.replace(/<h([23])>(.*?)<\/h\1>/g, (_m: string, level: string, text: string) => {
    const id = String(text).replace(/<[^>]+>/g, '').toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-')
    return `<h${level} id="${id}">${text}</h${level}>`
  })
  return DOMPurify.sanitize(withIds, { ADD_ATTR: ['style'] })
})
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-[1fr_220px]">
    <article class="prose-sr max-w-none leading-8" v-html="html"></article>
    <aside v-if="headings.length" class="glass sticky top-28 hidden h-fit rounded-3xl p-4 lg:block">
      <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-cyan-100/60">目录</p>
      <a v-for="h in headings" :key="h.id" :href="`#${h.id}`" class="block rounded-xl px-2 py-1 text-sm text-white/62 hover:bg-white/10 hover:text-white">
        {{ h.text }}
      </a>
    </aside>
  </div>
</template>
