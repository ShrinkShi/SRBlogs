<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

type NavItem = {
  label: string
  path: string
}

type NavGroup = {
  key: string
  title: string
  items: NavItem[]
}

const auth = useAuthStore()
const route = useRoute()

const groups: NavGroup[] = [
  {
    key: 'content',
    title: '内容',
    items: [
      { label: '文章', path: '/content/articles' },
      { label: '图片', path: '/content/photos' },
      { label: '音乐', path: '/content/music' },
      { label: '项目', path: '/content/projects' },
      { label: '友链', path: '/content/friends' },
      { label: '关于', path: '/content/about' },
      { label: '评论', path: '/content/article-comments' }
    ]
  },
  {
    key: 'settings',
    title: '设置',
    items: [{ label: '设置中心', path: '/settings' }]
  }
]

const activePath = computed(() => route.path)

function isItemActive(item: NavItem): boolean {
  return activePath.value === item.path || activePath.value.startsWith(`${item.path}/`)
}

function logout() {
  auth.logout()
  location.href = '/admin/login'
}
</script>

<template>
  <div class="admin-flat min-h-screen">
    <div class="grid min-h-screen xl:grid-cols-[292px_minmax(0,1fr)]">
      <aside class="admin-sidebar h-screen overflow-auto p-4 xl:sticky xl:top-0">
        <div class="mb-6 rounded-2xl border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-3">
            <span class="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-slate-950 text-sm font-black text-white">SR</span>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-black tracking-tight text-slate-950">SRBlogs</h1>
              <p class="text-xs font-semibold text-slate-500">后台管理系统</p>
            </div>
          </div>
        </div>

        <nav class="grid gap-3" aria-label="后台导航">
          <section v-for="group in groups" :key="group.key" class="admin-nav-group">
            <div class="admin-nav-parent">
              <b>{{ group.title }}</b>
            </div>
            <div class="admin-nav-children">
              <RouterLink
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="admin-nav-child"
                :class="isItemActive(item) ? 'admin-nav-child-active' : ''"
              >
                <span>{{ item.label }}</span>
              </RouterLink>
            </div>
          </section>
        </nav>

        <button type="button" class="admin-btn admin-btn-ghost mt-6 w-full" @click="logout">退出登录</button>
      </aside>

      <main class="min-w-0 p-4 md:p-6 xl:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
