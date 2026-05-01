<script setup lang="ts">
import { onMounted, ref } from 'vue'
import MomentTimeline from '@/components/MomentTimeline.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
const items = ref<ContentItem[]>([])
onMounted(async () => { items.value = await contentApi.list('moments') })
</script>
<template>
  <section>
    <h1 class="mb-6 text-4xl font-black text-white">时间线</h1>
    <MomentTimeline :items="items" />
  </section>
</template>
