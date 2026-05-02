<script setup lang="ts">
const back = () => window.history.length > 1 ? window.history.back() : location.assign('/')
</script>
<template>
  <button type="button" class="mb-5 rounded-2xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/80 transition hover:bg-white/[0.15] hover:text-white" @click="back">返回上一页</button>
</template>
