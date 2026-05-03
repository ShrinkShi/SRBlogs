<script setup lang="ts">
const model = defineModel<string>({ default: '' })
</script>

<template>
  <div class="flex items-center gap-3 border-b border-white/12 px-1 py-3 transition focus-within:border-cyan-200/55">
    <span class="text-xs font-bold uppercase tracking-[0.2em] text-white/36" aria-hidden="true">Search</span>
    <input
      v-model="model"
      aria-label="搜索标题、标签或内容"
      class="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35"
      placeholder="搜索标题、标签或内容..."
    />
  </div>
</template>
