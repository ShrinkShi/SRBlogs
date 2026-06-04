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
const dragPhotos = ref<PhotoItem[] | null>(null)
const draggedPhotoUrl = ref('')
const dragState = reactive({
  active: false,
  fromIndex: -1,
  currentIndex: -1,
  pointerId: 0,
  startX: 0,
  startY: 0,
  x: 0,
  y: 0,
  moved: false,
  lastSwapAt: 0
})
const suppressPhotoClick = ref(false)
let photoLongPressTimer: number | undefined
const createOpen = ref(false)
const editOpen = ref(false)
const editingAlbum = ref<AlbumView | null>(null)
const pageConfig = ref<PageConfig | null>(null)
const toneMap = reactive<Record<string, ImageTone>>({})
const title = computed(() => pageConfig.value?.pageText?.photos?.title || '相册')
const subtitle = computed(() => pageConfig.value?.pageText?.photos?.subtitle || '相册记录从后端 JSON 动态读取，点击封面可查看组内照片。')
useSeo({ title: () => title.value, description: () => subtitle.value, path: '/photowall' })
const visiblePhotos = computed(() => dragPhotos.value || activeAlbum.value?.photos || [])
const draggedPhoto = computed(() => visiblePhotos.value.find((photo) => photo.url === draggedPhotoUrl.value) || null)
const dragGhostStyle = computed(() => ({
  left: `${dragState.x}px`,
  top: `${dragState.y}px`
}))

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

function openAlbum(album: AlbumView) {
  activeAlbum.value = album
  active.value = album.photos[0] || null
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function closeAlbum() {
  activeAlbum.value = null
  active.value = null
  resetPhotoDrag()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function afterAlbumSaved() {
  activeAlbum.value = null
  active.value = null
  await load()
}

function toAlbumPayload(album: AlbumView, photos = album.photos): PhotoAlbum {
  return {
    title: album.title,
    description: album.description,
    cover: photos[0]?.url || '',
    date: album.date,
    tags: album.tags || [],
    tagColors: album.tagColors || {},
    photos: photos.map((photo) => ({ ...photo }))
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
  const payload = toAlbumPayload(album, photos)
  const next = [...rawPhotos.value]
  next[album.sourceIndex] = payload
  rawPhotos.value = next
  refreshActiveAlbum(album.sourceIndex, preferredUrl)
  await contentApi.adminPutJson('/photos', next)
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
  const photos = visiblePhotos.value
  const removed = photos[index]
  const nextPhotos = photos.filter((_, photoIndex) => photoIndex !== index)
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

function selectPhoto(photo: PhotoItem) {
  if (suppressPhotoClick.value) {
    suppressPhotoClick.value = false
    return
  }
  active.value = photo
}

function armPhotoDrag(index: number, event: PointerEvent) {
  if (!session.isAdmin) return
  if (event.pointerType === 'mouse' && event.button !== 0) return
  window.clearTimeout(photoLongPressTimer)
  dragState.startX = event.clientX
  dragState.startY = event.clientY
  dragState.x = event.clientX
  dragState.y = event.clientY
  dragState.pointerId = event.pointerId
  photoLongPressTimer = window.setTimeout(() => {
    const source = activeAlbum.value?.photos[index]
    if (!source) return
    dragReadyIndex.value = index
    dragPhotos.value = [...(activeAlbum.value?.photos || [])]
    draggedPhotoUrl.value = source.url
    dragState.active = true
    dragState.fromIndex = index
    dragState.currentIndex = index
    dragState.moved = false
    window.addEventListener('pointermove', movePhotoDrag)
    window.addEventListener('pointerup', finishPhotoDrag)
    window.addEventListener('pointercancel', cancelPhotoDrag)
  }, 220)
}

function disarmPhotoDrag() {
  window.clearTimeout(photoLongPressTimer)
  if (!dragState.active) dragReadyIndex.value = null
}

function photoIndexFromPoint(x: number, y: number) {
  const target = document.elementFromPoint(x, y)
  const node = target?.closest('[data-photo-index]')
  if (!(node instanceof HTMLElement)) return -1
  const value = Number(node.dataset.photoIndex)
  return Number.isFinite(value) ? value : -1
}

function movePhotoDrag(event: PointerEvent) {
  if (!dragState.active || event.pointerId !== dragState.pointerId || !dragPhotos.value) return
  event.preventDefault()
  dragState.x = event.clientX
  dragState.y = event.clientY
  if (Math.abs(event.clientX - dragState.startX) > 4 || Math.abs(event.clientY - dragState.startY) > 4) {
    dragState.moved = true
  }
  const overIndex = photoIndexFromPoint(event.clientX, event.clientY)
  if (overIndex < 0 || overIndex === dragState.currentIndex || overIndex >= dragPhotos.value.length) return
  const now = Date.now()
  if (dragState.lastSwapAt && now - dragState.lastSwapAt < 500) return

  const next = [...dragPhotos.value]
  const [moved] = next.splice(dragState.currentIndex, 1)
  next.splice(overIndex, 0, moved)
  dragPhotos.value = next
  dragState.currentIndex = overIndex
  dragState.lastSwapAt = now
}

async function finishPhotoDrag(event?: PointerEvent) {
  if (event && dragState.active && event.pointerId !== dragState.pointerId) return
  window.clearTimeout(photoLongPressTimer)
  cleanupPhotoDragListeners()
  if (!dragState.active) {
    resetPhotoDrag()
    return
  }
  const album = activeAlbum.value
  const nextPhotos = dragPhotos.value ? [...dragPhotos.value] : []
  const changed = dragState.fromIndex !== dragState.currentIndex
  const preferredUrl = active.value?.url || draggedPhotoUrl.value
  resetPhotoDrag()
  suppressPhotoClick.value = true
  window.setTimeout(() => (suppressPhotoClick.value = false), 60)
  if (!album || !changed) return
  try {
    await persistAlbumPhotos(album, nextPhotos, preferredUrl)
    ui.showToast('照片顺序已更新', 'success')
  } catch (exc) {
    await load()
    ui.showToast(exc instanceof Error ? exc.message : '排序保存失败', 'error')
  }
}

function cancelPhotoDrag() {
  window.clearTimeout(photoLongPressTimer)
  cleanupPhotoDragListeners()
  resetPhotoDrag()
}

function cleanupPhotoDragListeners() {
  window.removeEventListener('pointermove', movePhotoDrag)
  window.removeEventListener('pointerup', finishPhotoDrag)
  window.removeEventListener('pointercancel', cancelPhotoDrag)
}

function resetPhotoDrag() {
  dragReadyIndex.value = null
  dragPhotos.value = null
  draggedPhotoUrl.value = ''
  dragState.active = false
  dragState.fromIndex = -1
  dragState.currentIndex = -1
  dragState.pointerId = 0
  dragState.moved = false
  dragState.lastSwapAt = 0
}

onMounted(load)
onUnmounted(() => {
  window.clearTimeout(photoLongPressTimer)
  cleanupPhotoDragListeners()
})
</script>

<template>
  <section class="page-layout-grid">
    <GlassCard v-if="!activeAlbum" class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">{{ title }}</h1>
    </GlassCard>
    <template v-if="!activeAlbum">
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
        @click="openAlbum(album)"
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

      <div v-else class="photo-link-mode">
      <div
        v-for="album in filteredAlbums"
        :key="album.title + album.cover"
        class="relative"
      >
      <button
        type="button"
        class="photo-link-node text-left"
        :aria-label="`打开相册：${album.title}`"
        @click="openAlbum(album)"
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
    </template>
    <article v-else class="photo-detail-page">
      <header class="photo-detail-head">
        <button type="button" class="photo-detail-back" aria-label="返回相册列表" @click="closeAlbum">←</button>
        <div>
          <h1>{{ activeAlbum.title }}</h1>
          <p v-if="activeAlbum.description">{{ activeAlbum.description }}</p>
        </div>
        <button v-if="session.isAdmin" type="button" class="frontend-admin-inline-btn" @click="openAlbumEditor(activeAlbum)">编辑</button>
      </header>
      <div v-if="active" class="photo-active-frame photo-detail-main-image">
        <SafeImage :src="active.url" :alt="active.title || activeAlbum.title" img-class="mx-auto max-h-[68vh] max-w-full rounded-3xl border border-white/15 object-contain" />
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
      <TransitionGroup name="photo-thumb" tag="div" class="photo-thumb-grid photo-detail-thumbs">
        <div
          v-for="(photo, index) in visiblePhotos"
          :key="photo.url"
          class="photo-thumb-wrap"
          :data-photo-index="index"
          :class="{
            'photo-thumb-ready': dragReadyIndex === index,
            'photo-thumb-dragging': dragState.active && draggedPhotoUrl === photo.url
          }"
          @pointerdown="armPhotoDrag(index, $event)"
          @pointerup="disarmPhotoDrag"
          @pointerleave="disarmPhotoDrag"
        >
          <button type="button" class="photo-thumb-button" :class="active?.url === photo.url ? 'ring-2 ring-cyan-300' : ''" @click="selectPhoto(photo)">
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
          key="photo-add"
          type="button"
          class="photo-add-tile"
          :disabled="uploadingAlbumPhoto"
          aria-label="添加照片"
          @click="albumPhotoInput?.click()"
        >
          <span>{{ uploadingAlbumPhoto ? '...' : '+' }}</span>
        </button>
      </TransitionGroup>
      <input ref="albumPhotoInput" class="sr-only" type="file" accept="image/*" multiple @change="uploadAlbumPhotos" />
      <div v-if="dragState.active && draggedPhoto" class="photo-drag-ghost" :style="dragGhostStyle" aria-hidden="true">
        <SafeImage :src="draggedPhoto.url" :alt="draggedPhoto.title || '拖动中的照片'" img-class="aspect-square w-full object-cover" />
      </div>
      <p class="text-center text-white/70">{{ active?.title }}</p>
      <CommentBox v-if="activeAlbum" class="photo-detail-comments" resource="photos" :slug="activeAlbum.slug" frameless />
    </article>
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
.photo-link-mode {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
  gap: 1.25rem;
  align-items: stretch;
}
.photo-link-node {
  display: block;
  width: 100%;
  height: 100%;
}
.photo-detail-page {
  display: grid;
  grid-column: 1 / -1;
  gap: 1.25rem;
  width: min(88rem, 100%);
  margin: 0 auto;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 2rem;
  background: #1A1A1C;
  padding: clamp(1rem, 2vw, 1.75rem);
}
.photo-detail-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  gap: 1rem;
}
.photo-detail-head h1 {
  color: white;
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 900;
  line-height: 1.05;
}
.photo-detail-head p {
  margin-top: .45rem;
  color: rgba(255, 255, 255, .56);
}
.photo-detail-back {
  display: grid;
  width: 2.5rem;
  height: 2.5rem;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 999px;
  background: rgba(255, 255, 255, .07);
  color: white;
  font-size: 1.2rem;
  transition: transform .18s ease, background .18s ease;
}
.photo-detail-back:hover {
  transform: translateX(-2px);
  background: rgba(255, 255, 255, .12);
}
.photo-detail-main-image {
  margin-top: .25rem;
}
.photo-detail-thumbs {
  max-width: min(58rem, 100%);
  margin: 0 auto;
}
.photo-active-frame {
  position: relative;
  display: grid;
  width: fit-content;
  max-width: 100%;
  margin: 0 auto;
}
.photo-thumb-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .5rem;
}
.photo-thumb-wrap {
  position: relative;
  min-width: 0;
  cursor: grab;
  touch-action: none;
  transition: opacity .18s ease, transform .22s cubic-bezier(.2, .8, .2, 1);
}
.photo-thumb-wrap:active {
  cursor: grabbing;
}
.photo-thumb-ready .photo-thumb-button {
  border-color: rgba(255, 255, 255, .8);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, .18);
}
.photo-thumb-dragging {
  opacity: .2;
  transform: scale(.92);
}
.photo-thumb-button {
  display: block;
  width: 100%;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .1);
  border-radius: 1rem;
  background: rgba(255, 255, 255, .04);
}
.photo-thumb-move,
.photo-thumb-enter-active,
.photo-thumb-leave-active {
  transition: transform .24s cubic-bezier(.2, .8, .2, 1), opacity .18s ease;
}
.photo-thumb-enter-from,
.photo-thumb-leave-to {
  opacity: 0;
  transform: scale(.88);
}
.photo-thumb-leave-active {
  position: absolute;
}
.photo-drag-ghost {
  position: fixed;
  z-index: 120;
  width: clamp(5.4rem, 8vw, 7.5rem);
  pointer-events: none;
  transform: translate(-50%, -50%) scale(1.06);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, .42);
  border-radius: 1.05rem;
  background: rgba(255, 255, 255, .08);
  box-shadow: 0 24px 58px rgba(0, 0, 0, .5);
}
.photo-drag-ghost :deep(img) {
  display: block;
  border-radius: inherit;
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
.photo-detail-comments {
  width: 100%;
  margin-top: .75rem;
  border-top: 1px solid rgba(255, 255, 255, .12);
  padding-top: 1.4rem;
}
.photo-detail-comments :deep(.comment-section-divider) {
  display: none;
}
.photo-detail-comments :deep(.comment-board) {
  min-width: 0;
}
.photo-detail-comments :deep(.comment-input-shell) {
  grid-template-columns: auto minmax(0, 1fr) auto;
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
@media (max-width: 720px) {
  .photo-detail-page {
    border-radius: 1.35rem;
    padding: .85rem;
  }
  .photo-detail-head {
    grid-template-columns: auto minmax(0, 1fr);
  }
  .photo-detail-head .frontend-admin-inline-btn {
    grid-column: 2;
    justify-self: start;
  }
}
</style>
