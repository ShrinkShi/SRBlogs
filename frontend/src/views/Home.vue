<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, MusicItem, PhotoAlbum, PhotoItem, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'
import { formatDate } from '@/utils/date'

type UpdateItem = {
  type: 'posts' | 'moments' | 'chatters'
  label: string
  title: string
  date: string
  summary: string
  url: string
}

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const photos = ref<Array<PhotoItem | PhotoAlbum>>([])
const music = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
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
const lyricLine = computed(() => {
  if (remoteLyrics.value) return remoteLyrics.value.split('\n').map((line) => line.replace(/^\[[^\]]+\]/, '').trim()).find(Boolean) || `${track.value?.title} - ${track.value?.artist}`
  if (track.value?.lyrics) return track.value.lyrics.split('\n').map((line) => line.trim()).find(Boolean) || `${track.value.title} - ${track.value.artist}`
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
const recordStyle = computed<Record<string, string>>(() => (
  track.value?.cover ? { '--record-cover': `url(${track.value.cover})` } : {} as Record<string, string>
))
const homeBlocks = computed(() => settings.value?.pageLayouts?.home?.blocks || [])

function homeBlockStyle(id: string) {
  const block = homeBlocks.value.find((item) => item.id === id)
  if (!block) return {}
  return {
    order: Math.round(block.y),
    minHeight: `${Math.max(54, block.h * 4.2)}px`
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

onMounted(async () => {
  const [p, m, c, ph, s, mu] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<Array<PhotoItem | PhotoAlbum>>('/photos'),
    contentApi.json<SiteSettings>('/settings/public'),
    contentApi.json<MusicItem[]>('/music')
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (ph.status === 'fulfilled') photos.value = ph.value
  if (s.status === 'fulfilled') settings.value = s.value
  if (mu.status === 'fulfilled') music.value = mu.value
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
})
</script>

<template>
  <section class="grid min-w-0 max-w-full gap-6 md:gap-8">
    <div class="home-asymmetric-grid">
      <ProfileCard
        class="min-w-0 max-w-full"
        :style="homeBlockStyle('profile')"
        :settings="settings"
        :posts="posts.length"
        :chatters="chatters.length"
        :photos="photoCount || settings?.counts?.photos || 0"
      />

      <GlassCard hover class="music-compact-card min-w-0" :style="homeBlockStyle('music')">
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
              <div class="h-2 overflow-hidden rounded-full border border-white/10 bg-white/10">
                <div class="h-full rounded-full bg-gradient-to-r from-cyan-300 to-fuchsia-300 transition-all duration-300" :style="{ width: progressPercent }"></div>
              </div>
            </div>
          <div class="flex items-center justify-center gap-3">
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
          <div class="volume-control">
            <button type="button" class="icon-button h-9 w-9" :aria-label="player.muted ? 'unmute' : 'mute'" @click="player.toggleMuted()">
              <svg v-if="player.muted || player.volume <= 0" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.8 3 2.6-2.6-1.4-1.4-2.6 2.6-2.6-2.6-1.4 1.4L14 12l-2.6 2.6 1.4 1.4 2.6-2.6 2.6 2.6 1.4-1.4L16.8 12z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zm-2.5-9.2v2.1a7.5 7.5 0 0 1 0 14.2v2.1a9.5 9.5 0 0 0 0-18.4z" /></svg>
            </button>
            <input class="volume-slider" type="range" min="0" max="1" step="0.01" :value="player.muted ? 0 : player.volume" aria-label="volume" @input="setVolumeFromEvent" />
          </div>
          <p v-if="track && !track.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅显示信息。</p>
          </div>
        </div>
      </GlassCard>
    </div>

    <GlassCard hover class="sr-hero-panel lyrics-compact" :style="homeBlockStyle('lyrics')">
      <div class="flex min-h-[38px] flex-col items-center justify-center text-center">
        <p class="max-w-full truncate px-2 font-black leading-tight text-white/78" :style="lyricStyle">{{ lyricLine }}</p>
      </div>
    </GlassCard>

    <div class="home-carousel-layout" :style="homeBlockStyle('carousel')">
      <RouterLink
        v-if="currentPost"
        :to="`/posts/${currentPost.slug}`"
        class="home-media-carousel home-image-zoom home-carousel-tall"
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
      <div v-else class="home-media-carousel home-carousel-tall grid place-items-center text-white/58">暂无公开文章</div>

      <div class="home-carousel-right">
        <RouterLink v-if="currentPhoto" to="/photowall" class="home-media-carousel home-image-zoom">
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
        <div v-else class="home-media-carousel grid place-items-center text-white/58">暂无照片</div>

        <div class="home-carousel-bottom">
          <RouterLink v-if="currentUpdate" :to="currentUpdate.url" class="home-text-carousel sr-card-hover">
            <div>
              <div class="flex items-center justify-between gap-3">
                <span class="sr-chip px-3 py-1 text-xs">{{ currentUpdate.label }}</span>
                <span class="text-xs text-white/45">{{ formatDate(currentUpdate.date) }}</span>
              </div>
              <h2 class="mt-5 line-clamp-2 text-3xl font-black text-white">{{ currentUpdate.title }}</h2>
              <p class="mt-4 line-clamp-3 text-sm leading-7 text-white/60">{{ currentUpdate.summary }}</p>
            </div>
            <div v-if="latestUpdates.length > 1" class="mt-5 flex gap-2">
              <button v-for="(_, index) in latestUpdates" :key="index" type="button" class="carousel-dot" :class="{ 'carousel-dot-active': index === updateIndex }" :aria-label="`切换到第 ${index + 1} 条更新`" @mouseenter="setUpdate(index)" @click.prevent="setUpdate(index)"></button>
            </div>
          </RouterLink>
          <div v-else class="home-text-carousel grid place-items-center text-white/58">暂无更新内容</div>

          <button type="button" class="home-theme-card sr-card-hover" @click="ui.toggleColorMode">
            <span class="mode-orb grid h-20 w-20 place-items-center rounded-[28px] text-3xl">{{ ui.colorMode === 'day' ? '☀' : '☾' }}</span>
            <span class="mt-5 block text-2xl font-black text-white">{{ ui.colorMode === 'day' ? '日间模式' : '夜间模式' }}</span>
            <span class="mt-3 block text-sm leading-6 text-white/58">点击切换全站昼夜主题</span>
          </button>
        </div>
      </div>
    </div>

    <GlassCard hover :style="homeBlockStyle('status')">
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
  </section>
</template>
