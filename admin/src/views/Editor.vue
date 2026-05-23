<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import MarkdownPreview from '@/components/MarkdownPreview.vue'
import MarkdownToolbar from '@/components/MarkdownToolbar.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'
import { buildMarkdownInsertion, type MarkdownInsertion, type MarkdownToolbarCommand } from '@/utils/markdownTools'

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
const initialMarkdown = ref('')
const closeConfirmOpen = ref(false)
const mdImportName = ref('')
const adminSettings = ref<Record<string, any>>({})
const markdownMode = ref<'write' | 'preview'>('write')
const bodyTextarea = ref<HTMLTextAreaElement | null>(null)
const bodyImageInput = ref<HTMLInputElement | null>(null)
const coverImageInput = ref<HTMLInputElement | null>(null)
const bodyImageUploading = ref(false)
const coverUploading = ref(false)
const markdownToast = reactive({
  message: '',
  type: 'success' as 'success' | 'error'
})
let markdownToastTimer: ReturnType<typeof setTimeout> | undefined
let editorShortcutBound = false
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop'
const defaultCover = computed(() =>
  String(adminSettings.value.defaultPostCover || adminSettings.value.defaultCover || fallbackCover)
)

const slugPattern = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$/
const slugHelp = 'slug 会出现在公开 URL 中，只允许字母、数字、下划线和连字符。'
const summaryLength = computed(() => meta.summary.trim().length)
const summaryWarning = computed(() => summaryLength.value > 120)
const returnPath = computed(() => section.value === 'chatters' ? '/content/articles?kind=chatters' : '/content/articles')
const markdownDirty = computed(() => editorOpen.value && content.value !== initialMarkdown.value)
const dateInput = computed({
  get: () => {
    if (!meta.date) return ''
    if (/^\d{4}-\d{2}-\d{2}$/.test(meta.date)) return `${meta.date}T00:00`
    return meta.date.replace(' ', 'T').slice(0, 16)
  },
  set: (value: string) => {
    meta.date = value ? value.replace('T', ' ') : ''
  }
})
const coverDisplayName = computed(() => {
  const value = meta.cover.trim()
  if (!value) return '未设置封面'
  try {
    const parsed = new URL(value, window.location.origin)
    const filename = decodeURIComponent(parsed.pathname.split('/').filter(Boolean).pop() || '')
    return filename ? `已上传 ${filename}` : '已设置封面'
  } catch {
    const filename = value.split('/').filter(Boolean).pop() || ''
    return filename ? `已上传 ${filename}` : '已设置封面'
  }
})

onMounted(async () => {
  try {
    adminSettings.value = await adminApi.json<Record<string, any>>('/admin/settings')
  } catch {
    adminSettings.value = {}
  }
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

onBeforeUnmount(() => {
  unbindEditorShortcuts()
  if (markdownToastTimer) clearTimeout(markdownToastTimer)
})

watch(editorOpen, (open) => {
  if (open) {
    bindEditorShortcuts()
  } else {
    unbindEditorShortcuts()
    closeConfirmOpen.value = false
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
  const cover = meta.cover.trim() || defaultCover.value
  return {
    slug: slug.value.trim(),
    meta: {
      title: meta.title.trim(),
      date: meta.date,
      tags: meta.tagsText.split(',').map((item) => item.trim()).filter(Boolean),
      draft: draftOverride ?? meta.draft,
      cover,
      summary: meta.summary.trim()
    },
    content: content.value
  }
}

async function save(draftOverride = meta.draft, options: { notify?: boolean } = {}) {
  const payload = buildPayload(draftOverride)
  if (!payload) return false
  saving.value = true
  try {
    const saved = await adminApi.save(section.value, payload, oldSlug.value || undefined)
    oldSlug.value = saved.slug
    slug.value = saved.slug
    meta.draft = saved.meta.draft
    success.value = saved.meta.draft ? '草稿已保存。' : '内容已发布，前台可见。'
    if (options.notify !== false) ui.show(success.value)
    router.replace(`/editor/${section.value}/${saved.slug}`)
    return true
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
    return false
  } finally {
    saving.value = false
  }
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

function openEditor() {
  initialMarkdown.value = content.value
  closeConfirmOpen.value = false
  hideMarkdownToast()
  editorOpen.value = true
}

function closeEditor() {
  if (markdownDirty.value) {
    closeConfirmOpen.value = true
    return
  }
  closeEditorNow()
}

function closeEditorNow() {
  editorOpen.value = false
  closeConfirmOpen.value = false
}

function keepEditing() {
  closeConfirmOpen.value = false
}

function discardMarkdownChanges() {
  content.value = initialMarkdown.value
  closeEditorNow()
}

function showMarkdownToast(message: string, type: 'success' | 'error') {
  if (markdownToastTimer) clearTimeout(markdownToastTimer)
  markdownToast.message = message
  markdownToast.type = type
  markdownToastTimer = setTimeout(() => {
    markdownToast.message = ''
  }, 2000)
}

function hideMarkdownToast() {
  if (markdownToastTimer) clearTimeout(markdownToastTimer)
  markdownToast.message = ''
}

async function saveMarkdownEditor() {
  if (!editorOpen.value || saving.value) return
  const saved = await save(meta.draft, { notify: false })
  if (saved) {
    initialMarkdown.value = content.value
    closeConfirmOpen.value = false
    showMarkdownToast('Markdown 已保存', 'success')
    return
  }
  showMarkdownToast('保存失败，请重试', 'error')
}

function onEditorKeydown(event: KeyboardEvent) {
  if (!editorOpen.value) return
  const key = event.key.toLowerCase()
  if ((event.ctrlKey || event.metaKey) && key === 's') {
    event.preventDefault()
    void saveMarkdownEditor()
    return
  }
  if (event.key === 'Escape' && closeConfirmOpen.value) {
    event.preventDefault()
    keepEditing()
  }
}

function bindEditorShortcuts() {
  if (!editorOpen.value || editorShortcutBound) return
  window.addEventListener('keydown', onEditorKeydown)
  editorShortcutBound = true
}

function unbindEditorShortcuts() {
  if (!editorShortcutBound) return
  window.removeEventListener('keydown', onEditorKeydown)
  editorShortcutBound = false
}

function escapeAttribute(value: string) {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function insertTextAtCursor(text: string) {
  const textarea = bodyTextarea.value
  if (!textarea) {
    content.value += `\n${text}`
    return
  }
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  content.value = `${content.value.slice(0, start)}${text}${content.value.slice(end)}`
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + text.length, start + text.length)
  })
}

function selectedBodyText(fallback: string) {
  const textarea = bodyTextarea.value
  if (!textarea) return fallback
  return content.value.slice(textarea.selectionStart, textarea.selectionEnd) || fallback
}

function replaceBodySelection(insertion: MarkdownInsertion) {
  const textarea = bodyTextarea.value
  if (!textarea) {
    content.value += `\n${insertion.text}`
    return
  }
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  content.value = `${content.value.slice(0, start)}${insertion.text}${content.value.slice(end)}`
  const cursorStart = start + (insertion.selectFrom ?? insertion.text.length)
  const cursorEnd = start + (insertion.selectTo ?? (insertion.selectFrom ?? insertion.text.length))
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(cursorStart, cursorEnd)
  })
}

async function applyMarkdownToolbar(command: MarkdownToolbarCommand) {
  if (command.type === 'image') {
    chooseBodyImage()
    return
  }
  markdownMode.value = 'write'
  await nextTick()
  const insertion = buildMarkdownInsertion(command, selectedBodyText)
  if (insertion) replaceBodySelection(insertion)
}

function replaceFirstText(target: string, replacement: string) {
  const index = content.value.indexOf(target)
  if (index < 0) {
    insertTextAtCursor(replacement)
    return
  }
  content.value = `${content.value.slice(0, index)}${replacement}${content.value.slice(index + target.length)}`
}

function readImageSize(file: File): Promise<{ width: number; height: number } | null> {
  if (!file.type.startsWith('image/')) return Promise.resolve(null)
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const image = new Image()
    image.onload = () => {
      URL.revokeObjectURL(url)
      resolve({ width: image.naturalWidth, height: image.naturalHeight })
    }
    image.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(null)
    }
    image.src = url
  })
}

function buildImageHtml(file: File, url: string, size: { width: number; height: number } | null) {
  const alt = escapeAttribute(file.name.replace(/\.[^.]+$/, '') || '图片')
  const src = escapeAttribute(url)
  if (size?.width && size?.height) {
    return `<img width="${size.width}" height="${size.height}" alt="${alt}" src="${src}" />`
  }
  return `<img alt="${alt}" src="${src}" />`
}

function chooseBodyImage() {
  bodyImageInput.value?.click()
}

function chooseCoverImage() {
  coverImageInput.value?.click()
}

async function uploadBodyImage(files: FileList | null) {
  const file = files?.[0]
  if (!file) return
  markdownMode.value = 'write'
  const placeholder = `<!-- 正在上传 "${file.name}"... -->`
  error.value = ''
  bodyImageUploading.value = true
  await nextTick()
  insertTextAtCursor(`\n${placeholder}\n`)
  try {
    const [size, data] = await Promise.all([
      readImageSize(file),
      adminApi.upload(file)
    ])
    replaceFirstText(placeholder, buildImageHtml(file, data.url, size))
    ui.show('正文图片已插入')
  } catch (exc) {
    replaceFirstText(`\n${placeholder}\n`, '')
    replaceFirstText(placeholder, '')
    error.value = exc instanceof Error ? exc.message : '正文图片上传失败'
  } finally {
    bodyImageUploading.value = false
    if (bodyImageInput.value) bodyImageInput.value.value = ''
  }
}

async function uploadCoverImage(files: FileList | null) {
  const file = files?.[0]
  if (!file) return
  coverUploading.value = true
  error.value = ''
  try {
    const data = await adminApi.upload(file)
    meta.cover = data.url
    ui.show('封面已上传')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '封面上传失败'
  } finally {
    coverUploading.value = false
    if (coverImageInput.value) coverImageInput.value.value = ''
  }
}
</script>

<template>
  <section class="grid gap-5">
    <div class="editor-layout">
      <div class="editor-main-panel">
        <section class="editor-panel-section editor-panel-section-first">
          <label class="field">
            标题
            <input v-model="meta.title" aria-label="标题" class="admin-input editor-title-input" placeholder="请输入文章标题" />
          </label>
        </section>

        <section class="editor-panel-section">
          <div class="github-editor">
            <div class="github-editor-head">
              <div class="github-editor-tabs" role="tablist" aria-label="Markdown 正文模式">
                <button
                  type="button"
                  role="tab"
                  :aria-selected="markdownMode === 'write'"
                  :class="markdownMode === 'write' ? 'github-editor-tab-active' : ''"
                  @click="markdownMode = 'write'"
                >
                  编写
                </button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="markdownMode === 'preview'"
                  :class="markdownMode === 'preview' ? 'github-editor-tab-active' : ''"
                  @click="markdownMode = 'preview'"
                >
                  预览
                </button>
              </div>
              <MarkdownToolbar
                class="github-editor-toolbar"
                compact
                :disabled="markdownMode !== 'write' || bodyImageUploading"
                @command="applyMarkdownToolbar"
              />
              <div class="github-editor-tools">
                <label class="admin-btn admin-btn-ghost cursor-pointer px-3 py-2 text-sm">
                  导入 .md
                  <input class="hidden" type="file" accept=".md,text/markdown,text/plain" @change="importMarkdown(($event.target as HTMLInputElement).files)" />
                </label>
                <button class="admin-btn admin-btn-ghost px-3 py-2 text-sm" type="button" :disabled="bodyImageUploading" @click="chooseBodyImage">
                  {{ bodyImageUploading ? '上传中...' : '插入图片' }}
                </button>
                <button type="button" class="admin-btn admin-btn-ghost px-3 py-2 text-sm" @click="openEditor">打开 Markdown 编辑器</button>
                <input ref="bodyImageInput" class="hidden" type="file" accept="image/*" @change="uploadBodyImage(($event.target as HTMLInputElement).files)" />
              </div>
            </div>

            <p v-if="mdImportName" class="github-editor-note">已导入：{{ mdImportName }}</p>

            <textarea
              v-if="markdownMode === 'write'"
              ref="bodyTextarea"
              v-model="content"
              class="github-editor-textarea"
              aria-label="Markdown 正文"
              placeholder="在这里编写 Markdown 正文，支持直接粘贴大段内容。"
            ></textarea>
            <div v-else class="github-editor-preview">
              <MarkdownPreview :content="content" />
            </div>
          </div>
        </section>

        <div class="editor-action-bar">
          <label class="editor-draft-check">
            <input v-model="meta.draft" type="checkbox" />
            <span>存为草稿</span>
          </label>
          <div class="flex flex-wrap gap-2">
            <RouterLink :to="returnPath" class="admin-btn admin-btn-ghost">取消</RouterLink>
            <button :disabled="saving" class="admin-btn admin-btn-save" type="button" @click="save(meta.draft)">
              {{ saving ? '保存中...' : meta.draft ? '保存草稿' : '发布' }}
            </button>
          </div>
        </div>
      </div>

      <aside class="editor-side editor-side-panel">
        <section class="editor-panel-section editor-panel-section-first">
          <h2 class="editor-group-title">文章类型</h2>
          <div class="admin-radio-group mt-3" role="radiogroup" aria-label="内容类型">
            <label class="admin-radio-pill" :class="section === 'posts' ? 'admin-active-option admin-radio-pill-active' : ''">
              <input v-model="section" type="radio" value="posts" />
              <span>正经</span>
            </label>
            <label class="admin-radio-pill" :class="section === 'chatters' ? 'admin-active-option admin-radio-pill-active' : ''">
              <input v-model="section" type="radio" value="chatters" />
              <span>杂谈</span>
            </label>
          </div>
        </section>

        <section class="editor-panel-section">
          <h2 class="editor-group-title">日期</h2>
          <input v-model="dateInput" aria-label="日期" class="admin-input mt-3" type="datetime-local" />
        </section>

        <section class="editor-panel-section">
          <h2 class="editor-group-title">标签</h2>
          <input v-model="meta.tagsText" aria-label="标签" class="admin-input mt-3" placeholder="Vue, FastAPI, Blog" />
        </section>

        <section class="editor-panel-section">
          <h2 class="editor-group-title inline-flex items-center gap-2">
            简介
            <button
              type="button"
              class="admin-help-tip"
              data-tip="30 字，建议 120 字以内。"
              title="30 字，建议 120 字以内。"
              aria-label="卡片简介说明"
            >?</button>
          </h2>
          <textarea v-model="meta.summary" rows="3" aria-label="卡片简介" class="admin-input editor-summary-input mt-3 resize-y" placeholder="用于首页和列表卡片展示。"></textarea>
          <span :class="summaryWarning ? 'text-red-700' : 'text-slate-500'" class="mt-2 block text-xs font-bold">
            {{ summaryLength }} 字，建议 120 字以内
          </span>
        </section>

        <section class="editor-panel-section">
          <h2 class="editor-group-title">封面</h2>
          <div class="editor-cover-line mt-3">
            <span class="truncate">{{ coverDisplayName }}</span>
            <button class="admin-btn admin-btn-ghost shrink-0 px-3 py-2 text-sm" type="button" :disabled="coverUploading" @click="chooseCoverImage">
              {{ coverUploading ? '上传中...' : '上传' }}
            </button>
            <input ref="coverImageInput" class="hidden" type="file" accept="image/*" @change="uploadCoverImage(($event.target as HTMLInputElement).files)" />
          </div>
        </section>

        <details class="editor-details editor-panel-section">
          <summary>高级设置</summary>
          <label class="field mt-4">
            <span class="inline-flex items-center gap-2">
              Slug
              <button type="button" class="admin-help-tip" :data-tip="slugHelp" :title="slugHelp" aria-label="Slug 说明">?</button>
            </span>
            <input v-model="slug" aria-label="slug" class="admin-input font-mono" placeholder="vue-fastapi-blog" />
          </label>
          <label class="field mt-4">
            封面 URL
            <input v-model="meta.cover" aria-label="封面 URL" class="admin-input" placeholder="https://..." />
          </label>
        </details>
      </aside>
    </div>

    <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{{ error }}</p>
    <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-700">{{ success }}</p>

    <Teleport to="body">
      <div v-if="editorOpen" class="fixed inset-0 z-[9990] bg-black/45 p-3 md:p-6">
        <div class="mx-auto grid h-full max-w-[1500px] grid-rows-[auto_minmax(0,1fr)_auto] gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-2xl">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div class="min-w-0">
              <p class="text-xs font-bold tracking-[.18em] text-slate-500">Markdown 编辑器</p>
              <h2 class="truncate text-2xl font-black text-slate-950">{{ meta.title || '未命名' }}</h2>
            </div>
            <div class="flex flex-wrap gap-2">
              <button type="button" class="admin-btn admin-btn-ghost" @click="closeEditor">关闭</button>
            </div>
          </div>
          <div class="min-h-0 overflow-auto">
            <MarkdownEditor v-model="content" />
          </div>
          <div class="admin-bottom-actions border-t border-slate-200 pt-4">
            <button :disabled="saving" class="admin-btn admin-btn-save" @click="saveMarkdownEditor">{{ saving ? '保存中...' : meta.draft ? '保存草稿' : '发布' }}</button>
            <button type="button" class="admin-btn admin-btn-ghost" @click="closeEditor">关闭</button>
          </div>
        </div>
        <div v-if="closeConfirmOpen" class="editor-confirm-backdrop" @click.self="keepEditing">
          <div class="editor-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="editor-close-confirm-title">
            <h3 id="editor-close-confirm-title">未保存的修改</h3>
            <p>当前 Markdown 内容尚未保存，关闭后修改将丢失。</p>
            <div class="editor-confirm-actions">
              <button type="button" class="admin-btn admin-btn-ghost" @click="keepEditing">继续编辑</button>
              <button type="button" class="admin-btn admin-btn-danger" @click="discardMarkdownChanges">放弃修改</button>
            </div>
          </div>
        </div>
        <Transition name="editor-toast">
          <div
            v-if="markdownToast.message"
            class="editor-markdown-toast"
            :class="markdownToast.type === 'success' ? 'editor-markdown-toast-success' : 'editor-markdown-toast-error'"
            role="status"
          >
            {{ markdownToast.message }}
          </div>
        </Transition>
      </div>
    </Teleport>
  </section>
</template>
