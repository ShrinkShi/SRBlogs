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
  key: string
  title: string
  items: NavItem[]
}

const auth = useAuthStore()
const pendingStore = usePendingStore()
const route = useRoute()
const router = useRouter()
const queueOpen = ref(true)
const queueVisible = ref(false)
const expanded = ref('pages')

const groups: NavGroup[] = [
  {
    key: 'pages',
    title: '页面编辑',
    items: [
      { label: '首页', path: '/pages/home', note: '布局' },
      { label: '文章', path: '/pages/posts', note: '标题' },
      { label: '图片', path: '/pages/photos', note: '相册' },
      { label: '音乐', path: '/pages/music', note: '播放' },
      { label: '项目', path: '/pages/projects', note: '展示' },
      { label: '友链', path: '/pages/friends', note: '链接' },
      { label: '关于', path: '/pages/about', note: 'Markdown' }
    ]
  },
  {
    key: 'content',
    title: '内容管理',
    items: [
      { label: '写作编辑器', path: '/editor/posts', note: 'Markdown' },
      { label: '文章管理', path: '/posts', note: '发布' },
      { label: '草稿', path: '/drafts', note: '暂存' },
      { label: '动态', path: '/moments', note: '短记' },
      { label: '杂谈', path: '/chatters', note: '长文' },
      {
        label: '媒体',
        path: '/photos',
        note: '资源',
        children: [
          { label: '友链', path: '/friends' },
          { label: '项目', path: '/projects' },
          { label: '音乐', path: '/music' },
          { label: '图片', path: '/photos' }
        ]
      }
    ]
  },
  {
    key: 'messages',
    title: '评论管理',
    items: [
      { label: '留言管理', path: '/comments', note: '访客' }
    ]
  },
  {
    key: 'settings',
    title: '后台设置',
    items: [
      {
        label: '设置中心',
        path: '/settings?tab=site',
        note: '配置',
        children: [
          { label: '站点公开信息', path: '/settings?tab=site' },
          { label: '主题与背景', path: '/settings?tab=theme' },
          { label: '留言设置', path: '/settings?tab=comments' },
          { label: '图床设置', path: '/settings?tab=image' },
          { label: 'AI 设置', path: '/settings?tab=ai' },
          { label: '部署与安全提示', path: '/settings?tab=deploy' }
        ]
      },
      { label: 'AI 助手', path: '/chat', note: '开关' }
    ]
  },
  {
    key: 'logs',
    title: '日志备份',
    items: [
      { label: '总览', path: '/', note: '状态' },
      { label: '审计日志', path: '/audit', note: '追踪' },
      { label: '备份恢复', path: '/backups', note: '安全' }
    ]
  }
]

const activePath = computed(() => route.path)
const activeTarget = computed(() => route.path === '/settings' ? `${route.path}?tab=${route.query.tab || 'site'}` : route.path)

function stripQuery(path: string) {
  return path.split('?')[0]
}

function isItemActive(item: NavItem): boolean {
  if (item.children?.some(isItemActive)) return true
  if (item.path.includes('?')) return activeTarget.value === item.path
  const target = stripQuery(item.path)
  return target === activePath.value || (target !== '/' && activePath.value.startsWith(target))
}

function isGroupActive(group: NavGroup) {
  return group.items.some(isItemActive)
}

function goGroup(group: NavGroup) {
  expanded.value = group.key
  router.push(group.items[0].path)
}

function logout() {
  auth.logout()
  location.href = '/admin/login'
}
</script>

<template>
  <div class="admin-flat min-h-screen">
    <div class="grid min-h-screen gap-0 xl:grid-cols-[280px_minmax(0,1fr)]">
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
          <section v-for="group in groups" :key="group.key" class="admin-nav-group">
            <button
              type="button"
              class="admin-nav-parent"
              :class="isGroupActive(group) ? 'admin-nav-parent-active' : ''"
              @click="goGroup(group)"
            >
              <span>{{ group.title }}</span>
              <span>{{ expanded === group.key ? '收起' : '展开' }}</span>
            </button>
            <div v-if="expanded === group.key || isGroupActive(group)" class="admin-nav-children">
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
                    :class="activeTarget === child.path || route.path === stripQuery(child.path) ? 'admin-nav-child-active' : ''"
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

      <Transition name="queue-drawer">
        <aside v-if="queueVisible" class="fixed inset-y-0 right-0 z-[80] w-[min(23rem,calc(100vw-1rem))] p-3">
          <div class="glass flex h-full min-h-0 flex-col rounded-[28px] p-5">
            <div class="relative z-[1] flex items-center justify-between gap-3">
              <h2 class="font-black text-white">操作暂存区</h2>
              <div class="flex gap-2">
                <button type="button" class="text-xs text-white/45 hover:text-white/75" :aria-expanded="queueOpen" @click="queueOpen = !queueOpen">{{ queueOpen ? '收起内容' : '展开内容' }}</button>
                <button type="button" class="text-xs text-cyan-100/70 hover:text-cyan-100" @click="queueVisible = false">关闭</button>
              </div>
            </div>
            <div v-if="queueOpen" class="relative z-[1] mt-4 grid min-h-0 flex-1 gap-3 overflow-y-auto pr-1">
              <p class="rounded-2xl border border-amber-200/20 bg-amber-300/10 p-3 text-xs leading-5 text-amber-50/72">
                第一阶段为前端本地 pendingOperations，刷新页面会丢失。图片上传、Secret 修改、留言管理不进入本地队列。
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
      </Transition>

      <button
        v-if="!queueVisible"
        type="button"
        class="fixed bottom-5 right-5 z-50 rounded-2xl border border-cyan-200/25 bg-cyan-300/15 px-4 py-3 text-sm font-bold text-cyan-100 backdrop-blur"
        @click="queueVisible = true"
      >
        显示暂存区
      </button>
    </div>
  </div>
</template>

<style scoped>
.queue-drawer-enter-active,
.queue-drawer-leave-active {
  transition: transform .22s ease, opacity .22s ease;
}
.queue-drawer-enter-from,
.queue-drawer-leave-to {
  opacity: 0;
  transform: translateX(1.5rem);
}
</style>
