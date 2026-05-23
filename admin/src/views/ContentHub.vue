<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PostsManage from '@/views/PostsManage.vue'
import ChatterManage from '@/views/ChatterManage.vue'
import PhotowallManage from '@/views/PhotowallManage.vue'
import MusicManage from '@/views/MusicManage.vue'
import ProjectsManage from '@/views/ProjectsManage.vue'
import FriendsManage from '@/views/FriendsManage.vue'
import AboutEdit from '@/views/AboutEdit.vue'

const route = useRoute()

const section = computed(() => String(route.params.section || 'articles'))
const articleKind = computed<'posts' | 'chatters'>(() => route.query.kind === 'chatters' ? 'chatters' : 'posts')
</script>

<template>
  <section class="admin-workspace">
    <PostsManage v-if="section === 'articles' && articleKind === 'posts'" />
    <ChatterManage v-else-if="section === 'articles' && articleKind === 'chatters'" />
    <PhotowallManage v-else-if="section === 'photos'" />
    <MusicManage v-else-if="section === 'music'" />
    <ProjectsManage v-else-if="section === 'projects'" />
    <FriendsManage v-else-if="section === 'friends'" />
    <AboutEdit v-else-if="section === 'about'" />
    <PostsManage v-else />
  </section>
</template>
