<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

export interface StructuredField {
  key: string
  label: string
  type?: 'text' | 'textarea' | 'tags' | 'number' | 'select' | 'upload'
  placeholder?: string
  required?: boolean
  options?: string[]
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
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const advancedOpen = ref(false)
const jsonText = ref('[]')
const jsonError = ref('')
const uploadProgress = ref<Record<string, number>>({})

const isEditing = computed(() => editIndex.value !== null)

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value))
}

function normalizeList(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') as Record<string, unknown>[] : []
}

function resetForm() {
  form.value = clone(props.emptyItem)
  editIndex.value = null
  error.value = ''
  success.value = ''
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
  editIndex.value = index
  form.value = clone(items.value[index])
  error.value = ''
  success.value = ''
}

function valueAsText(key: string) {
  const value = form.value[key]
  return Array.isArray(value) ? value.join(', ') : String(value ?? '')
}

function updateText(key: string, value: string) {
  form.value[key] = value
}

function updateTags(key: string, value: string) {
  form.value[key] = value.split(',').map((item) => item.trim()).filter(Boolean)
}

function updateNumber(key: string, value: string) {
  form.value[key] = value === '' ? '' : Number(value)
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
  resetForm()
}

async function removeItem(index: number) {
  const item = items.value[index]
  const label = String(item.name || item.title || item.url || props.itemName)
  if (!confirm(`确认删除 ${label}？删除前后端会生成 JSON 备份。`)) return
  const nextItems = items.value.filter((_, itemIndex) => itemIndex !== index)
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
    success.value = '上传成功，URL 已填入表单'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '上传失败'
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-4xl font-black text-white">{{ title }}</h1>
          <p class="mt-2 text-sm text-white/52">主流程为表单化管理；高级 JSON 编辑仅作为兜底。</p>
        </div>
        <button class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">刷新</button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-200/85">{{ error }}</p>
      <p v-if="success" class="mt-3 text-sm text-emerald-200/85">{{ success }}</p>
    </GlassCard>

    <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.72fr)]">
      <GlassCard>
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-xl font-black text-white">{{ itemName }}列表</h2>
          <button class="rounded-2xl bg-cyan-300 px-4 py-2 text-sm font-bold text-slate-950" @click="resetForm">新增{{ itemName }}</button>
        </div>
        <p v-if="loading" class="mt-5 text-white/55">加载中...</p>
        <p v-else-if="!items.length" class="mt-5 rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-white/55">暂无{{ itemName }}记录。</p>
        <div v-else class="mt-5 grid gap-3">
          <div v-for="(item, index) in items" :key="`${index}-${item.url || item.name || item.title}`" class="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div class="min-w-0">
                <b class="block break-words text-white">{{ item.name || item.title || item.url || `${itemName} ${index + 1}` }}</b>
                <p class="mt-1 break-all text-xs text-white/45">{{ item.url || item.id || item.status || '未填写链接或 ID' }}</p>
                <p v-if="item.description" class="mt-2 line-clamp-2 text-sm leading-6 text-white/55">{{ item.description }}</p>
              </div>
              <div class="flex shrink-0 flex-wrap gap-2">
                <button class="rounded-xl bg-white/10 px-3 py-2 text-sm text-white/78" @click="editItem(index)">编辑</button>
                <button class="rounded-xl bg-red-500/18 px-3 py-2 text-sm text-red-100" @click="removeItem(index)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      <GlassCard>
        <h2 class="text-xl font-black text-white">{{ isEditing ? '编辑' : '新增' }}{{ itemName }}</h2>
        <div class="mt-5 grid gap-3">
          <label v-for="field in fields" :key="field.key" class="grid gap-2 text-sm text-white/68">
            <span>{{ field.label }}<b v-if="field.required" class="text-red-200"> *</b></span>
            <textarea
              v-if="field.type === 'textarea'"
              :value="valueAsText(field.key)"
              rows="4"
              class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-white outline-none focus:border-cyan-300/55"
              :placeholder="field.placeholder"
              @input="updateText(field.key, ($event.target as HTMLTextAreaElement).value)"
            ></textarea>
            <select
              v-else-if="field.type === 'select'"
              :value="valueAsText(field.key)"
              class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-white outline-none focus:border-cyan-300/55"
              @change="updateText(field.key, ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in field.options" :key="option" :value="option">{{ option }}</option>
            </select>
            <div v-else-if="field.type === 'upload'" class="grid gap-2">
              <div class="flex gap-2">
                <input
                  :value="valueAsText(field.key)"
                  class="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-white outline-none focus:border-cyan-300/55"
                  :placeholder="field.placeholder"
                  @input="updateText(field.key, ($event.target as HTMLInputElement).value)"
                />
                <label class="cursor-pointer rounded-2xl border border-cyan-200/25 px-4 py-3 text-cyan-100">
                  上传
                  <input type="file" accept="image/*" class="hidden" @change="uploadForField(field, ($event.target as HTMLInputElement).files)" />
                </label>
              </div>
              <div v-if="uploadProgress[field.key]" class="h-2 rounded-full bg-white/10">
                <div class="h-full rounded-full bg-cyan-300" :style="{ width: uploadProgress[field.key] + '%' }"></div>
              </div>
            </div>
            <input
              v-else
              :value="valueAsText(field.key)"
              :type="field.type === 'number' ? 'number' : 'text'"
              class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-white outline-none focus:border-cyan-300/55"
              :placeholder="field.placeholder"
              @input="field.type === 'tags' ? updateTags(field.key, ($event.target as HTMLInputElement).value) : field.type === 'number' ? updateNumber(field.key, ($event.target as HTMLInputElement).value) : updateText(field.key, ($event.target as HTMLInputElement).value)"
            />
          </label>
        </div>
        <div class="mt-5 flex flex-wrap gap-2">
          <button :disabled="saving" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50" @click="saveForm">{{ saving ? '保存中...' : '保存' }}</button>
          <button class="rounded-2xl border border-white/10 px-5 py-3 text-white/70" @click="resetForm">清空</button>
        </div>
      </GlassCard>
    </div>

    <GlassCard>
      <button class="flex w-full items-center justify-between text-left" @click="advancedOpen = !advancedOpen">
        <span class="font-bold text-white">高级 JSON 编辑</span>
        <span class="text-sm text-white/45">{{ advancedOpen ? '收起' : '展开' }}</span>
      </button>
      <div v-if="advancedOpen" class="mt-4 grid gap-3">
        <p class="text-sm leading-6 text-amber-100/70">仅用于批量修复或迁移。JSON 格式错误会阻止保存；保存仍会通过后端安全写入并生成备份。</p>
        <textarea v-model="jsonText" rows="18" class="rounded-[24px] border border-white/10 bg-black/20 p-4 font-mono text-sm text-white outline-none focus:border-cyan-300/55"></textarea>
        <p v-if="jsonError" class="text-sm text-red-200/85">{{ jsonError }}</p>
        <button :disabled="saving" class="w-fit rounded-2xl border border-amber-200/25 px-5 py-3 text-amber-100 disabled:opacity-50" @click="saveAdvancedJson">保存高级 JSON</button>
      </div>
    </GlassCard>
  </section>
</template>
