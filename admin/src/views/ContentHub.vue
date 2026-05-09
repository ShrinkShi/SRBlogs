<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PostsManage from '@/views/PostsManage.vue'
import ChatterManage from '@/views/ChatterManage.vue'
import PhotowallManage from '@/views/PhotowallManage.vue'
import MusicManage from '@/views/MusicManage.vue'
import ProjectsManage from '@/views/ProjectsManage.vue'
import FriendsManage from '@/views/FriendsManage.vue'
import AboutEdit from '@/views/AboutEdit.vue'
import CommentsManage from '@/views/CommentsManage.vue'

const route = useRoute()
const router = useRouter()

const section = computed(() => String(route.params.section || 'articles'))
const articleKind = computed<'posts' | 'chatters'>(() => route.query.kind === 'chatters' ? 'chatters' : 'posts')

const sectionMeta = computed(() => {
  const map: Record<string, { title: string; description: string }> = {
    articles: { title: '文章', description: '统一管理正经文章和杂谈，新增或编辑会进入 Markdown 编辑器。' },
    'article-comments': { title: '文章评论', description: '管理文章和杂谈对应的留言数据。' },
    photos: { title: '图片', description: '按相册组管理照片，支持封面、批量上传、排序和删除。' },
    'photo-comments': { title: '图片评论', description: '管理照片墙和相册对应的留言数据。' },
    music: { title: '音乐', description: '管理歌单、音频、歌词、封面和喜欢数。' },
    'music-comments': { title: '音乐评论', description: '管理音乐页留言数据。' },
    projects: { title: '项目', description: '管理项目卡片，项目必须保留可跳转链接。' },
    friends: { title: '友链', description: '管理友链卡片，保留站点链接和封面。' },
    about: { title: '关于', description: '编辑关于页结构化文案和兼容 Markdown。' }
  }
  return map[section.value] || map.articles
})

function setArticleKind(kind: 'posts' | 'chatters') {
  router.replace({ path: '/content/articles', query: kind === 'chatters' ? { kind } : {} })
}
</script>

<template>
  <section class="grid gap-5">
    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.28em] text-slate-500">content hub</p>
          <h1 class="mt-2 text-3xl font-black text-slate-950">{{ sectionMeta.title }}</h1>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{{ sectionMeta.description }}</p>
        </div>
        <div v-if="section === 'articles'" class="admin-segment">
          <button type="button" :class="articleKind === 'posts' ? 'admin-segment-active' : ''" @click="setArticleKind('posts')">正经</button>
          <button type="button" :class="articleKind === 'chatters' ? 'admin-segment-active' : ''" @click="setArticleKind('chatters')">杂谈</button>
        </div>
      </div>
    </div>

    <PostsManage v-if="section === 'articles' && articleKind === 'posts'" />
    <ChatterManage v-else-if="section === 'articles' && articleKind === 'chatters'" />
    <CommentsManage v-else-if="section === 'article-comments' || section === 'photo-comments' || section === 'music-comments'" />
    <PhotowallManage v-else-if="section === 'photos'" />
    <MusicManage v-else-if="section === 'music'" />
    <ProjectsManage v-else-if="section === 'projects'" />
    <FriendsManage v-else-if="section === 'friends'" />
    <AboutEdit v-else-if="section === 'about'" />
    <PostsManage v-else />
  </section>
</template>
