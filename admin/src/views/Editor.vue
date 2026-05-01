<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'

const route = useRoute(); const router = useRouter(); const ui = useUiStore()
const section = ref((route.params.section as 'posts' | 'moments' | 'chatters') || 'posts')
const oldSlug = ref(route.params.slug ? String(route.params.slug) : '')
const content = ref('# 新内容\n')
const meta = reactive({ title: '未命名', date: new Date().toISOString().slice(0,16).replace('T',' '), tagsText: '', draft: true, cover: '', summary: '' })
const slug = ref(`post-${Date.now()}`)

onMounted(async () => {
  if (!oldSlug.value) return
  const item = await adminApi.detail(section.value, oldSlug.value)
  slug.value = item.slug
  content.value = item.content
  meta.title = item.meta.title
  meta.date = item.meta.date
  meta.tagsText = item.meta.tags.join(',')
  meta.draft = item.meta.draft
  meta.cover = item.meta.cover || ''
  meta.summary = item.meta.summary || ''
})

async function save(){
  const payload: ContentItem = {
    slug: slug.value,
    meta: { title: meta.title, date: meta.date, tags: meta.tagsText.split(',').map(s => s.trim()).filter(Boolean), draft: meta.draft, cover: meta.cover, summary: meta.summary },
    content: content.value
  }
  const saved = await adminApi.save(section.value, payload, oldSlug.value || undefined)
  ui.show('已保存')
  router.replace(`/editor/${section.value}/${saved.slug}`)
}
function insertImage(url: string){ content.value += `\n![图片](${url})\n` }
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="grid gap-4 md:grid-cols-3">
        <input v-model="meta.title" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="标题" />
        <input v-model="slug" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="slug" />
        <select v-model="section" disabled class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none"><option>posts</option><option>moments</option><option>chatters</option></select>
        <input v-model="meta.date" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="日期" />
        <input v-model="meta.tagsText" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="标签，逗号分隔" />
        <label class="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-4 py-3"><input v-model="meta.draft" type="checkbox" />草稿</label>
      </div>
      <textarea v-model="meta.summary" rows="2" class="mt-4 w-full rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="摘要"></textarea>
      <input v-model="meta.cover" class="mt-4 w-full rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="封面 URL" />
      <div class="mt-4 flex gap-3"><button class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="save">保存</button><RouterLink to="/posts" class="rounded-2xl border border-white/10 px-5 py-3 text-white/70">返回列表</RouterLink></div>
    </GlassCard>
    <ImageUploader @uploaded="insertImage" />
    <MarkdownEditor v-model="content" />
  </section>
</template>
