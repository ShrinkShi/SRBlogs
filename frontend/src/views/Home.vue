<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, HomeComponentId, MusicItem, PageConfig, PhotoAlbum, PhotoItem, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'
import { formatDate } from '@/utils/date'
import { customBlocks, layoutStyle } from '@/utils/pageLayout'

type UpdateItem = {
  type: 'posts' | 'moments' | 'chatters'
  label: string
  title: string
  date: string
  summary: string
  url: string
}
type LyricEntry = { time: number; text: string }

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const photos = ref<Array<PhotoItem | PhotoAlbum>>([])
const music = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const pageConfig = ref<PageConfig | null>(null)
const remoteLyrics = ref('')
const currentTrack = ref(0)
const postIndex = ref(0)
const photoIndex = ref(0)
const updateIndex = ref(0)
const now = ref(new Date())
const ui = useUiStore()
const player = usePlayerStore()
let clockTimer = 0
let carouselTimer = 0
let volumeHideTimer = 0
const volumeOpen = ref(false)

useSeo({
  title: () => settings.value?.siteTitle || settings.value?.title || '首页',
  description: () => settings.value?.description || settings.value?.bio || 'SRBlogs 首页',
  image: () => settings.value?.avatar || settings.value?.avatarUrl || settings.value?.bgImages?.[0],
  path: '/'
})

const track = computed(() => player.track || music.value[currentTrack.value])
const postSlides = computed(() => posts.value.slice(0, 6))
function photoCover(item: PhotoItem | PhotoAlbum): PhotoItem {
  if ('photos' in item && Array.isArray(item.photos)) {
    const first = item.photos[0]
    return {
      url: item.cover || first?.url || '',
      title: item.title || first?.title,
      description: item.description || first?.description,
      date: item.date || first?.date,
      tags: item.tags || first?.tags
    }
  }
  return item as PhotoItem
}

const photoSlides = computed(() => photos.value.map(photoCover).filter((item) => item.url).slice(0, 6))
const photoCount = computed(() => photos.value.reduce((count, item) => {
  if ('photos' in item && Array.isArray(item.photos)) return count + item.photos.length
  return count + 1
}, 0))
const currentPost = computed(() => postSlides.value[postIndex.value] || postSlides.value[0])
const currentPhoto = computed(() => photoSlides.value[photoIndex.value] || photoSlides.value[0])
const latestUpdates = computed<UpdateItem[]>(() => {
  const mapItem = (type: UpdateItem['type'], item: ContentItem): UpdateItem => ({
    type,
    label: type === 'posts' ? '文章' : type === 'chatters' ? '杂谈' : '瞬间',
    title: item.meta.title,
    date: item.meta.date,
    summary: item.meta.summary || item.content.replace(/[#>*_`-]/g, '').slice(0, 120),
    url: `/${type}/${item.slug}`
  })

  return [
    ...posts.value.map((item) => mapItem('posts', item)),
    ...moments.value.map((item) => mapItem('moments', item)),
    ...chatters.value.map((item) => mapItem('chatters', item))
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 6)
})
const currentUpdate = computed(() => latestUpdates.value[updateIndex.value] || latestUpdates.value[0])
function parseTimeTag(tag: string) {
  const match = tag.match(/^(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?$/)
  if (!match) return null
  const minutes = Number(match[1])
  const seconds = Number(match[2])
  const fraction = match[3] ? Number(`0.${match[3].padEnd(3, '0').slice(0, 3)}`) : 0
  return minutes * 60 + seconds + fraction
}

function parseLrc(source: string): LyricEntry[] {
  const entries: LyricEntry[] = []
  const plainLines: string[] = []
  source.split('\n').forEach((rawLine) => {
    const line = rawLine.trim()
    if (!line) return
    const tags = [...line.matchAll(/\[([0-9:.]+)\]/g)]
    const text = line.replace(/\[[^\]]+\]/g, '').trim()
    if (!tags.length) {
      if (text) plainLines.push(text)
      return
    }
    tags.forEach((tag) => {
      const time = parseTimeTag(tag[1])
      if (time !== null && text) entries.push({ time, text })
    })
  })
  if (!entries.length && plainLines.length) return [{ time: 0, text: plainLines[0] }]
  return entries.sort((a, b) => a.time - b.time)
}

const lyricEntries = computed(() => parseLrc(remoteLyrics.value || track.value?.lyrics || ''))
const lyricLine = computed(() => {
  const entries = lyricEntries.value
  if (entries.length) {
    const current = Math.max(0, player.currentTime || 0)
    if (current < entries[0].time) return track.value ? `${track.value.title} / 等待歌词` : '等待歌词'
    let active = entries[0]
    for (const entry of entries) {
      if (entry.time <= current) active = entry
      else break
    }
    return active.text || '暂无歌词'
  }
  if (track.value?.lyricUrl || track.value?.lyrics) return '暂无歌词'
  if (track.value) return `${track.value.title} - ${track.value.artist} / ${player.playing ? '正在播放' : '等待播放'}`
  return '暂无歌词数据，添加歌曲后这里会显示当前播放信息'
})

watch(() => track.value?.lyricUrl, async (url) => {
  remoteLyrics.value = ''
  if (!url) return
  try {
    const response = await fetch(url)
    if (response.ok) remoteLyrics.value = await response.text()
  } catch {
    remoteLyrics.value = ''
  }
}, { immediate: true })
const lyricStyle = computed(() => {
  const len = lyricLine.value.length
  const size = len > 60 ? '1rem' : len > 42 ? '1.18rem' : len > 28 ? '1.35rem' : '1.65rem'
  return { fontSize: size }
})
const beijingTime = computed(() => now.value.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }))
const runtime = computed(() => {
  if (!settings.value?.buildDate) return '待部署后开始计时'
  const start = new Date(settings.value.buildDate).getTime()
  if (Number.isNaN(start)) return '待部署后开始计时'
  const days = Math.max(1, Math.floor((Date.now() - start) / 86400000))
  return `${days} 天`
})
const progressPercent = computed(() => player.duration ? `${Math.min(100, (player.currentTime / player.duration) * 100)}%` : '0%')
const currentSongId = computed(() => player.songKey(track.value))
const likedCurrent = computed(() => currentSongId.value ? player.isLiked(currentSongId.value) : false)
const currentLikes = computed(() => Math.max(0, Number(track.value?.likes || 0)))
const playModeLabel = computed(() => player.playMode === 'sequence' ? '顺序播放' : player.playMode === 'shuffle' ? '随机播放' : '单曲循环')
const recordStyle = computed<Record<string, string>>(() => (
  track.value?.cover ? { '--record-cover': `url(${track.value.cover})` } : {} as Record<string, string>
))
const homeSettings = computed<SiteSettings | null>(() => {
  const profile = pageConfig.value?.homeProfile
  if (!profile) return settings.value
  return {
    ...(settings.value || {}),
    author: profile.author || settings.value?.author,
    avatar: profile.avatar || settings.value?.avatar,
    description: profile.description || settings.value?.description,
    socialLinks: profile.socialLinks || settings.value?.socialLinks
  }
})

const defaultHomeLayout: Record<HomeComponentId, { order: number; w: number; h: number; rowSpan?: number; visible: boolean }> = {
  profileCard: { order: 1, w: 6, h: 2, visible: true },
  musicPlayer: { order: 2, w: 6, h: 2, visible: true },
  lyrics: { order: 3, w: 12, h: 1, visible: true },
  latestPostsCarousel: { order: 4, w: 4, h: 4, rowSpan: 2, visible: true },
  photoCarousel: { order: 5, w: 8, h: 2, visible: true },
  updatesCarousel: { order: 6, w: 4, h: 2, visible: true },
  themeToggle: { order: 7, w: 4, h: 2, visible: true },
  statusBar: { order: 8, w: 12, h: 1, visible: true }
}
const homeCustomBlocks = computed(() => customBlocks(pageConfig.value, 'home'))

function componentLayout(id: HomeComponentId) {
  const components = pageConfig.value?.pageLayouts?.home?.components || pageConfig.value?.homeLayout?.components || pageConfig.value?.home?.components || {}
  return { ...defaultHomeLayout[id], ...(components[id] || {}) }
}

function isComponentVisible(id: HomeComponentId) {
  return componentLayout(id).visible !== false
}

function homeComponentStyle(id: HomeComponentId) {
  const item = componentLayout(id)
  const span = Math.max(1, Math.min(12, Math.round(Number(item.w || 12))))
  const h = Math.max(0.5, Math.min(4, Number(item.h || 1)))
  const rowSpan = Math.max(1, Math.min(32, Math.round(h * 4)))
  return {
    order: Number(item.order || defaultHomeLayout[id].order),
    gridColumn: `span ${span} / span ${span}`,
    gridRow: `span ${rowSpan} / span ${rowSpan}`,
    minHeight: `${Math.max(3, h * 4)}rem`
  }
}

function setPost(index: number) {
  if (postSlides.value.length) postIndex.value = index % postSlides.value.length
}

function setPhoto(index: number) {
  if (photoSlides.value.length) photoIndex.value = index % photoSlides.value.length
}

function setUpdate(index: number) {
  if (latestUpdates.value.length) updateIndex.value = index % latestUpdates.value.length
}

function nextTrack() {
  player.next()
}

function prevTrack() {
  player.prev()
}

async function togglePlay() {
  if (!track.value?.url) {
    player.playing = false
    ui.showToast('当前歌曲没有可播放 URL', 'error')
    return
  }
  await player.toggle()
}

function formatTime(seconds: number) {
  if (!seconds || !Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${mins}:${secs}`
}

function setVolumeFromEvent(event: Event) {
  player.setVolume(Number((event.target as HTMLInputElement).value))
}

function seekFromEvent(event: Event) {
  const value = Number((event.target as HTMLInputElement).value)
  player.seek(value)
}

function showVolumeSlider() {
  if (volumeHideTimer) window.clearTimeout(volumeHideTimer)
  volumeOpen.value = true
}

function hideVolumeSliderSoon() {
  if (volumeHideTimer) window.clearTimeout(volumeHideTimer)
  volumeHideTimer = window.setTimeout(() => {
    volumeOpen.value = false
  }, 500)
}

async function toggleLike() {
  const id = currentSongId.value
  if (!id) {
    ui.showToast('当前歌曲缺少稳定 ID，无法喜欢', 'error')
    return
  }
  const nextLiked = !likedCurrent.value
  const previousLikes = currentLikes.value
  const nextLikes = Math.max(0, previousLikes + (nextLiked ? 1 : -1))
  player.setLikedLocal(id, nextLiked)
  player.updateTrackLikes(id, nextLikes)
  music.value = music.value.map((item) => player.songKey(item) === id ? { ...item, likes: nextLikes } : item)
  try {
    const result = await contentApi.updateMusicLike(id, nextLiked)
    player.updateTrackLikes(id, result.likes)
    music.value = music.value.map((item) => player.songKey(item) === id ? { ...item, likes: result.likes } : item)
  } catch (exc) {
    player.setLikedLocal(id, !nextLiked)
    player.updateTrackLikes(id, previousLikes)
    music.value = music.value.map((item) => player.songKey(item) === id ? { ...item, likes: previousLikes } : item)
    ui.showToast(exc instanceof Error ? exc.message : '喜欢状态保存失败', 'error')
  }
}

onMounted(async () => {
  const [p, m, c, ph, s, mu, pc] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<Array<PhotoItem | PhotoAlbum>>('/photos'),
    contentApi.json<SiteSettings>('/settings/public'),
    contentApi.json<MusicItem[]>('/music'),
    contentApi.json<PageConfig>('/pages/config')
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (ph.status === 'fulfilled') photos.value = ph.value
  if (s.status === 'fulfilled') settings.value = s.value
  if (mu.status === 'fulfilled') music.value = mu.value
  if (pc.status === 'fulfilled') pageConfig.value = pc.value
  if (mu.status === 'fulfilled') player.setTracks(mu.value)

  clockTimer = window.setInterval(() => { now.value = new Date() }, 1000)
  carouselTimer = window.setInterval(() => {
    setPost(postIndex.value + 1)
    setPhoto(photoIndex.value + 1)
    setUpdate(updateIndex.value + 1)
  }, 5600)
})

onBeforeUnmount(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  if (carouselTimer) window.clearInterval(carouselTimer)
  if (volumeHideTimer) window.clearTimeout(volumeHideTimer)
})
</script>

<template>
  <section class="grid min-w-0 max-w-full gap-6 md:gap-8">
    <div class="home-layout-grid">
      <ProfileCard
        v-if="isComponentVisible('profileCard')"
        class="home-profile-card home-card-opacity min-w-0 max-w-full"
        :style="homeComponentStyle('profileCard')"
        :settings="homeSettings"
        :posts="posts.length"
        :chatters="chatters.length"
        :photos="photoCount || settings?.counts?.photos || 0"
      />

      <GlassCard v-if="isComponentVisible('musicPlayer')" hover class="music-compact-card min-w-0" :style="homeComponentStyle('musicPlayer')">
        <div class="music-compact-layout">
          <div class="record-disc music-compact-disc rounded-full" :class="{ playing: player.playing }" :style="recordStyle" aria-hidden="true"></div>
          <div class="grid min-w-0 content-center justify-items-center gap-4 text-center">
            <div class="min-w-0">
              <h3 class="line-clamp-2 break-words text-3xl font-black text-white">{{ track?.title || '暂无歌曲' }}</h3>
              <p class="mt-2 text-sm text-white/58">{{ track?.artist || '请在后台音乐管理添加歌曲' }}</p>
            </div>
            <div class="w-full max-w-[24rem]">
              <div class="mb-2 flex items-center justify-between text-xs text-white/48">
                <span>{{ formatTime(player.currentTime) }}</span>
                <span>{{ formatTime(player.duration) }}</span>
              </div>
              <input class="progress-slider" type="range" min="0" :max="player.duration || 0" step="0.1" :value="player.currentTime" aria-label="播放进度" :style="{ '--progress': progressPercent }" @input="seekFromEvent" />
            </div>
          <div class="flex items-center justify-center gap-2 whitespace-nowrap">
            <button type="button" class="icon-button" :aria-label="playModeLabel" :title="playModeLabel" @click="player.cyclePlayMode()">
              <svg v-if="player.playMode === 'sequence'" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h12l-3-3 1.4-1.4L20.8 9l-6.4 6.4L13 14l3-3H4V7zm0 10h16v2H4v-2z" /></svg>
              <svg v-else-if="player.playMode === 'shuffle'" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3h5v5h-2V6.4l-4.8 4.8-1.4-1.4L17.6 5H16V3zM4 7h3.5l3.2 3.2-1.4 1.4L6.7 9H4V7zm10.2 5.8 4.8 4.8V16h2v5h-5v-2h1.6l-4.8-4.8 1.4-1.4zM4 17h2.7l10.1-10.1 1.4 1.4L7.5 19H4v-2z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7h8.6l-2.3-2.3L14.7 3 20 8.3l-5.3 5.3-1.4-1.7 2.3-2.3H7a3 3 0 0 0 0 6h1v2H7A5 5 0 0 1 7 7zm10 10h-4v-2h4a3 3 0 0 0 0-6h-1V7h1a5 5 0 0 1 0 10z" /></svg>
            </button>
            <div class="volume-control" :class="{ 'volume-open': volumeOpen }" @mouseenter="showVolumeSlider" @mouseleave="hideVolumeSliderSoon" @focusin="showVolumeSlider" @focusout="hideVolumeSliderSoon">
              <button type="button" class="icon-button h-9 w-9" :aria-label="player.muted ? '取消静音' : '静音'" @click="player.toggleMuted()">
                <svg v-if="player.muted || player.volume <= 0" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.8 3 2.6-2.6-1.4-1.4-2.6 2.6-2.6-2.6-1.4 1.4L14 12l-2.6 2.6 1.4 1.4 2.6-2.6 2.6 2.6 1.4-1.4L16.8 12z" /></svg>
                <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zm-2.5-9.2v2.1a7.5 7.5 0 0 1 0 14.2v2.1a9.5 9.5 0 0 0 0-18.4z" /></svg>
              </button>
              <input class="volume-slider" type="range" min="0" max="1" step="0.01" :value="player.muted ? 0 : player.volume" aria-label="音量" @input="setVolumeFromEvent" @pointerdown="showVolumeSlider" @pointerup="hideVolumeSliderSoon" />
            </div>
            <button type="button" class="icon-button" aria-label="previous track" @click="prevTrack">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 6h2v12H7zM18 6v12l-8.5-6z" /></svg>
            </button>
            <button type="button" class="icon-button icon-button-main" :aria-label="player.playing ? '暂停' : '播放'" @click="togglePlay">
              <svg v-if="player.playing" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" /></svg>
            </button>
            <button type="button" class="icon-button" aria-label="next track" @click="nextTrack">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6h2v12h-2zM6 6l8.5 6L6 18z" /></svg>
            </button>
            <button type="button" class="icon-button like-button-inline min-w-[4rem] gap-1 text-sm" :aria-label="likedCurrent ? '取消喜欢' : '喜欢当前歌曲'" @click="toggleLike">
              <svg viewBox="0 0 24 24" aria-hidden="true" :class="likedCurrent ? 'text-rose-300' : ''"><path d="M12 21s-7-4.4-9.4-8.6C.8 9.2 2.7 5.5 6.2 5.1c2-.2 3.6.7 4.7 2.1 1.1-1.4 2.8-2.3 4.7-2.1 3.5.4 5.4 4.1 3.6 7.3C19 16.6 12 21 12 21z" /></svg>
              <span>{{ currentLikes }}</span>
            </button>
          </div>
          <p v-if="track && !track.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅显示信息。</p>
          </div>
        </div>
      </GlassCard>

      <GlassCard v-if="isComponentVisible('lyrics')" hover class="sr-hero-panel lyrics-compact" :style="homeComponentStyle('lyrics')">
      <div class="flex h-full min-h-[38px] flex-col items-center justify-center px-4 py-3 text-center">
        <p class="mx-auto max-w-full truncate text-center font-black leading-tight text-white/78" :style="lyricStyle">{{ lyricLine }}</p>
      </div>
    </GlassCard>

      <RouterLink
        v-if="isComponentVisible('latestPostsCarousel') && currentPost"
        :to="`/posts/${currentPost.slug}`"
        class="home-media-carousel home-latest-posts-carousel home-image-zoom home-carousel-tall"
        :style="homeComponentStyle('latestPostsCarousel')"
      >
        <div class="image-layer absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.08), rgba(0,0,0,.72)), url(${currentPost.meta.cover || settings?.defaultPostCover || ''})` }"></div>
        <div class="home-carousel-copy">
          <span class="sr-chip px-3 py-1 text-xs">{{ formatDate(currentPost.meta.date) }}</span>
          <h2 class="mt-3 line-clamp-3 text-3xl font-black text-white">{{ currentPost.meta.title }}</h2>
          <p class="mt-3 line-clamp-3 text-sm leading-6 text-white/68">{{ currentPost.meta.summary || currentPost.content.slice(0, 120) }}</p>
        </div>
        <div v-if="postSlides.length > 1" class="home-carousel-dots">
            <button v-for="(_, index) in postSlides" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === postIndex }" :aria-label="`切换到第 ${index + 1} 篇文章`" @mouseenter="setPost(index)" @click.prevent="setPost(index)"></button>
        </div>
      </RouterLink>
      <div v-else-if="isComponentVisible('latestPostsCarousel')" class="home-media-carousel home-carousel-tall grid place-items-center text-white/58" :style="homeComponentStyle('latestPostsCarousel')">暂无公开文章</div>

        <RouterLink v-if="isComponentVisible('photoCarousel') && currentPhoto" to="/photowall" class="home-media-carousel home-photo-carousel-card home-image-zoom" :style="homeComponentStyle('photoCarousel')">
          <div class="image-layer absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.08), rgba(0,0,0,.66)), url(${currentPhoto.url})` }"></div>
          <div class="home-carousel-copy">
            <span class="sr-chip px-3 py-1 text-xs">{{ currentPhoto.date || 'photo' }}</span>
            <h2 class="mt-3 line-clamp-2 text-3xl font-black text-white">{{ currentPhoto.title || '照片墙' }}</h2>
            <p class="mt-3 line-clamp-2 text-sm leading-6 text-white/68">{{ currentPhoto.description || '记录生活里的片段和场景。' }}</p>
          </div>
          <div v-if="photoSlides.length > 1" class="home-carousel-dots">
            <button v-for="(_, index) in photoSlides" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === photoIndex }" :aria-label="`切换到第 ${index + 1} 张照片`" @mouseenter="setPhoto(index)" @click.prevent="setPhoto(index)"></button>
          </div>
        </RouterLink>
        <div v-else-if="isComponentVisible('photoCarousel')" class="home-media-carousel grid place-items-center text-white/58" :style="homeComponentStyle('photoCarousel')">暂无照片</div>

          <RouterLink v-if="isComponentVisible('updatesCarousel') && currentUpdate" :to="currentUpdate.url" class="home-text-carousel home-updates-carousel-card sr-card-hover" :style="homeComponentStyle('updatesCarousel')">
            <div>
              <div class="flex items-center justify-between gap-3">
                <span class="sr-chip px-3 py-1 text-xs">{{ currentUpdate.label }}</span>
                <span class="text-xs text-white/45">{{ formatDate(currentUpdate.date) }}</span>
              </div>
              <h2 class="mt-5 line-clamp-2 text-3xl font-black text-white">{{ currentUpdate.title }}</h2>
              <p class="mt-4 line-clamp-3 text-sm leading-7 text-white/60">{{ currentUpdate.summary }}</p>
            </div>
            <div v-if="latestUpdates.length > 1" class="home-carousel-dots">
              <button v-for="(_, index) in latestUpdates" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === updateIndex }" :aria-label="`切换到第 ${index + 1} 条更新`" @mouseenter="setUpdate(index)" @click.prevent="setUpdate(index)"></button>
            </div>
          </RouterLink>
          <div v-else-if="isComponentVisible('updatesCarousel')" class="home-text-carousel grid place-items-center text-white/58" :style="homeComponentStyle('updatesCarousel')">暂无更新内容</div>

          <button v-if="isComponentVisible('themeToggle')" type="button" class="home-theme-card sr-card-hover" :style="homeComponentStyle('themeToggle')" @click="ui.toggleColorMode">
            <span class="mode-orb grid h-20 w-20 place-items-center rounded-[28px] text-3xl">{{ ui.colorMode === 'day' ? '☀' : '☾' }}</span>
            <span class="mt-5 block text-2xl font-black text-white">{{ ui.colorMode === 'day' ? '日间模式' : '夜间模式' }}</span>
            <span class="mt-3 block text-sm leading-6 text-white/58">点击切换全站昼夜主题</span>
          </button>

    <GlassCard v-if="isComponentVisible('statusBar')" hover class="home-status-card home-card-opacity" :style="homeComponentStyle('statusBar')">
      <div class="home-status-grid">
        <div class="rounded-3xl border border-white/10 bg-white/[0.06] p-4">
          <p class="text-xs uppercase tracking-[.24em] text-white/38">beijing time</p>
          <b class="mt-2 block text-xl text-white">{{ beijingTime }}</b>
        </div>
        <div class="rounded-3xl border border-white/10 bg-white/[0.06] p-4">
          <p class="text-xs uppercase tracking-[.24em] text-white/38">runtime</p>
          <b class="mt-2 block text-xl text-white">{{ runtime }}</b>
        </div>
        <div class="rounded-3xl border border-white/10 bg-white/[0.06] p-4">
          <p class="text-xs uppercase tracking-[.24em] text-white/38">stack</p>
          <b class="mt-2 block text-sm leading-6 text-white">Vue 3 / Vite / Tailwind CSS / FastAPI</b>
        </div>
      </div>
    </GlassCard>

    <GlassCard v-for="block in homeCustomBlocks" :key="block.id" hover class="home-card-opacity" :style="layoutStyle(block)">
      <div v-if="block.type === 'divider'" class="h-px w-full bg-white/15"></div>
      <a v-else-if="block.type === 'linkButton'" :href="String(block.props?.url || '/')" class="sr-button-primary inline-flex w-fit">{{ block.props?.text || block.label }}</a>
      <div v-else-if="block.type === 'imageBlock'" class="grid gap-3">
        <img v-if="block.props?.url" :src="String(block.props.url)" :alt="String(block.props?.title || block.label)" class="max-h-72 w-full rounded-3xl object-cover" loading="lazy" />
        <h3 class="text-2xl font-black text-white">{{ block.props?.title || block.label }}</h3>
      </div>
      <p v-else class="whitespace-pre-wrap text-white/70">{{ block.props?.text || block.label }}</p>
    </GlassCard>
    </div>
  </section>
</template>
