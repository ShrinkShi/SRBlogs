import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/', component: () => import('@/views/Dashboard.vue') },
    { path: '/editor/:section?/:slug?', component: () => import('@/views/Editor.vue') },
    { path: '/drafts', component: () => import('@/views/Drafts.vue') },
    { path: '/posts', component: () => import('@/views/PostsManage.vue') },
    { path: '/moments', component: () => import('@/views/MomentsManage.vue') },
    { path: '/chatters', component: () => import('@/views/ChatterManage.vue') },
    { path: '/comments', component: () => import('@/views/CommentsManage.vue') },
    { path: '/friends', component: () => import('@/views/FriendsManage.vue') },
    { path: '/music', component: () => import('@/views/MusicManage.vue') },
    { path: '/photos', component: () => import('@/views/PhotowallManage.vue') },
    { path: '/projects', component: () => import('@/views/ProjectsManage.vue') },
    { path: '/about', component: () => import('@/views/AboutEdit.vue') },
    { path: '/settings', component: () => import('@/views/Settings.vue') },
    { path: '/chat', component: () => import('@/views/ChatAssistant.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.isAuthed) return '/login'
})

export default router
