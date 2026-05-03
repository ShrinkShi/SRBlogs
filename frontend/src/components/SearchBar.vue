<script setup lang="ts">
const model = defineModel<string>({ default: '' })
</script>

<template>
  <div class="flex items-center gap-3 rounded-[26px] bg-white/[0.06] px-4 py-3 ring-1 ring-white/[0.06]">
    <span class="text-xs font-bold uppercase tracking-[0.2em] text-white/36" aria-hidden="true">Search</span>
    <input
      v-model="model"
      aria-label="搜索标题、标签或内容"
      class="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35"
      placeholder="搜索标题、标签或内容..."
    />
  </div>
</template>
