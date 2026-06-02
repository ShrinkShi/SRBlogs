<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { contentApi } from '@/api/content'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import MarkdownToolbar from '@/components/MarkdownToolbar.vue'
import { useUiStore } from '@/stores/ui'
import { buildMarkdownInsertion, type MarkdownToolbarCommand } from '@/utils/markdownTools'
import type { ContentItem } from '@/types'

type Section = 'posts' | 'chatters' | 'moments'

const props = withDefaults(defineProps<{
  modelValue: boolean
  section: Section
  slug?: string
  title?: string
}>(), {
  slug: '',
  title: '编辑内容'
})

const emit = defineEmits<{ 'update:modelValue': [value: boolean]; saved: [item: ContentItem] }>()
const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const error = ref('')
const mode = ref<'write' | 'preview'>('write')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const imageInput = ref<HTMLInputElement | null>(null)
const coverInput = ref<HTMLInputElement | null>(null)
const currentSection = ref<Section>('posts')
const oldSlug = ref('')
const slug = ref('')
const content = ref('# 新内容\n')
const meta = reactive({
  title: '未命名',
  date: '',
  tagsText: '',
  draft: true,
  cover: '',
  summary: '',
  location: '',
  imagesText: ''
})

const isMoment = computed(() => currentSection.value === 'moments')
const modalTitle = computed(() => props.slug ? props.title || '编辑内容' : isMoment.value ? '新增说说' : currentSection.value === 'chatters' ? '新增杂谈' : '新增文章')
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

function defaultDate() {
  return new Date().toISOString().slice(0, 16).replace('T', ' ')
}

function defaultSlug(section: Section) {
  const prefix = section === 'moments' ? 'moment' : section === 'chatters' ? 'chatter' : 'post'
  return `${prefix}-${Date.now()}`
}

function resetForm() {
  currentSection.value = props.section
  oldSlug.value = props.slug || ''
  slug.value = props.slug || defaultSlug(props.section)
  content.value = isMoment.value ? '写一条说说。' : '# 新内容\n'
  meta.title = '未命名'
  meta.date = defaultDate()
  meta.tagsText = ''
  meta.draft = true
  meta.cover = ''
  meta.summary = ''
  meta.location = ''
  meta.imagesText = ''
  error.value = ''
  mode.value = 'write'
}

async function load() {
  resetForm()
  if (!props.slug) return
  loading.value = true
  try {
    const item = await contentApi.detail(props.section, props.slug, true)
    slug.value = item.slug
    content.value = item.content
    meta.title = item.meta.title
    meta.date = item.meta.date || defaultDate()
    meta.tagsText = (item.meta.tags || []).join(', ')
    meta.draft = item.meta.draft
    meta.cover = item.meta.cover || ''
    meta.summary = item.meta.summary || ''
    meta.location = item.meta.location || ''
    meta.imagesText = Array.isArray(item.meta.images) ? item.meta.images.join('\n') : ''
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '内容加载失败'
  } finally {
    loading.value = false
  }
}

function close() {
  emit('update:modelValue', false)
}

function getSelectedText(fallback: string) {
  const element = textareaRef.value
  if (!element) return fallback
  const selected = content.value.slice(element.selectionStart, element.selectionEnd)
  return selected || fallback
}

async function applyInsertion(text: string, selectFrom?: number, selectTo?: number) {
  const element = textareaRef.value
  if (!element) {
    content.value += text
    return
  }
  const start = element.selectionStart
  const end = element.selectionEnd
  content.value = `${content.value.slice(0, start)}${text}${content.value.slice(end)}`
  await nextTick()
  const selectionStart = start + (selectFrom ?? text.length)
  const selectionEnd = start + (selectTo ?? text.length)
  element.focus()
  element.setSelectionRange(selectionStart, selectionEnd)
}

async function runToolbar(command: MarkdownToolbarCommand) {
  if (command.type === 'image') {
    imageInput.value?.click()
    return
  }
  const insertion = buildMarkdownInsertion(command, getSelectedText)
  if (insertion) await applyInsertion(insertion.text, insertion.selectFrom, insertion.selectTo)
}

async function uploadInlineImage(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  ;(event.target as HTMLInputElement).value = ''
  if (!file) return
  uploading.value = true
  try {
    const data = await contentApi.upload(file)
    await applyInsertion(`\n<img alt="${file.name.replace(/"/g, '')}" src="${data.url}" />\n`)
    ui.showToast('图片已插入', 'success')
  } catch {
    ui.showToast('图片上传失败', 'error')
  } finally {
    uploading.value = false
  }
}

async function uploadCover(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  ;(event.target as HTMLInputElement).value = ''
  if (!file) return
  uploading.value = true
  try {
    const data = await contentApi.upload(file)
    meta.cover = data.url
    ui.showToast('封面已上传', 'success')
  } catch {
    ui.showToast('封面上传失败', 'error')
  } finally {
    uploading.value = false
  }
}

function validate() {
  error.value = ''
  if (!meta.title.trim()) error.value = '标题不能为空。'
  else if (!slug.value.trim()) error.value = 'Slug 不能为空。'
  else if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$/.test(slug.value.trim())) error.value = 'Slug 只能包含字母、数字、下划线和连字符。'
  else if (!content.value.trim()) error.value = '正文不能为空。'
  return !error.value
}

async function save() {
  if (!validate()) return
  saving.value = true
  try {
    const payload: ContentItem = {
      slug: slug.value.trim(),
      content: content.value,
      meta: {
        title: meta.title.trim(),
        date: meta.date || defaultDate(),
        tags: meta.tagsText.split(',').map((tag) => tag.trim()).filter(Boolean),
        draft: meta.draft,
        cover: meta.cover.trim(),
        summary: meta.summary.trim(),
        location: meta.location.trim(),
        images: meta.imagesText.split(/\r?\n/).map((url) => url.trim()).filter(Boolean)
      }
    }
    const result = await contentApi.saveContent(currentSection.value, payload, oldSlug.value || undefined)
    ui.showToast(meta.draft ? '草稿已保存' : '内容已发布', 'success')
    emit('saved', result)
    close()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
  } finally {
    saving.value = false
  }
}

watch(() => props.modelValue, (open) => {
  if (open) void load()
})
</script>

<template>
  <Teleport to="body">
    <Transition name="front-editor-pop">
      <div v-if="modelValue" class="front-editor-backdrop" role="dialog" aria-modal="true" @click.self="close" @keydown.esc.window="close">
        <section class="front-editor-shell">
          <header class="front-editor-head">
            <strong>{{ modalTitle }}</strong>
            <button type="button" aria-label="关闭编辑弹窗" @click="close">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
            </button>
          </header>

          <div v-if="loading" class="front-editor-state">内容加载中...</div>
          <div v-else class="front-editor-body">
            <main class="front-editor-main">
              <label class="front-editor-field">
                <span>{{ isMoment ? '说说标题 / 摘要' : '标题' }}</span>
                <input v-model="meta.title" class="front-editor-title-input" />
              </label>
              <section class="front-editor-markdown">
                <div class="front-editor-toolbar-row">
                  <div class="front-editor-tabs">
                    <button type="button" :class="{ active: mode === 'write' }" @click="mode = 'write'">编写</button>
                    <button type="button" :class="{ active: mode === 'preview' }" @click="mode = 'preview'">预览</button>
                  </div>
                  <MarkdownToolbar :disabled="mode === 'preview' || uploading" @command="runToolbar" />
                  <button type="button" class="front-editor-small-btn" :disabled="uploading" @click="imageInput?.click()">插入图片</button>
                  <input ref="imageInput" type="file" accept="image/*" class="hidden" @change="uploadInlineImage" />
                </div>
                <textarea v-if="mode === 'write'" ref="textareaRef" v-model="content" spellcheck="false"></textarea>
                <div v-else class="front-editor-preview"><MarkdownRenderer :content="content" /></div>
              </section>
            </main>

            <aside class="front-editor-side">
              <section class="front-editor-group">
                <h3>{{ isMoment ? '内容类型' : '文章类型' }}</h3>
                <div v-if="!isMoment" class="front-editor-radio">
                  <button type="button" :class="{ active: currentSection === 'posts' }" @click="currentSection = 'posts'">正经</button>
                  <button type="button" :class="{ active: currentSection === 'chatters' }" @click="currentSection = 'chatters'">杂谈</button>
                </div>
                <p v-else class="front-editor-muted">说说</p>
              </section>
              <label class="front-editor-field"><span>日期</span><input v-model="dateInput" type="datetime-local" /></label>
              <label class="front-editor-field"><span>标签</span><input v-model="meta.tagsText" placeholder="Vue, Blog" /></label>
              <label class="front-editor-field"><span>简介</span><textarea v-model="meta.summary" rows="4"></textarea></label>
              <label v-if="isMoment" class="front-editor-field"><span>定位</span><input v-model="meta.location" /></label>
              <label v-if="isMoment" class="front-editor-field"><span>图片 URL（每行一个）</span><textarea v-model="meta.imagesText" rows="4"></textarea></label>
              <section class="front-editor-group">
                <h3>封面</h3>
                <div class="front-editor-cover-row">
                  <input v-model="meta.cover" placeholder="封面 URL" />
                  <button type="button" :disabled="uploading" @click="coverInput?.click()">上传</button>
                  <input ref="coverInput" type="file" accept="image/*" class="hidden" @change="uploadCover" />
                </div>
              </section>
              <details class="front-editor-advanced">
                <summary>高级设置</summary>
                <label class="front-editor-field"><span>Slug</span><input v-model="slug" /></label>
              </details>
            </aside>
          </div>

          <footer class="front-editor-footer">
            <label><input v-model="meta.draft" type="checkbox" /> 存为草稿</label>
            <p v-if="error" role="alert">{{ error }}</p>
            <div>
              <button type="button" class="front-editor-cancel" @click="close">取消</button>
              <button type="button" class="front-editor-save" :disabled="saving || uploading" @click="save">{{ saving ? '保存中...' : meta.draft ? '保存草稿' : '发布' }}</button>
            </div>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.front-editor-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9998;
  display: grid;
  place-items: center;
  padding: clamp(.75rem, 2vw, 1.5rem);
  background: rgba(0, 0, 0, .72);
}
.front-editor-shell {
  display: grid;
  width: min(1180px, 100%);
  max-height: min(88vh, 900px);
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .16);
  border-radius: 1.35rem;
  background: #191A1B;
  color: white;
  box-shadow: 0 28px 90px rgba(0, 0, 0, .62);
}
.front-editor-head,
.front-editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding: .85rem 1rem;
}
.front-editor-footer {
  border-top: 1px solid rgba(255, 255, 255, .1);
  border-bottom: 0;
}
.front-editor-head button,
.front-editor-cancel,
.front-editor-small-btn,
.front-editor-cover-row button {
  border-radius: 999px;
  background: white;
  padding: .55rem .75rem;
  color: black;
  font-weight: 900;
}
.front-editor-head button {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 999px;
  padding: 0;
}
.front-editor-head svg {
  width: 1rem;
  height: 1rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
.front-editor-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, .36fr);
  gap: 1.3rem;
  overflow: auto;
  padding: 1rem;
}
.front-editor-main,
.front-editor-side {
  min-width: 0;
}
.front-editor-side {
  display: grid;
  align-content: start;
  gap: .95rem;
}
.front-editor-field {
  display: grid;
  gap: .45rem;
}
.front-editor-field span,
.front-editor-group h3 {
  color: rgba(255, 255, 255, .78);
  font-size: .9rem;
  font-weight: 900;
}
.front-editor-field input,
.front-editor-field textarea,
.front-editor-cover-row input {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .13);
  border-radius: .9rem;
  background: #202123;
  padding: .75rem .85rem;
  color: white;
  outline: none;
}
.front-editor-title-input {
  font-size: clamp(1.25rem, 2.4vw, 2rem);
  font-weight: 900;
}
.front-editor-markdown {
  margin-top: 1rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 1.1rem;
}
.front-editor-toolbar-row {
  display: flex;
  align-items: center;
  gap: .55rem;
  flex-wrap: wrap;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding: .65rem;
}
.front-editor-tabs {
  display: inline-flex;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 999px;
}
.front-editor-tabs button,
.front-editor-radio button {
  padding: .55rem .75rem;
  color: rgba(255, 255, 255, .65);
  font-weight: 900;
}
.front-editor-tabs button.active,
.front-editor-radio button.active {
  background: black;
  color: white;
}
.front-editor-markdown textarea {
  display: block;
  width: 100%;
  min-height: min(52vh, 580px);
  resize: vertical;
  border: 0;
  background: transparent;
  padding: 1rem;
  color: rgba(255, 255, 255, .86);
  outline: none;
}
.front-editor-preview {
  min-height: min(52vh, 580px);
  padding: 1rem;
}
.front-editor-radio {
  display: inline-flex;
  overflow: hidden;
  margin-top: .5rem;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 999px;
}
.front-editor-cover-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: .5rem;
  margin-top: .5rem;
}
.front-editor-advanced {
  border-top: 1px solid rgba(255, 255, 255, .1);
  padding-top: .9rem;
}
.front-editor-advanced summary {
  cursor: pointer;
  font-weight: 900;
}
.front-editor-muted,
.front-editor-footer p {
  color: rgba(255, 255, 255, .52);
}
.front-editor-footer p {
  flex: 1 1 auto;
  color: #fecaca;
}
.front-editor-footer label {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  font-weight: 900;
}
.front-editor-footer > div {
  display: flex;
  gap: .65rem;
}
.front-editor-save {
  border-radius: 999px;
  background: #86efac;
  padding: .62rem 1.1rem;
  color: black;
  font-weight: 900;
}
.front-editor-state {
  padding: 2rem;
  color: rgba(255, 255, 255, .62);
}
.front-editor-pop-enter-active,
.front-editor-pop-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.front-editor-pop-enter-from,
.front-editor-pop-leave-to {
  opacity: 0;
  transform: scale(.985);
}
@media (max-width: 860px) {
  .front-editor-body {
    grid-template-columns: 1fr;
  }
}
</style>
