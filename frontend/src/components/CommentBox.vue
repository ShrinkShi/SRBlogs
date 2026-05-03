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
const commentsEnabled = () => commentOptions().enabled !== false && commentOptions().localEnabled !== false
const maxLength = () => Number(commentOptions().maxLength || 1000)

async function load() {
  loading.value = true
  error.value = ''
  try {
    settings.value = await contentApi.json<SiteSettings>('/settings/public')
    github.value = await contentApi.githubMe()
    comments.value = await contentApi.comments(props.resource, props.slug)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论加载失败'
  } finally {
    loading.value = false
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  if (!commentsEnabled()) {
    error.value = '评论已关闭。'
    return
  }
  if (!github.value.user) {
    error.value = '请先使用 GitHub 登录后再评论。'
    return
  }
  if (!form.content.trim()) {
    error.value = '评论内容不能为空。'
    return
  }
  if (form.content.length > maxLength()) {
    error.value = `评论内容不能超过 ${maxLength()} 字。`
    return
  }
  submitting.value = true
  try {
    const item = await contentApi.createComment(props.resource, props.slug, { content: form.content })
    comments.value.push(item)
    form.content = ''
    success.value = '评论已提交。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '评论提交失败'
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
    <div class="flex items-center justify-between gap-3">
      <h3 class="text-xl font-black text-white">评论</h3>
      <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/50">{{ comments.length }} 条</span>
    </div>
    <p v-if="showDebug" class="mt-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-cyan-100/55">
      DEV comments target: {{ props.resource }}/{{ props.slug }}
    </p>
    <p v-if="loading" class="mt-4 text-white/50" role="status" aria-live="polite">评论加载中...</p>
    <div v-else class="mt-4 grid gap-3">
      <div v-for="item in comments" :key="item.id" class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between gap-3 text-sm">
          <div class="flex min-w-0 items-center gap-2">
            <img v-if="item.avatar" :src="item.avatar" :alt="item.author" class="h-8 w-8 rounded-full" loading="lazy" />
            <b class="truncate">{{ item.githubLogin ? `@${item.githubLogin}` : item.author }}</b>
          </div>
          <span class="text-white/45">{{ item.created_at }}</span>
        </div>
        <p class="mt-2 whitespace-pre-wrap break-words text-white/70">{{ item.content }}</p>
      </div>
      <p v-if="!comments.length" class="text-white/50">暂无评论。</p>
    </div>
    <div v-if="!commentsEnabled()" class="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4 text-white/58">评论已关闭。</div>
    <form v-else class="mt-5 grid gap-3" @submit.prevent="submit">
      <div v-if="!github.configured" class="rounded-2xl border border-amber-200/20 bg-amber-300/10 p-4 text-sm text-amber-50/80">
        GitHub 登录未配置，暂时无法发表评论。请在后端配置 GitHub OAuth Client ID 和 Secret。
      </div>
      <div v-else-if="!github.user" class="rounded-2xl border border-white/10 bg-white/[0.055] p-4">
        <p class="text-white/62">评论仅支持 GitHub 登录。登录后会使用你的 GitHub 公开头像和用户名发表评论。</p>
        <button type="button" class="mt-3 rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950" @click="loginWithGithub">使用 GitHub 登录后评论</button>
      </div>
      <template v-else>
        <div class="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/[0.055] p-3">
          <div class="flex min-w-0 items-center gap-3">
            <img v-if="github.user.avatar" :src="github.user.avatar" :alt="github.user.login" class="h-10 w-10 rounded-full" />
            <span class="truncate text-white/75">已登录 GitHub：@{{ github.user.login }}</span>
          </div>
          <button type="button" class="shrink-0 text-sm text-white/45 hover:text-white" @click="logoutGithub">退出</button>
        </div>
        <label class="grid gap-2 text-sm text-white/60">
          <span>评论内容</span>
          <textarea v-model="form.content" required :maxlength="maxLength()" rows="4" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-white outline-none focus:border-cyan-300/60" placeholder="写下评论，HTML 会被后端清洗"></textarea>
        </label>
        <div class="flex flex-wrap items-center gap-3">
          <button type="submit" :disabled="submitting" class="w-fit rounded-2xl bg-cyan-300 px-5 py-2 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50">{{ submitting ? '提交中...' : '发表评论' }}</button>
          <span v-if="success" class="text-sm text-emerald-200/80" role="status">{{ success }}</span>
          <span v-if="error" class="text-sm text-red-200/80" role="alert">{{ error }}</span>
        </div>
      </template>
    </form>
  </GlassCard>
</template>
