<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { usePendingStore } from '@/stores/pending'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'

const route = useRoute(); const router = useRouter(); const ui = useUiStore()
const pendingStore = usePendingStore()
const section = ref((route.params.section as 'posts' | 'moments' | 'chatters') || 'posts')
const oldSlug = ref(route.params.slug ? String(route.params.slug) : '')
const content = ref('# 新内容\n')
const meta = reactive({ title: '未命名', date: new Date().toISOString().slice(0,16).replace('T',' '), tagsText: '', draft: true, cover: '', summary: '' })
const slug = ref(`post-${Date.now()}`)
const saving = ref(false)
const error = ref('')
const success = ref('')
const editorOpen = ref(false)
const slugPattern = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$/
const slugHelp = 'slug 会出现在公开 URL 中，只允许字母、数字、下划线和连字符，例如 vue-fastapi-blog。'

onMounted(async () => {
  if (!oldSlug.value) return
  try {
    const item = await adminApi.detail(section.value, oldSlug.value)
    slug.value = item.slug
    content.value = item.content
    meta.title = item.meta.title
    meta.date = item.meta.date
    meta.tagsText = item.meta.tags.join(',')
    meta.draft = item.meta.draft
    meta.cover = item.meta.cover || ''
    meta.summary = item.meta.summary || ''
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '文章加载失败'
  }
})

function validateForm() {
  error.value = ''
  success.value = ''
  if (!meta.title.trim()) {
    error.value = '标题不能为空。'
    return false
  }
  if (!slug.value.trim()) {
    error.value = 'slug 不能为空。'
    return false
  }
  if (!slugPattern.test(slug.value.trim())) {
    error.value = 'slug 只能包含字母、数字、下划线和连字符，并且必须以字母或数字开头。'
    return false
  }
  if (!content.value.trim()) {
    error.value = 'Markdown 内容不能为空。'
    return false
  }
  return true
}

function buildPayload(draftOverride?: boolean): ContentItem | null {
  if (!validateForm()) return null
  return {
    slug: slug.value.trim(),
    meta: { title: meta.title.trim(), date: meta.date, tags: meta.tagsText.split(',').map(s => s.trim()).filter(Boolean), draft: draftOverride ?? meta.draft, cover: meta.cover, summary: meta.summary },
    content: content.value
  }
}

async function save(){
  const payload = buildPayload()
  if (!payload) return
  saving.value = true
  try {
    const saved = await adminApi.save(section.value, payload, oldSlug.value || undefined)
    oldSlug.value = saved.slug
    slug.value = saved.slug
    meta.draft = saved.meta.draft
    success.value = meta.draft
      ? '保存成功，已作为草稿写入后端文件；前台公开列表不会显示。'
      : '保存成功，已写入后端文件；前台文章列表和详情会显示最新内容。'
    ui.show(meta.draft ? '草稿已保存' : '文章已保存并公开')
    router.replace(`/editor/${section.value}/${saved.slug}`)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
  } finally {
    saving.value = false
  }
}
function stage(draftOverride?: boolean) {
  if (section.value !== 'posts') {
    error.value = 'pendingOperations 第一阶段只覆盖文章新建、编辑、删除和草稿发布。'
    return
  }
  const payload = buildPayload(draftOverride)
  if (!payload) return
  const isPublish = Boolean(oldSlug.value && meta.draft && draftOverride === false)
  pendingStore.add({
    kind: isPublish ? 'publishDraft' : oldSlug.value ? 'editPost' : 'createPost',
    section: section.value,
    title: payload.meta.title,
    slug: payload.slug,
    oldSlug: oldSlug.value || undefined,
    payload
  })
  success.value = isPublish ? '草稿发布已加入暂存队列，点击右侧应用后才会写入。' : '操作已加入暂存队列，点击右侧应用后才会写入。'
  ui.show('已加入暂存队列')
}
async function publishNow() {
  const payload = buildPayload(false)
  if (!payload) return
  saving.value = true
  try {
    const saved = await adminApi.save(section.value, payload, oldSlug.value || undefined)
    oldSlug.value = saved.slug
    slug.value = saved.slug
    meta.draft = false
    success.value = '发布成功，前台文章列表现在可见，文章详情可公开访问。'
    ui.show('草稿已发布，前台可见')
    router.replace(`/editor/${section.value}/${saved.slug}`)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '发布失败'
  } finally {
    saving.value = false
  }
}
function insertImage(url: string){ content.value += `\n![图片](${url})\n` }

function closeEditor() {
  if (!confirm('确认关闭 Markdown 编辑器？未保存内容请先点击保存。')) return
  editorOpen.value = false
}
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="mb-4 text-sm leading-6 text-amber-100/75">“保存”会直接持久化写入后端 Markdown 文件；“加入暂存”只进入本地 pendingOperations，刷新页面会丢失，点击右侧“应用”后才会写后端。</p>
      <div class="grid gap-4 md:grid-cols-3">
        <input v-model="meta.title" aria-label="文章标题" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="标题" />
        <label class="grid gap-1">
          <input v-model="slug" aria-label="文章 slug" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="slug" />
          <span class="px-1 text-xs text-white/45">{{ slugHelp }}</span>
        </label>
        <select v-model="section" disabled aria-label="内容类型" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none"><option>posts</option><option>moments</option><option>chatters</option></select>
        <input v-model="meta.date" aria-label="发布日期" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="日期" />
        <input v-model="meta.tagsText" aria-label="标签，逗号分隔" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="标签，逗号分隔" />
        <label class="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-4 py-3"><input v-model="meta.draft" type="checkbox" />{{ meta.draft ? '当前为草稿：前台不可见' : '当前为已发布：前台可见' }}</label>
      </div>
      <textarea v-model="meta.summary" rows="2" aria-label="文章摘要" class="mt-4 w-full rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="摘要"></textarea>
      <input v-model="meta.cover" aria-label="封面 URL" class="mt-4 w-full rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="封面 URL" />
      <div class="mt-4 flex flex-wrap items-center gap-3">
        <button :disabled="saving" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="save">{{ saving ? '保存中...' : '保存' }}</button>
        <button :disabled="saving" class="rounded-2xl border border-cyan-200/25 px-5 py-3 font-bold text-cyan-100 disabled:opacity-50" @click="stage()">加入暂存</button>
        <button v-if="meta.draft" :disabled="saving" class="rounded-2xl bg-emerald-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="publishNow">立即发布</button>
        <button v-if="meta.draft" :disabled="saving" class="rounded-2xl border border-emerald-200/25 px-5 py-3 font-bold text-emerald-100 disabled:opacity-50" @click="stage(false)">发布加入暂存</button>
        <RouterLink to="/posts" class="rounded-2xl border border-white/10 px-5 py-3 text-white/70">返回列表</RouterLink>
        <span v-if="error" class="text-sm text-red-200/80">{{ error }}</span>
        <span v-if="success" class="text-sm text-emerald-200/80">{{ success }}</span>
      </div>
    </GlassCard>
    <ImageUploader @uploaded="insertImage" />
    <GlassCard>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-2xl font-black text-white">Markdown 正文</h2>
          <p class="mt-2 text-sm text-white/55">点击按钮打开近全屏编辑器，左侧编辑，右侧安全预览；移动端可切换编辑/预览。</p>
        </div>
        <button type="button" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="editorOpen = true">打开 Markdown 编辑器</button>
      </div>
      <p class="mt-4 line-clamp-3 rounded-2xl border border-white/10 bg-white/[0.055] p-4 text-sm leading-6 text-white/56">{{ content || '暂无正文内容' }}</p>
    </GlassCard>

    <Teleport to="body">
      <div v-if="editorOpen" class="fixed inset-0 z-[9990] bg-slate-950/82 p-3 backdrop-blur-xl md:p-6">
        <div class="mx-auto grid h-full max-w-[1500px] grid-rows-[auto_minmax(0,1fr)] gap-4 rounded-[32px] border border-white/12 bg-slate-950/88 p-4 shadow-2xl">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs font-bold uppercase tracking-[.24em] text-cyan-100/45">immersive markdown editor</p>
              <h2 class="truncate text-2xl font-black text-white">{{ meta.title || '未命名文章' }}</h2>
            </div>
            <div class="flex flex-wrap gap-2">
              <button :disabled="saving" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="save">{{ saving ? '保存中...' : '保存' }}</button>
              <button type="button" class="rounded-2xl border border-white/10 px-5 py-3 text-white/72" @click="closeEditor">关闭</button>
            </div>
          </div>
          <div class="min-h-0 overflow-auto">
            <MarkdownEditor v-model="content" />
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>
