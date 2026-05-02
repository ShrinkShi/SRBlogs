<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { usePendingStore } from '@/stores/pending'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'
const posts = ref<ContentItem[]>([])
const loading = ref(false)
const error = ref('')
const ui = useUiStore()
const pendingStore = usePendingStore()
const drafts = computed(() => posts.value.filter(i => i.meta.draft))
async function load() {
  error.value = ''
  loading.value = true
  try {
    posts.value = await adminApi.list('posts')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '草稿加载失败'
  } finally {
    loading.value = false
  }
}
async function publish(item: ContentItem) {
  error.value = ''
  try {
    const payload = { ...item, meta: { ...item.meta, draft: false } }
    await adminApi.save('posts', payload, item.slug)
    ui.show('草稿已发布')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '草稿发布失败'
  }
}
function stagePublish(item: ContentItem) {
  pendingStore.add({
    kind: 'publishDraft',
    section: 'posts',
    title: item.meta.title,
    slug: item.slug,
    oldSlug: item.slug,
    payload: { ...item, meta: { ...item.meta, draft: false } }
  })
  ui.show('草稿发布已加入暂存')
}
onMounted(load)
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div><h1 class="text-4xl font-black">草稿箱</h1><p class="mt-2 text-sm text-white/50">draft=true 的文章只在后台可见，发布后才进入前台公开列表。</p></div>
        <button class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">刷新</button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-200/80">{{ error }}</p>
    </GlassCard>
    <GlassCard>
      <p v-if="loading" class="text-white/55">加载中...</p>
      <div v-else class="grid gap-3">
        <div v-for="item in drafts" :key="item.slug" class="rounded-2xl bg-white/5 p-4 hover:bg-white/10">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <RouterLink :to="`/editor/posts/${item.slug}`" class="min-w-0">
              <b class="break-words text-white">{{ item.meta.title }}</b>
              <p class="mt-1 break-all font-mono text-xs text-white/45">{{ item.slug }}</p>
              <p class="mt-1 text-sm text-white/45">{{ item.meta.date || '无日期' }}</p>
            </RouterLink>
            <div class="flex flex-wrap gap-2">
              <RouterLink :to="`/editor/posts/${item.slug}`" class="rounded-xl bg-white/10 px-3 py-2 text-sm">继续编辑</RouterLink>
              <button class="rounded-xl bg-emerald-300/20 px-3 py-2 text-sm text-emerald-100" @click="publish(item)">立即发布</button>
              <button class="rounded-xl border border-emerald-200/20 px-3 py-2 text-sm text-emerald-100" @click="stagePublish(item)">发布暂存</button>
            </div>
          </div>
        </div>
        <p v-if="!drafts.length" class="text-white/50">暂无草稿。</p>
      </div>
    </GlassCard>
  </section>
</template>
