<script setup lang="ts">
import GlassCard from '@/components/GlassCard.vue'
</script>

<template>
  <section>
    <GlassCard>
      <p class="text-sm font-bold uppercase tracking-[.3em] text-red-200/70">404 / not found</p>
      <h1 class="mt-3 text-4xl font-black text-white">页面不存在</h1>
      <p class="mt-3 max-w-2xl text-white/60">这个地址没有匹配到前台页面。请返回首页或文章列表继续浏览。</p>
      <div class="mt-6 flex flex-wrap gap-3">
        <RouterLink to="/" class="rounded-2xl bg-cyan-300 px-4 py-2 font-bold text-slate-950">返回首页</RouterLink>
        <RouterLink to="/posts" class="rounded-2xl border border-white/10 px-4 py-2 text-white/70">文章列表</RouterLink>
      </div>
    </GlassCard>
  </section>
</template>
