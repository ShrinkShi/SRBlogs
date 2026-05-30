<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { formatDate } from '@/utils/date'

const items = ref<ContentItem[]>([])
const loading = ref(true)
const error = ref('')

useSeo({ title: '说说', description: 'SRBlogs 的短动态、图片和生活片段。', path: '/moments' })

const publishedItems = computed(() => items.value.filter((item) => !item.meta.draft))

function plainText(item: ContentItem) {
  return (item.content || item.meta.summary || item.meta.title || '')
    .replace(/<[^>]+>/g, '')
    .replace(/[#>*_`~\-[\]()]/g, '')
    .trim()
}

function imagesFor(item: ContentItem) {
  const list = Array.isArray(item.meta.images) ? item.meta.images : []
  const cover = item.meta.cover ? [item.meta.cover] : []
  return Array.from(new Set([...list, ...cover].map(String).map((url) => url.trim()).filter(Boolean))).slice(0, 9)
}

function statNumber(item: ContentItem, key: 'view_count' | 'like_count' | 'comment_count' | 'share_count') {
  const value = Number(item.meta[key] || 0)
  return Number.isFinite(value) ? Math.max(0, value) : 0
}

function imageGridClass(count: number) {
  if (count <= 1) return 'saying-images-one'
  if (count <= 4) return 'saying-images-four'
  return 'saying-images-nine'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await contentApi.list('moments')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '说说加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="sayings-page">
    <GlassCard class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">说说</h1>
    </GlassCard>

    <GlassCard v-if="loading"><p class="text-white/60">说说加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-red-200/85">{{ error }}</p>
      <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!publishedItems.length"><p class="text-white/60">暂无说说。</p></GlassCard>

    <div v-else class="sayings-timeline">
      <article v-for="item in publishedItems" :key="item.slug" class="saying-card">
        <div class="saying-dot" aria-hidden="true"></div>
        <div class="saying-surface">
          <div class="saying-head">
            <div>
              <time>{{ formatDate(item.meta.date) }}</time>
              <p v-if="item.meta.location" class="saying-location">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.1 7-11a7 7 0 1 0-14 0c0 5.9 7 11 7 11Z" /><circle cx="12" cy="10" r="2.5" /></svg>
                {{ item.meta.location }}
              </p>
            </div>
            <RouterLink :to="`/moments/${item.slug}`" class="saying-detail-link">详情</RouterLink>
          </div>

          <p class="saying-content">{{ plainText(item) || '这条说说还没有内容。' }}</p>

          <div v-if="imagesFor(item).length" class="saying-images" :class="imageGridClass(imagesFor(item).length)">
            <SafeImage
              v-for="image in imagesFor(item)"
              :key="image"
              :src="image"
              :alt="item.meta.title || '说说图片'"
              img-class="h-full w-full object-cover"
            />
          </div>

          <div class="saying-stats">
            <span title="浏览"><svg viewBox="0 0 24 24"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="3" /></svg>{{ statNumber(item, 'view_count') }}</span>
            <span title="点赞"><svg viewBox="0 0 24 24"><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3m0 11V10l5-8 1 1a4 4 0 0 1 .8 4.1L13 10h5.6a2 2 0 0 1 2 2.3l-1.4 7.5a2 2 0 0 1-2 1.7H7Z" /></svg>{{ statNumber(item, 'like_count') }}</span>
            <span title="评论"><svg viewBox="0 0 24 24"><path d="M4 5h16v11H8l-4 4V5Z" /></svg>{{ statNumber(item, 'comment_count') }}</span>
            <span title="转发"><svg viewBox="0 0 24 24"><path d="M7 17 17 7M9 7h8v8" /><path d="M5 5h5M5 5v5M19 19h-5M19 19v-5" /></svg>{{ statNumber(item, 'share_count') }}</span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
