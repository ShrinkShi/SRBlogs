<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { usePendingStore } from '@/stores/pending'
import { useUiStore } from '@/stores/ui'
import type { ContentItem } from '@/types'
const props = defineProps<{ section: 'posts' | 'moments' | 'chatters'; title: string }>()
const ui = useUiStore()
const pendingStore = usePendingStore()
const items = ref<ContentItem[]>([])
const filter = ref<'all' | 'published' | 'draft'>('all')
const filterOptions: { value: 'all' | 'published' | 'draft'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'published', label: '已发布' },
  { value: 'draft', label: '草稿' }
]
const loading = ref(false)
const error = ref('')
const filteredItems = computed(() => items.value.filter((item) => {
  if (filter.value === 'published') return !item.meta.draft
  if (filter.value === 'draft') return item.meta.draft
  return true
}))
function publicPath(item: ContentItem) {
  const prefix = props.section === 'chatters' ? 'chatter' : props.section
  return `/${prefix}/${item.slug}`
}
async function load(){
  error.value = ''
  loading.value = true
  try {
    items.value = await adminApi.list(props.section)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '内容列表加载失败'
  } finally {
    loading.value = false
  }
}
async function remove(slug: string){
  if(confirm(`确认立即删除 ${slug}? 删除前后端会生成备份。`)){
    await adminApi.remove(props.section, slug)
    ui.show('已删除')
    await load()
  }
}
function stageDelete(item: ContentItem) {
  if (props.section !== 'posts') {
    error.value = 'pendingOperations 第一阶段只覆盖文章新建、编辑、删除和草稿发布。'
    return
  }
  if (!confirm(`确认将删除 ${item.slug} 加入暂存队列？应用后才会写入后端。`)) return
  pendingStore.add({
    kind: 'deletePost',
    section: props.section,
    title: item.meta.title,
    slug: item.slug
  })
  ui.show('已加入暂存队列')
}
onMounted(load)
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 class="text-4xl font-black text-white">{{ title }}</h1>
          <p class="mt-2 text-sm text-white/50">后台列表包含草稿；前台公开列表默认不显示 draft=true。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">刷新</button>
          <RouterLink :to="`/editor/${section}`" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950">新建</RouterLink>
        </div>
      </div>
      <div class="mt-5 flex flex-wrap gap-2">
        <button v-for="option in filterOptions" :key="option.value" class="rounded-2xl px-4 py-2 text-sm" :class="filter === option.value ? 'bg-white/18 text-white' : 'border border-white/10 text-white/58 hover:bg-white/8'" @click="filter = option.value">{{ option.label }}</button>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-200/80">{{ error }}</p>
    </GlassCard>
    <GlassCard>
      <p v-if="loading" class="text-white/55">加载中...</p>
      <p v-else-if="!filteredItems.length" class="text-white/55">当前筛选下暂无内容。</p>
      <div class="grid gap-3">
        <div v-for="item in filteredItems" :key="item.slug" class="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:flex-row md:items-center md:justify-between">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="break-words font-bold text-white">{{ item.meta.title }}</h2>
              <span v-if="item.meta.draft" class="rounded-full bg-amber-300/20 px-2 py-1 text-xs text-amber-100">草稿</span>
              <span v-else class="rounded-full bg-emerald-300/15 px-2 py-1 text-xs text-emerald-100">已发布</span>
            </div>
            <p class="mt-1 break-all font-mono text-xs text-white/45">{{ item.slug }}</p>
            <p class="mt-1 text-sm text-white/45">{{ item.meta.date || '无日期' }}</p>
            <div v-if="item.meta.tags?.length" class="mt-2 flex flex-wrap gap-2"><span v-for="tag in item.meta.tags" :key="tag" class="rounded-full border border-white/10 px-2 py-1 text-[11px] text-white/50">#{{ tag }}</span></div>
          </div>
          <div class="flex flex-wrap gap-2">
            <RouterLink :to="`/editor/${section}/${item.slug}`" class="rounded-xl bg-white/10 px-3 py-2 text-sm">编辑</RouterLink>
            <a :href="publicPath(item)" target="_blank" class="rounded-xl border border-white/10 px-3 py-2 text-sm text-white/70">前台预览</a>
            <button class="rounded-xl border border-amber-200/20 px-3 py-2 text-sm text-amber-100" @click="stageDelete(item)">暂存删除</button>
            <button class="rounded-xl bg-red-500/20 px-3 py-2 text-sm text-red-100" @click="remove(item.slug)">立即删除</button>
          </div>
        </div>
      </div>
    </GlassCard>
  </section>
</template>
