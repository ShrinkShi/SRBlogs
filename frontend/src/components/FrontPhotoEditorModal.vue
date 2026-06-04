<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { contentApi } from '@/api/content'
import { useUiStore } from '@/stores/ui'
import { normalizeTagColor, tagStyle, type TagColorMap } from '@/utils/tagStyles'
import type { PhotoAlbum } from '@/types'

const props = withDefaults(defineProps<{ modelValue: boolean; album?: PhotoAlbum | null; index?: number }>(), {
  album: null,
  index: -1
})
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; saved: [] }>()
const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const form = reactive({
  title: '',
  description: '',
  date: '',
  tagsText: '',
  tagColors: {} as TagColorMap
})
const editableTags = computed(() => form.tagsText.split(',').map((tag) => tag.trim()).filter(Boolean))
const modalTitle = computed(() => props.index >= 0 ? '编辑照片组' : '新增照片')

function today() {
  return new Date().toISOString().slice(0, 10)
}

function reset() {
  form.title = props.album?.title || ''
  form.description = props.album?.description || ''
  form.date = props.album?.date || today()
  form.tagsText = (props.album?.tags || []).join(', ')
  form.tagColors = { ...(props.album?.tagColors || {}) }
  error.value = ''
}

function normalizeList(value: unknown): PhotoAlbum[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') as PhotoAlbum[] : []
}

function close() {
  emit('update:modelValue', false)
}

function setTagColor(tag: string, color: string) {
  form.tagColors = { ...form.tagColors, [tag]: normalizeTagColor(color, '#334155') }
}

async function save() {
  error.value = ''
  if (!form.title.trim()) {
    error.value = '相册标题不能为空。'
    return
  }
  saving.value = true
  try {
    const list = normalizeList(await contentApi.json<unknown>('/photos'))
    const previous = props.album?.photos || []
    const payload: PhotoAlbum = {
      title: form.title.trim(),
      description: form.description.trim(),
      cover: previous[0]?.url || '',
      date: form.date || today(),
      tags: editableTags.value,
      tagColors: editableTags.value.reduce((colors, tag) => {
        colors[tag] = normalizeTagColor(form.tagColors[tag], '#334155')
        return colors
      }, {} as TagColorMap),
      photos: previous
    }
    const next = [...list]
    if (props.index >= 0 && props.index < next.length) next[props.index] = payload
    else next.unshift(payload)
    await contentApi.adminPutJson('/photos', next)
    ui.showToast(props.index >= 0 ? '照片组已保存' : '照片组已新增', 'success')
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
            <strong>{{ modalTitle }}</strong>
            <button type="button" aria-label="关闭新增照片弹窗" @click="close">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
            </button>
          </header>
          <div class="front-photo-body">
            <label><span>相册标题</span><input v-model="form.title" /></label>
            <label><span>相册描述</span><textarea v-model="form.description" rows="4"></textarea></label>
            <label><span>日期</span><input v-model="form.date" type="date" /></label>
            <label><span>标签</span><input v-model="form.tagsText" placeholder="生活, 截图, 旅行" /></label>
            <div v-if="editableTags.length" class="front-photo-tag-colors" aria-label="标签颜色">
              <label v-for="tag in editableTags" :key="tag">
                <span :style="tagStyle(tag, form.tagColors)"># {{ tag }}</span>
                <input
                  type="color"
                  :value="normalizeTagColor(form.tagColors[tag], '#334155')"
                  :aria-label="`${tag} 标签颜色`"
                  @input="setTagColor(tag, ($event.target as HTMLInputElement).value)"
                />
              </label>
            </div>
            <p v-if="error" class="front-photo-error" role="alert">{{ error }}</p>
          </div>
          <footer class="front-photo-footer">
            <button type="button" class="front-photo-cancel" @click="close">取消</button>
            <button type="button" class="front-photo-save" :disabled="loading || saving" @click="save">{{ saving ? '保存中...' : '保存照片' }}</button>
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
  font-size: .75rem;
}
.front-photo-head,
.front-photo-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .6rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding: .64rem .75rem;
}
.front-photo-footer {
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, .1);
  border-bottom: 0;
}
.front-photo-head button,
.front-photo-cancel {
  border-radius: 999px;
  background: white;
  padding: .42rem .58rem;
  color: black;
  font-weight: 900;
}
.front-photo-head button {
  display: grid;
  width: 1.7rem;
  height: 1.7rem;
  place-items: center;
  border-radius: 999px;
  padding: 0;
}
.front-photo-head svg {
  width: .75rem;
  height: .75rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
.front-photo-body {
  display: grid;
  gap: .6rem;
  overflow-y: auto;
  padding: .75rem;
}
.front-photo-body label {
  display: grid;
  gap: .32rem;
}
.front-photo-body label span {
  color: rgba(255, 255, 255, .72);
  font-weight: 900;
}
.front-photo-body input,
.front-photo-body textarea {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .13);
  border-radius: .68rem;
  background: #202123;
  padding: .54rem .62rem;
  color: white;
  outline: none;
}
.front-photo-tag-colors {
  display: flex;
  flex-wrap: wrap;
  gap: .45rem;
}
.front-photo-tag-colors label {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
}
.front-photo-tag-colors span {
  border: 1px solid;
  border-radius: 999px;
  padding: .25rem .5rem;
  font-size: .68rem;
  font-weight: 900;
}
.front-photo-tag-colors input {
  width: 1.55rem;
  height: 1.55rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  padding: 0;
}
.front-photo-save {
  border-radius: 999px;
  background: #86efac;
  padding: .47rem .85rem;
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
