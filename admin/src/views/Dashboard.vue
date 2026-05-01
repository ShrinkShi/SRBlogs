<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import type { Stats } from '@/types'
const stats = ref<Stats>({ posts: 0, moments: 0, chatters: 0, photos: 0 })
const quick = [
  ['写新文章', '/editor/posts', '进入沉浸式 Markdown 编辑器'],
  ['管理照片墙', '/photos', '上传与维护图床 URL'],
  ['图床与 AI 设置', '/settings', '配置上传、聊天与部署参数'],
  ['打开前台', '/', '预览博客展示效果']
]
onMounted(async () => { stats.value = await adminApi.stats() })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-sm font-bold uppercase tracking-[.32em] text-cyan-100/45">admin console</p>
      <h1 class="mt-2 text-4xl font-black text-white md:text-5xl">后台仪表盘</h1>
      <p class="mt-3 max-w-3xl leading-7 text-white/56">现在的控制台已经按 XHBlogs 的思路强化：沉浸写作、暂存区提示、图床配置、AI 助手、内容管理入口。底层仍是 Vue3 SPA + FastAPI。</p>
    </GlassCard>
    <div class="grid gap-4 md:grid-cols-4">
      <GlassCard v-for="(v,k) in stats" :key="k"><p class="text-xs uppercase tracking-[.24em] text-white/38">{{ k }}</p><b class="mt-2 block text-4xl text-white">{{ v }}</b><div class="mt-3 h-1 rounded-full bg-white/10"><div class="h-1 rounded-full bg-cyan-300/80" :style="{ width: Math.min(100, Number(v) * 20 + 10) + '%' }"></div></div></GlassCard>
    </div>
    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <RouterLink v-for="item in quick" :key="item[1]" :to="item[1]" class="glass rounded-[28px] p-5 transition hover:-translate-y-1 hover:border-cyan-200/30">
        <div class="relative z-[1]"><h2 class="text-xl font-black text-white">{{ item[0] }}</h2><p class="mt-2 text-sm leading-6 text-white/50">{{ item[2] }}</p></div>
      </RouterLink>
    </div>
    <GlassCard>
      <h2 class="text-2xl font-black text-white">发布流程</h2>
      <div class="mt-4 grid gap-3 md:grid-cols-3">
        <div class="rounded-3xl bg-white/[0.08] p-4"><b class="text-cyan-100">1. 写作/编辑</b><p class="mt-2 text-sm text-white/50">Markdown + Front Matter。</p></div>
        <div class="rounded-3xl bg-white/[0.08] p-4"><b class="text-cyan-100">2. 保存到后端</b><p class="mt-2 text-sm text-white/50">FastAPI 写入 backend/data。</p></div>
        <div class="rounded-3xl bg-white/[0.08] p-4"><b class="text-cyan-100">3. 前台刷新展示</b><p class="mt-2 text-sm text-white/50">Vue 前台通过 API 获取最新内容。</p></div>
      </div>
    </GlassCard>
  </section>
</template>
