<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import FrontJsonItemEditorModal from '@/components/FrontJsonItemEditorModal.vue'
import { contentApi } from '@/api/content'
import type { PageConfig, ProjectItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { tagStyle } from '@/utils/tagStyles'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'

const projects = ref<ProjectItem[]>([])
const session = useSessionStore()
const ui = useUiStore()
const loading = ref(false)
const error = ref('')
const editorOpen = ref(false)
const editingIndex = ref(-1)
const editingProject = ref<ProjectItem | null>(null)
const deleteArmed = ref('')
const pageConfig = ref<PageConfig | null>(null)
const pageTitle = computed(() => pageConfig.value?.pageText?.projects?.title || '项目陈列柜')
const pageSubtitle = computed(() => pageConfig.value?.pageText?.projects?.subtitle || '项目数据来自后端 JSON，可在后台表单化维护。')
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop'
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

function openProjectEditor(item: ProjectItem | null = null, index = -1) {
  editingProject.value = item
  editingIndex.value = index
  editorOpen.value = true
}

async function deleteProject(item: ProjectItem, index: number) {
  const key = item.name || String(index)
  if (deleteArmed.value !== key) {
    deleteArmed.value = key
    ui.showToast('再次点击删除以确认', 'info')
    window.setTimeout(() => {
      if (deleteArmed.value === key) deleteArmed.value = ''
    }, 3000)
    return
  }
  try {
    const next = projects.value.filter((_, itemIndex) => itemIndex !== index)
    await contentApi.adminPutJson('/projects', next)
    ui.showToast('项目已删除', 'success')
    deleteArmed.value = ''
    await load()
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '删除失败', 'error')
  }
}
</script>

<template>
  <section class="page-layout-grid">
    <GlassCard class="page-title-block text-center">
      <h1 class="text-4xl font-black text-white">{{ pageTitle }}</h1>
    </GlassCard>

    <div v-if="session.isAdmin" class="flex justify-end">
      <button type="button" class="frontend-admin-create-btn" @click="openProjectEditor()">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        新增项目
      </button>
    </div>

    <div>
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
        <GlassCard v-for="(item, index) in projects" :key="item.name" hover class="project-card h-full overflow-hidden !p-0">
          <article class="flex h-full min-w-0 flex-col">
            <div class="project-card-cover">
              <SafeImage :src="item.cover" :fallback="fallbackCover" :alt="item.name" img-class="h-full w-full object-cover opacity-90 transition duration-300 hover:scale-[1.035]" />
              <div class="image-contrast-overlay absolute inset-0"></div>
            </div>
            <div class="project-card-body">
              <div class="flex min-w-0 items-start justify-between gap-3">
                <h2 class="min-w-0 break-words text-2xl font-black text-white">{{ item.name }}</h2>
                <span v-if="item.status" class="shrink-0 rounded-full bg-emerald-300/[0.12] px-2 py-1 text-xs text-emerald-100">{{ item.status }}</span>
              </div>
              <p class="mt-3 line-clamp-3 break-words leading-7 text-white/58">{{ item.description }}</p>
              <div v-if="item.tags?.length" class="mt-auto flex flex-wrap gap-2 pt-4">
                <span v-for="tag in item.tags" :key="tag" class="rounded-full border px-3 py-1 text-xs font-bold" :style="tagStyle(tag)">{{ tag }}</span>
              </div>
              <div class="mt-5 flex flex-wrap gap-2">
                <a v-if="item.url" :href="item.url" target="_blank" rel="noopener noreferrer" class="rounded-2xl bg-white/10 px-4 py-2 text-sm text-white/70 hover:bg-white/[0.15]">查看项目</a>
                <a v-if="item.repo" :href="item.repo" target="_blank" rel="noopener noreferrer" class="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/60 hover:bg-white/[0.08]">代码仓库</a>
              </div>
              <div v-if="session.isAdmin" class="front-json-card-actions">
                <button type="button" @click="openProjectEditor(item, index)">编辑</button>
                <button type="button" class="danger" @click="deleteProject(item, index)">{{ deleteArmed === (item.name || String(index)) ? '确认删除' : '删除' }}</button>
              </div>
            </div>
          </article>
        </GlassCard>
      </div>
    </div>
    <FrontJsonItemEditorModal v-model="editorOpen" kind="project" :item="editingProject" :index="editingIndex" @saved="load" />
  </section>
</template>

<style scoped>
.project-card-cover {
  position: relative;
  height: 15rem;
  overflow: hidden;
  background: rgba(15, 23, 42, .72);
}
.project-card-body {
  display: flex;
  min-height: 17rem;
  flex: 1 1 auto;
  flex-direction: column;
  padding: 1.25rem;
}
.front-json-card-actions {
  display: flex;
  justify-content: flex-end;
  gap: .75rem;
  margin-top: 1rem;
}
.front-json-card-actions button {
  color: rgba(255, 255, 255, .68);
  font-weight: 900;
}
.front-json-card-actions button:hover {
  color: white;
}
.front-json-card-actions .danger {
  color: #fecaca;
}
</style>
