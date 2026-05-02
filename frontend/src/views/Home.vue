<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import SiteDashboard from '@/components/SiteDashboard.vue'
import LatestPostsCarousel from '@/components/LatestPostsCarousel.vue'
import LatestChatterCarousel from '@/components/LatestChatterCarousel.vue'
import MomentTimeline from '@/components/MomentTimeline.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, ProjectItem, SiteSettings, TagItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const projects = ref<ProjectItem[]>([])
const settings = ref<SiteSettings | null>(null)
const tags = ref<TagItem[]>([])

useSeo({
  title: () => settings.value?.siteTitle || settings.value?.title || '首页',
  description: () => settings.value?.description || settings.value?.bio || 'SRBlogs 首页',
  image: () => settings.value?.avatar || settings.value?.avatarUrl || settings.value?.bgImages?.[0],
  path: '/'
})

onMounted(async () => {
  const [p, m, c, pr, s, t] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<ProjectItem[]>('/projects'),
    contentApi.json<SiteSettings>('/settings/public'),
    contentApi.tags()
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (pr.status === 'fulfilled') projects.value = pr.value
  if (s.status === 'fulfilled') settings.value = s.value
  if (t.status === 'fulfilled') tags.value = t.value
})
</script>

<template>
  <section class="grid min-w-0 max-w-full gap-6 md:gap-8">
    <div class="home-hero-grid">
      <GlassCard class="min-w-0">
        <p class="text-sm font-bold uppercase tracking-[0.34em] text-cyan-200/70">Glassmorphism Blog System</p>
        <h1 class="cyber-title mt-5 break-words text-5xl font-black leading-tight md:text-7xl">{{ settings?.siteTitle || settings?.title || 'SRBlogs' }}</h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/68">仿照 XHBlogs 的视觉方向做出的 Vue3 + FastAPI 版本：毛玻璃、动态背景、个人资料卡、音乐挂件、照片墙、时间线、文章系统和独立管理控制台。技术栈没有迁移到 Next.js。</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink to="/posts" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 shadow-[0_0_34px_rgba(34,211,238,.22)]">进入文章宇宙</RouterLink>
          <RouterLink to="/search" class="rounded-2xl border border-white/15 px-5 py-3 text-white/80 hover:bg-white/10">搜索全站</RouterLink>
          <RouterLink to="/archive" class="rounded-2xl border border-white/15 px-5 py-3 text-white/80 hover:bg-white/10">查看归档</RouterLink>
          <RouterLink to="/music" class="rounded-2xl border border-fuchsia-200/20 px-5 py-3 text-fuchsia-100/80 hover:bg-fuchsia-200/10">云音乐挂件</RouterLink>
        </div>
        <div class="mt-8 grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div class="min-w-0 rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">frontend</p><b class="mt-2 block break-words text-white">Vue3 SPA</b></div>
          <div class="min-w-0 rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">backend</p><b class="mt-2 block break-words text-white">FastAPI API</b></div>
          <div class="min-w-0 rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">content</p><b class="mt-2 block break-words text-white">Markdown + JSON</b></div>
        </div>
      </GlassCard>
      <ProfileCard class="min-w-0 max-w-full" :settings="settings" :posts="posts.length" :moments="moments.length" :projects="projects.length" />
    </div>

    <SiteDashboard :settings="settings" :posts="posts.length" :moments="moments.length" :chatters="chatters.length" :projects="projects.length" />

    <GlassCard>
      <div class="flex min-w-0 flex-wrap items-start justify-between gap-4">
        <div class="min-w-0">
          <p class="text-xs font-bold uppercase tracking-[.3em] text-cyan-100/45">discover</p>
          <h2 class="mt-1 text-2xl font-black text-white">内容发现</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-white/52">搜索、标签和归档都来自 FastAPI 聚合接口，不直接读取本地文件。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <RouterLink to="/search" class="rounded-2xl bg-cyan-300 px-4 py-2 text-sm font-bold text-slate-950">搜索</RouterLink>
          <RouterLink to="/tags" class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70">标签</RouterLink>
          <RouterLink to="/archive" class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70">归档</RouterLink>
        </div>
      </div>
      <div v-if="tags.length" class="mt-5 flex flex-wrap gap-2">
        <RouterLink v-for="item in tags.slice(0, 10)" :key="item.tag" :to="`/tags/${encodeURIComponent(item.tag)}`" class="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs text-white/60 hover:bg-white/10"># {{ item.tag }} · {{ item.count }}</RouterLink>
      </div>
      <div class="mt-5 grid gap-3 md:grid-cols-3">
        <RouterLink v-for="item in posts.slice(0, 3)" :key="item.slug" :to="`/posts/${item.slug}`" class="min-w-0 rounded-2xl border border-white/10 bg-white/[0.06] p-4 hover:bg-white/[0.1]">
          <p class="text-xs text-white/38">{{ item.meta.date }}</p>
          <b class="mt-2 block truncate text-white">{{ item.meta.title }}</b>
        </RouterLink>
      </div>
    </GlassCard>

    <LatestPostsCarousel :items="posts.slice(0, 6)" :settings="settings" />
    <LatestChatterCarousel :items="chatters.slice(0, 3)" :title="settings?.chatterTitle" :description="settings?.chatterDescription" />

    <section>
      <div class="mb-4 flex min-w-0 flex-wrap items-end justify-between gap-3">
        <div class="min-w-0"><p class="text-xs font-bold uppercase tracking-[.3em] text-emerald-100/45">moments</p><h2 class="mt-1 text-2xl font-black text-white">最近瞬间</h2></div>
        <RouterLink to="/moments" class="text-sm text-cyan-100/70 hover:text-cyan-100">查看更多</RouterLink>
      </div>
      <MomentTimeline :items="moments.slice(0, 4)" />
    </section>
  </section>
</template>
