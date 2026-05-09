<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

export interface StructuredField {
  key: string
  label: string
  type?: 'text' | 'textarea' | 'tags' | 'number' | 'select' | 'upload' | 'gallery'
  placeholder?: string
  required?: boolean
  options?: string[]
  accept?: string
}

const props = defineProps<{
  title: string
  path: string
  itemName: string
  fields: StructuredField[]
  emptyItem: Record<string, unknown>
}>()

const ui = useUiStore()
const items = ref<Record<string, unknown>[]>([])
const form = ref<Record<string, unknown>>({})
const editIndex = ref<number | null>(null)
const modalOpen = ref(false)
const dirty = ref(false)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const advancedOpen = ref(false)
const jsonText = ref('[]')
const jsonError = ref('')
const uploadProgress = ref<Record<string, number>>({})
const dragPhotoIndex = ref<number | null>(null)
const query = ref('')

const isEditing = computed(() => editIndex.value !== null)
const filteredItems = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) => JSON.stringify(item).toLowerCase().includes(q))
})

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value))
}

function normalizeList(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') as Record<string, unknown>[] : []
}

function resetForm() {
  form.value = clone(props.emptyItem)
  editIndex.value = null
  dirty.value = false
  error.value = ''
  success.value = ''
}

function openCreate() {
  resetForm()
  modalOpen.value = true
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = normalizeList(await adminApi.json<unknown>(props.path))
    jsonText.value = JSON.stringify(items.value, null, 2)
    if (!Object.keys(form.value).length) resetForm()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '加载失败'
  } finally {
    loading.value = false
  }
}

function editItem(index: number) {
  const source = filteredItems.value[index]
  editIndex.value = items.value.indexOf(source)
  form.value = clone(source)
  normalizeGalleryFields()
  dirty.value = false
  modalOpen.value = true
  error.value = ''
  success.value = ''
}

function normalizeGalleryFields() {
  for (const field of props.fields) {
    if (field.type !== 'gallery') continue
    const current = galleryItems(field.key).slice(0, 50)
    const cover = String(form.value.cover || '')
    if (cover && !current.some((photo) => String(photo.url || '') === cover)) {
      current.unshift({ url: cover, title: '封面' })
    }
    form.value[field.key] = current.slice(0, 50)
    if (!form.value.cover && current[0]?.url) form.value.cover = current[0].url
  }
}

function closeForm() {
  if (dirty.value && !confirm('当前表单有未保存内容，确认关闭？')) return
  modalOpen.value = false
  resetForm()
}

function valueAsText(key: string) {
  const value = form.value[key]
  return Array.isArray(value) ? value.join(', ') : String(value ?? '')
}

function itemLabel(item: Record<string, unknown>, index: number) {
  return String(item.name || item.title || item.url || item.id || `${props.itemName} ${index + 1}`)
}

function itemCover(item: Record<string, unknown>) {
  const photos = Array.isArray(item.photos) ? item.photos as Record<string, unknown>[] : []
  return String(item.cover || item.avatar || photos[0]?.url || '')
}

function itemDescription(item: Record<string, unknown>) {
  return String(item.description || item.summary || item.artist || item.url || '')
}

function updateText(key: string, value: string) {
  form.value[key] = value
  dirty.value = true
}

function updateTags(key: string, value: string) {
  form.value[key] = value.split(',').map((item) => item.trim()).filter(Boolean)
  dirty.value = true
}

function updateNumber(key: string, value: string) {
  form.value[key] = value === '' ? '' : Number(value)
  dirty.value = true
}

function validateForm() {
  for (const field of props.fields) {
    if (!field.required) continue
    const value = form.value[field.key]
    if (Array.isArray(value) ? !value.length : !String(value ?? '').trim()) {
      error.value = `${field.label}不能为空`
      return false
    }
  }
  return true
}

async function persist(nextItems: Record<string, unknown>[], message: string) {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson(props.path, nextItems)
    items.value = normalizeList(await adminApi.json<unknown>(props.path))
    jsonText.value = JSON.stringify(items.value, null, 2)
    success.value = message
    ui.show(message)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
  } finally {
    saving.value = false
  }
}

async function saveForm() {
  if (!validateForm()) return
  const nextItems = clone(items.value)
  const payload = clone(form.value)
  if (isEditing.value && editIndex.value !== null) {
    nextItems[editIndex.value] = payload
  } else {
    nextItems.unshift(payload)
  }
  await persist(nextItems, isEditing.value ? '已保存修改' : '已新增记录')
  modalOpen.value = false
  resetForm()
}

async function removeItem(index: number) {
  const source = filteredItems.value[index]
  const realIndex = items.value.indexOf(source)
  const label = itemLabel(source, index)
  if (!confirm(`确认删除 ${label}？删除前后端会生成 JSON 备份。`)) return
  const nextItems = items.value.filter((_, itemIndex) => itemIndex !== realIndex)
  await persist(nextItems, '已删除记录')
  resetForm()
}

async function saveAdvancedJson() {
  jsonError.value = ''
  try {
    const parsed = JSON.parse(jsonText.value)
    if (!Array.isArray(parsed)) {
      jsonError.value = '高级 JSON 必须是数组'
      return
    }
    await persist(parsed, '高级 JSON 已保存')
    resetForm()
  } catch (exc) {
    jsonError.value = exc instanceof Error ? exc.message : 'JSON 格式错误'
  }
}

async function uploadForField(field: StructuredField, files: FileList | null) {
  if (!files?.length) return
  error.value = ''
  uploadProgress.value[field.key] = 0
  try {
    const data = await adminApi.upload(files[0], (percent) => {
      uploadProgress.value[field.key] = percent
    })
    form.value[field.key] = data.url
    dirty.value = true
    success.value = '上传成功，URL 已填入表单'
    ui.show('上传成功')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '上传失败'
  }
}

function galleryItems(key: string) {
  const value = form.value[key]
  return Array.isArray(value) ? value as Record<string, unknown>[] : []
}

function removeGalleryItem(key: string, index: number) {
  if (!confirm('确认删除这张照片？保存后前台相册会同步更新。')) return
  const removed = galleryItems(key)[index]
  const next = galleryItems(key).filter((_, itemIndex) => itemIndex !== index)
  form.value[key] = next
  if (form.value.cover === (removed?.url || '')) form.value.cover = next[0]?.url || ''
  dirty.value = true
}

function setGalleryCover(url: unknown) {
  form.value.cover = String(url || '')
  dirty.value = true
}

function moveGalleryItem(key: string, from: number, to: number) {
  const list = [...galleryItems(key)]
  if (from < 0 || to < 0 || from >= list.length || to >= list.length || from === to) return
  const [item] = list.splice(from, 1)
  list.splice(to, 0, item)
  form.value[key] = list
  if (!form.value.cover && list[0]?.url) form.value.cover = list[0].url
  dirty.value = true
}

function onGalleryDrop(key: string, index: number) {
  if (dragPhotoIndex.value === null) return
  moveGalleryItem(key, dragPhotoIndex.value, index)
  dragPhotoIndex.value = null
}

async function uploadGallery(field: StructuredField, files: FileList | null) {
  if (!files?.length) return
  const current = galleryItems(field.key)
  const selected = Array.from(files).slice(0, Math.max(0, 50 - current.length))
  if (!selected.length) {
    error.value = '每个相册最多 50 张照片'
    return
  }
  error.value = ''
  uploadProgress.value[field.key] = 0
  const next = [...current]
  try {
    for (let index = 0; index < selected.length; index += 1) {
      const data = await adminApi.upload(selected[index], (percent) => {
        uploadProgress.value[field.key] = Math.round(((index + percent / 100) / selected.length) * 100)
      })
      next.push({ url: data.url, title: selected[index].name })
    }
    form.value[field.key] = next
    if (!form.value.cover && next[0]?.url) form.value.cover = next[0].url
    dirty.value = true
    success.value = '照片已上传并加入相册'
    ui.show('照片已上传并加入相册')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '照片上传失败'
  } finally {
    uploadProgress.value[field.key] = 0
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <div class="admin-page-head">
      <div>
        <p class="eyebrow">content manager</p>
        <h1>{{ title }}</h1>
        <p>以表单方式管理{{ itemName }}数据；上传和保存继续走后端安全写入，列表支持快速检索。</p>
      </div>
      <div class="actions">
        <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
        <button class="admin-btn admin-btn-primary" type="button" @click="openCreate">新增{{ itemName }}</button>
      </div>
    </div>

    <div class="admin-card">
      <div class="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
        <input v-model="query" class="admin-input" :placeholder="`搜索${itemName}名称、简介、链接或标签`" />
        <div class="admin-meta">{{ filteredItems.length }} / {{ items.length }} 条</div>
      </div>
      <p v-if="error" class="mt-3 text-sm font-bold text-red-700">{{ error }}</p>
      <p v-if="success" class="mt-3 text-sm font-bold text-emerald-700">{{ success }}</p>
    </div>

    <div class="admin-table-card">
      <p v-if="loading" class="p-6 text-slate-500">加载中...</p>
      <p v-else-if="!filteredItems.length" class="p-6 text-slate-500">暂无{{ itemName }}记录。</p>
      <article v-else v-for="(item, index) in filteredItems" :key="`${index}-${item.url || item.name || item.title}`" class="admin-list-row">
        <div class="grid gap-4 lg:grid-cols-[8rem_minmax(0,1fr)_auto] lg:items-center">
          <div class="h-24 overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
            <img v-if="itemCover(item)" :src="itemCover(item)" alt="" class="h-full w-full object-cover" loading="lazy" />
            <div v-else class="grid h-full place-items-center text-xs font-bold text-slate-400">默认封面</div>
          </div>
          <div class="min-w-0">
            <h3 class="break-words text-lg font-black text-slate-950">{{ itemLabel(item, index) }}</h3>
            <p class="mt-1 break-all font-mono text-xs text-slate-500">{{ item.url || item.id || item.status || item.path || '未填写链接或 ID' }}</p>
            <p class="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">{{ itemDescription(item) || '未填写简介' }}</p>
            <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
              <span v-if="item.tags && Array.isArray(item.tags)">{{ item.tags.length }} 个标签</span>
              <span v-if="item.photos && Array.isArray(item.photos)">{{ item.photos.length }} 张照片</span>
              <span v-if="item.likes !== undefined">{{ item.likes }} 喜欢</span>
              <span v-if="item.date">{{ item.date }}</span>
            </div>
          </div>
          <div class="flex flex-wrap gap-2 lg:justify-end">
            <button class="admin-btn admin-btn-ghost text-sm" type="button" @click="editItem(index)">编辑</button>
            <button class="admin-btn admin-btn-danger text-sm" type="button" @click="removeItem(index)">删除</button>
          </div>
        </div>
      </article>
    </div>

    <Teleport to="body">
      <div v-if="modalOpen" class="fixed inset-0 z-[9990] flex items-center justify-center bg-black/45 p-4" @click.self="closeForm" @keydown.esc="closeForm">
        <div class="flex h-[85vh] max-h-[85vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <div class="flex shrink-0 items-center justify-between gap-4 border-b border-slate-200 p-5">
            <div>
              <p class="text-xs font-bold uppercase tracking-[.24em] text-slate-500">{{ isEditing ? 'edit' : 'create' }}</p>
              <h2 class="text-2xl font-black text-slate-950">{{ isEditing ? '编辑' : '新增' }}{{ itemName }}</h2>
            </div>
            <button class="admin-btn admin-btn-ghost" type="button" @click="closeForm">关闭</button>
          </div>

          <div class="min-h-0 flex-1 overflow-y-auto p-5">
            <div class="grid gap-4">
              <label v-for="field in fields" :key="field.key" class="field">
                <span>{{ field.label }}<b v-if="field.required" class="text-red-700"> *</b></span>
                <textarea
                  v-if="field.type === 'textarea'"
                  :value="valueAsText(field.key)"
                  rows="4"
                  class="admin-input resize-y"
                  :placeholder="field.placeholder"
                  @input="updateText(field.key, ($event.target as HTMLTextAreaElement).value)"
                ></textarea>
                <select
                  v-else-if="field.type === 'select'"
                  :value="valueAsText(field.key)"
                  class="admin-input"
                  @change="updateText(field.key, ($event.target as HTMLSelectElement).value)"
                >
                  <option v-for="option in field.options" :key="option" :value="option">{{ option }}</option>
                </select>
                <div v-else-if="field.type === 'upload'" class="grid gap-2">
                  <div class="flex flex-wrap gap-2">
                    <input
                      :value="valueAsText(field.key)"
                      class="admin-input min-w-0 flex-1"
                      :placeholder="field.placeholder"
                      @input="updateText(field.key, ($event.target as HTMLInputElement).value)"
                    />
                    <label class="admin-btn admin-btn-ghost cursor-pointer">
                      上传
                      <input type="file" :accept="field.accept || 'image/*,audio/*,video/*'" class="hidden" @change="uploadForField(field, ($event.target as HTMLInputElement).files)" />
                    </label>
                  </div>
                  <div v-if="uploadProgress[field.key]" class="h-2 rounded-full bg-slate-100">
                    <div class="h-full rounded-full bg-slate-950" :style="{ width: uploadProgress[field.key] + '%' }"></div>
                  </div>
                </div>
                <div v-else-if="field.type === 'gallery'" class="grid gap-3">
                  <div class="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <span class="text-xs font-bold text-slate-500">当前 {{ galleryItems(field.key).length }} / 50 张</span>
                    <label class="admin-btn admin-btn-ghost cursor-pointer">
                      批量上传
                      <input type="file" accept="image/*" multiple class="hidden" @change="uploadGallery(field, ($event.target as HTMLInputElement).files)" />
                    </label>
                  </div>
                  <div v-if="uploadProgress[field.key]" class="h-2 rounded-full bg-slate-100">
                    <div class="h-full rounded-full bg-slate-950" :style="{ width: uploadProgress[field.key] + '%' }"></div>
                  </div>
                  <div v-if="galleryItems(field.key).length" class="grid gap-3 sm:grid-cols-[repeat(auto-fill,minmax(180px,1fr))]">
                    <div
                      v-for="(photo, photoIndex) in galleryItems(field.key)"
                      :key="`${photoIndex}-${photo.url}`"
                      class="rounded-xl border border-slate-200 bg-slate-50 p-2"
                      draggable="true"
                      @dragstart="dragPhotoIndex = photoIndex"
                      @dragover.prevent
                      @drop="onGalleryDrop(field.key, photoIndex)"
                    >
                      <div class="relative overflow-hidden rounded-lg bg-slate-200">
                        <img v-if="photo.url" :src="String(photo.url)" alt="" class="h-[90px] w-full object-cover" loading="lazy" />
                        <div v-else class="grid h-[90px] place-items-center text-xs text-slate-400">无图片</div>
                        <span v-if="form.cover === photo.url || (!form.cover && photoIndex === 0)" class="absolute left-2 top-2 rounded-full bg-slate-950 px-2 py-1 text-[10px] font-bold text-white">封面</span>
                      </div>
                      <input
                        :value="String(photo.url || '')"
                        class="admin-input mt-2 px-3 py-2 text-xs"
                        @input="photo.url = ($event.target as HTMLInputElement).value; dirty = true"
                      />
                      <div class="mt-2 flex flex-wrap gap-2">
                        <button type="button" class="admin-btn admin-btn-ghost px-3 py-1.5 text-xs" @click="moveGalleryItem(field.key, photoIndex, photoIndex - 1)">上移</button>
                        <button type="button" class="admin-btn admin-btn-ghost px-3 py-1.5 text-xs" @click="moveGalleryItem(field.key, photoIndex, photoIndex + 1)">下移</button>
                        <button type="button" class="admin-btn admin-btn-primary px-3 py-1.5 text-xs" @click="setGalleryCover(photo.url)">设为封面</button>
                        <button type="button" class="admin-btn admin-btn-danger px-3 py-1.5 text-xs" @click="removeGalleryItem(field.key, photoIndex)">删除</button>
                      </div>
                    </div>
                  </div>
                </div>
                <input
                  v-else
                  :value="valueAsText(field.key)"
                  :type="field.type === 'number' ? 'number' : 'text'"
                  class="admin-input"
                  :placeholder="field.placeholder"
                  @input="field.type === 'tags' ? updateTags(field.key, ($event.target as HTMLInputElement).value) : field.type === 'number' ? updateNumber(field.key, ($event.target as HTMLInputElement).value) : updateText(field.key, ($event.target as HTMLInputElement).value)"
                />
              </label>
            </div>
          </div>

          <div class="flex shrink-0 flex-wrap gap-2 border-t border-slate-200 p-5">
            <button :disabled="saving" class="admin-btn admin-btn-primary" type="button" @click="saveForm">{{ saving ? '保存中...' : '保存' }}</button>
            <button class="admin-btn admin-btn-ghost" type="button" @click="resetForm">清空</button>
            <button class="admin-btn admin-btn-ghost" type="button" @click="closeForm">取消</button>
          </div>
        </div>
      </div>
    </Teleport>

    <div class="admin-card">
      <button class="flex w-full items-center justify-between text-left" type="button" @click="advancedOpen = !advancedOpen">
        <span class="font-black text-slate-950">高级 JSON 编辑</span>
        <span class="text-sm font-bold text-slate-500">{{ advancedOpen ? '收起' : '展开' }}</span>
      </button>
      <div v-if="advancedOpen" class="mt-4 grid gap-3">
        <p class="text-sm leading-6 text-amber-700">仅用于批量修复或迁移。JSON 格式错误会阻止保存；保存仍会通过后端安全写入并生成备份。</p>
        <textarea v-model="jsonText" rows="18" class="admin-input font-mono text-sm"></textarea>
        <p v-if="jsonError" class="text-sm font-bold text-red-700">{{ jsonError }}</p>
        <button :disabled="saving" class="admin-btn admin-btn-ghost w-fit" type="button" @click="saveAdvancedJson">保存高级 JSON</button>
      </div>
    </div>
  </section>
</template>
