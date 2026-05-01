<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import ManageBase from './ManageBase.vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import type { ContentItem } from '@/types'
const posts = ref<ContentItem[]>([])
const drafts = computed(() => posts.value.filter(i => i.meta.draft))
onMounted(async()=>{ posts.value = await adminApi.list('posts') })
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><h1 class="text-4xl font-black">草稿箱</h1></GlassCard>
    <GlassCard><div class="grid gap-3"><RouterLink v-for="item in drafts" :key="item.slug" :to="`/editor/posts/${item.slug}`" class="rounded-2xl bg-white/5 p-4 hover:bg-white/10"><b>{{ item.meta.title }}</b><p class="text-sm text-white/45">{{ item.slug }}</p></RouterLink><p v-if="!drafts.length" class="text-white/50">暂无草稿。</p></div></GlassCard>
  </section>
</template>
