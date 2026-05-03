<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StateBlock from '@/components/StateBlock.vue'

const router = useRouter()

onMounted(() => {
  router.replace({ path: '/posts', query: { section: 'chatters' } })
})
</script>

<template>
  <StateBlock message="正在进入杂谈板块..." />
</template>
