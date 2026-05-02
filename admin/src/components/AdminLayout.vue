<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePendingStore } from '@/stores/pending'

const auth = useAuthStore()
const pendingStore = usePendingStore()
const route = useRoute()
const queueOpen = ref(true)
const links = [
  ['仪表盘', '/', '总览'],
  ['写作', '/editor/posts', 'Markdown'],
  ['文章', '/posts', '发布'],
  ['草稿', '/drafts', '暂存'],
  ['动态', '/moments', '短记'],
  ['杂谈', '/chatters', '长记'],
  ['评论', '/comments', '本地'],
  ['审计', '/audit', '日志'],
  ['备份', '/backups', '恢复'],
  ['友链', '/friends', '链接'],
  ['音乐', '/music', '歌单'],
  ['照片墙', '/photos', '图片'],
  ['项目', '/projects', '展示'],
  ['关于', '/about', '页面'],
  ['AI助手', '/chat', '双线'],
  ['设置', '/settings', '配置']
]
const active = computed(() => route.path)

function logout() {
  auth.logout()
  location.href = '/admin/login'
}
</script>

<template>
  <div class="min-h-screen p-3 md:p-6">
    <div class="mx-auto grid max-w-[1500px] gap-5 xl:grid-cols-[260px_minmax(0,1fr)_300px]">
      <aside class="glass h-fit max-h-[72vh] overflow-auto rounded-[32px] p-4 xl:sticky xl:top-6 xl:max-h-[calc(100vh-3rem)]">
        <div class="mb-5 px-3">
          <div class="flex items-center gap-3">
            <span class="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-cyan-300/15 text-cyan-100">SR</span>
            <div class="min-w-0">
              <h1 class="truncate text-2xl font-black text-white">SRBlogs</h1>
              <p class="text-xs text-white/45">管理控制台</p>
            </div>
          </div>
        </div>
        <nav class="grid gap-1" aria-label="后台导航">
          <RouterLink
            v-for="link in links"
            :key="link[1]"
            :to="link[1]"
            class="relative z-[1] flex items-center justify-between gap-3 rounded-2xl px-3 py-2.5 text-sm transition"
            :class="active === link[1] ? 'bg-cyan-300/[0.16] text-cyan-100' : 'text-white/64 hover:bg-white/10 hover:text-white'"
          >
            <span>{{ link[0] }}</span>
            <span class="text-[10px] text-white/35">{{ link[2] }}</span>
          </RouterLink>
        </nav>
        <button type="button" class="admin-btn admin-btn-ghost relative z-[1] mt-5 w-full text-sm" @click="logout">退出登录</button>
      </aside>

      <main class="min-w-0"><slot /></main>

      <aside class="hidden xl:block">
        <div class="glass sticky top-6 rounded-[32px] p-5">
          <div class="relative z-[1] flex items-center justify-between gap-3">
            <h2 class="font-black text-white">操作暂存区</h2>
            <button type="button" class="text-xs text-white/45 hover:text-white/75" :aria-expanded="queueOpen" @click="queueOpen = !queueOpen">{{ queueOpen ? '收起' : '展开' }}</button>
          </div>
          <div v-if="queueOpen" class="relative z-[1] mt-4 grid gap-3">
            <p class="rounded-2xl border border-amber-200/20 bg-amber-300/10 p-3 text-xs leading-5 text-amber-50/72">
              第一阶段为前端本地 pendingOperations，刷新页面会丢失。图片上传、Secret 修改、评论管理不进入本地队列。
            </p>
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
    </div>
  </div>
</template>
