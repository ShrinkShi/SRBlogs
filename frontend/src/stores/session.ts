import { defineStore } from 'pinia'
import { contentApi, type AdminUser, type VisitorUser } from '@/api/content'

type VisitorState = { configured: { github: boolean; qq: boolean; email?: boolean }; user: VisitorUser | null }

function apiBase() {
  const envBase = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  const localBackend = `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000/api`
  const fallbackBase = ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : '/api'
  const selectedBase = envBase === '/api' && ['5173', '5174', '5175'].includes(window.location.port) ? localBackend : (envBase || fallbackBase)
  const rawBase = selectedBase.replace(/\/$/, '')
  return rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`
}

export const useSessionStore = defineStore('session', {
  state: () => ({
    loading: false,
    adminToken: localStorage.getItem('srblogs-token') || '',
    admin: null as AdminUser | null,
    visitor: {
      configured: { github: false, qq: false },
      user: null
    } as VisitorState
  }),
  getters: {
    isAdmin: (state) => Boolean(state.adminToken && state.admin),
    displayName: (state) => {
      if (state.adminToken && state.admin) return state.admin.username
      if (state.visitor.user) return state.visitor.user.name || state.visitor.user.login || state.visitor.user.id
      return '游客'
    },
    displayRole: (state) => {
      if (state.adminToken && state.admin) return '管理员登录'
      if (state.visitor.user?.provider === 'github') return 'GitHub 登录'
      if (state.visitor.user?.provider === 'qq') return 'QQ 登录'
      if (state.visitor.user?.provider === 'email') return '邮箱登录'
      return '游客登录'
    },
    avatar: (state) => state.visitor.user?.avatar || ''
  },
  actions: {
    async refreshVisitor() {
      try {
        this.visitor = await contentApi.visitorMe()
      } catch {
        this.visitor = { configured: { github: false, qq: false, email: true }, user: null }
      }
    },
    async refreshAdmin() {
      if (!this.adminToken) {
        this.admin = null
        return
      }
      try {
        this.admin = await contentApi.adminMe()
      } catch {
        this.admin = null
        this.adminToken = ''
        localStorage.removeItem('srblogs-token')
      }
    },
    async refresh() {
      this.loading = true
      try {
        await Promise.all([this.refreshVisitor(), this.refreshAdmin()])
      } finally {
        this.loading = false
      }
    },
    async loginAdmin(username: string, password: string) {
      if (this.visitor.user) throw new Error('请先退出当前登录账号。')
      const data = await contentApi.adminLogin(username, password)
      this.adminToken = data.access_token
      localStorage.setItem('srblogs-token', this.adminToken)
      await this.refreshAdmin()
    },
    async loginEmail(email: string, password: string, mode: 'login' | 'register') {
      if (this.adminToken) throw new Error('请先退出管理员账号。')
      const data = mode === 'register'
        ? await contentApi.emailRegister({ email, password })
        : await contentApi.emailLogin({ email, password })
      this.visitor.user = data.user
      this.visitor.configured = { ...this.visitor.configured, email: true }
    },
    logoutAdmin() {
      this.adminToken = ''
      this.admin = null
      localStorage.removeItem('srblogs-token')
    },
    async logoutVisitor() {
      await contentApi.visitorLogout()
      await this.refreshVisitor()
    },
    loginWithGithub() {
      const returnTo = `${window.location.pathname}${window.location.search}${window.location.hash}`
      window.location.href = `${apiBase()}/auth/github/login?returnTo=${encodeURIComponent(returnTo)}`
    }
  }
})
