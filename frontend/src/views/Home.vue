<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import SiteDashboard from '@/components/SiteDashboard.vue'
import LatestPostsCarousel from '@/components/LatestPostsCarousel.vue'
import LatestChatterCarousel from '@/components/LatestChatterCarousel.vue'
import MomentTimeline from '@/components/MomentTimeline.vue'
import { contentApi } from '@/api/content'
import type { ContentItem, ProjectItem, SiteSettings } from '@/types'

const posts = ref<ContentItem[]>([])
const moments = ref<ContentItem[]>([])
const chatters = ref<ContentItem[]>([])
const projects = ref<ProjectItem[]>([])
const settings = ref<SiteSettings | null>(null)

onMounted(async () => {
  const [p, m, c, pr, s] = await Promise.allSettled([
    contentApi.list('posts'),
    contentApi.list('moments'),
    contentApi.list('chatters'),
    contentApi.json<ProjectItem[]>('/projects'),
    contentApi.json<SiteSettings>('/settings')
  ])
  if (p.status === 'fulfilled') posts.value = p.value
  if (m.status === 'fulfilled') moments.value = m.value
  if (c.status === 'fulfilled') chatters.value = c.value
  if (pr.status === 'fulfilled') projects.value = pr.value
  if (s.status === 'fulfilled') settings.value = s.value
})
</script>

<template>
  <section class="grid gap-8">
    <div class="grid gap-6 lg:grid-cols-[1.45fr_.55fr] lg:items-stretch">
      <GlassCard>
        <p class="text-sm font-bold uppercase tracking-[0.34em] text-cyan-200/70">Glassmorphism Blog System</p>
        <h1 class="cyber-title mt-5 text-5xl font-black leading-tight md:text-7xl">{{ settings?.title || 'SRBlogs' }}</h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-white/68">仿照 XHBlogs 的视觉方向做出的 Vue3 + FastAPI 版本：毛玻璃、动态背景、个人资料卡、音乐挂件、照片墙、时间线、文章系统和独立管理控制台。技术栈没有迁移到 Next.js。</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink to="/posts" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 shadow-[0_0_34px_rgba(34,211,238,.22)]">进入文章宇宙</RouterLink>
          <RouterLink to="/timeline" class="rounded-2xl border border-white/15 px-5 py-3 text-white/80 hover:bg-white/10">查看时间线</RouterLink>
          <RouterLink to="/music" class="rounded-2xl border border-fuchsia-200/20 px-5 py-3 text-fuchsia-100/80 hover:bg-fuchsia-200/10">云音乐挂件</RouterLink>
        </div>
        <div class="mt-8 grid gap-3 md:grid-cols-3">
          <div class="rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">frontend</p><b class="mt-2 block text-white">Vue3 SPA</b></div>
          <div class="rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">backend</p><b class="mt-2 block text-white">FastAPI API</b></div>
          <div class="rounded-3xl border border-white/10 bg-white/[0.08] p-4"><p class="text-xs uppercase tracking-[.24em] text-white/38">content</p><b class="mt-2 block text-white">Markdown + JSON</b></div>
        </div>
      </GlassCard>
      <ProfileCard :settings="settings" :posts="posts.length" :moments="moments.length" :projects="projects.length" />
    </div>

    <SiteDashboard :settings="settings" :posts="posts.length" :moments="moments.length" :chatters="chatters.length" :projects="projects.length" />
    <LatestPostsCarousel :items="posts.slice(0, 6)" :settings="settings" />
    <LatestChatterCarousel :items="chatters.slice(0, 3)" :title="settings?.chatterTitle" :description="settings?.chatterDescription" />

    <section>
      <div class="mb-4 flex items-end justify-between gap-3">
        <div><p class="text-xs font-bold uppercase tracking-[.3em] text-emerald-100/45">moments</p><h2 class="mt-1 text-2xl font-black text-white">最近瞬间</h2></div>
        <RouterLink to="/moments" class="text-sm text-cyan-100/70 hover:text-cyan-100">查看更多</RouterLink>
      </div>
      <MomentTimeline :items="moments.slice(0, 4)" />
    </section>
  </section>
</template>
