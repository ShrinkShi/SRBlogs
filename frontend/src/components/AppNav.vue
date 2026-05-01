<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
const open = ref(false)
const route = useRoute()
const links = [
  ['首页', '/'], ['文章', '/posts'], ['时间线', '/timeline'], ['碎碎念', '/chatter'],
  ['友链', '/friends'], ['音乐', '/music'], ['照片墙', '/photowall'], ['项目', '/projects'], ['关于', '/about']
]
const activePath = computed(() => route.path)
</script>

<template>
  <header class="fixed left-0 right-0 top-0 z-40 px-3 py-4 md:px-5">
    <nav class="glass mx-auto flex max-w-7xl items-center justify-between rounded-[28px] px-4 py-3 md:px-5">
      <RouterLink to="/" class="group flex items-center gap-3">
        <span class="grid h-10 w-10 place-items-center rounded-2xl border border-cyan-200/25 bg-cyan-200/[0.12] shadow-[0_0_35px_rgba(34,211,238,.18)]">
          <span class="h-3 w-3 rounded-full bg-cyan-200 shadow-[0_0_18px_rgba(103,232,249,.9)]"></span>
        </span>
        <span>
          <span class="block text-lg font-black leading-tight text-white">SRBlogs</span>
          <span class="hidden text-[10px] uppercase tracking-[.32em] text-white/42 sm:block">glass console</span>
        </span>
      </RouterLink>
      <button class="relative z-[2] rounded-2xl border border-white/15 px-3 py-2 text-sm text-white/80 md:hidden" @click="open = !open">菜单</button>
      <div class="hidden items-center gap-1 md:flex">
        <RouterLink v-for="link in links" :key="link[1]" :to="link[1]" class="relative rounded-2xl px-3 py-2 text-sm transition" :class="activePath === link[1] ? 'bg-white/[0.14] text-white' : 'text-white/68 hover:bg-white/10 hover:text-white'">
          {{ link[0] }}
        </RouterLink>
        <a href="/admin/" class="ml-2 rounded-2xl border border-cyan-200/25 bg-cyan-300/[0.12] px-3 py-2 text-sm font-bold text-cyan-100 hover:bg-cyan-300/20">后台</a>
      </div>
    </nav>
    <div v-if="open" class="glass mx-auto mt-2 grid max-w-7xl grid-cols-2 gap-2 rounded-[28px] p-3 md:hidden">
      <RouterLink v-for="link in links" :key="link[1]" :to="link[1]" class="rounded-2xl px-3 py-2 text-sm text-white/80 hover:bg-white/10" @click="open = false">
        {{ link[0] }}
      </RouterLink>
      <a href="/admin/" class="rounded-2xl border border-cyan-200/25 px-3 py-2 text-sm text-cyan-100">后台</a>
    </div>
  </header>
</template>
