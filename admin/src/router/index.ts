import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Editor from '@/views/Editor.vue'
import { adminApi } from '@/api/admin'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/', redirect: '/content/articles' },

    { path: '/content/:section?', component: () => import('@/views/ContentHub.vue') },
    { path: '/settings', component: () => import('@/views/Settings.vue') },
    { path: '/audit', component: () => import('@/views/AuditLogs.vue') },
    { path: '/backups', component: () => import('@/views/BackupsManage.vue') },

    // 旧入口只保留兼容，不再出现在左侧主导航。
    { path: '/editor/:section?/:slug?', component: Editor },
    { path: '/posts', redirect: '/content/articles' },
    { path: '/chatters', redirect: '/content/articles?kind=chatters' },
    { path: '/comments', redirect: '/content/articles' },
    { path: '/photos', redirect: '/content/photos' },
    { path: '/music', redirect: '/content/music' },
    { path: '/projects', redirect: '/content/projects' },
    { path: '/friends', redirect: '/content/friends' },
    { path: '/about', redirect: '/content/about' },
    { path: '/drafts', redirect: '/content/articles' },
    { path: '/moments', redirect: '/content/articles' },
    { path: '/pages/:page?', redirect: '/content/about' },
    { path: '/content/editor/:section?/:slug?', redirect: (to) => `/editor/${to.params.section || 'posts'}${to.params.slug ? `/${to.params.slug}` : ''}` },
    { path: '/content/posts', redirect: '/content/articles' },
    { path: '/content/chatters', redirect: '/content/articles?kind=chatters' },
    { path: '/content/drafts', redirect: '/content/articles' },
    { path: '/content/moments', redirect: '/content/articles' },
    { path: '/logs/audit', redirect: '/audit' },
    { path: '/logs/backups', redirect: '/backups' },
    { path: '/chat', redirect: '/settings' },
    { path: '/:pathMatch(.*)*', redirect: '/content/articles' }
  ]
})

function installUrl() {
  if (typeof window === 'undefined') return '/install'
  if (window.location.port === '5174') {
    return `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:5173/install`
  }
  return '/install'
}

router.beforeEach(async (to) => {
  try {
    const status = await adminApi.installStatus()
    if (status.needsInstall) {
      window.location.href = installUrl()
      return false
    }
  } catch {
    // If the install status endpoint is unreachable, continue to the normal login
    // flow so existing deployments can still surface the backend error there.
  }
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.token) return '/login'
  if (to.path === '/login' && auth.token) return '/content/articles'
})

export default router
