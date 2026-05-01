<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
const props = defineProps<{ content: string }>()
marked.use({ gfm: true, breaks: true, highlight(code, lang) { const language = hljs.getLanguage(lang) ? lang : 'plaintext'; return hljs.highlight(code, { language }).value } } as any)
const html = computed(() => DOMPurify.sanitize(marked.parse(props.content) as string))
</script>
<template><article class="prose-sr max-w-none" v-html="html"></article></template>
