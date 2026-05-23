<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { contentApi, type CommentResource, type VisitorUser } from '@/api/content'
import GlassCard from './GlassCard.vue'
import type { CommentItem, SiteSettings } from '@/types'

const props = defineProps<{ resource: CommentResource; slug: string }>()

const comments = ref<CommentItem[]>([])
const settings = ref<SiteSettings | null>(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const form = reactive({ content: '' })
const visitor = ref<{ configured: { github: boolean; qq: boolean }; user: VisitorUser | null }>({
  configured: { github: false, qq: false },
  user: null
})
const showDebug = false

const options = computed(() => settings.value?.comments || {})
const providerOptions = computed(() => options.value.providers || {})
const boardEnabled = computed(() => options.value.enabled !== false)
const maxLength = computed(() => Number(options.value.maxLength || 1000))
const githubEnabled = computed(() => providerOptions.value.github?.enabled ?? options.value.githubLoginEnabled ?? true)
const qqEnabled = computed(() => providerOptions.value.qq?.enabled ?? options.value.qqLoginEnabled ?? true)
const githubConfigured = computed(() => {
  const github = providerOptions.value.github
  if (typeof github?.configured === 'boolean') return github.configured
  if (typeof github?.clientIdConfigured === 'boolean' || typeof github?.secretConfigured === 'boolean') {
    return github?.clientIdConfigured === true && github?.secretConfigured === true
  }
  return options.value.githubLoginConfigured ?? visitor.value.configured.github
})
const qqConfigured = computed(() => {
  const qq = providerOptions.value.qq
  if (typeof qq?.configured === 'boolean') return qq.configured
  if (typeof qq?.appIdConfigured === 'boolean' || typeof qq?.secretConfigured === 'boolean') {
    return qq?.appIdConfigured === true && qq?.secretConfigured === true
  }
  return options.value.qqLoginConfigured ?? visitor.value.configured.qq
})
const githubReady = computed(() => githubEnabled.value !== false && githubConfigured.value === true)
const qqReady = computed(() => qqEnabled.value !== false && qqConfigured.value === true)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [publicSettings, visitorState, list] = await Promise.all([
      contentApi.publicSettings<SiteSettings>(),
      contentApi.visitorMe(),
      contentApi.comments(props.resource, props.slug)
    ])
    settings.value = publicSettings
    visitor.value = visitorState
    comments.value = list
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言加载失败'
  } finally {
    loading.value = false
  }
}

function loginWith(provider: 'github' | 'qq') {
  const envBase = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  const localBackend = `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000/api`
  const fallbackBase = ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : '/api'
  const selectedBase = envBase === '/api' && ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : (envBase || fallbackBase)
  const rawBase = selectedBase.replace(/\/$/, '')
  const apiBase = rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`
  const returnTo = `${window.location.pathname}${window.location.search}${window.location.hash}`
  window.location.href = `${apiBase}/auth/${provider}/login?returnTo=${encodeURIComponent(returnTo)}`
}

async function logoutVisitor() {
  error.value = ''
  try {
    await contentApi.visitorLogout()
    visitor.value = await contentApi.visitorMe()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '退出登录失败'
  }
}

async function submit() {
  error.value = ''
  success.value = ''
  if (!boardEnabled.value) {
    error.value = '留言板已关闭。'
    return
  }
  if (!visitor.value.user) {
    error.value = '请先登录后再留言。'
    return
  }
  if (!form.content.trim()) {
    error.value = '留言内容不能为空。'
    return
  }
  if (form.content.length > maxLength.value) {
    error.value = `留言不能超过 ${maxLength.value} 个字符。`
    return
  }
  submitting.value = true
  try {
    const item = await contentApi.createComment(props.resource, props.slug, { content: form.content })
    comments.value.push(item)
    form.content = ''
    success.value = '留言已发布。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言提交失败'
  } finally {
    submitting.value = false
  }
}

function providerLabel(provider?: string) {
  if (provider === 'qq') return 'QQ'
  if (provider === 'github') return 'GitHub'
  return '访客'
}

function displayName(item: CommentItem) {
  if (item.githubLogin) return `@${item.githubLogin}`
  return item.author || '访客'
}

onMounted(load)
watch(() => `${props.resource}/${props.slug}`, load)
</script>

<template>
  <GlassCard class="comment-board mt-8">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-xs font-bold tracking-[.28em] text-cyan-100/45">留言</p>
        <h3 class="mt-1 text-2xl font-black text-white">留言板</h3>
        <p class="mt-2 text-sm text-white/52">登录后留言，站点只读取公开头像和昵称。</p>
      </div>
      <span class="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-white/50">{{ comments.length }} 条留言</span>
    </div>

    <p v-if="showDebug" class="mt-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-cyan-100/55">
      DEV 留言目标：{{ props.resource }}/{{ props.slug }}
    </p>

    <p v-if="loading" class="mt-4 text-white/50" role="status" aria-live="polite">留言加载中...</p>

    <div v-else class="mt-5 grid gap-3">
      <article v-for="item in comments" :key="item.id" class="rounded-[24px] border border-white/10 bg-white/[0.055] p-4">
        <div class="flex items-center justify-between gap-3 text-sm">
          <div class="flex min-w-0 items-center gap-3">
            <img v-if="item.avatar" :src="item.avatar" :alt="item.author" class="h-9 w-9 rounded-full object-cover" loading="lazy" />
            <div v-else class="grid h-9 w-9 place-items-center rounded-full bg-cyan-200/15 text-xs font-black text-cyan-100">
              {{ providerLabel(item.provider).slice(0, 2) }}
            </div>
            <div class="min-w-0">
              <b class="block truncate text-white/80">{{ displayName(item) }}</b>
              <span class="text-xs text-white/38">{{ providerLabel(item.provider) }}</span>
            </div>
          </div>
          <span class="shrink-0 text-white/45">{{ item.created_at }}</span>
        </div>
        <p class="mt-3 whitespace-pre-wrap break-words leading-7 text-white/70">{{ item.content }}</p>
      </article>
      <p v-if="!comments.length" class="rounded-[24px] border border-white/10 bg-white/[0.045] p-4 text-white/50">暂无留言。</p>
    </div>

    <div v-if="!boardEnabled" class="mt-5 rounded-[24px] border border-white/10 bg-white/[0.05] p-4 text-white/58">留言板已关闭。</div>
    <section v-else class="mt-5 rounded-[28px] border border-white/10 bg-white/[0.045] p-4">
      <div class="grid gap-4 lg:grid-cols-[auto_minmax(0,1fr)_auto] lg:items-start">
        <div class="grid justify-items-center gap-2">
          <img v-if="visitor.user?.avatar" :src="visitor.user.avatar" :alt="visitor.user.name || visitor.user.id" class="h-14 w-14 rounded-full object-cover ring-2 ring-cyan-200/25" loading="lazy" />
          <div v-else class="grid h-14 w-14 place-items-center rounded-full bg-white/[0.08] text-lg font-black text-white/55">Hi</div>
          <span class="max-w-[7rem] truncate text-xs text-white/45">{{ visitor.user ? `${providerLabel(visitor.user.provider)} · ${visitor.user.name || visitor.user.id}` : '访客' }}</span>
        </div>

        <form v-if="visitor.user" class="min-w-0" @submit.prevent="submit">
          <textarea
            v-model="form.content"
            :maxlength="maxLength"
            rows="4"
            class="w-full resize-none rounded-[22px] border border-white/10 bg-black/15 px-4 py-3 text-white outline-none transition placeholder:text-white/35 focus:border-cyan-300/60"
            placeholder="写下你的留言..."
          ></textarea>
          <div class="mt-2 flex flex-wrap items-center gap-3 text-xs">
            <span class="text-white/38">{{ form.content.length }} / {{ maxLength }}</span>
            <span v-if="success" class="text-emerald-200/85" role="status">{{ success }}</span>
            <span v-if="error" class="text-red-200/85" role="alert">{{ error }}</span>
          </div>
        </form>

        <div v-else class="min-w-0 rounded-[22px] border border-dashed border-white/12 bg-black/10 px-4 py-5 text-sm leading-7 text-white/55">
          <p v-if="githubReady || qqReady">请选择已启用的平台登录后留言。</p>
          <div v-else class="grid gap-2">
            <p v-if="githubEnabled !== false">站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。</p>
            <p v-if="qqEnabled !== false">站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。</p>
          </div>
          <p v-if="error" class="mt-2 text-red-200/85" role="alert">{{ error }}</p>
        </div>

        <div class="grid gap-2">
          <template v-if="!visitor.user">
            <button
              type="button"
              :disabled="!githubReady"
              class="rounded-2xl px-5 py-3 font-bold transition"
              :class="githubReady ? 'bg-cyan-300 text-slate-950 hover:scale-[1.02]' : 'border border-white/10 text-white/40'"
              @click="githubReady && loginWith('github')"
            >
              使用 GitHub 登录后留言
            </button>
            <button
              type="button"
              :disabled="!qqReady"
              class="rounded-2xl px-5 py-3 font-bold transition"
              :class="qqReady ? 'bg-emerald-300 text-slate-950 hover:scale-[1.02]' : 'border border-white/10 text-white/40'"
              @click="qqReady && loginWith('qq')"
            >
              使用 QQ 登录后留言
            </button>
          </template>
          <template v-else>
            <button type="button" :disabled="submitting" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50" @click="submit">
              {{ submitting ? '发布中...' : '发布留言' }}
            </button>
            <button type="button" class="rounded-2xl border border-white/10 px-5 py-2 text-sm text-white/52 hover:text-white" @click="logoutVisitor">退出登录</button>
          </template>
        </div>
      </div>
    </section>
  </GlassCard>
</template>
