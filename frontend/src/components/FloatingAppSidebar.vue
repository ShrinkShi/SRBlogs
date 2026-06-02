<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { floatingApps, type FloatingAppIcon, type FloatingAppItem } from '@/config/floatingApps'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'

const emit = defineEmits<{ action: [app: FloatingAppItem] }>()
const session = useSessionStore()
const ui = useUiStore()
const open = ref(false)
const accountOpen = ref(false)
const loggingIn = ref(false)
const accountError = ref('')
const form = reactive({ username: 'admin', password: '' })

const apps = computed(() =>
  floatingApps
    .filter((app) => app.enabled !== false)
    .filter((app) => !app.adminOnly || session.isAdmin)
    .sort((a, b) => Number(a.order ?? 0) - Number(b.order ?? 0))
)

const accountInitials = computed(() => session.displayName.slice(0, 2).toUpperCase())
const hasVisitorLogin = computed(() => Boolean(session.visitor.user))
const canUseVisitorLogin = computed(() => !session.isAdmin && !hasVisitorLogin.value)
const canUseAdminLogin = computed(() => !session.isAdmin && !hasVisitorLogin.value)

function iconPath(icon: FloatingAppIcon) {
  const paths: Record<FloatingAppIcon, string> = {
    settings: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm8.5 3.5a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7.4 7.4 0 0 0-2-1.2L15.7 2h-4l-.4 3.2a7.4 7.4 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5A7 7 0 0 0 6.8 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1c.6.5 1.3.9 2 1.2l.4 3.2h4l.4-3.2c.7-.3 1.4-.7 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z',
    music: 'M9 18V5l11-2v13M9 18a3 3 0 1 1-2-2.8A3 3 0 0 1 9 18Zm11-2a3 3 0 1 1-2-2.8A3 3 0 0 1 20 16Z',
    search: 'M11 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm9 15-4.2-4.2',
    calculator: 'M6 3h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 4h8M8 12h.1M12 12h.1M16 12h.1M8 16h.1M12 16h.1M16 16h.1',
    article: 'M6 4h9l3 3v13H6V4Zm8 0v4h4M9 11h6M9 15h6M9 18h4',
    update: 'M20 6v5h-5M4 18v-5h5M18.6 9a7 7 0 0 0-11.2-2.2L4 10m16 4-3.4 3.2A7 7 0 0 1 5.4 15'
  }
  return paths[icon]
}

function trigger(app: FloatingAppItem) {
  emit('action', app)
  if (app.actionType !== 'toggle') open.value = false
}

async function submitAdmin() {
  loggingIn.value = true
  accountError.value = ''
  try {
    await session.loginAdmin(form.username.trim(), form.password)
    form.password = ''
    ui.showToast('管理员已登录', 'success')
  } catch (exc) {
    accountError.value = exc instanceof Error ? exc.message : '管理员登录失败'
  } finally {
    loggingIn.value = false
  }
}

async function logoutVisitor() {
  accountError.value = ''
  try {
    await session.logoutVisitor()
    ui.showToast('已退出访客登录', 'success')
  } catch (exc) {
    accountError.value = exc instanceof Error ? exc.message : '退出失败'
  }
}

function logoutAdmin() {
  session.logoutAdmin()
  ui.showToast('管理员已退出', 'success')
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
            <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="iconPath(app.icon)" /></svg>
          </span>
          <span>{{ app.name }}</span>
        </button>
      </div>

      <footer class="app-sidebar-account">
        <button type="button" class="app-sidebar-account-trigger" @click="accountOpen = !accountOpen">
          <img v-if="session.avatar" :src="session.avatar" alt="" />
          <span v-else>{{ accountInitials }}</span>
          <b>{{ session.displayName }}</b>
          <small>{{ session.displayRole }}</small>
        </button>

        <Transition name="app-account-pop">
          <section v-if="accountOpen" class="app-account-panel">
            <button
              type="button"
              class="app-account-primary"
              :disabled="!session.visitor.configured.github || !canUseVisitorLogin"
              @click="session.loginWithGithub"
            >
              使用 GitHub 登录
            </button>
            <p v-if="!session.visitor.configured.github" class="app-account-note">站点尚未配置 GitHub 登录。</p>
            <p v-else-if="session.isAdmin" class="app-account-note">管理员已登录，请先退出管理员账号再使用 GitHub 登录。</p>
            <button v-if="session.visitor.user" type="button" class="app-account-ghost" @click="logoutVisitor">退出 GitHub / QQ</button>

            <form class="app-account-form" @submit.prevent="submitAdmin">
              <p>管理员登录</p>
              <p v-if="hasVisitorLogin" class="app-account-note">请先退出当前 GitHub / QQ 登录，再登录管理员账号。</p>
              <input v-model="form.username" autocomplete="username" placeholder="管理员账号" :disabled="!canUseAdminLogin" />
              <input v-model="form.password" autocomplete="current-password" type="password" placeholder="管理员密码" :disabled="!canUseAdminLogin" />
              <button type="submit" class="app-account-primary app-account-admin" :disabled="loggingIn || !canUseAdminLogin">
                {{ loggingIn ? '登录中...' : '管理员登录' }}
              </button>
            </form>
            <button v-if="session.isAdmin" type="button" class="app-account-ghost" @click="logoutAdmin">退出管理员</button>
            <p v-if="accountError" class="app-account-error">{{ accountError }}</p>
          </section>
        </Transition>
      </footer>
    </aside>
  </Transition>
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
.app-sidebar-head,
.app-sidebar-account-trigger {
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
  transition: transform .18s var(--motion-ease), background .18s var(--motion-ease), color .18s var(--motion-ease);
}
.app-sidebar-item:hover {
  background: rgba(248, 113, 113, .12);
  color: #fecaca;
  transform: translateY(-2px);
}
.app-sidebar-icon {
  display: grid;
  width: 3.75rem;
  height: 3.75rem;
  place-items: center;
  border-radius: 1.25rem;
  border: 1px solid rgba(255, 255, 255, .12);
  background: #202123;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .08);
}
.app-sidebar-icon svg {
  width: 1.65rem;
  height: 1.65rem;
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
  position: relative;
  border-top: 1px solid rgba(255, 255, 255, .1);
  padding-top: .85rem;
}
.app-sidebar-account-trigger {
  width: 100%;
  border-radius: 999px;
  background: #202123;
  padding: .65rem;
  text-align: left;
}
.app-sidebar-account-trigger img,
.app-sidebar-account-trigger > span {
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
.app-sidebar-account-trigger b {
  min-width: 0;
  flex: 1 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: .86rem;
}
.app-sidebar-account-trigger small {
  flex: 0 0 auto;
  color: rgba(255, 255, 255, .45);
  font-size: .68rem;
}
.app-account-panel {
  position: absolute;
  left: 0;
  right: 0;
  bottom: calc(100% + .75rem);
  display: grid;
  gap: .55rem;
  border: 1px solid rgba(255, 255, 255, .14);
  border-radius: 1.25rem;
  background: rgba(25, 26, 27, .98);
  padding: .85rem;
  box-shadow: 0 18px 48px rgba(0, 0, 0, .46);
}
.app-account-form {
  display: grid;
  gap: .5rem;
  border-top: 1px solid rgba(255, 255, 255, .1);
  padding-top: .65rem;
}
.app-account-form p {
  color: rgba(255, 255, 255, .42);
  font-size: .72rem;
  font-weight: 900;
}
.app-account-form input {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 999px;
  background: #202123;
  padding: .62rem .75rem;
  color: white;
  outline: none;
}
.app-account-primary,
.app-account-ghost {
  border-radius: 999px;
  padding: .65rem .8rem;
  font-weight: 900;
}
.app-account-primary {
  background: black;
  color: white;
}
.app-account-admin {
  background: #86efac;
  color: black;
}
.app-account-primary:disabled {
  cursor: not-allowed;
  background: rgba(255, 255, 255, .08);
  color: rgba(255, 255, 255, .35);
}
.app-account-ghost {
  background: white;
  color: black;
}
.app-account-note,
.app-account-error {
  font-size: .76rem;
  line-height: 1.45;
}
.app-account-note {
  color: rgba(255, 255, 255, .42);
}
.app-account-error {
  color: #fecaca;
}
.app-sidebar-slide-enter-active,
.app-sidebar-slide-leave-active,
.app-account-pop-enter-active,
.app-account-pop-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.app-sidebar-slide-enter-from,
.app-sidebar-slide-leave-to {
  opacity: 0;
  transform: translateX(-.75rem) scale(.985);
}
.app-account-pop-enter-from,
.app-account-pop-leave-to {
  opacity: 0;
  transform: translateY(.5rem) scale(.98);
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
    width: 3.3rem;
    height: 3.3rem;
  }
}
</style>
