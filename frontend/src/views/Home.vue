<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, MusicItem, SiteSettings } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/date'

type UpdateItem = {
  type: 'posts' | 'moments' | 'chatters'
  label: string
  title: string
  date: string
  summary: string
  url: string
}

type ThemeSlide = {
  label: string
  title: string
  summary: string
  action: 'mode' | 'ambience' | 'theme'
}

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const music = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const currentTrack = ref(0)
const postIndex = ref(0)
const updateIndex = ref(0)
const themeIndex = ref(0)
const playing = ref(false)
const duration = ref(0)
const currentTime = ref(0)
const audio = ref<HTMLAudioElement | null>(null)
const now = ref(new Date())
const ui = useUiStore()
let clockTimer = 0
let carouselTimer = 0

useSeo({
  title: () => settings.value?.siteTitle || settings.value?.title || '首页',
  description: () => settings.value?.description || settings.value?.bio || 'SRBlogs 首页',
  image: () => settings.value?.avatar || settings.value?.avatarUrl || settings.value?.bgImages?.[0],
  path: '/'
})

const track = computed(() => music.value[currentTrack.value])
const postSlides = computed(() => posts.value.slice(0, 6))
const currentPost = computed(() => postSlides.value[postIndex.value] || postSlides.value[0])
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
const themeSlides = computed<ThemeSlide[]>(() => [
  {
    label: 'theme mode',
    title: ui.colorMode === 'day' ? '日间模式' : '夜间模式',
    summary: '点击切换全站昼夜 token，阅读、卡片和导航会同步调整。',
    action: 'mode'
  },
  {
    label: 'ambience',
    title: ui.ambience ? '氛围效果开启' : '氛围效果关闭',
    summary: '控制背景气泡、动态层和装饰效果，关闭后仍保留基础毛玻璃质感。',
    action: 'ambience'
  },
  {
    label: 'palette',
    title: `当前主题 ${ui.theme}`,
    summary: '切换预置主题色，用更轻的方式改变页面气质。',
    action: 'theme'
  }
])
const currentThemeSlide = computed(() => themeSlides.value[themeIndex.value])
const lyricText = computed(() => {
  if (track.value?.lyrics) return track.value.lyrics.split('\n').filter(Boolean).slice(0, 4).join('\n')
  if (track.value) return `${track.value.title}\n${track.value.artist}\n${playing.value ? '正在播放' : '点击播放，让音乐进入当前页面'}`
  return '暂无歌词数据\n在后台音乐管理添加歌曲后，这里会显示当前播放信息'
})
const beijingTime = computed(() => now.value.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }))
const runtime = computed(() => {
  if (!settings.value?.buildDate) return '待部署后开始计时'
  const start = new Date(settings.value.buildDate).getTime()
  if (Number.isNaN(start)) return '待部署后开始计时'
  const days = Math.max(1, Math.floor((Date.now() - start) / 86400000))
  return `${days} 天`
})
const progressPercent = computed(() => duration.value ? `${Math.min(100, (currentTime.value / duration.value) * 100)}%` : '0%')
const recordStyle = computed<Record<string, string>>(() => (
  track.value?.cover ? { '--record-cover': `url(${track.value.cover})` } : {} as Record<string, string>
))

function setPost(index: number) {
  if (!postSlides.value.length) return
  postIndex.value = index % postSlides.value.length
}

function setUpdate(index: number) {
  if (!latestUpdates.value.length) return
  updateIndex.value = index % latestUpdates.value.length
}

function setThemeSlide(index: number) {
  themeIndex.value = index % themeSlides.value.length
}

function nextTrack() {
  if (!music.value.length) return
  currentTrack.value = (currentTrack.value + 1) % music.value.length
}

function prevTrack() {
  if (!music.value.length) return
  currentTrack.value = (currentTrack.value - 1 + music.value.length) % music.value.length
}

async function togglePlay() {
  if (!track.value?.url || !audio.value) {
    playing.value = false
    ui.showToast('当前歌曲没有可播放 URL')
    return
  }
  if (playing.value) {
    audio.value.pause()
    playing.value = false
    return
  }
  try {
    await audio.value.play()
    playing.value = true
  } catch {
    playing.value = false
    ui.showToast('播放失败，请检查歌曲 URL')
  }
}

function syncDuration() {
  duration.value = audio.value?.duration && Number.isFinite(audio.value.duration) ? audio.value.duration : 0
}

function syncTime() {
  currentTime.value = audio.value?.currentTime || 0
}

function formatTime(seconds: number) {
  if (!seconds || !Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${mins}:${secs}`
}

function handleThemeAction(action: ThemeSlide['action']) {
  if (action === 'mode') ui.toggleColorMode()
  if (action === 'ambience') ui.toggleAmbience()
  if (action === 'theme') ui.nextTheme()
}

watch(track, async () => {
  playing.value = false
  duration.value = 0
  currentTime.value = 0
  await nextTick()
  audio.value?.load()
})

onMounted(async () => {
  const [p, m, c, s, mu] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<SiteSettings>('/settings/public'),
    contentApi.json<MusicItem[]>('/music')
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (s.status === 'fulfilled') settings.value = s.value
  if (mu.status === 'fulfilled') music.value = mu.value

  clockTimer = window.setInterval(() => { now.value = new Date() }, 1000)
  carouselTimer = window.setInterval(() => {
    setPost(postIndex.value + 1)
    setUpdate(updateIndex.value + 1)
    setThemeSlide(themeIndex.value + 1)
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
        :settings="settings"
        :posts="posts.length"
        :chatters="chatters.length"
        :photos="settings?.counts?.photos || 0"
      />

      <GlassCard class="min-w-0">
        <div class="flex min-w-0 flex-col items-center gap-5 text-center">
          <div class="flex w-full items-start justify-between gap-4">
            <div class="min-w-0 text-left">
              <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/50">music player</p>
              <h2 class="mt-2 text-2xl font-black text-white">今日播放</h2>
            </div>
            <RouterLink to="/music" class="sr-chip sr-chip-cyan shrink-0 px-3 py-1 text-xs">歌单</RouterLink>
          </div>

          <div
            class="record-disc h-44 w-44 rounded-full"
            :class="{ playing }"
            :style="recordStyle"
            aria-hidden="true"
          ></div>

          <div class="min-w-0">
            <h3 class="break-words text-3xl font-black text-white">{{ track?.title || '暂无歌曲' }}</h3>
            <p class="mt-2 text-sm text-white/58">{{ track?.artist || '请在后台音乐管理添加歌曲' }}</p>
          </div>

          <div class="w-full max-w-md">
            <div class="mb-2 flex items-center justify-between text-xs text-white/48">
              <span>{{ formatTime(currentTime) }}</span>
              <span>{{ formatTime(duration) }}</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full border border-white/10 bg-white/10">
              <div class="h-full rounded-full bg-gradient-to-r from-cyan-300 to-fuchsia-300 transition-all duration-300" :style="{ width: progressPercent }"></div>
            </div>
          </div>

          <div class="flex items-center justify-center gap-3">
            <button type="button" class="icon-button" aria-label="上一首" @click="prevTrack">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 6h2v12H7zM18 6v12l-8.5-6z" /></svg>
            </button>
            <button type="button" class="icon-button icon-button-main" :aria-label="playing ? '暂停' : '播放'" @click="togglePlay">
              <svg v-if="playing" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" /></svg>
            </button>
            <button type="button" class="icon-button" aria-label="下一首" @click="nextTrack">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6h2v12h-2zM6 6l8.5 6L6 18z" /></svg>
            </button>
          </div>

          <p v-if="track && !track.url" class="text-xs text-amber-100/70">当前歌曲没有 URL，仅显示信息。</p>
          <audio
            v-if="track?.url"
            ref="audio"
            :src="track.url"
            preload="metadata"
            @loadedmetadata="syncDuration"
            @timeupdate="syncTime"
            @ended="nextTrack"
          ></audio>
        </div>
      </GlassCard>
    </div>

    <GlassCard class="sr-hero-panel min-h-[220px]">
      <div class="flex min-h-[172px] flex-col items-center justify-center text-center">
        <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/50">lyrics</p>
        <h2 class="mt-2 text-2xl font-black text-white">歌词与播放状态</h2>
        <pre class="mt-5 max-w-3xl whitespace-pre-wrap break-words text-center font-sans text-lg leading-8 text-white/72">{{ lyricText }}</pre>
      </div>
    </GlassCard>

    <div class="home-feature-grid">
      <GlassCard dense class="home-carousel-card min-w-0">
        <div class="flex h-full min-w-0 flex-col">
          <div class="flex items-center justify-between gap-3 p-1">
            <div>
              <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/55">latest posts</p>
              <h2 class="mt-1 text-xl font-black text-white">最新文章轮播</h2>
            </div>
            <RouterLink to="/posts" class="sr-chip sr-chip-cyan shrink-0 px-3 py-1 text-xs">全部</RouterLink>
          </div>
          <RouterLink
            v-if="currentPost"
            :to="`/posts/${currentPost.slug}`"
            class="home-carousel-slide home-image-zoom relative mt-4 min-h-[18rem] min-w-0 flex-1 overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.06]"
          >
            <div class="image-layer absolute inset-0 bg-cover bg-center" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.06), rgba(0,0,0,.7)), url(${currentPost.meta.cover || settings?.defaultPostCover || ''})` }"></div>
            <div class="absolute inset-x-0 bottom-0 z-[1] p-5">
              <span class="sr-chip px-3 py-1 text-xs">{{ formatDate(currentPost.meta.date) }}</span>
              <h3 class="mt-3 line-clamp-2 text-2xl font-black text-white">{{ currentPost.meta.title }}</h3>
              <p class="mt-3 line-clamp-2 text-sm leading-6 text-white/64">{{ currentPost.meta.summary || currentPost.content.slice(0, 110) }}</p>
            </div>
          </RouterLink>
          <div v-else class="mt-4 grid min-h-[18rem] place-items-center rounded-[28px] border border-white/10 bg-white/[0.05] text-white/52">暂无公开文章</div>
          <div v-if="postSlides.length > 1" class="mt-4 flex justify-center gap-2">
            <button
              v-for="(_, index) in postSlides"
              :key="index"
              type="button"
              class="carousel-dot"
              :class="{ 'carousel-dot-active': index === postIndex }"
              :aria-label="`切换到第 ${index + 1} 篇文章`"
              @click="setPost(index)"
            ></button>
          </div>
        </div>
      </GlassCard>

      <GlassCard hover class="home-carousel-card min-w-0">
        <div class="flex h-full min-w-0 flex-col">
          <p class="text-xs font-bold uppercase tracking-[.28em] text-emerald-100/55">latest updates</p>
          <h2 class="mt-1 text-xl font-black text-white">最新更新内容</h2>
          <RouterLink
            v-if="currentUpdate"
            :to="currentUpdate.url"
            class="home-carousel-slide mt-5 flex min-h-[16rem] flex-1 flex-col justify-between rounded-[28px] border border-white/10 bg-white/[0.055] p-5"
          >
            <div>
              <div class="flex items-center justify-between gap-3">
                <span class="sr-chip px-3 py-1 text-xs">{{ currentUpdate.label }}</span>
                <span class="text-xs text-white/45">{{ formatDate(currentUpdate.date) }}</span>
              </div>
              <h3 class="mt-5 line-clamp-2 text-3xl font-black text-white">{{ currentUpdate.title }}</h3>
              <p class="mt-4 line-clamp-4 text-sm leading-7 text-white/60">{{ currentUpdate.summary }}</p>
            </div>
            <span class="mt-5 text-sm font-bold text-cyan-100/75">查看内容</span>
          </RouterLink>
          <div v-else class="mt-5 grid min-h-[16rem] flex-1 place-items-center rounded-[28px] border border-white/10 bg-white/[0.05] text-white/52">暂无更新内容</div>
          <div v-if="latestUpdates.length > 1" class="mt-4 flex justify-center gap-2">
            <button
              v-for="(_, index) in latestUpdates.slice(0, 6)"
              :key="index"
              type="button"
              class="carousel-dot"
              :class="{ 'carousel-dot-active': index === updateIndex }"
              :aria-label="`切换到第 ${index + 1} 条更新`"
              @click="setUpdate(index)"
            ></button>
          </div>
        </div>
      </GlassCard>

      <GlassCard hover class="home-carousel-card min-w-0">
        <button type="button" class="flex h-full w-full min-w-0 flex-col justify-between text-left" @click="handleThemeAction(currentThemeSlide.action)">
          <div>
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <p class="text-xs font-bold uppercase tracking-[.28em] text-fuchsia-100/55">{{ currentThemeSlide.label }}</p>
                <h2 class="mt-2 text-2xl font-black text-white">{{ currentThemeSlide.title }}</h2>
              </div>
              <span class="mode-orb grid h-20 w-20 shrink-0 place-items-center rounded-[28px] text-3xl">{{ ui.colorMode === 'day' ? '☀' : '☾' }}</span>
            </div>
            <p class="mt-6 text-sm leading-7 text-white/60">{{ currentThemeSlide.summary }}</p>
          </div>
          <div>
            <span class="sr-button-primary mt-8 px-5 py-2 text-sm">立即切换</span>
            <div class="mt-5 flex justify-center gap-2">
              <span
                v-for="(_, index) in themeSlides"
                :key="index"
                class="carousel-dot"
                :class="{ 'carousel-dot-active': index === themeIndex }"
              ></span>
            </div>
          </div>
        </button>
      </GlassCard>
    </div>

    <GlassCard>
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
