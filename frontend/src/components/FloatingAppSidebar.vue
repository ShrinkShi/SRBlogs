<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { floatingApps, type FloatingAppIcon, type FloatingAppItem } from '@/config/floatingApps'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'
import type { SiteSettings } from '@/types'
import calculatorIcon from '../../../assets/appicon/计算器.png'
import musicIcon from '../../../assets/appicon/音乐播放器.png'
import searchIcon from '../../../assets/appicon/全局搜索.png'
import settingsIcon from '../../../assets/appicon/设置.png'

const props = defineProps<{ settings?: SiteSettings | null }>()
const emit = defineEmits<{ action: [app: FloatingAppItem] }>()
const session = useSessionStore()
const ui = useUiStore()
const open = ref(false)
const authOpen = ref(false)
const authMode = ref<'login' | 'register'>('login')
const logoutConfirmOpen = ref(false)
const loggingIn = ref(false)
const accountError = ref('')
const form = reactive({ username: 'admin', password: '', email: '', emailPassword: '' })

const apps = computed(() =>
  floatingApps
    .filter((app) => app.enabled !== false)
    .filter((app) => !app.adminOnly || session.isAdmin)
    .sort((a, b) => Number(a.order ?? 0) - Number(b.order ?? 0))
)

const iconImages: Partial<Record<FloatingAppIcon, string>> = {
  settings: settingsIcon,
  music: musicIcon,
  search: searchIcon,
  calculator: calculatorIcon
}

function stringFromSettings(paths: string[]) {
  const root = (props.settings || {}) as Record<string, unknown>
  const profile = (root.profile || {}) as Record<string, unknown>
  const about = (root.about || {}) as Record<string, unknown>
  const candidates: Record<string, unknown> = { ...root, ...profile, ...about }
  for (const key of paths) {
    const value = candidates[key]
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return ''
}

const ownerName = computed(() =>
  stringFromSettings(['author', 'authorName', 'ownerName', 'name', 'siteOwner']) || '站点拥有者'
)
const ownerAvatar = computed(() =>
  stringFromSettings(['avatar', 'avatarUrl', 'authorAvatar', 'ownerAvatar'])
)
const isLoggedIn = computed(() => session.isAdmin || Boolean(session.visitor.user))
const accountName = computed(() => {
  if (session.isAdmin) return ownerName.value
  if (session.visitor.user) return session.visitor.user.name || session.visitor.user.login || session.visitor.user.id
  return '未登录'
})
const accountRole = computed(() => {
  if (session.isAdmin) return '管理员登录'
  if (session.visitor.user?.provider === 'github') return 'GitHub 登录'
  if (session.visitor.user?.provider === 'qq') return 'QQ 登录'
  return '游客浏览'
})
const accountAvatar = computed(() => session.isAdmin ? ownerAvatar.value : (session.visitor.user?.avatar || ''))
const accountInitials = computed(() => accountName.value.slice(0, 2).toUpperCase())
const canLogin = computed(() => !session.isAdmin && !session.visitor.user)

function iconImage(icon: FloatingAppIcon) {
  return iconImages[icon] || ''
}

function iconPath(icon: FloatingAppIcon) {
  const paths: Record<FloatingAppIcon, string> = {
    settings: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm8.5 3.5a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7.4 7.4 0 0 0-2-1.2L15.7 2h-4l-.4 3.2a7.4 7.4 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5A7 7 0 0 0 6.8 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1c.6.5 1.3.9 2 1.2l.4 3.2h4l.4-3.2c.7-.3 1.4-.7 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z',
    music: 'M9 18V5l11-2v13M9 18a3 3 0 1 1-2-2.8A3 3 0 0 1 9 18Zm11-2a3 3 0 1 1-2-2.8A3 3 0 0 1 20 16Z',
    search: 'M11 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm9 15-4.2-4.2',
    calculator: 'M6 3h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 4h8M8 12h.1M12 12h.1M16 12h.1M8 16h.1M12 16h.1M16 16h.1'
  }
  return paths[icon]
}

function apiBase() {
  const envBase = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  const localBackend = `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000/api`
  const fallbackBase = ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : '/api'
  const selectedBase = envBase === '/api' && ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : (envBase || fallbackBase)
  const rawBase = selectedBase.replace(/\/$/, '')
  return rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`
}

function trigger(app: FloatingAppItem) {
  emit('action', app)
  if (app.actionType !== 'toggle') open.value = false
}

function openAuth(mode: 'login' | 'register' = 'login') {
  accountError.value = ''
  authMode.value = mode
  authOpen.value = true
}

function providerLogin(provider: 'github' | 'qq') {
  if (!canLogin.value) return
  const returnTo = `${window.location.pathname}${window.location.search}${window.location.hash}`
  window.location.href = `${apiBase()}/auth/${provider}/login?returnTo=${encodeURIComponent(returnTo)}`
}

async function submitAdmin() {
  if (!canLogin.value) return
  loggingIn.value = true
  accountError.value = ''
  try {
    await session.loginAdmin(form.username.trim(), form.password)
    form.password = ''
    authOpen.value = false
    ui.showToast('已登录', 'success')
  } catch (exc) {
    accountError.value = exc instanceof Error ? exc.message : '管理员登录失败'
  } finally {
    loggingIn.value = false
  }
}

async function submitEmail() {
  if (!canLogin.value) return
  loggingIn.value = true
  accountError.value = ''
  try {
    await session.loginEmail(form.email.trim(), form.emailPassword, authMode.value)
    form.emailPassword = ''
    authOpen.value = false
    ui.showToast(authMode.value === 'register' ? '注册并登录成功' : '已登录', 'success')
  } catch (exc) {
    accountError.value = exc instanceof Error ? exc.message : '邮箱登录失败'
  } finally {
    loggingIn.value = false
  }
}

async function performLogout() {
  logoutConfirmOpen.value = false
  accountError.value = ''
  try {
    if (session.isAdmin) {
      session.logoutAdmin()
    } else if (session.visitor.user) {
      await session.logoutVisitor()
    }
    ui.showToast('已退出登录', 'success')
  } catch (exc) {
    accountError.value = exc instanceof Error ? exc.message : '退出失败'
    ui.showToast(accountError.value, 'error')
  }
}

onMounted(() => {
  session.refresh()
})
</script>

<template>
  <button
    v-if="!open"
    type="button"
    class="app-sidebar-toggle"
    aria-label="打开应用侧边栏"
    @click="open = true"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 5h6v6H4V5Zm10 0h6v6h-6V5ZM4 13h6v6H4v-6Zm10 0h6v6h-6v-6Z" />
    </svg>
  </button>

  <Transition name="app-sidebar-slide">
    <aside v-if="open" class="app-sidebar" aria-label="应用侧边栏">
      <header class="app-sidebar-head">
        <div>
          <p>Apps</p>
          <h2>功能应用</h2>
        </div>
        <button type="button" aria-label="收起应用侧边栏" @click="open = false">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
        </button>
      </header>

      <div class="app-sidebar-grid">
        <button
          v-for="app in apps"
          :key="app.id"
          type="button"
          class="app-sidebar-item"
          :title="app.tooltip || app.name"
          @click="trigger(app)"
        >
          <span class="app-sidebar-icon">
            <img v-if="iconImage(app.icon)" :src="iconImage(app.icon)" alt="" />
            <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path :d="iconPath(app.icon)" /></svg>
          </span>
          <span>{{ app.name }}</span>
        </button>
      </div>

      <footer class="app-sidebar-account">
        <div class="app-sidebar-account-card">
          <div class="app-sidebar-account-meta">
            <img v-if="accountAvatar" :src="accountAvatar" alt="" />
            <span v-else>{{ accountInitials }}</span>
            <div>
              <b>{{ accountName }}</b>
              <small>{{ accountRole }}</small>
            </div>
          </div>
          <button
            v-if="isLoggedIn"
            type="button"
            class="app-sidebar-auth-text app-sidebar-auth-logout"
            @click="logoutConfirmOpen = true"
          >
            退出登录
          </button>
          <button v-else type="button" class="app-sidebar-auth-text app-sidebar-auth-login" @click="openAuth('login')">
            登录/注册
          </button>
        </div>
      </footer>
    </aside>
  </Transition>

  <Teleport to="body">
    <Transition name="app-auth-fade">
      <div v-if="authOpen" class="app-auth-overlay" role="dialog" aria-modal="true" aria-label="登录或注册" @click.self="authOpen = false">
        <section class="app-auth-modal">
          <button type="button" class="app-auth-close" aria-label="关闭登录窗口" @click="authOpen = false">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
          <h2>登录或注册</h2>
          <p>登录后可以留言、上传附件，并在管理员身份下维护站点内容。</p>

          <div class="app-auth-providers">
            <button type="button" :disabled="!session.visitor.configured.github || !canLogin" @click="providerLogin('github')">
              使用 GitHub 继续
            </button>
            <button type="button" :disabled="!session.visitor.configured.qq || !canLogin" @click="providerLogin('qq')">
              使用 QQ 继续
            </button>
          </div>

          <div class="app-auth-divider"><span>或</span></div>

          <form class="app-auth-email" @submit.prevent="submitEmail">
            <input v-model="form.email" type="email" autocomplete="email" placeholder="电子邮件地址" />
            <input
              v-model="form.emailPassword"
              type="password"
              :autocomplete="authMode === 'register' ? 'new-password' : 'current-password'"
              placeholder="密码，至少 8 位"
            />
            <button type="submit" :disabled="loggingIn || !canLogin">
              {{ loggingIn ? '处理中...' : (authMode === 'register' ? '注册并登录' : '继续') }}
            </button>
          </form>

          <button type="button" class="app-auth-mode" @click="authMode = authMode === 'login' ? 'register' : 'login'">
            {{ authMode === 'login' ? '没有账号？使用邮箱注册' : '已有账号？返回登录' }}
          </button>

          <form class="app-auth-admin" @submit.prevent="submitAdmin">
            <p>管理员账号</p>
            <input v-model="form.username" autocomplete="username" placeholder="管理员账号" :disabled="!canLogin" />
            <input v-model="form.password" autocomplete="current-password" type="password" placeholder="管理员密码" :disabled="!canLogin" />
            <button type="submit" :disabled="loggingIn || !canLogin">{{ loggingIn ? '登录中...' : '管理员登录' }}</button>
          </form>

          <p v-if="accountError" class="app-auth-error">{{ accountError }}</p>
        </section>
      </div>
    </Transition>

    <Transition name="app-auth-fade">
      <div v-if="logoutConfirmOpen" class="app-auth-overlay" role="dialog" aria-modal="true" aria-label="退出登录确认" @click.self="logoutConfirmOpen = false">
        <section class="app-confirm-modal">
          <h2>确认退出</h2>
          <p>退出后将回到游客浏览状态，留言身份和管理员操作会被关闭。</p>
          <div>
            <button type="button" class="app-confirm-cancel" @click="logoutConfirmOpen = false">取消</button>
            <button type="button" class="app-confirm-danger" @click="performLogout">退出登录</button>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.app-sidebar-toggle {
  position: fixed;
  left: 1rem;
  bottom: 1rem;
  z-index: 88;
  display: grid;
  width: 3.65rem;
  height: 3.65rem;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, .14);
  border-radius: 999px;
  background: rgba(25, 26, 27, .92);
  color: #fecaca;
  box-shadow: 0 18px 48px rgba(0, 0, 0, .38), 0 0 0 1px rgba(244, 0, 2, .12) inset;
}
.app-sidebar-toggle svg,
.app-sidebar svg {
  width: 1.35rem;
  height: 1.35rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.1;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.app-sidebar {
  position: fixed;
  left: 1rem;
  bottom: 1rem;
  z-index: 89;
  display: grid;
  width: min(21rem, calc(100vw - 2rem));
  height: min(36rem, calc(100vh - 2rem));
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, .14);
  border-radius: 1.6rem;
  background: rgba(25, 26, 27, .94);
  padding: 1rem;
  color: white;
  box-shadow: 0 26px 80px rgba(0, 0, 0, .54), 0 0 0 1px rgba(244, 0, 2, .09) inset;
}
.app-sidebar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .8rem;
}
.app-sidebar-head p {
  color: rgba(255, 255, 255, .42);
  font-size: .72rem;
  font-weight: 900;
  letter-spacing: .22em;
  text-transform: uppercase;
}
.app-sidebar-head h2 {
  margin-top: .15rem;
  font-size: 1.25rem;
  font-weight: 900;
}
.app-sidebar-head button {
  display: grid;
  width: 2.3rem;
  height: 2.3rem;
  place-items: center;
  border-radius: 999px;
  background: white;
  color: black;
}
.app-sidebar-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-content: start;
  gap: .85rem;
  overflow-y: auto;
  padding: .2rem .1rem .4rem;
}
.app-sidebar-item {
  display: grid;
  justify-items: center;
  gap: .45rem;
  min-width: 0;
  border-radius: 1.2rem;
  padding: .55rem .35rem;
  color: rgba(255, 255, 255, .75);
}
.app-sidebar-item:hover {
  color: #fecaca;
}
.app-sidebar-icon {
  display: grid;
  width: 4.55rem;
  height: 4.55rem;
  place-items: center;
  border-radius: 1.25rem;
  border: 0;
  background: transparent;
  box-shadow: none;
  transition: transform .18s var(--motion-ease);
}
.app-sidebar-item:hover .app-sidebar-icon {
  transform: scale(1.16);
}
.app-sidebar-icon svg {
  width: 2.15rem;
  height: 2.15rem;
}
.app-sidebar-icon img {
  width: 3.45rem;
  height: 3.45rem;
  object-fit: contain;
}
.app-sidebar-item > span:last-child {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: .76rem;
  font-weight: 900;
}
.app-sidebar-account {
  border-top: 1px solid rgba(255, 255, 255, .1);
  padding-top: .85rem;
}
.app-sidebar-account-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .65rem;
  border-radius: 999px;
  background: #202123;
  padding: .65rem .75rem .65rem .65rem;
}
.app-sidebar-account-meta {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: .62rem;
}
.app-sidebar-account-meta img,
.app-sidebar-account-meta > span {
  display: grid;
  width: 2.55rem;
  height: 2.55rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 999px;
  background: rgba(248, 113, 113, .18);
  color: #fecaca;
  font-size: .78rem;
  font-weight: 900;
  object-fit: cover;
}
.app-sidebar-account-meta div {
  min-width: 0;
}
.app-sidebar-account-meta b,
.app-sidebar-account-meta small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.app-sidebar-account-meta b {
  font-size: .86rem;
}
.app-sidebar-account-meta small {
  color: rgba(255, 255, 255, .45);
  font-size: .68rem;
}
.app-sidebar-auth-text {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  padding: .25rem 0;
  font-size: .76rem;
  font-weight: 900;
}
.app-sidebar-auth-login {
  color: #86efac;
}
.app-sidebar-auth-logout {
  color: #f87171;
}
.app-auth-overlay {
  position: fixed;
  inset: 0;
  z-index: 110;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, .68);
  padding: 1rem;
}
.app-auth-modal,
.app-confirm-modal {
  position: relative;
  width: min(32rem, calc(100vw - 2rem));
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 1.5rem;
  background: #202123;
  color: white;
  padding: 2.2rem;
  box-shadow: 0 30px 90px rgba(0, 0, 0, .52);
}
.app-auth-close {
  position: absolute;
  right: 1rem;
  top: 1rem;
  display: grid;
  width: 2.4rem;
  height: 2.4rem;
  place-items: center;
  border-radius: 999px;
  color: white;
}
.app-auth-close svg {
  width: 1.25rem;
  height: 1.25rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  stroke-linecap: round;
}
.app-auth-modal h2,
.app-confirm-modal h2 {
  text-align: center;
  font-size: 2rem;
  font-weight: 900;
}
.app-auth-modal > p,
.app-confirm-modal > p {
  margin: .85rem auto 1.5rem;
  max-width: 24rem;
  text-align: center;
  color: rgba(255, 255, 255, .72);
  line-height: 1.7;
}
.app-auth-providers,
.app-auth-email,
.app-auth-admin {
  display: grid;
  gap: .75rem;
}
.app-auth-providers button,
.app-auth-email input,
.app-auth-email button,
.app-auth-admin input,
.app-auth-admin button,
.app-confirm-modal button {
  min-height: 3.1rem;
  border-radius: 999px;
  font-weight: 900;
}
.app-auth-providers button,
.app-auth-admin input,
.app-auth-email input {
  border: 1px solid rgba(255, 255, 255, .16);
  background: #050505;
  color: white;
  padding: 0 1.05rem;
}
.app-auth-providers button {
  background: transparent;
}
.app-auth-providers button:disabled,
.app-auth-admin button:disabled {
  cursor: not-allowed;
  opacity: .42;
}
.app-auth-email button,
.app-auth-admin button,
.app-confirm-cancel {
  background: white;
  color: black;
}
.app-auth-divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: .85rem;
  margin: 1.3rem 0;
  color: rgba(255, 255, 255, .42);
  font-size: .8rem;
}
.app-auth-divider::before,
.app-auth-divider::after {
  content: "";
  height: 1px;
  background: rgba(255, 255, 255, .12);
}
.app-auth-mode {
  margin: .9rem auto 1.15rem;
  display: block;
  color: rgba(255, 255, 255, .72);
  font-weight: 800;
}
.app-auth-admin {
  border-top: 1px solid rgba(255, 255, 255, .12);
  padding-top: 1rem;
}
.app-auth-admin p {
  color: rgba(255, 255, 255, .42);
  font-size: .78rem;
  font-weight: 900;
  letter-spacing: .12em;
}
.app-auth-error {
  margin-top: .9rem;
  color: #fecaca;
  text-align: center;
  font-weight: 800;
}
.app-confirm-modal div {
  display: flex;
  justify-content: center;
  gap: .75rem;
}
.app-confirm-modal button {
  min-width: 8rem;
  padding: 0 1rem;
}
.app-confirm-danger {
  background: #ef4444;
  color: white;
}
.app-sidebar-slide-enter-active,
.app-sidebar-slide-leave-active,
.app-auth-fade-enter-active,
.app-auth-fade-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.app-sidebar-slide-enter-from,
.app-sidebar-slide-leave-to {
  opacity: 0;
  transform: translateX(-.75rem) scale(.985);
}
.app-auth-fade-enter-from,
.app-auth-fade-leave-to {
  opacity: 0;
  transform: scale(.985);
}
@media (max-width: 640px) {
  .app-sidebar-toggle {
    left: .85rem;
    bottom: .85rem;
  }
  .app-sidebar {
    left: .85rem;
    right: .85rem;
    bottom: .85rem;
    width: auto;
    height: min(34rem, calc(100vh - 1.7rem));
  }
  .app-sidebar-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .app-sidebar-icon {
    width: 4rem;
    height: 4rem;
  }
  .app-auth-modal,
  .app-confirm-modal {
    padding: 1.7rem;
  }
}
</style>
