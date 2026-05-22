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

function setArticleKind(kind: 'posts' | 'chatters') {
  router.replace({ path: '/content/articles', query: kind === 'chatters' ? { kind } : {} })
}
</script>

<template>
  <section class="admin-workspace">
    <div v-if="section === 'articles'" class="admin-inline-toolbar">
      <div class="admin-segment shrink-0" aria-label="文章类型">
        <button type="button" :class="articleKind === 'posts' ? 'admin-segment-active' : ''" @click="setArticleKind('posts')">正经</button>
        <button type="button" :class="articleKind === 'chatters' ? 'admin-segment-active' : ''" @click="setArticleKind('chatters')">杂谈</button>
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
