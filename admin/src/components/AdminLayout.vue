<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePendingStore } from '@/stores/pending'

type NavItem = {
  label: string
  path: string
  note?: string
  children?: NavItem[]
}

type NavGroup = {
  title: string
  items: NavItem[]
}

const auth = useAuthStore()
const pendingStore = usePendingStore()
const route = useRoute()
const router = useRouter()
const queueOpen = ref(true)
const queueVisible = ref(true)
const expanded = ref('content')

const groups: NavGroup[] = [
  {
    title: '总览',
    items: [
      { label: '仪表盘', path: '/', note: '状态' },
      { label: '审计日志', path: '/audit', note: '追踪' },
      { label: '备份恢复', path: '/backups', note: '安全' }
    ]
  },
  {
    title: '内容',
    items: [
      { label: '写作编辑器', path: '/editor/posts', note: 'Markdown' },
      { label: '文章管理', path: '/posts', note: '发布' },
      { label: '草稿', path: '/drafts', note: '暂存' },
      { label: '动态', path: '/moments', note: '短记' },
      { label: '杂谈', path: '/chatters', note: '长文' },
      { label: '关于页', path: '/about', note: 'Markdown' }
    ]
  },
  {
    title: '互动',
    items: [
      { label: '评论', path: '/comments', note: 'GitHub' },
      { label: 'AI 助手', path: '/chat', note: '开关' }
    ]
  },
  {
    title: '媒体',
    items: [
      { label: '友链', path: '/friends', note: '链接' },
      { label: '项目', path: '/projects', note: '展示' },
      { label: '音乐', path: '/music', note: '歌单' },
      { label: '照片墙', path: '/photos', note: '相册' }
    ]
  },
  {
    title: '系统',
    items: [
      {
        label: '设置中心',
        path: '/settings?tab=site',
        note: '配置',
        children: [
          { label: '站点公开信息', path: '/settings?tab=site' },
          { label: '主题与背景', path: '/settings?tab=theme' },
          { label: '评论设置', path: '/settings?tab=comments' },
          { label: '图床设置', path: '/settings?tab=image' },
          { label: 'AI 设置', path: '/settings?tab=ai' },
          { label: '部署与安全提示', path: '/settings?tab=deploy' }
        ]
      }
    ]
  }
]

const activePath = computed(() => route.path)
const activeTarget = computed(() => route.path === '/settings' ? `${route.path}?tab=${route.query.tab || 'site'}` : route.path)
const layoutClass = computed(() => queueVisible.value
  ? 'xl:grid-cols-[280px_minmax(0,1fr)_300px]'
  : 'xl:grid-cols-[280px_minmax(0,1fr)]'
)

function groupKey(group: NavGroup) {
  return group.title === '总览' ? 'overview'
    : group.title === '内容' ? 'content'
      : group.title === '互动' ? 'interaction'
        : group.title === '媒体' ? 'media'
          : 'system'
}

function stripQuery(path: string) {
  return path.split('?')[0]
}

function isItemActive(item: NavItem) {
  if (item.children?.some(isItemActive)) return true
  if (item.path.includes('?')) return activeTarget.value === item.path
  return item.path === activePath.value || (item.path !== '/' && activePath.value.startsWith(item.path))
}

function isGroupActive(group: NavGroup) {
  return group.items.some(isItemActive)
}

function goGroup(group: NavGroup) {
  expanded.value = groupKey(group)
  router.push(group.items[0].path)
}

function logout() {
  auth.logout()
  location.href = '/admin/login'
}
</script>

<template>
  <div class="min-h-screen">
    <div class="grid min-h-screen gap-0" :class="layoutClass">
      <aside class="admin-sidebar h-screen overflow-auto rounded-none border-y-0 border-l-0 p-3 xl:sticky xl:top-0">
        <div class="mb-4 px-3 py-3">
          <div class="flex items-center gap-3">
            <span class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-cyan-300/15 text-cyan-100">SR</span>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-black text-white">SRBlogs</h1>
              <p class="text-xs text-white/45">管理控制台</p>
            </div>
          </div>
        </div>

        <nav class="relative z-[1] grid gap-1" aria-label="后台导航">
          <section v-for="group in groups" :key="group.title" class="admin-nav-group">
            <button
              type="button"
              class="admin-nav-parent"
              :class="isGroupActive(group) ? 'admin-nav-parent-active' : ''"
              @click="goGroup(group)"
            >
              <span>{{ group.title }}</span>
              <span>{{ expanded === groupKey(group) ? '收起' : '展开' }}</span>
            </button>
            <div v-if="expanded === groupKey(group) || isGroupActive(group)" class="admin-nav-children">
              <template v-for="item in group.items" :key="item.path">
                <RouterLink
                  :to="item.path"
                  class="admin-nav-child"
                  :class="isItemActive(item) ? 'admin-nav-child-active' : ''"
                >
                  <span>{{ item.label }}</span>
                  <small>{{ item.note }}</small>
                </RouterLink>
                <div v-if="item.children && isItemActive(item)" class="ml-3 grid gap-1 border-l border-white/10 pl-3">
                  <RouterLink
                    v-for="child in item.children"
                    :key="child.path"
                    :to="child.path"
                    class="admin-nav-child text-xs"
                    :class="activeTarget === child.path ? 'admin-nav-child-active' : ''"
                  >
                    <span>{{ child.label }}</span>
                  </RouterLink>
                </div>
              </template>
            </div>
          </section>
        </nav>

        <button type="button" class="admin-btn admin-btn-ghost relative z-[1] mt-5 w-full text-sm" @click="logout">退出登录</button>
      </aside>

      <main class="min-w-0 p-4 md:p-6"><slot /></main>

      <aside v-if="queueVisible" class="hidden p-4 xl:block">
        <div class="glass sticky top-6 rounded-[28px] p-5">
          <div class="relative z-[1] flex items-center justify-between gap-3">
            <h2 class="font-black text-white">操作暂存区</h2>
            <div class="flex gap-2">
              <button type="button" class="text-xs text-white/45 hover:text-white/75" :aria-expanded="queueOpen" @click="queueOpen = !queueOpen">{{ queueOpen ? '收起内容' : '展开内容' }}</button>
              <button type="button" class="text-xs text-cyan-100/70 hover:text-cyan-100" @click="queueVisible = false">完全隐藏</button>
            </div>
          </div>
          <div v-if="queueOpen" class="relative z-[1] mt-4 grid gap-3">
            <p class="rounded-2xl border border-amber-200/20 bg-amber-300/10 p-3 text-xs leading-5 text-amber-50/72">
              第一阶段为前端本地 pendingOperations，刷新页面会丢失。图片上传、Secret 修改、评论管理不进入本地队列。
            </p>
            <button
              v-if="pendingStore.pendingCount"
              type="button"
              class="rounded-2xl bg-cyan-300 px-4 py-2 text-sm font-bold text-slate-950"
              @click="pendingStore.applyAll()"
            >
              一键应用全部 {{ pendingStore.pendingCount }} 项
            </button>
            <div v-if="!pendingStore.operations.length" class="rounded-2xl border border-white/10 bg-white/[0.07] p-3 text-sm text-white/52">暂无暂存操作。</div>
            <div v-for="item in pendingStore.operations" :key="item.id" class="rounded-2xl border border-white/10 bg-white/[0.07] p-3 text-sm">
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <b class="block text-white">{{ pendingStore.label(item.kind) }}</b>
                  <p class="mt-1 truncate text-white/58">{{ item.title }}</p>
                  <p class="mt-1 truncate font-mono text-xs text-cyan-100/45">{{ item.slug }}</p>
                </div>
                <span class="shrink-0 rounded-full px-2 py-1 text-[10px]" :class="item.status === 'applied' ? 'bg-emerald-300/15 text-emerald-100' : item.status === 'failed' ? 'bg-red-300/15 text-red-100' : 'bg-cyan-300/15 text-cyan-100'">{{ item.status }}</span>
              </div>
              <p class="mt-2 text-xs text-white/35">{{ item.createdAt }}</p>
              <p v-if="item.error" class="mt-2 text-xs text-red-100/80">{{ item.error }}</p>
              <div class="mt-3 flex flex-wrap gap-2">
                <button v-if="item.status === 'pending'" type="button" class="rounded-xl bg-cyan-300 px-3 py-1.5 text-xs font-bold text-slate-950" @click="pendingStore.apply(item.id)">应用</button>
                <button v-if="item.status === 'failed'" type="button" class="rounded-xl bg-amber-300/20 px-3 py-1.5 text-xs text-amber-100" @click="pendingStore.retry(item.id)">重试</button>
                <button type="button" class="rounded-xl border border-white/10 px-3 py-1.5 text-xs text-white/62" @click="pendingStore.remove(item.id)">移除</button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <button
        v-else
        type="button"
        class="fixed bottom-5 right-5 z-50 rounded-2xl border border-cyan-200/25 bg-cyan-300/15 px-4 py-3 text-sm font-bold text-cyan-100 backdrop-blur"
        @click="queueVisible = true"
      >
        显示暂存区
      </button>
    </div>
  </div>
</template>
