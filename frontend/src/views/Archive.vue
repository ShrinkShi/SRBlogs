<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import StateBlock from '@/components/StateBlock.vue'
import { contentApi } from '@/api/content'
import type { ArchiveResponse } from '@/types'
import { useSeo } from '@/composables/useSeo'

const archive = ref<ArchiveResponse>({ years: [] })
const loading = ref(true)
const error = ref('')
const typeLabels: Record<string, string> = { posts: '文章', moments: '瞬间', chatters: '杂谈' }
useSeo({ title: '内容归档', description: '按年份和月份浏览 SRBlogs 的公开文章、瞬间和杂谈。', path: '/archive' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    archive.value = await contentApi.archive()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '归档加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard class="page-title-block text-center">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">archive</p>
      <h1 class="mt-2 text-4xl font-black text-white">内容归档</h1>
      <p class="mt-3 text-white/56">按年月聚合公开文章、瞬间和杂谈。</p>
    </GlassCard>
    <StateBlock v-if="loading" message="归档加载中..." />
    <StateBlock v-else-if="error" title="归档加载失败" :message="error" @retry="load" />
    <GlassCard v-else-if="!archive.years.length"><p class="text-white/60">暂无归档内容。</p></GlassCard>
    <div v-else class="grid gap-5">
      <GlassCard v-for="year in archive.years" :key="year.year">
        <h2 class="text-3xl font-black text-white">{{ year.year }}</h2>
        <div class="mt-5 grid gap-5">
          <section v-for="month in year.months" :key="`${year.year}-${month.month}`" class="min-w-0">
            <h3 class="mb-3 text-lg font-black text-cyan-100">{{ month.month }} 月</h3>
            <div class="grid gap-3">
              <RouterLink v-for="item in month.items" :key="`${item.type}-${item.slug}`" :to="item.url" class="min-w-0 rounded-2xl border border-white/10 bg-white/[0.06] p-4 hover:bg-white/[0.1]">
                <div class="flex min-w-0 flex-wrap items-center gap-2 text-xs text-white/42">
                  <span class="rounded-full bg-cyan-200/[0.12] px-2 py-1 text-cyan-100">{{ typeLabels[item.type] || item.type }}</span>
                  <span>{{ item.date }}</span>
                </div>
                <h4 class="mt-2 break-words text-xl font-black text-white">{{ item.title }}</h4>
                <div v-if="item.tags?.length" class="mt-3 flex flex-wrap gap-2">
                  <span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-2 py-1 text-xs text-white/45"># {{ tag }}</span>
                </div>
              </RouterLink>
            </div>
          </section>
        </div>
      </GlassCard>
    </div>
  </section>
</template>
