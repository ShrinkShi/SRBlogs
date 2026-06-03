<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { contentApi, type CommentResource, type VisitorUser } from '@/api/content'
import GlassCard from './GlassCard.vue'
import SrTextButton from './ui/SrTextButton.vue'
import type { CommentAttachment, CommentItem, SiteSettings } from '@/types'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'

const props = withDefaults(defineProps<{ resource: CommentResource; slug: string; frameless?: boolean }>(), { frameless: false })
const session = useSessionStore()
const ui = useUiStore()

const comments = ref<CommentItem[]>([])
const settings = ref<SiteSettings | null>(null)
const loading = ref(false)
const submitting = ref(false)
const deletingCommentId = ref('')
const confirmDeleteId = ref('')
const error = ref('')
const success = ref('')
const form = reactive({ content: '' })
const attachments = ref<CommentAttachment[]>([])
const replyTarget = ref<CommentItem | null>(null)
const attachmentMenuOpen = ref(false)
const uploadingAttachment = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const imageInput = ref<HTMLInputElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const emojiList = ['😀', '😂', '🥹', '👍', '❤️', '🔥', '🎉', '🤝']
const visitor = ref<{ configured: { github: boolean; qq: boolean; email?: boolean }; user: VisitorUser | null }>({
  configured: { github: false, qq: false, email: true },
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
const showLoginHint = computed(() => !session.isAdmin && !visitor.value.user)
const adminAvatar = computed(() => {
  const root = (settings.value || {}) as Record<string, unknown>
  const profile = (root.profile || {}) as Record<string, unknown>
  const candidates = [root.avatar, root.avatarUrl, root.authorAvatar, root.ownerAvatar, profile.avatar]
  for (const value of candidates) {
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return ''
})
const adminName = computed(() => {
  const root = (settings.value || {}) as Record<string, unknown>
  const profile = (root.profile || {}) as Record<string, unknown>
  const about = (root.about || {}) as Record<string, unknown>
  const candidates = [
    root.author,
    root.authorName,
    profile.name,
    about.name,
    root.ownerName,
    root.siteOwner
  ]
  for (const value of candidates) {
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return '站点拥有者'
})
const activeCommenter = computed(() => {
  if (session.isAdmin) {
    return { name: adminName.value, avatar: adminAvatar.value, label: '管理员' }
  }
  if (visitor.value.user) {
    const user = visitor.value.user
    return {
      name: user.name || user.id,
      avatar: user.avatar || '',
      label: `${providerLabel(user.provider)} · ${user.name || user.id}`
    }
  }
  return null
})
const canComment = computed(() => Boolean(activeCommenter.value))
const canSubmit = computed(() => canComment.value && Boolean(form.content.trim()))

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

async function submit() {
  error.value = ''
  success.value = ''
  if (!session.isAdmin && !boardEnabled.value) {
    error.value = '留言板已关闭。'
    return
  }
  if (!canComment.value) {
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
    const item = await contentApi.createComment(props.resource, props.slug, {
      content: form.content,
      parentId: replyTarget.value?.id || '',
      attachments: attachments.value
    })
    comments.value.push(item)
    form.content = ''
    attachments.value = []
    replyTarget.value = null
    success.value = '留言已发布。'
    resizeComposer()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '留言提交失败'
  } finally {
    submitting.value = false
  }
}

function resizeComposer() {
  nextTick(() => {
    const el = textareaRef.value
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(180, Math.max(42, el.scrollHeight))}px`
  })
}

function startReply(item: CommentItem) {
  replyTarget.value = item
  textareaRef.value?.focus()
}

function cancelReply() {
  replyTarget.value = null
}

async function copyComment(item: CommentItem) {
  try {
    await navigator.clipboard.writeText(item.content)
    ui.showToast('留言内容已复制', 'success')
  } catch {
    ui.showToast('复制失败', 'error')
  }
}

function removeAttachment(index: number) {
  attachments.value.splice(index, 1)
}

async function uploadAttachment(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  ;(event.target as HTMLInputElement).value = ''
  attachmentMenuOpen.value = false
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ui.showToast('附件不能超过 2MB', 'error')
    return
  }
  uploadingAttachment.value = true
  try {
    const data = await contentApi.uploadCommentAttachment(file)
    attachments.value.push(data)
    ui.showToast('附件已上传', 'success')
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '附件上传失败', 'error')
  } finally {
    uploadingAttachment.value = false
  }
}

async function insertEmoji(emoji: string) {
  const el = textareaRef.value
  if (!el) {
    form.content += emoji
    return
  }
  const start = el.selectionStart
  const end = el.selectionEnd
  form.content = `${form.content.slice(0, start)}${emoji}${form.content.slice(end)}`
  await nextTick()
  el.focus()
  el.setSelectionRange(start + emoji.length, start + emoji.length)
  resizeComposer()
}

async function deleteComment(item: CommentItem) {
  if (!session.isAdmin || deletingCommentId.value) return
  if (confirmDeleteId.value !== item.id) {
    confirmDeleteId.value = item.id
    ui.showToast('再次点击删除以确认', 'info')
    window.setTimeout(() => {
      if (confirmDeleteId.value === item.id) confirmDeleteId.value = ''
    }, 3200)
    return
  }
  deletingCommentId.value = item.id
  error.value = ''
  try {
    await contentApi.deleteComment(props.resource, props.slug, item.id)
    comments.value = comments.value.filter((comment) => comment.id !== item.id)
    confirmDeleteId.value = ''
    ui.showToast('已删除', 'success')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '删除失败，请重试'
    ui.showToast('删除失败，请重试', 'error')
  } finally {
    deletingCommentId.value = ''
  }
}

function providerLabel(provider?: string) {
  if (provider === 'admin') return '管理员'
  if (provider === 'qq') return 'QQ'
  if (provider === 'email') return '邮箱'
  if (provider === 'github') return 'GitHub'
  return '访客'
}

function displayName(item: CommentItem) {
  if (item.githubLogin) return `@${item.githubLogin}`
  return item.author || '访客'
}

function replySummary(item: CommentItem) {
  return item.replyTo?.content || ''
}

function attachmentName(item: CommentAttachment) {
  return item.originalName || item.filename || '附件'
}

onMounted(load)
watch(() => `${props.resource}/${props.slug}`, load)
watch(() => form.content, resizeComposer)
</script>

<template>
  <component :is="props.frameless ? 'section' : GlassCard" class="comment-board" :class="props.frameless ? 'comment-board-frameless' : 'mt-8'">
    <div class="comment-section-divider" aria-hidden="true"></div>
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h3 class="mt-1 text-2xl font-black text-white">留言板</h3>
        <p v-if="showLoginHint" class="mt-2 text-sm text-white/52">登录后留言，站点只读取公开头像和昵称。</p>
      </div>
      <span class="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-white/50">{{ comments.length }} 条留言</span>
    </div>

    <p v-if="showDebug" class="mt-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 font-mono text-xs text-cyan-100/55">
      DEV 留言目标：{{ props.resource }}/{{ props.slug }}
    </p>

    <p v-if="loading" class="mt-4 text-white/50" role="status" aria-live="polite">留言加载中...</p>

    <div v-else class="comment-list">
      <article v-for="item in comments" :key="item.id" class="comment-item">
        <div class="flex items-start justify-between gap-3 text-sm">
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
          <div class="comment-item-actions">
            <span class="text-white/45">{{ item.created_at }}</span>
            <SrTextButton @click="copyComment(item)">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 8h10v12H8z" /><path d="M6 16H5a1 1 0 0 1-1-1V5h10v1" /></svg>
              复制
            </SrTextButton>
            <SrTextButton v-if="canComment" @click="startReply(item)">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 10 4 15l5 5" /><path d="M4 15h9a7 7 0 0 0 7-7V5" /></svg>
              回复
            </SrTextButton>
            <SrTextButton
              v-if="session.isAdmin"
              tone="danger"
              :disabled="deletingCommentId === item.id"
              @click="deleteComment(item)"
            >
              {{ deletingCommentId === item.id ? '删除中' : confirmDeleteId === item.id ? '确认删除' : '删除' }}
            </SrTextButton>
          </div>
        </div>
        <div v-if="item.replyTo?.id" class="comment-reply-card">
          <b>回复 @{{ item.replyTo.author || '访客' }}</b>
          <span>{{ replySummary(item) || '原留言暂无摘要' }}</span>
        </div>
        <p class="comment-content" :class="{ 'comment-content-locked': !session.isAdmin }">{{ item.content }}</p>
        <div v-if="item.attachments?.length" class="comment-attachments">
          <a
            v-for="attachment in item.attachments"
            :key="attachment.url"
            :href="attachment.url"
            target="_blank"
            rel="noopener noreferrer"
            class="comment-attachment"
          >
            <img v-if="attachment.kind === 'image'" :src="attachment.url" :alt="attachmentName(attachment)" loading="lazy" />
            <span v-else>📎</span>
            <b>{{ attachmentName(attachment) }}</b>
          </a>
        </div>
      </article>
      <p v-if="!comments.length" class="comment-empty">暂无留言。</p>
    </div>

    <div v-if="!boardEnabled && !session.isAdmin" class="mt-5 rounded-[24px] border border-white/10 bg-white/[0.05] p-4 text-white/58">留言板已关闭。</div>
    <section v-else class="comment-composer-section">
      <form v-if="canComment" class="comment-composer" @submit.prevent="submit">
        <div v-if="replyTarget" class="comment-replying">
          <span>回复 @{{ displayName(replyTarget) }}：{{ replyTarget.content.slice(0, 60) }}</span>
          <SrTextButton @click="cancelReply">取消</SrTextButton>
        </div>
        <div class="comment-input-shell">
          <button type="button" class="comment-plus-btn" aria-label="添加附件" @click="attachmentMenuOpen = !attachmentMenuOpen">+</button>
          <div v-if="attachmentMenuOpen" class="comment-attach-menu">
            <button type="button" class="comment-attach-option" data-tip="选择本地图片" @click="imageInput?.click()">上传图片</button>
            <button type="button" class="comment-attach-option" data-tip="选择本地文件" @click="fileInput?.click()">上传文件</button>
            <div class="comment-emoji-grid" aria-label="插入表情">
              <button v-for="emoji in emojiList" :key="emoji" type="button" @click="insertEmoji(emoji)">{{ emoji }}</button>
            </div>
          </div>
          <input ref="imageInput" type="file" accept="image/*" class="hidden" @change="uploadAttachment" />
          <input ref="fileInput" type="file" accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf" class="hidden" @change="uploadAttachment" />
          <textarea
            ref="textareaRef"
            v-model="form.content"
            :maxlength="maxLength"
            rows="1"
            class="comment-textarea"
            placeholder="写下你的留言..."
            @input="resizeComposer"
          ></textarea>
          <button type="submit" class="comment-submit-round" :disabled="submitting || uploadingAttachment || !canSubmit" aria-label="发布留言">
            {{ submitting ? '…' : '↵' }}
          </button>
        </div>
        <div v-if="attachments.length" class="comment-attachment-drafts">
          <span v-for="(attachment, index) in attachments" :key="attachment.url">
            {{ attachmentName(attachment) }}
            <button type="button" @click="removeAttachment(index)">移除</button>
          </span>
        </div>
        <div class="comment-composer-meta">
          <span>{{ form.content.length }} / {{ maxLength }}</span>
          <span v-if="success" class="comment-success" role="status">{{ success }}</span>
          <span v-if="error" class="comment-error" role="alert">{{ error }}</span>
        </div>
      </form>

      <div v-else class="comment-login-panel">
          <p v-if="githubReady || qqReady">请选择已启用的平台登录后留言。</p>
          <div v-else class="grid gap-2">
            <p v-if="githubEnabled !== false">站点暂未开启 GitHub 留言，请稍后再试或联系站点管理员。</p>
            <p v-if="qqEnabled !== false">站点暂未开启 QQ 留言，请稍后再试或联系站点管理员。</p>
          </div>
          <p v-if="error" class="mt-2 text-red-200/85" role="alert">{{ error }}</p>
        <div class="comment-login-actions">
          <button
            type="button"
            :disabled="!githubReady"
            :class="githubReady ? 'comment-auth-btn comment-auth-black' : 'comment-auth-btn comment-auth-disabled'"
            @click="githubReady && loginWith('github')"
          >
            使用 GitHub 登录后留言
          </button>
          <button
            type="button"
            :disabled="!qqReady"
            :class="qqReady ? 'comment-auth-btn comment-auth-green' : 'comment-auth-btn comment-auth-disabled'"
            @click="qqReady && loginWith('qq')"
          >
            使用 QQ 登录后留言
          </button>
        </div>
      </div>
    </section>
  </component>
</template>

<style scoped>
.comment-board-frameless {
  display: block;
}
.comment-section-divider {
  height: 1px;
  margin: 0 0 1.6rem;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .18), transparent);
}
.comment-list {
  display: grid;
  margin-top: 1.25rem;
}
.comment-item {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, .11);
}
.comment-item:first-child {
  border-top: 1px solid rgba(255, 255, 255, .11);
}
.comment-empty {
  border-top: 1px solid rgba(255, 255, 255, .11);
  border-bottom: 1px solid rgba(255, 255, 255, .11);
  padding: 1rem 0;
  color: rgba(255, 255, 255, .5);
}
.comment-item-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: .75rem;
}
.comment-item-actions svg {
  width: .9rem;
  height: .9rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.comment-reply-card {
  display: grid;
  gap: .2rem;
  margin: .85rem 0 0 3rem;
  border-left: 2px solid rgba(255, 255, 255, .18);
  padding-left: .75rem;
  color: rgba(255, 255, 255, .48);
  font-size: .82rem;
}
.comment-reply-card b {
  color: rgba(255, 255, 255, .68);
}
.comment-content {
  margin-top: .8rem;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.75;
  color: rgba(255, 255, 255, .72);
}
.comment-content-locked {
  user-select: none;
}
.comment-attachments,
.comment-attachment-drafts {
  display: flex;
  flex-wrap: wrap;
  gap: .55rem;
  margin-top: .75rem;
}
.comment-attachment {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  max-width: 15rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, .07);
  padding: .35rem .65rem;
  color: rgba(255, 255, 255, .7);
  font-size: .78rem;
}
.comment-attachment img {
  width: 1.35rem;
  height: 1.35rem;
  border-radius: 999px;
  object-fit: cover;
}
.comment-attachment b,
.comment-attachment-drafts span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comment-composer-section {
  margin-top: 1.25rem;
}
.comment-composer {
  display: grid;
  gap: .65rem;
}
.comment-replying {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .75rem;
  color: rgba(255, 255, 255, .52);
  font-size: .82rem;
}
.comment-replying span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comment-input-shell {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: end;
  gap: .55rem;
  border-radius: 1.35rem;
  background: #333335;
  padding: .55rem;
}
.comment-textarea {
  min-height: 42px;
  max-height: 180px;
  resize: none;
  border: 0;
  background: transparent;
  padding: .58rem 2.8rem .58rem .35rem;
  color: white;
  line-height: 1.55;
  outline: none;
}
.comment-textarea::placeholder {
  color: rgba(255, 255, 255, .36);
}
.comment-plus-btn {
  position: relative;
  display: grid;
  width: 2.35rem;
  height: 2.35rem;
  place-items: center;
  align-self: end;
  border: 0;
  border-radius: 999px;
  background: #333335;
  color: white;
  font-size: 1.25rem;
  font-weight: 900;
  transition: background .18s ease, transform .18s ease;
}
.comment-plus-btn:hover,
.comment-plus-btn:focus-visible {
  background: #3d3d40;
}
.comment-plus-btn:active {
  transform: scale(.96);
  background: #454548;
}
.comment-submit-round {
  position: absolute;
  right: .65rem;
  bottom: .65rem;
  display: grid;
  width: 2.15rem;
  height: 2.15rem;
  place-items: center;
  border-radius: 999px;
  background: white;
  color: black;
  font-size: 1.1rem;
  font-weight: 900;
}
.comment-submit-round:disabled {
  cursor: not-allowed;
  opacity: .42;
}
.comment-attach-menu {
  position: absolute;
  left: .55rem;
  bottom: calc(100% + .45rem);
  z-index: 3;
  display: grid;
  min-width: 10.5rem;
  gap: .35rem;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 1rem;
  background: #191A1B;
  padding: .55rem;
  box-shadow: 0 18px 42px rgba(0, 0, 0, .44);
}
.comment-attach-option {
  position: relative;
  border-radius: 999px;
  background: #333335;
  padding: .45rem .7rem;
  color: rgba(255, 255, 255, .78);
  font-weight: 900;
  text-align: left;
  transition: background .18s ease, color .18s ease;
}
.comment-attach-option:hover {
  background: #424245;
  color: white;
}
.comment-attach-option:hover::after,
.comment-attach-option:focus-visible::after {
  content: attr(data-tip);
  position: absolute;
  left: calc(100% + .5rem);
  top: 50%;
  z-index: 4;
  transform: translateY(-50%);
  white-space: nowrap;
  border-radius: 999px;
  background: rgba(255, 255, 255, .94);
  padding: .32rem .55rem;
  color: black;
  font-size: .72rem;
  box-shadow: 0 12px 28px rgba(0, 0, 0, .28);
}
.comment-emoji-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .32rem;
  border-top: 1px solid rgba(255, 255, 255, .1);
  margin-top: .2rem;
  padding-top: .45rem;
}
.comment-emoji-grid button {
  display: grid;
  min-height: 2rem;
  place-items: center;
  border-radius: .75rem;
  background: #333335;
  transition: background .18s ease, transform .18s ease;
}
.comment-emoji-grid button:hover {
  background: #424245;
  transform: translateY(-1px);
}
.comment-attachment-drafts span {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  max-width: 16rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, .08);
  padding: .35rem .6rem;
  color: rgba(255, 255, 255, .64);
  font-size: .76rem;
}
.comment-attachment-drafts button {
  color: #fecaca;
  font-weight: 900;
}
.comment-composer-meta {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem;
  color: rgba(255, 255, 255, .38);
  font-size: .78rem;
}
.comment-success {
  color: rgba(187, 247, 208, .86);
}
.comment-error {
  color: rgba(254, 202, 202, .9);
}
.comment-login-panel {
  display: grid;
  gap: .85rem;
  color: rgba(255, 255, 255, .56);
  font-size: .9rem;
  line-height: 1.75;
}
.comment-login-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .65rem;
}
.comment-auth-btn {
  border-radius: 999px;
  padding: .7rem 1rem;
  font-weight: 900;
}
.comment-auth-black {
  background: black;
  color: white;
}
.comment-auth-green {
  background: #86efac;
  color: black;
}
.comment-auth-disabled {
  cursor: not-allowed;
  background: rgba(255, 255, 255, .1);
  color: rgba(255, 255, 255, .4);
}
@media (max-width: 720px) {
  .comment-item-actions {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
  .comment-reply-card {
    margin-left: 0;
  }
}
</style>
