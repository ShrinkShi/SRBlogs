<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { FriendItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const friends = ref<FriendItem[]>([])
const loading = ref(false)
const error = ref('')
useSeo({ title: '友链', description: 'SRBlogs 的朋友站点和推荐链接。', path: '/friends' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    friends.value = await contentApi.json<FriendItem[]>('/friends')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '友链加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">friends</p>
      <h1 class="mt-2 text-4xl font-black text-white">星际友链</h1>
      <p class="mt-3 text-white/56">朋友站点、项目站点和个人链接会从后端 JSON 动态读取。</p>
    </GlassCard>

    <GlassCard v-if="loading">
      <p class="text-white/60">友链加载中...</p>
    </GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!friends.length">
      <p class="text-white/60">暂无友链。</p>
    </GlassCard>

    <div v-else class="grid min-w-0 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <GlassCard v-for="item in friends" :key="item.url" hover>
        <a :href="item.url" target="_blank" rel="noopener noreferrer" class="block min-w-0">
          <div class="flex min-w-0 items-center gap-4">
            <div class="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-[24px] border border-white/12 bg-white/10">
              <SafeImage v-if="item.avatar" :src="item.avatar" :alt="item.name" img-class="h-full w-full object-cover" />
              <span v-else class="text-xl font-black text-cyan-100">{{ item.name?.slice(0, 1) || '?' }}</span>
            </div>
            <div class="min-w-0">
              <h2 class="truncate text-xl font-black text-white">{{ item.name }}</h2>
              <p class="truncate text-sm text-white/45">{{ item.url }}</p>
            </div>
          </div>
          <p class="mt-4 break-words leading-7 text-white/62">{{ item.description || '这个站点还没有描述。' }}</p>
          <div v-if="item.tags?.length" class="mt-4 flex flex-wrap gap-2">
            <span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-3 py-1 text-xs text-white/50">#{{ tag }}</span>
          </div>
        </a>
      </GlassCard>
    </div>
  </section>
</template>
