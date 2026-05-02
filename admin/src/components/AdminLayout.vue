<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const queueOpen = ref(true)
const links = [
  ['仪表盘','/','总览'], ['写作','/editor/posts','Markdown'], ['文章','/posts','发布'], ['草稿','/drafts','暂存'],
  ['动态','/moments','短记'], ['杂谈','/chatters','长记'], ['评论','/comments','本地'], ['友链','/friends','链接'],
  ['音乐','/music','歌单'], ['照片墙','/photos','图片'], ['项目','/projects','展示'], ['关于','/about','页面'],
  ['AI助手','/chat','双线'], ['设置','/settings','配置']
]
const pending = ref(['暂存队列尚未实现', '内容保存后直接写入 FastAPI 数据目录', '部署同步接口预留'])
const active = computed(() => route.path)
function logout(){ auth.logout(); location.href = '/admin/login' }
</script>
<template>
  <div class="min-h-screen p-3 md:p-6">
    <div class="mx-auto grid max-w-[1500px] gap-5 xl:grid-cols-[260px_1fr_300px]">
      <aside class="glass h-fit rounded-[32px] p-4 xl:sticky xl:top-6">
        <div class="mb-5 px-3">
          <div class="flex items-center gap-3"><span class="grid h-10 w-10 place-items-center rounded-2xl bg-cyan-300/15 text-cyan-100">SR</span><div><h1 class="text-2xl font-black text-white">SRBlogs</h1><p class="text-xs text-white/45">管理控制台</p></div></div>
        </div>
        <nav class="grid gap-1">
          <RouterLink v-for="link in links" :key="link[1]" :to="link[1]" class="relative z-[1] flex items-center justify-between rounded-2xl px-3 py-2.5 text-sm transition" :class="active === link[1] ? 'bg-cyan-300/[0.16] text-cyan-100' : 'text-white/64 hover:bg-white/10 hover:text-white'">
            <span>{{ link[0] }}</span><span class="text-[10px] text-white/35">{{ link[2] }}</span>
          </RouterLink>
        </nav>
        <button class="admin-btn admin-btn-ghost relative z-[1] mt-5 w-full text-sm" @click="logout">退出登录</button>
      </aside>
      <main class="min-w-0"><slot /></main>
      <aside class="hidden xl:block">
        <div class="glass sticky top-6 rounded-[32px] p-5">
          <div class="relative z-[1] flex items-center justify-between"><h2 class="font-black text-white">操作暂存区</h2><button class="text-xs text-white/45" @click="queueOpen = !queueOpen">{{ queueOpen ? '收起' : '展开' }}</button></div>
          <div v-if="queueOpen" class="relative z-[1] mt-4 grid gap-3">
            <div v-for="item in pending" :key="item" class="rounded-2xl border border-white/10 bg-white/[0.07] p-3 text-sm text-white/62">{{ item }}</div>
            <button class="admin-btn admin-btn-primary">更新本地</button>
            <button class="admin-btn admin-btn-ghost">同步 Blog</button>
            <p class="text-xs leading-5 text-white/36">当前仍以 FastAPI 直接持久化为主，pendingOperations 队列未实现。</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>
