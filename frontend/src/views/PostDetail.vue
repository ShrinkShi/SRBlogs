<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { contentApi } from '@/api/content'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import GlassCard from '@/components/GlassCard.vue'
import BackButton from '@/components/BackButton.vue'
import ShareButtons from '@/components/ShareButtons.vue'
import CommentBox from '@/components/CommentBox.vue'
import SafeImage from '@/components/SafeImage.vue'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'

const props = withDefaults(defineProps<{ section?: 'posts' | 'moments' | 'chatters' }>(), { section: 'posts' })
const route = useRoute()
const item = ref<ContentItem | null>(null)
const loading = ref(true)
const error = ref('')
const slug = computed(() => String(route.params.slug))
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop'
const coverUrl = computed(() => item.value?.meta.cover || fallbackCover)

useSeo({
  title: () => error.value ? '404 内容不存在' : item.value?.meta.title || '内容加载中',
  description: () => item.value?.meta.summary || item.value?.content?.slice(0, 140) || error.value || 'SRBlogs 内容详情',
  image: () => coverUrl.value,
  type: 'article',
  path: () => `/${props.section}/${slug.value}`
})

async function load(){
  loading.value = true
  error.value = ''
  item.value = null
  try {
    item.value = await contentApi.detail(props.section, slug.value)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '内容不存在或加载失败'
  } finally {
    loading.value = false
  }
}
onMounted(load)
watch(() => route.params.slug, load)
</script>

<template>
  <section class="grid gap-5">
    <BackButton />
    <GlassCard v-if="loading"><p class="text-white/60">文章加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-sm font-bold uppercase tracking-[.3em] text-red-200/70">404 / error</p>
      <h1 class="mt-3 text-3xl font-black text-white">内容无法打开</h1>
      <p class="mt-3 text-white/60">{{ error }}</p>
      <RouterLink to="/posts" class="mt-5 inline-flex rounded-2xl bg-cyan-300 px-4 py-2 font-bold text-slate-950">返回文章列表</RouterLink>
    </GlassCard>
    <GlassCard v-else-if="item" class="overflow-hidden">
      <div class="-mx-5 -mt-5 mb-8 h-[260px] overflow-hidden bg-slate-900/70 md:-mx-6 md:-mt-6 md:h-[360px]">
        <SafeImage :src="coverUrl" :fallback="fallbackCover" :alt="item.meta.title" eager img-class="h-full w-full object-cover opacity-85" />
      </div>
      <div class="rounded-[28px] border border-white/10 bg-white/[0.055] p-5 md:p-7">
        <p class="text-sm font-bold uppercase tracking-[.22em] text-cyan-100/60">{{ item.meta.date }}</p>
        <h1 class="cyber-title mt-3 text-4xl font-black leading-tight md:text-6xl">{{ item.meta.title }}</h1>
        <p v-if="item.meta.summary" class="mt-4 max-w-3xl text-lg leading-8 text-white/64">{{ item.meta.summary }}</p>
        <div class="mt-5 flex flex-wrap gap-2"><span v-for="tag in item.meta.tags" :key="tag" class="sr-chip sr-chip-cyan px-3 py-1 text-xs"># {{ tag }}</span></div>
      </div>
      <div class="mt-10 rounded-[28px] border border-white/10 bg-slate-950/20 p-4 md:p-7"><MarkdownRenderer :content="item.content" /></div>
      <ShareButtons />
    </GlassCard>
    <CommentBox v-if="item" :resource="props.section" :slug="slug" />
  </section>
</template>
