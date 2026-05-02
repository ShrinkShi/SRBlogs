<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import SiteDashboard from '@/components/SiteDashboard.vue'
import LatestPostsCarousel from '@/components/LatestPostsCarousel.vue'
import LatestChatterCarousel from '@/components/LatestChatterCarousel.vue'
import MomentTimeline from '@/components/MomentTimeline.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, MusicItem, ProjectItem, SiteSettings, TagItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/date'

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const projects = ref<ProjectItem[]>([])
const music = ref<MusicItem[]>([])
const settings = ref<SiteSettings | null>(null)
const tags = ref<TagItem[]>([])
const currentTrack = ref(0)
const playing = ref(false)
const audio = ref<HTMLAudioElement | null>(null)
const now = ref(new Date())
const ui = useUiStore()
let timer = 0

useSeo({
  title: () => settings.value?.siteTitle || settings.value?.title || '首页',
  description: () => settings.value?.description || settings.value?.bio || 'SRBlogs 首页',
  image: () => settings.value?.avatar || settings.value?.avatarUrl || settings.value?.bgImages?.[0],
  path: '/'
})

const track = computed(() => music.value[currentTrack.value])
const lyricText = computed(() => {
  if (track.value?.lyrics) return track.value.lyrics.split('\n').slice(0, 4).join('\n')
  if (track.value) return `${track.value.title} / ${track.value.artist}\n${playing.value ? '正在播放中' : '点击播放，让音乐成为今天的背景'}`
  return '暂无歌词数据。添加歌曲 URL 或云音乐 ID 后，这里会展示当前歌曲信息。'
})
const beijingTime = computed(() => now.value.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }))
const runtime = computed(() => {
  if (!settings.value?.buildDate) return '待部署后开始计时'
  const start = new Date(settings.value.buildDate).getTime()
  if (Number.isNaN(start)) return '待部署后开始计时'
  const days = Math.max(1, Math.floor((Date.now() - start) / 86400000))
  return `${days} 天`
})
const latestUpdates = computed(() => {
  const mapItem = (type: 'posts' | 'moments' | 'chatters', item: ContentItem) => ({
    type,
    title: item.meta.title,
    date: item.meta.date,
    summary: item.meta.summary || item.content.slice(0, 120),
    url: `/${type}/${item.slug}`
  })
  return [
    ...posts.value.map((item) => mapItem('posts', item)),
    ...moments.value.map((item) => mapItem('moments', item)),
    ...chatters.value.map((item) => mapItem('chatters', item))
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 6)
})

function nextTrack() {
  if (!music.value.length) return
  currentTrack.value = (currentTrack.value + 1) % music.value.length
  playing.value = false
  if (audio.value) {
    audio.value.pause()
    audio.value.load()
  }
}

async function togglePlay() {
  if (!track.value?.url || !audio.value) {
    playing.value = !playing.value
    return
  }
  if (playing.value) {
    audio.value.pause()
    playing.value = false
    return
  }
  await audio.value.play()
  playing.value = true
}

onMounted(async () => {
  const [p, m, c, pr, s, t, mu] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<ProjectItem[]>('/projects'),
    contentApi.json<SiteSettings>('/settings/public'),
    contentApi.tags(),
    contentApi.json<MusicItem[]>('/music')
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (pr.status === 'fulfilled') projects.value = pr.value
  if (s.status === 'fulfilled') settings.value = s.value
  if (t.status === 'fulfilled') tags.value = t.value
  if (mu.status === 'fulfilled') music.value = mu.value
  timer = window.setInterval(() => { now.value = new Date() }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <section class="grid min-w-0 max-w-full gap-6 md:gap-8">
    <div class="home-asymmetric-grid">
      <ProfileCard class="min-w-0 max-w-full" :settings="settings" :posts="posts.length" :moments="moments.length" :projects="projects.length" />

      <GlassCard hover class="min-w-0">
        <div class="flex min-w-0 flex-col gap-5">
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/50">music console</p>
              <h2 class="mt-2 text-2xl font-black text-white">今日播放</h2>
            </div>
            <RouterLink to="/music" class="sr-chip sr-chip-cyan shrink-0 px-3 py-1 text-xs">歌单</RouterLink>
          </div>
          <div v-if="track" class="grid min-w-0 gap-4 sm:grid-cols-[8rem_minmax(0,1fr)]">
            <div class="home-image-zoom h-32 w-32 overflow-hidden rounded-[28px] border border-white/15 bg-white/10">
              <SafeImage v-if="track.cover" :src="track.cover" :alt="track.title" img-class="h-full w-full object-cover" />
              <div v-else class="grid h-full w-full place-items-center text-3xl">♪</div>
            </div>
            <div class="min-w-0">
              <h3 class="break-words text-3xl font-black text-white">{{ track.title }}</h3>
              <p class="mt-1 text-white/58">{{ track.artist }}</p>
              <p class="mt-3 break-all text-xs text-white/38">{{ track.id || track.url || '未配置歌曲 ID 或 URL' }}</p>
              <div class="mt-5 flex flex-wrap gap-2">
                <button type="button" class="sr-button-primary px-5 py-2 text-sm" @click="togglePlay">{{ playing ? '暂停' : '播放' }}</button>
                <button type="button" class="sr-button-ghost px-4 py-2 text-sm" @click="nextTrack">下一首</button>
              </div>
            </div>
            <audio v-if="track.url" ref="audio" :src="track.url" preload="none" @ended="nextTrack"></audio>
          </div>
          <p v-else class="text-white/60">暂无歌单。后台音乐管理添加歌曲后，这里会显示首页播放器。</p>
        </div>
      </GlassCard>
    </div>

    <GlassCard class="sr-hero-panel">
      <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
        <div class="min-w-0">
          <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/50">lyrics</p>
          <h2 class="mt-2 text-2xl font-black text-white">歌词与播放状态</h2>
          <pre class="mt-4 whitespace-pre-wrap break-words font-sans text-lg leading-8 text-white/72">{{ lyricText }}</pre>
        </div>
        <div class="rounded-[28px] border border-white/10 bg-white/[0.08] p-4 text-sm text-white/56">
          <p>当前模式：{{ ui.colorMode === 'day' ? '日间' : '夜间' }}</p>
          <p class="mt-2">播放状态：{{ playing ? '播放中' : '待播放' }}</p>
        </div>
      </div>
    </GlassCard>

    <div class="home-feature-grid">
      <RouterLink v-if="posts[0]" :to="`/posts/${posts[0].slug}`" class="glass sr-card sr-card-hover wide home-image-zoom relative min-w-0 overflow-hidden rounded-[32px]">
        <div class="image-layer h-56 bg-cover bg-center md:h-full" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.08), rgba(0,0,0,.66)), url(${posts[0].meta.cover || settings?.defaultPostCover || ''})` }"></div>
        <div class="absolute inset-x-0 bottom-0 z-[1] p-6">
          <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/65">latest post</p>
          <h2 class="mt-2 line-clamp-2 text-3xl font-black text-white">{{ posts[0].meta.title }}</h2>
          <p class="mt-3 line-clamp-2 text-sm leading-6 text-white/62">{{ posts[0].meta.summary || posts[0].content.slice(0, 100) }}</p>
        </div>
      </RouterLink>

      <GlassCard hover>
        <p class="text-xs font-bold uppercase tracking-[.3em] text-emerald-100/50">latest updates</p>
        <h2 class="mt-2 text-2xl font-black text-white">最新更新内容</h2>
        <div class="mt-4 grid gap-3">
          <RouterLink v-for="item in latestUpdates.slice(0, 3)" :key="item.type + item.url" :to="item.url" class="sr-card-hover rounded-2xl border border-white/10 bg-white/[0.06] p-4">
            <div class="flex items-center justify-between gap-3">
              <span class="sr-chip px-2 py-1 text-[11px]">{{ item.type }}</span>
              <span class="text-xs text-white/42">{{ formatDate(item.date) }}</span>
            </div>
            <h3 class="mt-2 line-clamp-1 font-black text-white">{{ item.title }}</h3>
            <p class="mt-2 line-clamp-2 text-sm leading-6 text-white/56">{{ item.summary }}</p>
          </RouterLink>
        </div>
      </GlassCard>

      <button type="button" class="glass sr-card sr-card-hover min-w-0 rounded-[32px] p-6 text-left" @click="ui.toggleColorMode">
        <div class="relative z-[1] flex items-center justify-between gap-4">
          <div class="min-w-0">
            <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/50">theme mode</p>
            <h2 class="mt-2 text-2xl font-black text-white">{{ ui.colorMode === 'day' ? '日间模式' : '夜间模式' }}</h2>
            <p class="mt-2 text-sm leading-6 text-white/56">点击切换全站昼夜 token，刷新后仍保留当前偏好。</p>
          </div>
          <span class="mode-orb grid h-20 w-20 shrink-0 place-items-center rounded-[28px] text-3xl">{{ ui.colorMode === 'day' ? '☀' : '☾' }}</span>
        </div>
      </button>
    </div>

    <GlassCard>
      <div class="flex min-w-0 flex-wrap items-start justify-between gap-4">
        <div class="min-w-0">
          <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/45">discover</p>
          <h2 class="mt-1 text-2xl font-black text-white">内容发现</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-white/52">搜索、标签和归档都来自 FastAPI 聚合接口，不直接读取本地文件。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <RouterLink to="/search" class="sr-button-primary px-4 py-2 text-sm">搜索</RouterLink>
          <RouterLink to="/tags" class="sr-button-ghost px-4 py-2 text-sm">标签</RouterLink>
          <RouterLink to="/archive" class="sr-button-ghost px-4 py-2 text-sm">归档</RouterLink>
        </div>
      </div>
      <div v-if="tags.length" class="mt-5 flex flex-wrap gap-2">
        <RouterLink v-for="item in tags.slice(0, 10)" :key="item.tag" :to="`/tags/${encodeURIComponent(item.tag)}`" class="sr-chip sr-chip-cyan px-3 py-1 text-xs"># {{ item.tag }} · {{ item.count }}</RouterLink>
      </div>
    </GlassCard>

    <SiteDashboard :settings="settings" :posts="posts.length" :moments="moments.length" :chatters="chatters.length" :projects="projects.length" />
    <LatestPostsCarousel :items="posts.slice(0, 6)" :settings="settings" />
    <LatestChatterCarousel :items="chatters.slice(0, 3)" :title="settings?.chatterTitle" :description="settings?.chatterDescription" />

    <section>
      <div class="mb-4 flex min-w-0 flex-wrap items-end justify-between gap-3">
        <div class="min-w-0"><p class="text-xs font-bold uppercase tracking-[.3em] text-emerald-100/45">moments</p><h2 class="mt-1 text-2xl font-black text-white">最近瞬间</h2></div>
        <RouterLink to="/moments" class="text-sm text-cyan-100/70 hover:text-cyan-100">查看更多</RouterLink>
      </div>
      <MomentTimeline :items="moments.slice(0, 4)" />
    </section>

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
