<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { contentApi } from '@/api/content'
const content = ref('')
onMounted(async () => { content.value = (await contentApi.about()).content })
</script>
<template>
  <section>
    <GlassCard>
      <MarkdownRenderer :content="content" />
    </GlassCard>
  </section>
</template>
