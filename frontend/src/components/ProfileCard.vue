<script setup lang="ts">
import GlassCard from '@/components/GlassCard.vue'
import SafeImage from '@/components/SafeImage.vue'
import type { SiteSettings } from '@/types'
import { useUiStore } from '@/stores/ui'

const props = defineProps<{ settings?: SiteSettings | null; posts?: number; chatters?: number; photos?: number }>()
const ui = useUiStore()

const avatar = () => props.settings?.avatar || props.settings?.avatarUrl
const author = () => props.settings?.author || props.settings?.authorName || 'Shrink'
const description = () => props.settings?.description || props.settings?.bio || '在代码、文字与生活碎片之间，搭建一座轻量而清晰的个人博客。'
const social = () => props.settings?.socialLinks || props.settings?.social || {}
const github = () => social().github || 'https://github.com/ShrinkShi'
const email = () => social().email || 'you@example.com'
const qq = () => social().qq || '10000'
const wechat = () => social().wechat || 'srblogs'

async function copy(value: string, label: string) {
  try {
    await navigator.clipboard.writeText(value)
    ui.showToast(`${label} 已复制`, 'success')
  } catch {
    ui.showToast(`${label} 复制失败`, 'error')
  }
}
</script>

<template>
  <GlassCard hover class="min-h-full min-w-0 max-w-full">
    <div class="grid min-w-0 gap-6">
      <div class="grid min-w-0 gap-5 sm:grid-cols-[8.5rem_minmax(0,1fr)] sm:items-center">
        <div class="relative mx-auto sm:mx-0">
          <div class="absolute inset-0 rounded-[36px] bg-cyan-300/25 blur-2xl"></div>
          <SafeImage
            v-if="avatar()"
            :src="avatar()"
            :alt="author()"
            eager
            img-class="relative h-32 w-32 rounded-[36px] border border-white/20 object-cover shadow-2xl"
          />
          <div v-else class="relative grid h-32 w-32 place-items-center rounded-[36px] border border-white/20 bg-white/[0.12] text-4xl font-black text-white">SR</div>
        </div>
        <div class="min-w-0 text-center sm:text-left">
          <p class="text-xs font-bold uppercase tracking-[.32em] text-cyan-100/50">profile</p>
          <h2 class="mt-2 break-words text-4xl font-black text-white">{{ author() || 'Shrink' }}</h2>
          <p class="mt-3 max-w-2xl break-words text-sm leading-7 text-white/62">{{ description() }}</p>
        </div>
      </div>

      <div class="grid min-w-0 gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div class="grid min-w-0 grid-cols-3 gap-2">
          <RouterLink to="/posts" class="profile-plain-action min-w-0 p-3 text-center">
            <b class="block break-words text-2xl text-white">{{ props.posts || 0 }}</b>
            <span class="text-xs text-white/42">文章</span>
          </RouterLink>
          <RouterLink to="/chatters" class="profile-plain-action min-w-0 p-3 text-center">
            <b class="block break-words text-2xl text-white">{{ props.chatters || 0 }}</b>
            <span class="text-xs text-white/42">杂谈</span>
          </RouterLink>
          <RouterLink to="/photowall" class="profile-plain-action min-w-0 p-3 text-center">
            <b class="block break-words text-2xl text-white">{{ props.photos || 0 }}</b>
            <span class="text-xs text-white/42">照片</span>
          </RouterLink>
        </div>

        <div class="flex flex-wrap justify-center gap-2 lg:justify-end">
          <a :href="github()" target="_blank" rel="noopener noreferrer" class="profile-icon-action grid h-11 w-11 place-items-center" data-tip="github" aria-label="打开 GitHub">
            <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current text-white/72" aria-hidden="true">
              <path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.18-3.37-1.18-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.04 1.53 1.04.88 1.51 2.32 1.08 2.88.82.09-.65.35-1.08.63-1.33-2.22-.25-4.56-1.11-4.56-4.94 0-1.1.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.5 9.5 0 0 1 12 6.02c.85 0 1.7.11 2.5.34 1.9-1.3 2.74-1.03 2.74-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.86V21c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>
            </svg>
          </a>
          <button type="button" class="profile-icon-action grid h-11 w-11 place-items-center" data-tip="email" aria-label="复制邮箱" @click="copy(email(), '邮箱')">
            <svg viewBox="0 0 24 24" class="h-5 w-5 fill-none stroke-current text-white/72" aria-hidden="true">
              <path stroke-width="2" d="M4 6h16v12H4z"/><path stroke-width="2" d="m4 7 8 6 8-6"/>
            </svg>
          </button>
          <button type="button" class="profile-icon-action grid h-11 w-11 place-items-center" data-tip="qq" aria-label="复制 QQ" @click="copy(qq(), 'QQ')">
            <svg viewBox="0 0 24 24" class="h-5 w-5 fill-none stroke-current text-white/72" aria-hidden="true">
              <path stroke-width="2" d="M12 3c3 0 5 2.6 5 6.6 0 2 .7 3.4 1.5 4.7.4.7-.1 1.5-.9 1.3l-1.4-.3c-.8 1.8-2.2 3-4.2 3s-3.4-1.2-4.2-3l-1.4.3c-.8.2-1.3-.6-.9-1.3C6.3 13 7 11.6 7 9.6 7 5.6 9 3 12 3Z"/><path stroke-width="2" d="M9 21c.8-.8 1.8-1.2 3-1.2s2.2.4 3 1.2"/>
            </svg>
          </button>
          <button type="button" class="profile-icon-action grid h-11 w-11 place-items-center" data-tip="微信" aria-label="复制微信" @click="copy(wechat(), '微信')">
            <svg viewBox="0 0 24 24" class="h-5 w-5 fill-none stroke-current text-white/72" aria-hidden="true">
              <path stroke-width="2" d="M9.5 16.5c-3.6 0-6.5-2.2-6.5-5s2.9-5 6.5-5 6.5 2.2 6.5 5-2.9 5-6.5 5Z"/><path stroke-width="2" d="M14.5 10.5c3.6 0 6.5 2.2 6.5 5 0 1.2-.6 2.4-1.6 3.2l.4 2-2.3-1c-.9.5-1.9.8-3 .8-2.6 0-4.8-1.1-5.9-2.8"/><path stroke-width="2" d="M7.5 10h.01M11.5 10h.01M13.5 15h.01M17.5 15h.01"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </GlassCard>
</template>

<style scoped>
.profile-plain-action,
.profile-icon-action {
  position: relative;
  border: 0;
  background: transparent;
  border-radius: 1rem;
  color: rgba(255,255,255,.72);
  transition: transform .22s var(--motion-ease), opacity .22s var(--motion-ease), color .22s var(--motion-ease), text-shadow .22s var(--motion-ease);
}
.profile-plain-action:hover {
  transform: scale(1.12);
  opacity: .95;
}
.profile-icon-action:hover {
  transform: scale(1.1);
  opacity: .92;
}
.profile-plain-action:hover {
  text-shadow: 0 0 22px rgba(103,232,249,.28);
}
.profile-icon-action:hover {
  color: var(--accent);
}
.profile-icon-action:hover svg,
.profile-icon-action:focus-visible svg {
  color: var(--accent) !important;
}
.profile-icon-action::after {
  content: attr(data-tip);
  pointer-events: none;
  position: absolute;
  left: 50%;
  bottom: calc(100% + .45rem);
  transform: translateX(-50%) translateY(4px) scale(.96);
  opacity: 0;
  white-space: nowrap;
  border-radius: .7rem;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(2,6,23,.88);
  padding: .28rem .55rem;
  color: white;
  font-size: .68rem;
  font-weight: 800;
  transition: opacity .18s ease, transform .18s ease;
  z-index: 5;
}
.profile-icon-action:hover::after,
.profile-icon-action:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0) scale(1);
}
</style>
