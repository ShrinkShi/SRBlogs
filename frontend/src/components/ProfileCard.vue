<script setup lang="ts">
import GlassCard from '@/components/GlassCard.vue'
import type { SiteSettings } from '@/types'
const props = defineProps<{ settings?: SiteSettings | null; posts?: number; moments?: number; projects?: number }>()
const socialKeys = ['github', 'gitee', 'email', 'qq', 'wechat']
</script>
<template>
  <GlassCard class="min-h-full min-w-0 max-w-full">
    <div class="flex min-w-0 flex-col items-center text-center">
      <div class="relative">
        <div class="absolute inset-0 rounded-[34px] bg-cyan-300/30 blur-2xl"></div>
        <img v-if="props.settings?.avatarUrl" :src="props.settings.avatarUrl" class="relative h-28 w-28 rounded-[34px] border border-white/20 object-cover shadow-2xl" />
        <div v-else class="relative grid h-28 w-28 place-items-center rounded-[34px] border border-white/20 bg-white/[0.12] text-4xl font-black text-white">SR</div>
      </div>
      <h2 class="mt-5 text-2xl font-black text-white">{{ props.settings?.authorName || 'SRBlogs' }}</h2>
      <p class="mt-2 max-w-sm break-words text-sm leading-7 text-white/62">{{ props.settings?.bio || '在代码、文字与生活碎片之间，搭建一座轻量而漂亮的个人博客。' }}</p>
      <div class="mt-5 grid w-full min-w-0 max-w-full grid-cols-[repeat(auto-fit,minmax(min(100%,5.5rem),1fr))] gap-2">
        <div class="min-w-0 rounded-2xl bg-white/[0.08] p-3"><b class="block break-words text-2xl text-white">{{ props.posts || 0 }}</b><span class="text-xs text-white/42">文章</span></div>
        <div class="min-w-0 rounded-2xl bg-white/[0.08] p-3"><b class="block break-words text-2xl text-white">{{ props.moments || 0 }}</b><span class="text-xs text-white/42">瞬间</span></div>
        <div class="min-w-0 rounded-2xl bg-white/[0.08] p-3"><b class="block break-words text-2xl text-white">{{ props.projects || 0 }}</b><span class="text-xs text-white/42">项目</span></div>
      </div>
      <div v-if="props.settings?.social" class="mt-5 flex max-w-full flex-wrap justify-center gap-2">
        <a v-for="key in socialKeys" :key="key" v-show="props.settings?.social?.[key]" :href="key === 'email' ? `mailto:${props.settings?.social?.[key]}` : props.settings?.social?.[key]" target="_blank" class="rounded-full border border-white/12 bg-white/[0.08] px-3 py-1 text-xs text-white/60 hover:bg-white/[0.14] hover:text-white">{{ key }}</a>
      </div>
    </div>
  </GlassCard>
</template>
