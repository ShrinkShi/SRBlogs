<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import { contentApi } from '@/api/content'
import type { PageConfig, ProjectItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { customBlocks, isVisible, layoutBlock, layoutStyle } from '@/utils/pageLayout'

const projects = ref<ProjectItem[]>([])
const loading = ref(false)
const error = ref('')
const pageConfig = ref<PageConfig | null>(null)
const pageTitle = computed(() => pageConfig.value?.pageText?.projects?.title || '项目陈列柜')
const pageSubtitle = computed(() => pageConfig.value?.pageText?.projects?.subtitle || '项目数据来自后端 JSON，可在后台表单化维护。')
const customLayoutBlocks = computed(() => customBlocks(pageConfig.value, 'projects'))
const blockStyle = (id: string) => layoutStyle(layoutBlock(pageConfig.value, 'projects', id))
const showBlock = (id: string) => isVisible(pageConfig.value, 'projects', id)
useSeo({ title: () => pageTitle.value, description: () => pageSubtitle.value, path: '/projects' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [projectData, publicSettings] = await Promise.all([
      contentApi.json<ProjectItem[]>('/projects'),
      contentApi.json<PageConfig>('/pages/config')
    ])
    projects.value = projectData
    pageConfig.value = publicSettings
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '项目加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="page-layout-grid">
    <GlassCard v-if="showBlock('pageTitle')" class="page-title-block text-center" :style="blockStyle('pageTitle')">
      <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/45">projects</p>
      <h1 class="mt-2 text-4xl font-black text-white">{{ pageTitle }}</h1>
      <p class="mt-3 text-white/56">{{ pageSubtitle }}</p>
    </GlassCard>

    <div v-if="showBlock('projectList')" :style="blockStyle('projectList')">
      <GlassCard v-if="loading">
        <p class="text-white/60">项目加载中...</p>
      </GlassCard>
      <GlassCard v-else-if="error">
        <p class="text-red-200/85">{{ error }}</p>
        <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
      </GlassCard>
      <GlassCard v-else-if="!projects.length">
        <p class="text-white/60">暂无项目。</p>
      </GlassCard>

      <div v-else class="grid min-w-0 gap-5 md:grid-cols-2 xl:grid-cols-3">
        <GlassCard v-for="item in projects" :key="item.name" hover>
        <div v-if="item.cover" class="mb-4 h-36 overflow-hidden rounded-[24px] bg-white/10">
          <SafeImage :src="item.cover" :alt="item.name" img-class="h-full w-full object-cover" />
        </div>
        <div class="flex min-w-0 items-start justify-between gap-3">
          <h2 class="min-w-0 break-words text-2xl font-black text-white">{{ item.name }}</h2>
          <span v-if="item.status" class="shrink-0 rounded-full bg-emerald-300/[0.12] px-2 py-1 text-xs text-emerald-100">{{ item.status }}</span>
        </div>
        <p class="mt-3 break-words leading-7 text-white/58">{{ item.description }}</p>
        <div v-if="item.tags?.length" class="mt-4 flex flex-wrap gap-2">
          <span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-3 py-1 text-xs text-white/50">{{ tag }}</span>
        </div>
        <div class="mt-5 flex flex-wrap gap-2">
          <a v-if="item.url" :href="item.url" target="_blank" rel="noopener noreferrer" class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/70 hover:bg-white/[0.15]">查看项目</a>
          <a v-if="item.repo" :href="item.repo" target="_blank" rel="noopener noreferrer" class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/60 hover:bg-white/[0.08]">代码仓库</a>
        </div>
        </GlassCard>
      </div>
    </div>

    <GlassCard v-for="block in customLayoutBlocks" :key="block.id" :style="layoutStyle(block)">
      <p class="text-white/70">{{ block.props?.text || block.label }}</p>
    </GlassCard>
  </section>
</template>
