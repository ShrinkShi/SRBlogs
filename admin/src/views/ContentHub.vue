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
  const map: Record<string, { eyebrow: string; title: string; description: string }> = {
    articles: {
      eyebrow: 'CONTENT / ARTICLES',
      title: '文章管理',
      description: '统一管理正经文章和杂谈。新增或编辑会进入 Markdown 编辑器，正文和卡片简介分离维护。'
    },
    'article-comments': {
      eyebrow: 'CONTENT / MESSAGES',
      title: '文章评论',
      description: '管理文章、杂谈对应的留言数据。评论区开关保留在留言设置中维护。'
    },
    photos: {
      eyebrow: 'CONTENT / PHOTOS',
      title: '图片相册',
      description: '按相册组管理照片，支持封面、批量上传、排序和删除，每组最多 50 张。'
    },
    'photo-comments': {
      eyebrow: 'CONTENT / MESSAGES',
      title: '图片评论',
      description: '管理照片墙和相册对应的留言数据。'
    },
    music: {
      eyebrow: 'CONTENT / MUSIC',
      title: '音乐管理',
      description: '维护歌曲、音频、歌词、封面、排序和喜欢数。'
    },
    'music-comments': {
      eyebrow: 'CONTENT / MESSAGES',
      title: '音乐评论',
      description: '管理音乐页留言数据。'
    },
    projects: {
      eyebrow: 'CONTENT / PROJECTS',
      title: '项目管理',
      description: '维护项目卡片。项目必须保留跳转链接，封面为空时前台使用默认封面。'
    },
    friends: {
      eyebrow: 'CONTENT / FRIENDS',
      title: '友链管理',
      description: '维护友链卡片。友链必须保留站点链接，封面为空时前台使用默认封面。'
    },
    about: {
      eyebrow: 'CONTENT / ABOUT',
      title: '关于页面',
      description: '编辑关于页面结构化文案和兼容 Markdown 内容。'
    }
  }
  return map[section.value] || map.articles
})

function setArticleKind(kind: 'posts' | 'chatters') {
  router.replace({ path: '/content/articles', query: kind === 'chatters' ? { kind } : {} })
}
</script>

<template>
  <section class="admin-workspace">
    <header class="admin-page-head">
      <div class="min-w-0">
        <p class="admin-section-title">{{ sectionMeta.eyebrow }}</p>
        <h1>{{ sectionMeta.title }}</h1>
        <p>{{ sectionMeta.description }}</p>
      </div>
      <div v-if="section === 'articles'" class="admin-segment shrink-0">
        <button type="button" :class="articleKind === 'posts' ? 'admin-segment-active' : ''" @click="setArticleKind('posts')">正经</button>
        <button type="button" :class="articleKind === 'chatters' ? 'admin-segment-active' : ''" @click="setArticleKind('chatters')">杂谈</button>
      </div>
    </header>

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
