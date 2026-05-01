<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PostList from '@/components/PostList.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
const items = ref<ContentItem[]>([])
onMounted(async () => { items.value = await contentApi.list('chatters') })
</script>
<template>
  <section>
    <h1 class="mb-6 text-4xl font-black text-white">碎碎念</h1>
    <PostList :items="items" base="/chatter" />
  </section>
</template>
