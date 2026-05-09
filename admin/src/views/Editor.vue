<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const section = ref((route.params.section as 'posts' | 'moments' | 'chatters') || 'posts')
const oldSlug = ref(route.params.slug ? String(route.params.slug) : '')
const content = ref('# 新内容\n')
const meta = reactive({
  title: '未命名',
  date: new Date().toISOString().slice(0, 16).replace('T', ' '),
  tagsText: '',
  draft: true,
  cover: '',
  summary: ''
})
const slug = ref(`post-${Date.now()}`)
const saving = ref(false)
const error = ref('')
const success = ref('')
const editorOpen = ref(false)
const mdImportName = ref('')

const slugPattern = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$/
const slugHelp = 'slug 会出现在公开 URL 中，只允许字母、数字、下划线和连字符。'
const summaryLength = computed(() => meta.summary.trim().length)
const summaryWarning = computed(() => summaryLength.value > 120)
const contentTypeLabel = computed(() => section.value === 'chatters' ? '杂谈' : section.value === 'moments' ? '动态' : '文章')

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
    error.value = exc instanceof Error ? exc.message : '内容加载失败'
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
    error.value = 'Markdown 正文不能为空。'
    return false
  }
  return true
}

function buildPayload(draftOverride?: boolean): ContentItem | null {
  if (!validateForm()) return null
  return {
    slug: slug.value.trim(),
    meta: {
      title: meta.title.trim(),
      date: meta.date,
      tags: meta.tagsText.split(',').map((item) => item.trim()).filter(Boolean),
      draft: draftOverride ?? meta.draft,
      cover: meta.cover.trim(),
      summary: meta.summary.trim()
    },
    content: content.value
  }
}

async function save(draftOverride?: boolean) {
  const payload = buildPayload(draftOverride)
  if (!payload) return
  saving.value = true
  try {
    const saved = await adminApi.save(section.value, payload, oldSlug.value || undefined)
    oldSlug.value = saved.slug
    slug.value = saved.slug
    meta.draft = saved.meta.draft
    success.value = saved.meta.draft ? '草稿已保存。' : '内容已发布，前台可见。'
    ui.show(success.value)
    router.replace(`/editor/${section.value}/${saved.slug}`)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
  } finally {
    saving.value = false
  }
}

function insertImage(url: string) {
  content.value += `\n![图片](${url})\n`
}

function setCover(url: string) {
  meta.cover = url
}

async function importMarkdown(files: FileList | null) {
  const file = files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.md') && !file.type.startsWith('text/')) {
    error.value = '请上传 .md 或文本格式文件。'
    return
  }
  content.value = await file.text()
  mdImportName.value = file.name
  if (!meta.title.trim() || meta.title === '未命名') {
    meta.title = file.name.replace(/\.md$/i, '')
  }
  ui.show('Markdown 文件已导入编辑区')
}

function closeEditor() {
  if (!confirm('确认关闭 Markdown 编辑器？未保存内容请先点击保存。')) return
  editorOpen.value = false
}
</script>

<template>
  <section class="grid gap-5">
    <div class="admin-page-head">
      <div>
        <p class="eyebrow">markdown editor</p>
        <h1>{{ oldSlug ? `编辑${contentTypeLabel}` : `新增${contentTypeLabel}` }}</h1>
        <p>正文 Markdown 与卡片简介分离维护；封面为空时前台使用默认封面，简介用于首页和列表卡片。</p>
      </div>
      <div class="actions">
        <button :disabled="saving" class="admin-btn admin-btn-ghost" type="button" @click="save(true)">
          {{ saving ? '保存中...' : '保存草稿' }}
        </button>
        <button :disabled="saving" class="admin-btn admin-btn-primary" type="button" @click="save(false)">发布</button>
        <RouterLink to="/content/posts" class="admin-btn admin-btn-ghost">返回内容管理</RouterLink>
      </div>
    </div>

    <div class="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">基础信息</h2>
        <div class="mt-4 grid gap-4">
          <label class="field">
            标题
            <input v-model="meta.title" aria-label="标题" class="admin-input" placeholder="请输入标题" />
          </label>
          <label class="field">
            Slug
            <input v-model="slug" aria-label="slug" class="admin-input font-mono" placeholder="vue-fastapi-blog" />
            <span class="text-xs text-slate-500">{{ slugHelp }}</span>
          </label>
          <div class="grid gap-4 md:grid-cols-2">
            <label class="field">
              日期
              <input v-model="meta.date" aria-label="日期" class="admin-input" />
            </label>
            <label class="field">
              类型
              <select v-model="section" disabled aria-label="内容类型" class="admin-input">
                <option value="posts">正经文章</option>
                <option value="chatters">杂谈</option>
                <option value="moments">动态</option>
              </select>
            </label>
          </div>
          <label class="field">
            标签
            <input v-model="meta.tagsText" aria-label="标签" class="admin-input" placeholder="Vue, FastAPI, Blog" />
          </label>
          <label class="field">
            卡片简介
            <textarea v-model="meta.summary" rows="4" aria-label="卡片简介" class="admin-input resize-y" placeholder="用于首页和列表卡片展示，不等同于 Markdown 正文。"></textarea>
            <span :class="summaryWarning ? 'text-red-700' : 'text-slate-500'" class="text-xs font-bold">
              {{ summaryLength }} 字，建议 120 字以内
            </span>
          </label>
          <label class="field flex-row items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3">
            <span>{{ meta.draft ? '当前为草稿，前台公开列表不可见' : '当前已发布，前台可见' }}</span>
            <input v-model="meta.draft" type="checkbox" />
          </label>
        </div>
      </div>

      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">封面与素材</h2>
        <p class="mt-2 text-sm leading-6 text-slate-600">文章和杂谈必须有封面；这里可直接上传图片，也可留空使用设置中的默认封面。</p>
        <div class="mt-4 grid gap-4">
          <label class="field">
            封面 URL
            <input v-model="meta.cover" aria-label="封面 URL" class="admin-input" placeholder="https://..." />
          </label>
          <ImageUploader @uploaded="setCover" />
          <div v-if="meta.cover" class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <img :src="meta.cover" alt="封面预览" class="h-48 w-full object-cover" />
          </div>
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <h3 class="font-black text-slate-950">正文图片</h3>
            <p class="mt-1 text-sm text-slate-600">上传成功后会自动插入 Markdown 图片语法。</p>
            <div class="mt-3">
              <ImageUploader @uploaded="insertImage" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-black text-slate-950">Markdown 正文</h2>
          <p class="mt-2 text-sm leading-6 text-slate-600">可以直接导入 .md 文件，也可以打开近全屏编辑器进行编辑与预览。</p>
          <p v-if="mdImportName" class="mt-1 text-xs font-bold text-slate-500">已导入：{{ mdImportName }}</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <label class="admin-btn admin-btn-ghost cursor-pointer">
            导入 .md
            <input class="hidden" type="file" accept=".md,text/markdown,text/plain" @change="importMarkdown(($event.target as HTMLInputElement).files)" />
          </label>
          <button type="button" class="admin-btn admin-btn-primary" @click="editorOpen = true">打开 Markdown 编辑器</button>
        </div>
      </div>
      <textarea v-model="content" class="admin-input mt-4 min-h-[360px] font-mono text-sm leading-6" aria-label="Markdown 正文"></textarea>
      <p v-if="error" class="mt-3 text-sm font-bold text-red-700">{{ error }}</p>
      <p v-if="success" class="mt-3 text-sm font-bold text-emerald-700">{{ success }}</p>
    </div>

    <Teleport to="body">
      <div v-if="editorOpen" class="fixed inset-0 z-[9990] bg-black/45 p-3 md:p-6">
        <div class="mx-auto grid h-full max-w-[1500px] grid-rows-[auto_minmax(0,1fr)] gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-2xl">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div class="min-w-0">
              <p class="text-xs font-bold uppercase tracking-[.24em] text-slate-500">markdown editor</p>
              <h2 class="truncate text-2xl font-black text-slate-950">{{ meta.title || '未命名' }}</h2>
            </div>
            <div class="flex flex-wrap gap-2">
              <button :disabled="saving" class="admin-btn admin-btn-primary" @click="save()">{{ saving ? '保存中...' : '保存' }}</button>
              <button type="button" class="admin-btn admin-btn-ghost" @click="closeEditor">关闭</button>
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
