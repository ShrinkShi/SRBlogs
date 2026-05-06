<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'

type PageKey = 'home' | 'posts' | 'photos' | 'music' | 'projects' | 'friends' | 'about'
type TextKey = PageKey | 'chatters'

const route = useRoute()
const pageKeys: PageKey[] = ['home', 'posts', 'photos', 'music', 'projects', 'friends', 'about']
const pageKey = computed<PageKey>(() => {
  const key = String(route.params.page || 'home')
  return pageKeys.includes(key as PageKey) ? key as PageKey : 'home'
})

const pages: Array<{ key: PageKey; label: string; path: string; note: string }> = [
  { key: 'home', label: '首页', path: '/', note: '名片、头像、简介与社交链接' },
  { key: 'posts', label: '文章', path: '/posts', note: '文章页标题、副标题与杂谈板块文案' },
  { key: 'photos', label: '图片', path: '/photowall', note: '图片页标题与说明文案' },
  { key: 'music', label: '音乐', path: '/music', note: '音乐页标题与说明文案' },
  { key: 'projects', label: '项目', path: '/projects', note: '项目页标题与说明文案' },
  { key: 'friends', label: '友链', path: '/friends', note: '友链页标题与说明文案' },
  { key: 'about', label: '关于', path: '/about', note: '关于页标题、副标题与 Markdown' }
]

const defaultText: Record<TextKey, { title: string; subtitle: string }> = {
  home: { title: '首页', subtitle: '名片、音乐、歌词、轮播与状态区。' },
  posts: { title: '文章归档', subtitle: '从 FastAPI 读取 Markdown 内容，草稿默认不会出现在公开列表。' },
  chatters: { title: '云端杂谈', subtitle: '长一点的念头，短一点的文章。' },
  photos: { title: '图片', subtitle: '相册记录从后端 JSON 动态读取，点击封面可查看组内照片。' },
  music: { title: '音乐歌单', subtitle: '左侧控制播放，右侧查看歌词和歌单。' },
  projects: { title: '项目陈列柜', subtitle: '记录正在构建和已经完成的作品。' },
  friends: { title: '星际友链', subtitle: '把值得长期访问的站点放在这里。' },
  about: { title: '关于', subtitle: '关于 SRBlogs 与站点作者。' }
}

const currentPage = computed(() => pages.find((item) => item.key === pageKey.value) || pages[0])
const fieldLabel = computed(() => `编辑${currentPage.value.label}信息`)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const dirty = ref(false)
const raw = ref<Record<string, any>>({})
const aboutContent = ref('')
const summary = ref('')

const pageText = reactive<Record<TextKey, { title: string; subtitle: string }>>({
  home: { ...defaultText.home },
  posts: { ...defaultText.posts },
  chatters: { ...defaultText.chatters },
  photos: { ...defaultText.photos },
  music: { ...defaultText.music },
  projects: { ...defaultText.projects },
  friends: { ...defaultText.friends },
  about: { ...defaultText.about }
})

const home = reactive({
  author: '',
  avatar: '',
  description: '',
  socialLinks: { github: '', email: '', qq: '', wechat: '' } as Record<string, string>
})

function hydrate(data: Record<string, any>) {
  const savedText = data.pageText || {}
  ;(Object.keys(defaultText) as TextKey[]).forEach((key) => {
    pageText[key].title = savedText[key]?.title || defaultText[key].title
    pageText[key].subtitle = savedText[key]?.subtitle || defaultText[key].subtitle
  })
  const profile = data.homeProfile || {}
  home.author = profile.author || ''
  home.avatar = profile.avatar || ''
  home.description = profile.description || ''
  home.socialLinks = {
    github: '',
    email: '',
    qq: '',
    wechat: '',
    ...(profile.socialLinks || {})
  }
}

async function loadSummary(key: PageKey) {
  try {
    if (key === 'posts') {
      const posts = await adminApi.list('posts')
      const chatters = await adminApi.list('chatters')
      summary.value = `真实文章 ${posts.length} 篇，杂谈 ${chatters.length} 篇。前台布局由 Vue/CSS 固定实现。`
    } else if (key === 'photos') {
      const list = await adminApi.json<any[]>('/photos')
      summary.value = `真实相册 ${Array.isArray(list) ? list.length : 0} 组。相册管理仍在内容管理中维护。`
    } else if (key === 'music') {
      const list = await adminApi.json<any[]>('/music')
      summary.value = `真实歌曲 ${Array.isArray(list) ? list.length : 0} 首。播放器布局由前台固定实现。`
    } else if (key === 'projects') {
      const list = await adminApi.json<any[]>('/projects')
      summary.value = `真实项目 ${Array.isArray(list) ? list.length : 0} 个。`
    } else if (key === 'friends') {
      const list = await adminApi.json<any[]>('/friends')
      summary.value = `真实友链 ${Array.isArray(list) ? list.length : 0} 条。`
    } else if (key === 'about') {
      const data = await adminApi.json<{ content: string }>('/about')
      aboutContent.value = data.content || ''
      summary.value = `关于页 Markdown，${aboutContent.value.length} 个字符。`
    } else {
      summary.value = '首页信息用于前台名片。首页版式由代码固定，不再读取低代码布局字段。'
    }
  } catch (exc) {
    summary.value = exc instanceof Error ? `真实数据摘要读取失败：${exc.message}` : '真实数据摘要读取失败。'
  }
}

async function load() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    raw.value = await adminApi.json<Record<string, any>>('/admin/pages/config')
    hydrate(raw.value)
    await loadSummary(pageKey.value)
    dirty.value = false
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面信息加载失败'
  } finally {
    loading.value = false
  }
}

function payload() {
  return {
    ...raw.value,
    homeProfile: {
      author: home.author,
      avatar: home.avatar,
      description: home.description,
      socialLinks: { ...home.socialLinks }
    },
    pageText: Object.fromEntries((Object.keys(pageText) as TextKey[]).map((key) => [key, { ...pageText[key] }]))
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/pages/config', payload())
    if (pageKey.value === 'about') await adminApi.putJson('/about', { content: aboutContent.value })
    raw.value = await adminApi.json<Record<string, any>>('/admin/pages/config')
    hydrate(raw.value)
    success.value = '页面信息已保存，刷新前台后生效。'
    dirty.value = false
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '页面信息保存失败'
  } finally {
    saving.value = false
  }
}

function markDirty() {
  dirty.value = true
}

watch(pageKey, async () => {
  await loadSummary(pageKey.value)
})

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.22em] text-slate-500">PAGE INFO</p>
          <h1 class="mt-2 text-4xl font-black text-slate-950">页面信息编辑</h1>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            前台布局已回归代码固定实现。这里仅维护页面标题、简介、首页名片和关于 Markdown 等真实字段。
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <a class="admin-btn admin-btn-ghost" :href="currentPage.path" target="_blank" rel="noopener noreferrer">预览前台</a>
          <button class="admin-btn admin-btn-primary" type="button" :disabled="saving || loading" @click="save">
            {{ saving ? '保存中...' : '保存页面信息' }}
          </button>
        </div>
      </div>
    </GlassCard>

    <div class="grid gap-5 lg:grid-cols-[15rem_minmax(0,1fr)]">
      <GlassCard>
        <div class="grid gap-2">
          <RouterLink
            v-for="page in pages"
            :key="page.key"
            :to="`/pages/${page.key}`"
            class="rounded-xl px-3 py-3 text-sm font-bold transition"
            :class="page.key === pageKey ? 'bg-slate-950 !text-white [&_*]:!text-white' : 'text-slate-700 hover:bg-slate-100'"
          >
            <span class="block">{{ page.label }}</span>
            <small class="mt-1 block font-normal opacity-70">{{ page.note }}</small>
          </RouterLink>
        </div>
      </GlassCard>

      <GlassCard>
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-200 pb-4">
          <div>
            <h2 class="text-2xl font-black text-slate-950">{{ fieldLabel }}</h2>
            <p class="mt-1 text-sm text-slate-600">{{ summary }}</p>
          </div>
          <span v-if="dirty" class="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">有未保存修改</span>
        </div>

        <div v-if="loading" class="py-10 text-center text-slate-500">页面信息加载中...</div>
        <div v-else class="mt-5 grid gap-5">
          <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{{ error }}</div>
          <div v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-700">{{ success }}</div>

          <div v-if="pageKey === 'home'" class="settings-grid">
            <label class="field">首页作者
              <input v-model="home.author" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">头像 URL
              <input v-model="home.avatar" class="admin-input" @input="markDirty" />
            </label>
            <label class="field md:col-span-2">首页简介
              <textarea v-model="home.description" rows="4" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">GitHub
              <input v-model="home.socialLinks.github" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">Email
              <input v-model="home.socialLinks.email" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">QQ
              <input v-model="home.socialLinks.qq" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">微信
              <input v-model="home.socialLinks.wechat" class="admin-input" @input="markDirty" />
            </label>
          </div>

          <div v-else-if="pageKey === 'posts'" class="settings-grid">
            <label class="field">文章页标题
              <input v-model="pageText.posts.title" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">文章页副标题
              <input v-model="pageText.posts.subtitle" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">杂谈板块标题
              <input v-model="pageText.chatters.title" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">杂谈板块副标题
              <input v-model="pageText.chatters.subtitle" class="admin-input" @input="markDirty" />
            </label>
          </div>

          <div v-else-if="pageKey === 'about'" class="grid gap-5">
            <div class="settings-grid">
              <label class="field">关于页标题
                <input v-model="pageText.about.title" class="admin-input" @input="markDirty" />
              </label>
              <label class="field">关于页副标题
                <input v-model="pageText.about.subtitle" class="admin-input" @input="markDirty" />
              </label>
            </div>
            <label class="field">关于 Markdown
              <textarea v-model="aboutContent" rows="18" class="admin-input font-mono" @input="markDirty" />
            </label>
          </div>

          <div v-else class="settings-grid">
            <label class="field">页面标题
              <input v-model="pageText[pageKey].title" class="admin-input" @input="markDirty" />
            </label>
            <label class="field">页面副标题
              <input v-model="pageText[pageKey].subtitle" class="admin-input" @input="markDirty" />
            </label>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
            旧版页面布局字段仅作为兼容数据保存在配置文件中，不再影响前台实际布局。文章、图片、音乐、项目、友链、关于和留言数据不会被这里的保存操作删除。
          </div>

          <div class="flex flex-wrap justify-end gap-2">
            <button class="admin-btn admin-btn-primary" type="button" :disabled="saving" @click="save">
              {{ saving ? '保存中...' : '保存页面信息' }}
            </button>
          </div>
        </div>
      </GlassCard>
    </div>
  </section>
</template>
