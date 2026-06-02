<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { contentApi } from '@/api/content'
import { useUiStore } from '@/stores/ui'
import type { PhotoAlbum } from '@/types'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; saved: [] }>()
const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const error = ref('')
const imageInput = ref<HTMLInputElement | null>(null)
const form = reactive({
  title: '',
  description: '',
  date: '',
  tagsText: '',
  cover: '',
  photosText: ''
})

function today() {
  return new Date().toISOString().slice(0, 10)
}

function reset() {
  form.title = ''
  form.description = ''
  form.date = today()
  form.tagsText = ''
  form.cover = ''
  form.photosText = ''
  error.value = ''
}

function normalizeList(value: unknown): PhotoAlbum[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') as PhotoAlbum[] : []
}

function close() {
  emit('update:modelValue', false)
}

async function uploadImages(event: Event) {
  const files = Array.from((event.target as HTMLInputElement).files || [])
  ;(event.target as HTMLInputElement).value = ''
  if (!files.length) return
  uploading.value = true
  try {
    const uploaded = []
    for (const file of files.slice(0, 50)) {
      const data = await contentApi.upload(file)
      uploaded.push(data.url)
    }
    const current = form.photosText.split(/\r?\n/).map((url) => url.trim()).filter(Boolean)
    const next = [...current, ...uploaded]
    form.photosText = next.join('\n')
    if (!form.cover && uploaded[0]) form.cover = uploaded[0]
    ui.showToast('图片已上传', 'success')
  } catch {
    ui.showToast('图片上传失败', 'error')
  } finally {
    uploading.value = false
  }
}

async function save() {
  error.value = ''
  if (!form.title.trim()) {
    error.value = '相册标题不能为空。'
    return
  }
  const urls = form.photosText.split(/\r?\n/).map((url) => url.trim()).filter(Boolean).slice(0, 50)
  if (!urls.length && !form.cover.trim()) {
    error.value = '请至少上传或填写一张图片。'
    return
  }
  saving.value = true
  try {
    const list = normalizeList(await contentApi.json<unknown>('/photos'))
    const photos = urls.map((url, index) => ({ url, title: `${form.title.trim()} ${index + 1}` }))
    const payload: PhotoAlbum = {
      title: form.title.trim(),
      description: form.description.trim(),
      cover: form.cover.trim() || photos[0]?.url || '',
      date: form.date || today(),
      tags: form.tagsText.split(',').map((tag) => tag.trim()).filter(Boolean),
      photos
    }
    await contentApi.adminPutJson('/photos', [payload, ...list])
    ui.showToast('照片已新增', 'success')
    emit('saved')
    close()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '保存失败'
  } finally {
    saving.value = false
  }
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
})
</script>

<template>
  <Teleport to="body">
    <Transition name="front-photo-pop">
      <div v-if="modelValue" class="front-photo-backdrop" role="dialog" aria-modal="true" @click.self="close" @keydown.esc.window="close">
        <section class="front-photo-shell">
          <header class="front-photo-head">
            <strong>新增照片</strong>
            <button type="button" aria-label="关闭新增照片弹窗" @click="close">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
            </button>
          </header>
          <div class="front-photo-body">
            <label><span>相册标题</span><input v-model="form.title" /></label>
            <label><span>相册描述</span><textarea v-model="form.description" rows="4"></textarea></label>
            <label><span>日期</span><input v-model="form.date" type="date" /></label>
            <label><span>标签</span><input v-model="form.tagsText" placeholder="生活, 截图, 旅行" /></label>
            <label><span>封面 URL</span><input v-model="form.cover" placeholder="留空则使用第一张图片" /></label>
            <label><span>图片 URL（每行一个）</span><textarea v-model="form.photosText" rows="7"></textarea></label>
            <div class="front-photo-upload">
              <button type="button" :disabled="uploading" @click="imageInput?.click()">{{ uploading ? '上传中...' : '上传图片' }}</button>
              <input ref="imageInput" type="file" accept="image/*" multiple class="hidden" @change="uploadImages" />
            </div>
            <p v-if="error" class="front-photo-error" role="alert">{{ error }}</p>
          </div>
          <footer class="front-photo-footer">
            <button type="button" class="front-photo-cancel" @click="close">取消</button>
            <button type="button" class="front-photo-save" :disabled="loading || saving || uploading" @click="save">{{ saving ? '保存中...' : '保存照片' }}</button>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.front-photo-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9998;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, .72);
}
.front-photo-shell {
  display: grid;
  width: min(720px, 100%);
  max-height: 88vh;
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .16);
  border-radius: 1.35rem;
  background: #191A1B;
  color: white;
}
.front-photo-head,
.front-photo-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .8rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding: .85rem 1rem;
}
.front-photo-footer {
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, .1);
  border-bottom: 0;
}
.front-photo-head button,
.front-photo-cancel,
.front-photo-upload button {
  border-radius: 999px;
  background: white;
  padding: .55rem .75rem;
  color: black;
  font-weight: 900;
}
.front-photo-head button {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 999px;
  padding: 0;
}
.front-photo-head svg {
  width: 1rem;
  height: 1rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
.front-photo-body {
  display: grid;
  gap: .8rem;
  overflow-y: auto;
  padding: 1rem;
}
.front-photo-body label {
  display: grid;
  gap: .42rem;
}
.front-photo-body label span {
  color: rgba(255, 255, 255, .72);
  font-weight: 900;
}
.front-photo-body input,
.front-photo-body textarea {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .13);
  border-radius: .9rem;
  background: #202123;
  padding: .72rem .82rem;
  color: white;
  outline: none;
}
.front-photo-upload {
  display: flex;
  justify-content: flex-end;
}
.front-photo-save {
  border-radius: 999px;
  background: #86efac;
  padding: .62rem 1.1rem;
  color: black;
  font-weight: 900;
}
.front-photo-error {
  color: #fecaca;
}
.front-photo-pop-enter-active,
.front-photo-pop-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.front-photo-pop-enter-from,
.front-photo-pop-leave-to {
  opacity: 0;
  transform: scale(.985);
}
</style>
