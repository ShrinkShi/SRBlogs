<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { contentApi } from '@/api/content'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import GlassCard from '@/components/GlassCard.vue'
import CommentBox from '@/components/CommentBox.vue'
import SafeImage from '@/components/SafeImage.vue'
import FrontContentEditorModal from '@/components/FrontContentEditorModal.vue'
import SrTextButton from '@/components/ui/SrTextButton.vue'
import type { ContentItem } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'

const props = withDefaults(defineProps<{ section?: 'posts' | 'moments' | 'chatters' }>(), { section: 'posts' })
const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const ui = useUiStore()
const item = ref<ContentItem | null>(null)
const loading = ref(true)
const error = ref('')
const deleting = ref(false)
const deleteArmed = ref(false)
const editorOpen = ref(false)
const slug = computed(() => String(route.params.slug))
const fallbackCover = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop'
const coverUrl = computed(() => item.value?.meta.cover || fallbackCover)
const listRoute = computed(() => `/${props.section}`)

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

function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push(listRoute.value)
}

async function copyLink() {
  const url = window.location.href
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(url)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = url
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    ui.showToast('链接已复制', 'success')
  } catch {
    ui.showToast('复制失败，请手动复制地址栏链接', 'error')
  }
}

function openAdminEditor() {
  editorOpen.value = true
}

async function deleteCurrentContent() {
  if (!item.value || deleting.value) return
  if (!deleteArmed.value) {
    deleteArmed.value = true
    ui.showToast('再次点击删除以确认', 'info')
    window.setTimeout(() => {
      deleteArmed.value = false
    }, 3200)
    return
  }
  deleting.value = true
  try {
    await contentApi.deleteContent(props.section, slug.value)
    ui.showToast('已删除', 'success')
    router.push(listRoute.value)
  } catch {
    ui.showToast('删除失败，请重试', 'error')
  } finally {
    deleting.value = false
    deleteArmed.value = false
  }
}
</script>

<template>
  <section class="grid gap-5">
    <GlassCard v-if="loading"><p class="text-white/60">文章加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="text-sm font-bold uppercase tracking-[.3em] text-red-200/70">404 / error</p>
      <h1 class="mt-3 text-3xl font-black text-white">内容无法打开</h1>
      <p class="mt-3 text-white/60">{{ error }}</p>
      <RouterLink :to="listRoute" class="mt-5 inline-flex rounded-2xl bg-cyan-300 px-4 py-2 font-bold text-slate-950">返回列表</RouterLink>
    </GlassCard>
    <GlassCard v-else-if="item" class="detail-shell overflow-hidden">
      <div class="detail-cover">
        <SafeImage :src="coverUrl" :fallback="fallbackCover" :alt="item.meta.title" eager img-class="h-full w-full object-cover opacity-88" />
      </div>
      <div class="detail-cover-actions">
        <button type="button" class="detail-icon-button" aria-label="返回上一页" title="返回上一页" @click="goBack">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18 9 12l6-6" /><path d="M9 12h12" /></svg>
        </button>
      </div>
      <article class="detail-article">
        <p class="text-sm font-bold uppercase tracking-[.22em] text-cyan-100/60">{{ item.meta.date }}</p>
        <h1 class="cyber-title mt-3 text-4xl font-black leading-tight md:text-6xl">{{ item.meta.title }}</h1>
        <p v-if="item.meta.summary" class="mt-4 max-w-3xl text-lg leading-8 text-white/64">{{ item.meta.summary }}</p>
        <div v-if="item.meta.tags?.length" class="mt-5 flex flex-wrap gap-2">
          <span v-for="tag in item.meta.tags" :key="tag" class="sr-chip sr-chip-cyan px-3 py-1 text-xs"># {{ tag }}</span>
        </div>
        <div class="detail-body"><MarkdownRenderer :content="item.content" /></div>
        <div class="detail-action-row">
          <template v-if="session.isAdmin">
            <SrTextButton @click="openAdminEditor">编辑</SrTextButton>
            <SrTextButton tone="danger" :disabled="deleting" @click="deleteCurrentContent">
              {{ deleting ? '删除中' : deleteArmed ? '确认删除' : '删除' }}
            </SrTextButton>
          </template>
          <button type="button" class="detail-icon-button" aria-label="复制链接" title="复制链接" @click="copyLink">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.1.1l2-2a5 5 0 0 0-7.1-7.1l-1.2 1.2" /><path d="M14 11a5 5 0 0 0-7.1-.1l-2 2a5 5 0 0 0 7.1 7.1l1.2-1.2" /></svg>
          </button>
        </div>
      </article>
      <CommentBox class="detail-comments" :resource="props.section" :slug="slug" frameless />
      <FrontContentEditorModal v-model="editorOpen" title="编辑内容" :section="props.section" :slug="slug" @saved="load" />
    </GlassCard>
  </section>
</template>

<style scoped>
.detail-shell {
  padding: 0;
}
.detail-cover {
  height: clamp(15rem, 34vw, 25rem);
  overflow: hidden;
  background: rgba(15, 23, 42, .72);
}
.detail-cover-actions {
  padding: 1rem 1.25rem 0;
}
.detail-article {
  padding: 1.15rem 1.25rem 0;
}
.detail-body {
  margin-top: 2.2rem;
}
.detail-action-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: .85rem;
  margin-top: 2rem;
}
.detail-icon-button {
  display: inline-grid;
  width: 2.6rem;
  height: 2.6rem;
  place-items: center;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: rgba(255, 255, 255, .72);
  transition: color .18s ease, border-color .18s ease, background .18s ease, transform .18s ease;
}
.detail-icon-button:hover {
  color: white;
  transform: translateY(-1px);
}
.detail-icon-button svg {
  width: 1.15rem;
  height: 1.15rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.detail-comments {
  margin-top: 2.4rem;
  padding: 0 1.25rem 1.25rem;
}
@media (min-width: 768px) {
  .detail-cover-actions,
  .detail-article {
    padding-left: 1.75rem;
    padding-right: 1.75rem;
  }
  .detail-comments {
    padding-left: 1.75rem;
    padding-right: 1.75rem;
    padding-bottom: 1.75rem;
  }
}
</style>
