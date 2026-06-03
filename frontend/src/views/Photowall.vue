<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import CommentBox from '@/components/CommentBox.vue'
import FrontPhotoEditorModal from '@/components/FrontPhotoEditorModal.vue'
import { contentApi } from '@/api/content'
import type { PageConfig, PhotoAlbum, PhotoItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { detectImageTone, type ImageTone } from '@/utils/imageTone'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'
import { tagStyle } from '@/utils/tagStyles'

type AlbumView = PhotoAlbum & { slug: string; sourceIndex: number }

const rawPhotos = ref<Array<PhotoItem | PhotoAlbum>>([])
const session = useSessionStore()
const ui = useUiStore()
const activeAlbum = ref<AlbumView | null>(null)
const active = ref<PhotoItem | null>(null)
const activeIndex = computed(() => {
  if (!activeAlbum.value || !active.value) return -1
  return activeAlbum.value.photos.findIndex((photo) => photo.url === active.value?.url)
})
const viewMode = ref<'grid' | 'link'>('grid')
const searchQ = ref('')
const loading = ref(false)
const error = ref('')
const albumPhotoInput = ref<HTMLInputElement | null>(null)
const uploadingAlbumPhoto = ref(false)
const dragReadyIndex = ref<number | null>(null)
const draggingPhotoIndex = ref<number | null>(null)
let photoLongPressTimer: number | undefined
const createOpen = ref(false)
const editOpen = ref(false)
const editingAlbum = ref<AlbumView | null>(null)
const pageConfig = ref<PageConfig | null>(null)
const toneMap = reactive<Record<string, ImageTone>>({})
const title = computed(() => pageConfig.value?.pageText?.photos?.title || '相册')
const subtitle = computed(() => pageConfig.value?.pageText?.photos?.subtitle || '相册记录从后端 JSON 动态读取，点击封面可查看组内照片。')
useSeo({ title: () => title.value, description: () => subtitle.value, path: '/photowall' })

function slugify(value: string, fallback: string) {
  const slug = value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug || fallback
}

function normalizeAlbum(item: PhotoItem | PhotoAlbum, index: number): AlbumView {
  if ('photos' in item && Array.isArray(item.photos)) {
    const photos = item.photos.slice(0, 50)
    return {
      ...item,
      title: item.title || `相册 ${index + 1}`,
      slug: slugify(item.title || item.cover || `album-${index + 1}`, `album-${index + 1}`),
      sourceIndex: index,
      cover: item.cover || photos[0]?.url || '',
      tagColors: item.tagColors || {},
      photos
    }
  }
  const photo = item as PhotoItem
  return {
    title: photo.title || `相册 ${index + 1}`,
    slug: slugify(photo.title || photo.url || `album-${index + 1}`, `album-${index + 1}`),
    sourceIndex: index,
    description: photo.description,
    cover: photo.url,
    date: photo.date,
    tags: photo.tags,
    tagColors: {},
    photos: [photo]
  }
}

const albums = computed(() => rawPhotos.value.map(normalizeAlbum).filter((album) => album.photos.length || album.cover || session.isAdmin))
const filteredAlbums = computed(() => {
  const q = searchQ.value.trim().toLowerCase()
  if (!q) return albums.value
  return albums.value.filter((album) => [
    album.title,
    album.description,
    album.date,
    ...(album.tags || []),
    ...album.photos.flatMap((photo) => [photo.title, photo.description, photo.date, ...(photo.tags || [])])
  ].filter(Boolean).join(' ').toLowerCase().includes(q))
})

watch(albums, (list) => {
  list.forEach(async (album) => {
    toneMap[album.slug] = await detectImageTone(album.cover || album.photos[0]?.url, 'dark')
  })
}, { immediate: true })

async function load() {
  loading.value = true
  error.value = ''
  try {
    rawPhotos.value = await contentApi.json<Array<PhotoItem | PhotoAlbum>>('/photos')
    pageConfig.value = await contentApi.json<PageConfig>('/pages/config')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '相册加载失败'
  } finally {
    loading.value = false
  }
}

function openAlbumEditor(album: AlbumView) {
  editingAlbum.value = album
  editOpen.value = true
}

async function afterAlbumSaved() {
  activeAlbum.value = null
  active.value = null
  await load()
}

function toAlbumPayload(album: AlbumView): PhotoAlbum {
  return {
    title: album.title,
    description: album.description,
    cover: album.cover,
    date: album.date,
    tags: album.tags || [],
    tagColors: album.tagColors || {},
    photos: album.photos.map((photo) => ({ ...photo }))
  }
}

function refreshActiveAlbum(sourceIndex: number, preferredUrl = '') {
  const source = rawPhotos.value[sourceIndex]
  if (!source) {
    activeAlbum.value = null
    active.value = null
    return
  }
  const refreshed = normalizeAlbum(source, sourceIndex)
  activeAlbum.value = refreshed
  active.value = refreshed.photos.find((photo) => photo.url === preferredUrl) || refreshed.photos[0] || null
}

async function persistAlbumPhotos(album: AlbumView, photos: PhotoItem[], preferredUrl = '') {
  if (album.sourceIndex < 0 || album.sourceIndex >= rawPhotos.value.length) return
  const payload = toAlbumPayload(album)
  payload.photos = photos.map((photo) => ({ ...photo }))
  if (!payload.photos.some((photo) => photo.url === payload.cover)) {
    payload.cover = payload.photos[0]?.url || ''
  }
  const next = [...rawPhotos.value]
  next[album.sourceIndex] = payload
  await contentApi.adminPutJson('/photos', next)
  rawPhotos.value = next
  refreshActiveAlbum(album.sourceIndex, preferredUrl)
}

async function uploadAlbumPhotos(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (!activeAlbum.value || !files.length) return
  uploadingAlbumPhoto.value = true
  try {
    const uploaded: PhotoItem[] = []
    for (const file of files) {
      const result = await contentApi.upload(file)
      uploaded.push({
        url: result.url,
        title: file.name.replace(/\.[^.]+$/, ''),
        date: new Date().toISOString().slice(0, 10)
      })
    }
    const nextPhotos = [...activeAlbum.value.photos, ...uploaded]
    await persistAlbumPhotos(activeAlbum.value, nextPhotos, uploaded[0]?.url || active.value?.url || '')
    ui.showToast(files.length > 1 ? '照片已上传' : '照片已添加', 'success')
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '照片上传失败', 'error')
  } finally {
    uploadingAlbumPhoto.value = false
    input.value = ''
  }
}

async function deleteAlbumPhoto(index: number) {
  if (!activeAlbum.value || index < 0) return
  const removed = activeAlbum.value.photos[index]
  const nextPhotos = activeAlbum.value.photos.filter((_, photoIndex) => photoIndex !== index)
  const preferredUrl = active.value?.url === removed?.url
    ? nextPhotos[Math.max(0, index - 1)]?.url || nextPhotos[0]?.url || ''
    : active.value?.url || ''
  try {
    await persistAlbumPhotos(activeAlbum.value, nextPhotos, preferredUrl)
    ui.showToast('照片已删除', 'success')
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '删除失败', 'error')
  }
}

function armPhotoDrag(index: number) {
  if (!session.isAdmin) return
  window.clearTimeout(photoLongPressTimer)
  photoLongPressTimer = window.setTimeout(() => {
    dragReadyIndex.value = index
  }, 320)
}

function disarmPhotoDrag() {
  window.clearTimeout(photoLongPressTimer)
  if (draggingPhotoIndex.value === null) dragReadyIndex.value = null
}

function startPhotoDrag(index: number, event: DragEvent) {
  if (!session.isAdmin || dragReadyIndex.value !== index) {
    event.preventDefault()
    return
  }
  draggingPhotoIndex.value = index
  event.dataTransfer?.setData('text/plain', String(index))
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
}

async function dropPhoto(index: number, event: DragEvent) {
  event.preventDefault()
  if (!activeAlbum.value || draggingPhotoIndex.value === null || draggingPhotoIndex.value === index) {
    endPhotoDrag()
    return
  }
  const from = draggingPhotoIndex.value
  const nextPhotos = [...activeAlbum.value.photos]
  const [moved] = nextPhotos.splice(from, 1)
  nextPhotos.splice(index, 0, moved)
  try {
    await persistAlbumPhotos(activeAlbum.value, nextPhotos, active.value?.url || moved.url)
    ui.showToast('照片顺序已更新', 'success')
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '排序保存失败', 'error')
  } finally {
    endPhotoDrag()
  }
}

function endPhotoDrag() {
  window.clearTimeout(photoLongPressTimer)
  dragReadyIndex.value = null
  draggingPhotoIndex.value = null
}

onMounted(load)
onUnmounted(() => window.clearTimeout(photoLongPressTimer))
</script>

<template>
  <section class="page-layout-grid">
    <GlassCard class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">{{ title }}</h1>
    </GlassCard>
    <form class="page-local-search" role="search" @submit.prevent>
      <input v-model="searchQ" type="search" placeholder="搜索相册标题、描述或标签..." aria-label="相册页搜索" />
      <button type="submit" aria-label="搜索相册">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.7-3.7" />
        </svg>
      </button>
    </form>
    <div class="flex justify-center">
      <div class="inline-flex rounded-full bg-white/[0.05] p-1">
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="viewMode === 'grid' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="viewMode = 'grid'">矩阵网格</button>
        <button type="button" class="rounded-full px-4 py-2 text-sm font-bold transition" :class="viewMode === 'link' ? 'bg-cyan-300 text-slate-950' : 'text-white/58 hover:text-white'" @click="viewMode = 'link'">中枢链路</button>
      </div>
    </div>

    <div v-if="session.isAdmin" class="flex justify-end">
      <button type="button" class="frontend-admin-create-btn" @click="createOpen = true">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        新增照片
      </button>
    </div>

    <div>
      <GlassCard v-if="loading">
        <p class="text-white/60">相册加载中...</p>
      </GlassCard>
      <GlassCard v-else-if="error">
        <p class="text-red-200/85">{{ error }}</p>
        <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
      </GlassCard>
      <GlassCard v-else-if="!albums.length">
        <p class="text-white/60">暂无相册。</p>
      </GlassCard>
      <GlassCard v-else-if="searchQ.trim() && !filteredAlbums.length">
        <p class="text-white/60">没有找到匹配的相册。</p>
      </GlassCard>

      <div v-else-if="viewMode === 'grid'" class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="album in filteredAlbums"
        :key="album.title + album.cover"
        class="relative"
      >
      <button
        type="button"
        class="photo-card-theme glass glass-hover block w-full overflow-hidden rounded-[30px] text-left"
        :class="toneMap[album.slug] === 'light' ? 'image-tone-light' : 'image-tone-dark'"
        :aria-label="`打开相册：${album.title}`"
        @click="activeAlbum = album; active = album.photos[0] || null"
      >
        <SafeImage :src="album.cover || album.photos[0]?.url" :alt="album.title || 'album'" img-class="relative z-[1] aspect-[4/3] w-full object-cover transition duration-300 hover:scale-[1.035]" />
        <div class="photo-card-content relative z-[1] flex min-h-48 flex-col p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h3 class="break-words font-bold text-white">{{ album.title || '未命名相册' }}</h3>
            <span v-if="album.date" class="text-xs text-white/42">{{ album.date }}</span>
          </div>
          <p class="mt-1 text-xs text-white/42">{{ album.photos.length }} 张照片</p>
          <p v-if="album.description" class="mt-1 break-words text-sm leading-6 text-white/55">{{ album.description }}</p>
          <div v-if="album.tags?.length" class="mt-auto flex flex-wrap gap-2 pt-3">
            <span v-for="tag in album.tags" :key="tag" class="content-tag rounded-full border px-2 py-1 text-[11px]" :style="tagStyle(tag, album.tagColors)">#{{ tag }}</span>
          </div>
        </div>
      </button>
      <button v-if="session.isAdmin" type="button" class="photo-admin-edit" @click="openAlbumEditor(album)">编辑</button>
      </div>
      </div>

      <div v-else class="article-link-mode">
      <div
        v-for="(album, index) in filteredAlbums"
        :key="album.title + album.cover"
        class="relative"
        :class="index % 2 === 0 ? 'article-link-left' : 'article-link-right'"
      >
      <button
        type="button"
        class="article-link-node text-left"
        :aria-label="`打开相册：${album.title}`"
        @click="activeAlbum = album; active = album.photos[0] || null"
      >
        <GlassCard hover class="photo-card-theme h-full overflow-hidden !p-0" :class="toneMap[album.slug] === 'light' ? 'image-tone-light' : 'image-tone-dark'">
          <article class="flex h-full min-w-0 flex-col">
            <div class="relative h-48 overflow-hidden bg-slate-900/60">
              <SafeImage :src="album.cover || album.photos[0]?.url" :alt="album.title || 'album'" img-class="h-full w-full object-cover transition duration-300 hover:scale-[1.035]" />
              <div class="image-contrast-overlay absolute inset-0"></div>
            </div>
            <div class="photo-card-content flex min-h-[14rem] flex-1 flex-col gap-3 p-5">
              <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-white/45">
                <span v-if="album.date">{{ album.date }}</span>
                <span>{{ album.photos.length }} 张照片</span>
              </div>
              <h2 class="line-clamp-2 text-xl font-black text-white">{{ album.title || '未命名相册' }}</h2>
              <p v-if="album.description" class="line-clamp-3 text-sm leading-7 text-white/58">{{ album.description }}</p>
              <div v-if="album.tags?.length" class="mt-auto flex flex-wrap gap-2 pt-3">
                <span v-for="tag in album.tags" :key="tag" class="content-tag rounded-full border px-3 py-1 text-xs" :style="tagStyle(tag, album.tagColors)"># {{ tag }}</span>
              </div>
            </div>
          </article>
        </GlassCard>
      </button>
      <button v-if="session.isAdmin" type="button" class="photo-admin-edit photo-admin-edit-link" @click="openAlbumEditor(album)">编辑</button>
      </div>
      </div>
    </div>
    <div
      v-if="activeAlbum"
      class="fixed inset-0 z-50 grid place-items-center bg-black/75 p-4"
      role="dialog"
      aria-modal="true"
      @click="activeAlbum = null; active = null"
      @keydown.esc.window="activeAlbum = null; active = null"
    >
      <div class="relative grid max-h-[92vh] w-full max-w-6xl gap-4 overflow-auto rounded-[32px] border border-white/15 bg-slate-950/82 p-4" @click.stop>
        <button
          type="button"
          class="absolute right-4 top-4 z-10 rounded-full border border-white/15 bg-black/45 px-3 py-2 text-sm text-white hover:bg-black/70"
          aria-label="关闭相册预览"
          @click="activeAlbum = null; active = null"
        >
          关闭
        </button>
        <div class="pr-16">
          <div class="flex flex-wrap items-center gap-3">
            <h2 class="text-2xl font-black text-white">{{ activeAlbum.title }}</h2>
            <button v-if="session.isAdmin" type="button" class="frontend-admin-inline-btn" @click="openAlbumEditor(activeAlbum)">编辑</button>
          </div>
          <p class="mt-1 text-sm text-white/50">{{ activeAlbum.description }}</p>
        </div>
        <div v-if="active" class="photo-active-frame">
          <SafeImage :src="active.url" :alt="active.title || activeAlbum.title" img-class="mx-auto max-h-[60vh] max-w-full rounded-3xl border border-white/15 object-contain" />
          <button
            v-if="session.isAdmin"
            type="button"
            class="photo-delete-btn photo-delete-active"
            aria-label="删除当前照片"
            @click.stop="deleteAlbumPhoto(activeIndex)"
          >
            ×
          </button>
        </div>
        <div class="photo-thumb-grid">
          <div
            v-for="(photo, index) in activeAlbum.photos"
            :key="photo.url"
            class="photo-thumb-wrap"
            :class="{
              'photo-thumb-ready': dragReadyIndex === index,
              'photo-thumb-dragging': draggingPhotoIndex === index
            }"
            :draggable="session.isAdmin"
            @pointerdown="armPhotoDrag(index)"
            @pointerup="disarmPhotoDrag"
            @pointerleave="disarmPhotoDrag"
            @dragstart="startPhotoDrag(index, $event)"
            @dragover.prevent
            @drop="dropPhoto(index, $event)"
            @dragend="endPhotoDrag"
          >
            <button type="button" class="photo-thumb-button" :class="active?.url === photo.url ? 'ring-2 ring-cyan-300' : ''" @click="active = photo">
              <SafeImage :src="photo.url" :alt="photo.title || 'photo'" img-class="aspect-square w-full object-cover" />
            </button>
            <button
              v-if="session.isAdmin"
              type="button"
              class="photo-delete-btn"
              aria-label="删除照片"
              @click.stop="deleteAlbumPhoto(index)"
            >
              ×
            </button>
          </div>
          <button
            v-if="session.isAdmin"
            type="button"
            class="photo-add-tile"
            :disabled="uploadingAlbumPhoto"
            aria-label="添加照片"
            @click="albumPhotoInput?.click()"
          >
            <span>{{ uploadingAlbumPhoto ? '...' : '+' }}</span>
          </button>
          <input ref="albumPhotoInput" class="sr-only" type="file" accept="image/*" multiple @change="uploadAlbumPhotos" />
        </div>
        <p class="text-center text-white/70">{{ active?.title }}</p>
        <CommentBox v-if="activeAlbum" resource="photos" :slug="activeAlbum.slug" frameless />
      </div>
    </div>
    <FrontPhotoEditorModal v-model="createOpen" @saved="load" />
    <FrontPhotoEditorModal v-model="editOpen" :album="editingAlbum" :index="editingAlbum?.sourceIndex ?? -1" @saved="afterAlbumSaved" />
  </section>
</template>

<style scoped>
.frontend-admin-inline-btn {
  border-radius: 999px;
  background: white;
  padding: .45rem .75rem;
  color: black;
  font-size: .82rem;
  font-weight: 900;
}
.photo-admin-edit {
  position: absolute;
  right: .85rem;
  top: .85rem;
  z-index: 2;
  border-radius: 999px;
  background: white;
  padding: .45rem .75rem;
  color: black;
  font-size: .82rem;
  font-weight: 900;
  box-shadow: 0 12px 28px rgba(0, 0, 0, .26);
}
.photo-admin-edit-link {
  right: 1rem;
  top: 1rem;
}
.photo-active-frame {
  position: relative;
  display: grid;
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
}
.photo-thumb-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .5rem;
}
.photo-thumb-wrap {
  position: relative;
  min-width: 0;
  cursor: grab;
  touch-action: manipulation;
}
.photo-thumb-wrap:active {
  cursor: grabbing;
}
.photo-thumb-ready .photo-thumb-button {
  border-color: rgba(255, 255, 255, .8);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, .18);
}
.photo-thumb-dragging {
  opacity: .58;
}
.photo-thumb-button {
  display: block;
  width: 100%;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .1);
  border-radius: 1rem;
  background: rgba(255, 255, 255, .04);
}
.photo-add-tile {
  display: grid;
  min-height: 100%;
  aspect-ratio: 1;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, .78);
  border-radius: 1rem;
  background: rgba(255, 255, 255, .18);
  color: white;
  transition: transform .16s ease, background .16s ease, border-color .16s ease;
}
.photo-add-tile:hover:not(:disabled) {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, .24);
  border-color: white;
}
.photo-add-tile:disabled {
  cursor: wait;
  opacity: .62;
}
.photo-add-tile span {
  font-size: 2rem;
  font-weight: 300;
  line-height: 1;
}
.photo-delete-btn {
  position: absolute;
  right: .35rem;
  top: .35rem;
  z-index: 3;
  display: grid;
  width: 1.6rem;
  height: 1.6rem;
  place-items: center;
  border: 1px solid rgba(248, 113, 113, .86);
  border-radius: 999px;
  background: rgba(127, 29, 29, .48);
  color: #f87171;
  font-size: 1.1rem;
  font-weight: 900;
  line-height: 1;
  transition: transform .16s ease, background .16s ease;
}
.photo-delete-btn:hover {
  transform: scale(1.06);
  background: rgba(153, 27, 27, .66);
}
.photo-delete-active {
  right: .75rem;
  top: .75rem;
}
@media (min-width: 640px) {
  .photo-thumb-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
@media (min-width: 768px) {
  .photo-thumb-grid {
    grid-template-columns: repeat(8, minmax(0, 1fr));
  }
}
</style>
