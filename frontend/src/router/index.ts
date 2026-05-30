import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/About.vue') },
    { path: '/install', name: 'install', component: () => import('@/views/Install.vue') },
    { path: '/posts', name: 'posts', component: () => import('@/views/Posts.vue') },
    { path: '/posts/:slug', name: 'post-detail', component: () => import('@/views/PostDetail.vue') },
    { path: '/search', name: 'search', component: () => import('@/views/Search.vue') },
    { path: '/tags', name: 'tags', component: () => import('@/views/Tags.vue') },
    { path: '/tags/:tag', name: 'tag-detail', component: () => import('@/views/TagDetail.vue') },
    { path: '/archive', name: 'archive', component: () => import('@/views/Archive.vue') },
    { path: '/moments', name: 'moments', component: () => import('@/views/Moments.vue') },
    { path: '/moments/:slug', name: 'moment-detail', component: () => import('@/views/PostDetail.vue'), props: { section: 'moments' } },
    { path: '/sayings', redirect: '/moments' },
    { path: '/chatter', redirect: '/chatters' },
    { path: '/chatter/:slug', redirect: (to) => `/chatters/${to.params.slug}` },
    { path: '/chatters', name: 'chatters', component: () => import('@/views/Chatter.vue') },
    { path: '/chatters/:slug', name: 'chatter-detail', component: () => import('@/views/ChatterDetail.vue') },
    { path: '/friends', name: 'friends', component: () => import('@/views/Friends.vue') },
    { path: '/music', name: 'music', component: () => import('@/views/Music.vue') },
    { path: '/photowall', name: 'photowall', component: () => import('@/views/Photowall.vue') },
    { path: '/projects', name: 'projects', component: () => import('@/views/Projects.vue') },
    { path: '/about', redirect: '/' },
    { path: '/timeline', name: 'timeline', component: () => import('@/views/Timeline.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFound.vue') }
  ]
})

export default router
