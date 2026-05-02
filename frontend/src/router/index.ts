import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
    { path: '/posts', name: 'posts', component: () => import('@/views/Posts.vue') },
    { path: '/posts/:slug', name: 'post-detail', component: () => import('@/views/PostDetail.vue') },
    { path: '/moments', name: 'moments', component: () => import('@/views/Moments.vue') },
    { path: '/moments/:slug', name: 'moment-detail', component: () => import('@/views/PostDetail.vue'), props: { section: 'moments' } },
    { path: '/chatter', redirect: '/chatters' },
    { path: '/chatter/:slug', redirect: (to) => `/chatters/${to.params.slug}` },
    { path: '/chatters', name: 'chatters', component: () => import('@/views/Chatter.vue') },
    { path: '/chatters/:slug', name: 'chatter-detail', component: () => import('@/views/ChatterDetail.vue') },
    { path: '/friends', name: 'friends', component: () => import('@/views/Friends.vue') },
    { path: '/music', name: 'music', component: () => import('@/views/Music.vue') },
    { path: '/photowall', name: 'photowall', component: () => import('@/views/Photowall.vue') },
    { path: '/projects', name: 'projects', component: () => import('@/views/Projects.vue') },
    { path: '/about', name: 'about', component: () => import('@/views/About.vue') },
    { path: '/timeline', name: 'timeline', component: () => import('@/views/Timeline.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFound.vue') }
  ]
})

export default router
