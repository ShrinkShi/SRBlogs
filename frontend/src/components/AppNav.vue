<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const open = ref(false)
const hidden = ref(false)
const route = useRoute()
const links = [
  ['首页', '/'],
  ['文章', '/posts'],
  ['相册', '/photowall'],
  ['说说', '/moments'],
  ['音乐', '/music'],
  ['项目', '/projects'],
  ['友链', '/friends']
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
      <RouterLink to="/" class="group flex min-w-0 items-center" aria-label="返回首页">
        <span class="block min-w-0 truncate text-[24px] font-black leading-tight text-[var(--text-primary)]">
          <span class="text-[#f40002]">&lt;</span>Shrink<span class="text-[#f40002]">/&gt;</span>
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

      <div class="hidden min-w-0 items-center gap-6 lg:flex xl:gap-10">
        <RouterLink
          v-for="link in links"
          :key="link[1]"
          :to="link[1]"
          class="nav-link relative rounded-2xl px-3 py-2 text-sm transition"
          :class="activePath === link[1] ? 'nav-link-active' : 'nav-link-idle'"
        >
          {{ link[0] }}
        </RouterLink>
      </div>
    </nav>

    <div v-if="open" id="mobile-nav" class="sr-page-shell grid grid-cols-2 gap-2 pb-3 sm:grid-cols-3 lg:hidden">
      <RouterLink
        v-for="link in links"
        :key="link[1]"
        :to="link[1]"
        class="rounded-2xl border border-white/10 bg-white/[0.07] px-3 py-2 text-sm text-white/80 hover:bg-white/10"
        @click="open = false"
      >
        {{ link[0] }}
      </RouterLink>
    </div>
  </header>
</template>
