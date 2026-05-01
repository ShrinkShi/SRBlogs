<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { contentApi } from '@/api/content'
import type { FriendItem } from '@/types'
const friends = ref<FriendItem[]>([])
onMounted(async () => { friends.value = await contentApi.json<FriendItem[]>('/friends') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">friends</p>
      <h1 class="mt-2 text-4xl font-black text-white">星际友链</h1>
      <p class="mt-3 text-white/56">保持毛玻璃卡片风格，适合展示朋友站点、项目站点和个人链接。</p>
    </GlassCard>
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <GlassCard v-for="item in friends" :key="item.url" hover>
        <a :href="item.url" target="_blank" class="block">
          <div class="flex items-center gap-4">
            <div class="h-16 w-16 rounded-[24px] border border-white/12 bg-white/10 bg-cover bg-center" :style="{ backgroundImage: item.avatar ? `url(${item.avatar})` : '' }"></div>
            <div class="min-w-0"><h2 class="truncate text-xl font-black text-white">{{ item.name }}</h2><p class="truncate text-sm text-white/45">{{ item.url }}</p></div>
          </div>
          <p class="mt-4 leading-7 text-white/62">{{ item.description }}</p>
        </a>
      </GlassCard>
    </div>
  </section>
</template>
