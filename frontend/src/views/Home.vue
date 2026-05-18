<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import PlayerVolumeControl from '@/components/PlayerVolumeControl.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, MusicItem, PageConfig, PhotoAlbum, PhotoItem, SearchResultItem, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'
import { formatDate } from '@/utils/date'
import { detectImageTone, type ImageTone } from '@/utils/imageTone'

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
const postTone = ref<ImageTone>('dark')
const photoTone = ref<ImageTone>('dark')
const homeSearchQ = ref('')
const homeSearchResults = ref<SearchResultItem[]>([])
const homeSearchLoading = ref(false)
const homeSearchError = ref('')
const ui = useUiStore()
const player = usePlayerStore()
let clockTimer = 0
let carouselTimer = 0
let searchTimer = 0

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

watch(() => currentPost.value?.meta.cover || settings.value?.defaultPostCover || '', async (url) => {
  postTone.value = await detectImageTone(url, 'dark')
}, { immediate: true })

watch(() => currentPhoto.value?.url || '', async (url) => {
  photoTone.value = await detectImageTone(url, 'dark')
}, { immediate: true })

watch(homeSearchQ, () => {
  if (searchTimer) window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(runHomeSearch, 260)
})
const lyricStyle = computed(() => {
  const len = lyricLine.value.length
  const size = len > 60 ? '.78rem' : len > 42 ? '.88rem' : len > 28 ? '.98rem' : '1.08rem'
  return { fontSize: size }
})
const beijingTime = computed(() => now.value.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }))
const runtime = computed(() => {
  const startedAt = settings.value?.siteStartTime || settings.value?.buildDate
  if (!startedAt) return '待完成安装后开始计时'
  const start = new Date(startedAt).getTime()
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

function seekFromEvent(event: Event) {
  const value = Number((event.target as HTMLInputElement).value)
  player.seek(value)
}

async function runHomeSearch() {
  const q = homeSearchQ.value.trim()
  if (!q) {
    homeSearchResults.value = []
    homeSearchError.value = ''
    return
  }
  homeSearchLoading.value = true
  homeSearchError.value = ''
  try {
    const result = await contentApi.search({ q, type: 'all', limit: 8 })
    homeSearchResults.value = result.items
  } catch (exc) {
    homeSearchError.value = exc instanceof Error ? exc.message : '搜索失败'
    homeSearchResults.value = []
  } finally {
    homeSearchLoading.value = false
  }
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
  if (searchTimer) window.clearTimeout(searchTimer)
})
</script>

<template>
  <section class="grid min-w-0 max-w-full gap-6 md:gap-8">
    <div class="home-search-wrap">
      <form class="home-search-bar" role="search" @submit.prevent="runHomeSearch">
        <input v-model="homeSearchQ" type="search" placeholder="搜索全站内容..." aria-label="首页全站搜索" />
        <button type="submit" aria-label="搜索">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.7-3.7" />
          </svg>
        </button>
      </form>
      <div v-if="homeSearchQ.trim()" class="home-search-popover">
        <p v-if="homeSearchLoading" class="home-search-state">搜索中...</p>
        <p v-else-if="homeSearchError" class="home-search-state text-rose-600">{{ homeSearchError }}</p>
        <p v-else-if="!homeSearchResults.length" class="home-search-state">暂无匹配结果</p>
        <div v-else class="grid gap-2">
          <RouterLink v-for="item in homeSearchResults" :key="`${item.type}-${item.url}-${item.title}`" :to="item.url" class="home-search-result">
            <span>{{ item.type }}</span>
            <b>{{ item.title }}</b>
            <small>{{ item.summary || '点击查看详情' }}</small>
          </RouterLink>
        </div>
      </div>
    </div>
    <div class="home-fixed-grid">
      <ProfileCard
        class="home-profile-card home-card-opacity min-w-0 max-w-full"
        :settings="homeSettings"
        :posts="posts.length"
        :chatters="chatters.length"
        :photos="photoCount || settings?.counts?.photos || 0"
      />

      <GlassCard hover class="music-compact-card min-w-0">
        <div class="music-compact-layout">
          <div class="record-disc music-compact-disc rounded-full" :class="{ playing: player.playing }" :style="recordStyle" aria-hidden="true"></div>
          <div class="music-compact-body">
            <div class="min-w-0 text-center">
              <h3 class="line-clamp-2 break-words text-3xl font-black text-white">{{ track?.title || '暂无歌曲' }}</h3>
              <p class="mt-2 text-sm text-white/58">{{ track?.artist || '请在后台音乐管理添加歌曲' }}</p>
            </div>
            <div class="music-mini-controls">
              <button type="button" class="icon-button" :aria-label="playModeLabel" :title="playModeLabel" @click="player.cyclePlayMode()">
              <svg v-if="player.playMode === 'sequence'" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h12l-3-3 1.4-1.4L20.8 9l-6.4 6.4L13 14l3-3H4V7zm0 10h16v2H4v-2z" /></svg>
              <svg v-else-if="player.playMode === 'shuffle'" viewBox="0 0 24 24" aria-hidden="true"><path d="M16 3h5v5h-2V6.4l-4.8 4.8-1.4-1.4L17.6 5H16V3zM4 7h3.5l3.2 3.2-1.4 1.4L6.7 9H4V7zm10.2 5.8 4.8 4.8V16h2v5h-5v-2h1.6l-4.8-4.8 1.4-1.4zM4 17h2.7l10.1-10.1 1.4 1.4L7.5 19H4v-2z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7h8.6l-2.3-2.3L14.7 3 20 8.3l-5.3 5.3-1.4-1.7 2.3-2.3H7a3 3 0 0 0 0 6h1v2H7A5 5 0 0 1 7 7zm10 10h-4v-2h4a3 3 0 0 0 0-6h-1V7h1a5 5 0 0 1 0 10z" /></svg>
              </button>
              <PlayerVolumeControl />
              <button type="button" class="icon-button like-button-inline gap-1 text-sm" :aria-label="likedCurrent ? '取消喜欢' : '喜欢当前歌曲'" @click="toggleLike">
                <svg viewBox="0 0 24 24" aria-hidden="true" :class="likedCurrent ? 'text-rose-300' : ''"><path d="M12 21s-7-4.4-9.4-8.6C.8 9.2 2.7 5.5 6.2 5.1c2-.2 3.6.7 4.7 2.1 1.1-1.4 2.8-2.3 4.7-2.1 3.5.4 5.4 4.1 3.6 7.3C19 16.6 12 21 12 21z" /></svg>
                <span>{{ currentLikes }}</span>
              </button>
            </div>
            <div class="music-progress-block">
              <div class="mb-2 flex items-center justify-between text-xs text-white/48">
                <span>{{ formatTime(player.currentTime) }}</span>
                <span>{{ formatTime(player.duration) }}</span>
              </div>
              <input class="progress-slider" type="range" min="0" :max="player.duration || 0" step="0.1" :value="player.currentTime" aria-label="播放进度" :style="{ '--progress': progressPercent }" @input="seekFromEvent" />
            </div>
            <div class="music-main-controls">
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
            </div>
          <p v-if="track && !track.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅显示信息。</p>
          </div>
        </div>
      </GlassCard>

      <GlassCard hover class="sr-hero-panel lyrics-compact">
      <div class="flex h-full min-h-[38px] flex-col items-center justify-center px-4 py-2 text-center">
        <p class="home-lyric-line mx-auto max-w-full truncate text-center font-black leading-tight" :style="lyricStyle">{{ lyricLine }}</p>
      </div>
    </GlassCard>

      <div class="home-mosaic-grid">
        <RouterLink
          v-if="currentPost"
          :to="`/posts/${currentPost.slug}`"
          class="home-media-carousel home-latest-posts-carousel home-image-zoom home-carousel-tall"
          :class="postTone === 'light' ? 'image-tone-light' : 'image-tone-dark'"
        >
          <div class="image-layer absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `url(${currentPost.meta.cover || settings?.defaultPostCover || ''})` }"></div>
          <div class="image-contrast-overlay absolute inset-0"></div>
          <div class="home-carousel-copy">
            <span class="sr-chip px-3 py-1 text-xs">{{ formatDate(currentPost.meta.date) }}</span>
            <h2 class="mt-3 line-clamp-3 text-3xl font-black text-white">{{ currentPost.meta.title }}</h2>
            <p class="mt-3 line-clamp-3 text-sm leading-6 text-white/68">{{ currentPost.meta.summary || currentPost.content.slice(0, 120) }}</p>
          </div>
          <div v-if="postSlides.length > 1" class="home-carousel-dots">
              <button v-for="(_, index) in postSlides" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === postIndex }" :aria-label="`切换到第 ${index + 1} 篇文章`" @mouseenter="setPost(index)" @click.prevent="setPost(index)"></button>
          </div>
        </RouterLink>
        <div v-else class="home-media-carousel home-latest-posts-carousel home-carousel-tall grid place-items-center text-white/58">暂无公开文章</div>

          <RouterLink v-if="currentPhoto" to="/photowall" class="home-media-carousel home-photo-carousel-card home-image-zoom" :class="photoTone === 'light' ? 'image-tone-light' : 'image-tone-dark'">
            <div class="image-layer absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `url(${currentPhoto.url})` }"></div>
            <div class="image-contrast-overlay absolute inset-0"></div>
            <div class="home-carousel-copy">
              <span class="sr-chip px-3 py-1 text-xs">{{ currentPhoto.date || 'photo' }}</span>
              <h2 class="mt-3 line-clamp-2 text-3xl font-black text-white">{{ currentPhoto.title || '照片墙' }}</h2>
              <p class="mt-3 line-clamp-2 text-sm leading-6 text-white/68">{{ currentPhoto.description || '记录生活里的片段和场景。' }}</p>
            </div>
            <div v-if="photoSlides.length > 1" class="home-carousel-dots">
              <button v-for="(_, index) in photoSlides" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === photoIndex }" :aria-label="`切换到第 ${index + 1} 张照片`" @mouseenter="setPhoto(index)" @click.prevent="setPhoto(index)"></button>
            </div>
          </RouterLink>
          <div v-else class="home-media-carousel home-photo-carousel-card grid place-items-center text-white/58">暂无照片</div>

            <RouterLink v-if="currentUpdate" :to="currentUpdate.url" class="home-text-carousel home-updates-carousel-card sr-card-hover">
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
            <div v-else class="home-text-carousel home-updates-carousel-card grid place-items-center text-white/58">暂无更新内容</div>

            <button type="button" class="home-theme-card sr-card-hover" @click="ui.toggleColorMode">
              <span class="mode-orb grid h-20 w-20 place-items-center rounded-[28px] text-4xl" aria-hidden="true">{{ ui.colorMode === 'day' ? '☀️' : '🌙' }}</span>
              <span class="mt-5 block text-2xl font-black text-white">{{ ui.colorMode === 'day' ? '日间模式' : '夜间模式' }}</span>
              <span class="mt-3 block text-sm leading-6 text-white/58">{{ ui.colorMode === 'day' ? '燎原破晓的黎明' : '赤旗翻转的长夜' }}</span>
            </button>
      </div>

    <GlassCard hover dense class="home-status-card home-card-opacity">
      <div class="home-status-grid">
        <div class="home-status-cell home-status-time">
          <b class="block text-xl">{{ beijingTime }}</b>
        </div>
        <div class="home-status-cell">
          <b class="block text-xl">{{ runtime }}</b>
        </div>
        <div class="home-status-cell">
          <div class="readme-badges" aria-label="技术栈">
            <span><b>Vue</b><em>3</em></span>
            <span><b>Vite</b><em>5</em></span>
            <span><b>FastAPI</b><em>API</em></span>
          </div>
        </div>
        <div class="home-status-cell home-icp-cell">
          <b class="block text-sm">备案号待获取</b>
        </div>
      </div>
    </GlassCard>

    </div>
  </section>
</template>
