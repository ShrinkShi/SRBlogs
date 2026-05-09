<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
const route = useRoute()
const router = useRouter()
const expanded = ref('content')

const groups: NavGroup[] = [
  {
    key: 'content',
    title: '内容管理',
    items: [
      {
        label: '文章',
        path: '/content/articles',
        note: '正经 / 杂谈',
        children: [{ label: '评论', path: '/content/article-comments' }]
      },
      {
        label: '图片',
        path: '/content/photos',
        note: '相册组',
        children: [{ label: '评论', path: '/content/photo-comments' }]
      },
      {
        label: '音乐',
        path: '/content/music',
        note: '歌单',
        children: [{ label: '评论', path: '/content/music-comments' }]
      },
      { label: '项目', path: '/content/projects', note: '封面 / 链接' },
      { label: '友链', path: '/content/friends', note: '站点卡片' },
      { label: '关于', path: '/content/about', note: '页面文案' }
    ]
  },
  {
    key: 'settings',
    title: '设置',
    items: [{ label: '设置中心', path: '/settings', note: '站点 / 我的 / 主题 / 留言' }]
  },
  {
    key: 'audit',
    title: '审计日志',
    items: [{ label: '审计日志', path: '/audit', note: '操作记录' }]
  },
  {
    key: 'backup',
    title: '备份恢复',
    items: [{ label: '备份恢复', path: '/backups', note: '导入 / 导出 / 回滚' }]
  }
]

const activePath = computed(() => route.path)

function isItemActive(item: NavItem): boolean {
  if (item.children?.some(isItemActive)) return true
  return activePath.value === item.path || activePath.value.startsWith(`${item.path}/`)
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
            <span class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-950">SR</span>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-black text-slate-950">SRBlogs</h1>
              <p class="text-xs text-slate-500">管理控制台</p>
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
                <div v-if="item.children && isItemActive(item)" class="ml-3 grid gap-1 border-l border-slate-200 pl-3">
                  <RouterLink
                    v-for="child in item.children"
                    :key="child.path"
                    :to="child.path"
                    class="admin-nav-child text-xs"
                    :class="activePath === child.path ? 'admin-nav-child-active' : ''"
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
    </div>
  </div>
</template>
