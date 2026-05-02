<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const open = ref(false)
const hidden = ref(false)
const route = useRoute()
const links = [
  ['首页', '/'],
  ['文章', '/posts'],
  ['搜索', '/search'],
  ['归档', '/archive'],
  ['碎碎念', '/chatters'],
  ['友链', '/friends'],
  ['音乐', '/music'],
  ['照片墙', '/photowall'],
  ['项目', '/projects'],
  ['关于', '/about']
]
const activePath = computed(() => route.path)
let lastY = 0

function onScroll() {
  const current = window.scrollY
  if (current < 20 || current < lastY) hidden.value = false
  else if (current > 120 && current > lastY + 8) {
    hidden.value = true
    open.value = false
  }
  lastY = current
}

function onPointerMove(event: MouseEvent) {
  if (event.clientY < 72) hidden.value = false
}

onMounted(() => {
  lastY = window.scrollY
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('mousemove', onPointerMove, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('mousemove', onPointerMove)
})
</script>

<template>
  <header class="app-topbar fixed left-0 right-0 top-0 z-40" :class="hidden ? 'app-topbar-hidden' : ''">
    <nav class="sr-page-shell flex min-w-0 items-center justify-between gap-4 py-3" aria-label="前台导航">
      <RouterLink to="/" class="group flex min-w-0 items-center gap-3" aria-label="返回首页">
        <span class="grid h-11 w-11 shrink-0 place-items-center rounded-2xl border border-cyan-200/25 bg-cyan-200/[0.12] shadow-[0_0_35px_rgba(34,211,238,.18)]">
          <span class="h-3 w-3 rounded-full bg-cyan-200 shadow-[0_0_18px_rgba(103,232,249,.9)]"></span>
        </span>
        <span class="min-w-0">
          <span class="block truncate text-lg font-black leading-tight text-white">SRBlogs</span>
          <span class="hidden text-[10px] uppercase tracking-[.32em] text-white/42 sm:block">glass console</span>
        </span>
      </RouterLink>

      <button
        type="button"
        class="relative z-[2] shrink-0 rounded-2xl border border-white/15 px-3 py-2 text-sm text-white/80 lg:hidden"
        :aria-expanded="open"
        aria-controls="mobile-nav"
        aria-label="切换移动端导航菜单"
        @click="open = !open"
      >
        菜单
      </button>

      <div class="hidden min-w-0 items-center gap-1 lg:flex">
        <RouterLink
          v-for="link in links"
          :key="link[1]"
          :to="link[1]"
          class="relative rounded-2xl px-3 py-2 text-sm transition"
          :class="activePath === link[1] ? 'bg-white/[0.14] text-white shadow-[inset_0_-2px_0_rgba(103,232,249,.8)]' : 'text-white/68 hover:bg-white/10 hover:text-white'"
        >
          {{ link[0] }}
        </RouterLink>
        <a href="/admin/" class="ml-2 rounded-2xl border border-cyan-200/25 bg-cyan-300/[0.12] px-3 py-2 text-sm font-bold text-cyan-100 hover:bg-cyan-300/20">后台</a>
      </div>
    </nav>

    <div v-if="open" id="mobile-nav" class="sr-page-shell grid grid-cols-2 gap-2 pb-3 sm:grid-cols-3 lg:hidden">
      <RouterLink v-for="link in links" :key="link[1]" :to="link[1]" class="rounded-2xl border border-white/10 bg-white/[0.07] px-3 py-2 text-sm text-white/80 hover:bg-white/10" @click="open = false">
        {{ link[0] }}
      </RouterLink>
      <a href="/admin/" class="rounded-2xl border border-cyan-200/25 px-3 py-2 text-sm text-cyan-100">后台</a>
    </div>
  </header>
</template>
