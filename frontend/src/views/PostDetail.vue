<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { contentApi } from '@/api/content'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import GlassCard from '@/components/GlassCard.vue'
import BackButton from '@/components/BackButton.vue'
import ShareButtons from '@/components/ShareButtons.vue'
import CommentBox from '@/components/CommentBox.vue'
import type { ContentItem } from '@/types'

const props = withDefaults(defineProps<{ section?: 'posts' | 'moments' | 'chatters' }>(), { section: 'posts' })
const route = useRoute()
const item = ref<ContentItem | null>(null)
const slug = computed(() => String(route.params.slug))
async function load(){ item.value = await contentApi.detail(props.section, slug.value) }
onMounted(load)
watch(() => route.params.slug, load)
</script>

<template>
  <section class="grid gap-5">
    <BackButton />
    <GlassCard v-if="item" class="overflow-hidden">
      <div v-if="item.meta.cover" class="-mx-5 -mt-5 mb-8 h-[260px] bg-cover bg-center md:-mx-6 md:-mt-6 md:h-[360px]" :style="{ backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,.12), rgba(5,7,19,.86)), url(${item.meta.cover})` }"></div>
      <p class="text-sm text-cyan-100/60">{{ item.meta.date }}</p>
      <h1 class="cyber-title mt-3 text-4xl font-black md:text-6xl">{{ item.meta.title }}</h1>
      <p v-if="item.meta.summary" class="mt-4 max-w-3xl text-lg leading-8 text-white/58">{{ item.meta.summary }}</p>
      <div class="mt-5 flex flex-wrap gap-2"><span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-cyan-200/20 bg-cyan-200/[0.08] px-3 py-1 text-xs text-cyan-100/70"># {{ tag }}</span></div>
      <div class="mt-10"><MarkdownRenderer :content="item.content" /></div>
      <ShareButtons />
    </GlassCard>
    <CommentBox v-if="item" :resource="props.section" :slug="slug" />
  </section>
</template>
