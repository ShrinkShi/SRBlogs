<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { contentApi } from '@/api/content'
import GlassCard from './GlassCard.vue'
import type { CommentItem, SiteSettings } from '@/types'

const props = defineProps<{ resource: 'posts' | 'moments' | 'chatters'; slug: string }>()
const comments = ref<CommentItem[]>([])
const settings = ref<SiteSettings | null>(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ content: '' })
const github = ref<{ configured: boolean; user: null | { login: string; name?: string; avatar?: string; html_url?: string } }>({ configured: false, user: null })
const showDebug = import.meta.env.DEV

const commentOptions = () => settings.value?.comments || {}
const boardEnabled = () => commentOptions().enabled !== false
const maxLength = () => Number(commentOptions().maxLength || 1000)

async function load() {
  loading.value = true
  error.value = ''
  try {
    settings.value = await contentApi.json<SiteSettings>('/settings/public')
    github.value = await contentApi.githubMe()
    comments.value = await contentApi.comments(props.resource, props.slug)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言加载失败'
  } finally {
    loading.value = false
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  if (!boardEnabled()) {
    error.value = '留言板暂时关闭。'
    return
  }
  if (!github.value.user) {
    error.value = '请先使用 GitHub 登录后再留言。'
    return
  }
  if (!form.content.trim()) {
    error.value = '留言内容不能为空。'
    return
  }
  if (form.content.length > maxLength()) {
    error.value = `留言内容不能超过 ${maxLength()} 字。`
    return
  }
  submitting.value = true
  try {
    const item = await contentApi.createComment(props.resource, props.slug, { content: form.content })
    comments.value.push(item)
    form.content = ''
    success.value = '留言已提交。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言提交失败'
  } finally {
    submitting.value = false
  }
}

function loginWithGithub() {
  window.location.href = `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/github/login?return_to=${encodeURIComponent(window.location.href)}`
}

async function logoutGithub() {
  await contentApi.githubLogout()
  github.value = await contentApi.githubMe()
}

onMounted(load)
watch(() => props.slug, load)
</script>

<template>
  <GlassCard class="mt-8">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">message board</p>
        <h3 class="mt-1 text-2xl font-black text-white">留言板</h3>
        <p class="mt-2 text-sm text-white/52">使用 GitHub 登录后留言，站点只会读取你的公开头像和用户名。</p>
      </div>
      <span class="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-white/50">{{ comments.length }} 条留言</span>
    </div>

    <p v-if="showDebug" class="mt-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-cyan-100/55">
      DEV message target: {{ props.resource }}/{{ props.slug }}
    </p>

    <p v-if="loading" class="mt-4 text-white/50" role="status" aria-live="polite">留言加载中...</p>

    <div v-else class="mt-5 grid gap-3">
      <article v-for="item in comments" :key="item.id" class="rounded-[24px] border border-white/10 bg-white/[0.055] p-4">
        <div class="flex items-center justify-between gap-3 text-sm">
          <div class="flex min-w-0 items-center gap-3">
            <img v-if="item.avatar" :src="item.avatar" :alt="item.author" class="h-9 w-9 rounded-full" loading="lazy" />
            <div v-else class="grid h-9 w-9 rounded-full bg-cyan-200/15 place-items-center text-xs font-black text-cyan-100">G</div>
            <b class="truncate text-white/80">{{ item.githubLogin ? `@${item.githubLogin}` : item.author }}</b>
          </div>
          <span class="shrink-0 text-white/45">{{ item.created_at }}</span>
        </div>
        <p class="mt-3 whitespace-pre-wrap break-words leading-7 text-white/70">{{ item.content }}</p>
      </article>
      <p v-if="!comments.length" class="rounded-[24px] border border-white/10 bg-white/[0.045] p-4 text-white/50">暂无留言。</p>
    </div>

    <div v-if="!boardEnabled()" class="mt-5 rounded-[24px] border border-white/10 bg-white/[0.05] p-4 text-white/58">留言板暂时关闭。</div>
    <form v-else class="mt-5 rounded-[28px] border border-white/10 bg-white/[0.045] p-4" @submit.prevent="submit">
      <div class="grid gap-4 lg:grid-cols-[auto_minmax(0,1fr)_auto] lg:items-start">
        <div class="grid justify-items-center gap-2">
          <img v-if="github.user?.avatar" :src="github.user.avatar" :alt="github.user.login" class="h-14 w-14 rounded-full ring-2 ring-cyan-200/25" />
          <div v-else class="grid h-14 w-14 place-items-center rounded-full bg-white/[0.08] text-lg font-black text-white/55">GH</div>
          <span class="max-w-[6rem] truncate text-xs text-white/45">{{ github.user ? `@${github.user.login}` : '访客' }}</span>
        </div>

        <div class="min-w-0">
          <textarea
            v-model="form.content"
            :disabled="!github.user || !github.configured"
            :maxlength="maxLength()"
            rows="4"
            class="w-full resize-none rounded-[22px] border border-white/10 bg-black/15 px-4 py-3 text-white outline-none transition placeholder:text-white/35 focus:border-cyan-300/60 disabled:cursor-not-allowed disabled:opacity-60"
            placeholder="登录 GitHub 后写下留言..."
          ></textarea>
          <div class="mt-2 flex flex-wrap items-center gap-3 text-xs">
            <span class="text-white/38">{{ form.content.length }} / {{ maxLength() }}</span>
            <span v-if="success" class="text-emerald-200/85" role="status">{{ success }}</span>
            <span v-if="error" class="text-red-200/85" role="alert">{{ error }}</span>
          </div>
        </div>

        <div class="grid gap-2">
          <div v-if="!github.configured" class="max-w-[16rem] rounded-2xl border border-amber-200/20 bg-amber-300/10 p-3 text-sm leading-6 text-amber-50/82">
            站点暂未开启 GitHub 登录留言，请稍后再试或联系站点管理员。
          </div>
          <button v-else-if="!github.user" type="button" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="loginWithGithub">
            使用 GitHub 登录
          </button>
          <template v-else>
            <button type="submit" :disabled="submitting" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50">
              {{ submitting ? '提交中...' : '发布留言' }}
            </button>
            <button type="button" class="rounded-2xl border border-white/10 px-5 py-2 text-sm text-white/52 hover:text-white" @click="logoutGithub">退出登录</button>
          </template>
        </div>
      </div>
    </form>
  </GlassCard>
</template>
