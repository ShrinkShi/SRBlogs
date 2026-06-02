<script setup lang="ts">
import { reactive, watch } from 'vue'
import { contentApi } from '@/api/content'
import { useUiStore } from '@/stores/ui'
import type { FriendItem, MusicItem, ProjectItem } from '@/types'

type JsonKind = 'project' | 'friend' | 'music'
type EditableItem = ProjectItem | FriendItem | MusicItem

const props = withDefaults(defineProps<{
  modelValue: boolean
  kind: JsonKind
  item?: EditableItem | null
  index?: number
}>(), {
  item: null,
  index: -1
})
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; saved: [] }>()
const ui = useUiStore()

const saving = reactive({ value: false })
const error = reactive({ value: '' })
const form = reactive({
  name: '',
  title: '',
  artist: '',
  description: '',
  url: '',
  repo: '',
  cover: '',
  avatar: '',
  status: '',
  tagsText: '',
  id: '',
  sort: 0,
  lyrics: '',
  lyricUrl: ''
})

const config = {
  project: { title: '项目', path: '/projects' },
  friend: { title: '友链', path: '/friends' },
  music: { title: '歌曲', path: '/music' }
} as const

function close() {
  emit('update:modelValue', false)
}

function reset() {
  const item = props.item as any
  form.name = String(item?.name || '')
  form.title = String(item?.title || '')
  form.artist = String(item?.artist || '')
  form.description = String(item?.description || '')
  form.url = String(item?.url || '')
  form.repo = String(item?.repo || '')
  form.cover = String(item?.cover || '')
  form.avatar = String(item?.avatar || '')
  form.status = String(item?.status || '')
  form.tagsText = Array.isArray(item?.tags) ? item.tags.join(', ') : ''
  form.id = String(item?.id || '')
  form.sort = Number(item?.sort || 0)
  form.lyrics = String(item?.lyrics || '')
  form.lyricUrl = String(item?.lyricUrl || '')
  error.value = ''
}

function normalizeList(value: unknown): any[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') : []
}

function buildItem() {
  if (props.kind === 'project') {
    return {
      name: form.name.trim(),
      description: form.description.trim(),
      url: form.url.trim(),
      repo: form.repo.trim(),
      cover: form.cover.trim(),
      status: form.status.trim(),
      tags: form.tagsText.split(',').map((tag) => tag.trim()).filter(Boolean)
    } satisfies ProjectItem
  }
  if (props.kind === 'friend') {
    return {
      name: form.name.trim(),
      url: form.url.trim(),
      avatar: form.avatar.trim(),
      description: form.description.trim(),
      tags: form.tagsText.split(',').map((tag) => tag.trim()).filter(Boolean)
    } satisfies FriendItem
  }
  return {
    title: form.title.trim(),
    artist: form.artist.trim(),
    url: form.url.trim(),
    cover: form.cover.trim(),
    id: form.id.trim(),
    sort: Number(form.sort || 0),
    lyricUrl: form.lyricUrl.trim(),
    lyrics: form.lyrics,
    likes: Number((props.item as MusicItem | null)?.likes || 0)
  } satisfies MusicItem
}

function validate() {
  error.value = ''
  if (props.kind === 'project' && !form.name.trim()) error.value = '项目名称不能为空。'
  if (props.kind === 'friend' && !form.name.trim()) error.value = '友链名称不能为空。'
  if (props.kind === 'friend' && !form.url.trim()) error.value = '友链地址不能为空。'
  if (props.kind === 'music' && !form.title.trim()) error.value = '歌曲名称不能为空。'
  if (props.kind === 'music' && !form.artist.trim()) error.value = '歌手不能为空。'
  return !error.value
}

async function save() {
  if (!validate()) return
  saving.value = true
  try {
    const path = config[props.kind].path
    const list = normalizeList(await contentApi.json<unknown>(path))
    const nextItem = buildItem()
    const next = [...list]
    if (props.index >= 0 && props.index < next.length) next[props.index] = nextItem
    else next.unshift(nextItem)
    await contentApi.adminPutJson(path, next)
    ui.showToast(props.index >= 0 ? '已保存' : '已新增', 'success')
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
    <Transition name="front-json-pop">
      <div v-if="modelValue" class="front-json-backdrop" role="dialog" aria-modal="true" @click.self="close" @keydown.esc.window="close">
        <section class="front-json-shell">
          <header class="front-json-head">
            <strong>{{ index >= 0 ? '编辑' : '新增' }}{{ config[kind].title }}</strong>
            <button type="button" aria-label="关闭弹窗" @click="close">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
            </button>
          </header>

          <div class="front-json-body">
            <template v-if="kind === 'project'">
              <label><span>项目名称</span><input v-model="form.name" /></label>
              <label><span>描述</span><textarea v-model="form.description" rows="4"></textarea></label>
              <label><span>项目链接</span><input v-model="form.url" /></label>
              <label><span>代码仓库</span><input v-model="form.repo" /></label>
              <label><span>封面 URL</span><input v-model="form.cover" /></label>
              <label><span>状态</span><input v-model="form.status" placeholder="开发中 / 已上线" /></label>
              <label><span>标签</span><input v-model="form.tagsText" placeholder="Vue, FastAPI" /></label>
            </template>

            <template v-else-if="kind === 'friend'">
              <label><span>名称</span><input v-model="form.name" /></label>
              <label><span>链接</span><input v-model="form.url" /></label>
              <label><span>头像 URL</span><input v-model="form.avatar" /></label>
              <label><span>描述</span><textarea v-model="form.description" rows="4"></textarea></label>
              <label><span>标签</span><input v-model="form.tagsText" placeholder="博客, 朋友" /></label>
            </template>

            <template v-else>
              <label><span>歌曲名称</span><input v-model="form.title" /></label>
              <label><span>歌手</span><input v-model="form.artist" /></label>
              <label><span>音频 URL</span><input v-model="form.url" /></label>
              <label><span>封面 URL</span><input v-model="form.cover" /></label>
              <label><span>歌曲 ID</span><input v-model="form.id" /></label>
              <label><span>排序</span><input v-model.number="form.sort" type="number" /></label>
              <label><span>歌词 URL</span><input v-model="form.lyricUrl" /></label>
              <label><span>内联歌词</span><textarea v-model="form.lyrics" rows="6"></textarea></label>
            </template>
            <p v-if="error.value" class="front-json-error" role="alert">{{ error.value }}</p>
          </div>

          <footer class="front-json-footer">
            <button type="button" class="front-json-cancel" @click="close">取消</button>
            <button type="button" class="front-json-save" :disabled="saving.value" @click="save">{{ saving.value ? '保存中' : '保存' }}</button>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.front-json-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9998;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, .72);
}
.front-json-shell {
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
.front-json-head,
.front-json-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .8rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding: .85rem 1rem;
}
.front-json-footer {
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, .1);
  border-bottom: 0;
}
.front-json-head button,
.front-json-cancel {
  border-radius: 999px;
  background: white;
  padding: .55rem .75rem;
  color: black;
  font-weight: 900;
}
.front-json-head button {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  padding: 0;
}
.front-json-head svg {
  width: 1rem;
  height: 1rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}
.front-json-body {
  display: grid;
  gap: .8rem;
  overflow-y: auto;
  padding: 1rem;
}
.front-json-body label {
  display: grid;
  gap: .42rem;
}
.front-json-body label span {
  color: rgba(255, 255, 255, .72);
  font-weight: 900;
}
.front-json-body input,
.front-json-body textarea {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .13);
  border-radius: .9rem;
  background: #202123;
  padding: .72rem .82rem;
  color: white;
  outline: none;
}
.front-json-save {
  border-radius: 999px;
  background: #86efac;
  padding: .62rem 1.1rem;
  color: black;
  font-weight: 900;
}
.front-json-error {
  color: #fecaca;
}
.front-json-pop-enter-active,
.front-json-pop-leave-active {
  transition: opacity .18s ease, transform .18s ease;
}
.front-json-pop-enter-from,
.front-json-pop-leave-to {
  opacity: 0;
  transform: scale(.985);
}
</style>
