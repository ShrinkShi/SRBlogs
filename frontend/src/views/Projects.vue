<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { ProjectItem } from '@/types'
const projects = ref<ProjectItem[]>([])
onMounted(async () => { projects.value = await contentApi.json<ProjectItem[]>('/projects') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">projects</p>
      <h1 class="mt-2 text-4xl font-black text-white">项目陈列柜</h1>
    </GlassCard>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <GlassCard v-for="item in projects" :key="item.name" hover>
        <div v-if="item.cover" class="mb-4 h-36 rounded-[24px] bg-cover bg-center" :style="{ backgroundImage: `url(${item.cover})` }"></div>
        <div class="flex items-start justify-between gap-3"><h2 class="text-2xl font-black text-white">{{ item.name }}</h2><span v-if="item.status" class="rounded-full bg-emerald-300/[0.12] px-2 py-1 text-xs text-emerald-100">{{ item.status }}</span></div>
        <p class="mt-3 leading-7 text-white/58">{{ item.description }}</p>
        <div class="mt-4 flex flex-wrap gap-2"><span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-3 py-1 text-xs text-white/50">{{ tag }}</span></div>
        <a v-if="item.url" :href="item.url" target="_blank" class="mt-5 inline-block rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/70 hover:bg-white/[0.15]">查看项目</a>
      </GlassCard>
    </div>
  </section>
</template>
