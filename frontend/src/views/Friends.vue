<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import FrontJsonItemEditorModal from '@/components/FrontJsonItemEditorModal.vue'
import { contentApi } from '@/api/content'
import type { FriendItem, PageConfig } from '@/types'
import { useSeo } from '@/composables/useSeo'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'

const friends = ref<FriendItem[]>([])
const session = useSessionStore()
const ui = useUiStore()
const loading = ref(false)
const error = ref('')
const editorOpen = ref(false)
const editingIndex = ref(-1)
const editingFriend = ref<FriendItem | null>(null)
const deleteArmed = ref('')
const pageConfig = ref<PageConfig | null>(null)
const pageTitle = computed(() => pageConfig.value?.pageText?.friends?.title || '星际友链')
const pageSubtitle = computed(() => pageConfig.value?.pageText?.friends?.subtitle || '朋友站点、项目站点和个人链接会从后端 JSON 动态读取。')
useSeo({ title: () => pageTitle.value, description: () => pageSubtitle.value, path: '/friends' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [friendData, publicSettings] = await Promise.all([
      contentApi.json<FriendItem[]>('/friends'),
      contentApi.json<PageConfig>('/pages/config')
    ])
    friends.value = friendData
    pageConfig.value = publicSettings
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '友链加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function openFriendEditor(item: FriendItem | null = null, index = -1) {
  editingFriend.value = item
  editingIndex.value = index
  editorOpen.value = true
}

async function deleteFriend(item: FriendItem, index: number) {
  const key = item.url || item.name || String(index)
  if (deleteArmed.value !== key) {
    deleteArmed.value = key
    ui.showToast('再次点击删除以确认', 'info')
    window.setTimeout(() => {
      if (deleteArmed.value === key) deleteArmed.value = ''
    }, 3000)
    return
  }
  try {
    await contentApi.adminPutJson('/friends', friends.value.filter((_, itemIndex) => itemIndex !== index))
    ui.showToast('友链已删除', 'success')
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
      <button type="button" class="frontend-admin-create-btn" @click="openFriendEditor()">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        新增友链
      </button>
    </div>

    <div>
      <GlassCard v-if="loading">
        <p class="text-white/60">友链加载中...</p>
      </GlassCard>
      <GlassCard v-else-if="error">
        <p class="text-red-200/85">{{ error }}</p>
        <button class="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-sm text-white/70" @click="load">重试</button>
      </GlassCard>
      <GlassCard v-else-if="!friends.length">
        <p class="text-white/60">暂无友链。</p>
      </GlassCard>

      <div v-else class="grid min-w-0 gap-5 md:grid-cols-2 xl:grid-cols-3">
        <GlassCard v-for="(item, index) in friends" :key="item.url" hover>
        <a :href="item.url" target="_blank" rel="noopener noreferrer" class="block min-w-0">
          <div class="flex min-w-0 items-center gap-4">
            <div class="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-[24px] border border-white/12 bg-white/10">
              <SafeImage v-if="item.avatar" :src="item.avatar" :alt="item.name" img-class="h-full w-full object-cover" />
              <span v-else class="text-xl font-black text-cyan-100">{{ item.name?.slice(0, 1) || '?' }}</span>
            </div>
            <div class="min-w-0">
              <h2 class="truncate text-xl font-black text-white">{{ item.name }}</h2>
              <p class="truncate text-sm text-white/45">{{ item.url }}</p>
            </div>
          </div>
          <p class="mt-4 break-words leading-7 text-white/62">{{ item.description || '这个站点还没有描述。' }}</p>
          <div v-if="item.tags?.length" class="mt-4 flex flex-wrap gap-2">
            <span v-for="tag in item.tags" :key="tag" class="rounded-full border border-white/10 px-3 py-1 text-xs text-white/50">#{{ tag }}</span>
          </div>
        </a>
        <div v-if="session.isAdmin" class="front-json-card-actions">
          <button type="button" @click="openFriendEditor(item, index)">编辑</button>
          <button type="button" class="danger" @click="deleteFriend(item, index)">{{ deleteArmed === (item.url || item.name || String(index)) ? '确认删除' : '删除' }}</button>
        </div>
        </GlassCard>
      </div>
    </div>
    <FrontJsonItemEditorModal v-model="editorOpen" kind="friend" :item="editingFriend" :index="editingIndex" @saved="load" />
  </section>
</template>

<style scoped>
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
