<script setup lang="ts">
const model = defineModel<string>({ default: '' })
</script>
<template>
  <div class="glass flex items-center gap-3 rounded-[26px] px-4 py-3">
    <span class="text-white/36">⌕</span>
    <input v-model="model" aria-label="搜索标题、标签或内容" class="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35" placeholder="搜索标题、标签或内容..." />
  </div>
</template>
