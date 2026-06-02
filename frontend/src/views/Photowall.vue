<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import CommentBox from '@/components/CommentBox.vue'
import FrontPhotoEditorModal from '@/components/FrontPhotoEditorModal.vue'
import { contentApi } from '@/api/content'
import type { PageConfig, PhotoAlbum, PhotoItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { detectImageTone, type ImageTone } from '@/utils/imageTone'
import { useSessionStore } from '@/stores/session'

type AlbumView = PhotoAlbum & { slug: string; sourceIndex: number }

const rawPhotos = ref<Array<PhotoItem | PhotoAlbum>>([])
const session = useSessionStore()
const activeAlbum = ref<AlbumView | null>(null)
const active = ref<PhotoItem | null>(null)
const viewMode = ref<'grid' | 'link'>('grid')
const searchQ = ref('')
const loading = ref(false)
const error = ref('')
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
    photos: [photo]
  }
}

const albums = computed(() => rawPhotos.value.map(normalizeAlbum).filter((album) => album.photos.length || album.cover))
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

onMounted(load)
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
            <span v-for="tag in album.tags" :key="tag" class="content-tag rounded-full border px-2 py-1 text-[11px]">#{{ tag }}</span>
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
                <span v-for="tag in album.tags" :key="tag" class="content-tag rounded-full border px-3 py-1 text-xs"># {{ tag }}</span>
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
            <button v-if="session.isAdmin" type="button" class="frontend-admin-inline-btn" @click="openAlbumEditor(activeAlbum)">编辑照片组</button>
          </div>
          <p class="mt-1 text-sm text-white/50">{{ activeAlbum.description }}</p>
        </div>
        <SafeImage v-if="active" :src="active.url" :alt="active.title || activeAlbum.title" img-class="mx-auto max-h-[60vh] max-w-full rounded-3xl border border-white/15 object-contain" />
        <div class="grid grid-cols-3 gap-2 sm:grid-cols-5 md:grid-cols-8">
          <button v-for="photo in activeAlbum.photos" :key="photo.url" type="button" class="overflow-hidden rounded-2xl border border-white/10" :class="active?.url === photo.url ? 'ring-2 ring-cyan-300' : ''" @click="active = photo">
            <SafeImage :src="photo.url" :alt="photo.title || 'photo'" img-class="aspect-square w-full object-cover" />
          </button>
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
</style>
