<script setup lang="ts">
const model = defineModel<string>({ default: '' })
</script>

<template>
  <div class="flex items-center gap-3 rounded-[28px] border border-white/10 bg-white/[0.08] px-5 py-4 shadow-inner shadow-white/[0.03] transition focus-within:border-cyan-200/55 focus-within:bg-white/[0.11]">
    <span class="text-xs font-bold uppercase tracking-[0.2em] text-white/42" aria-hidden="true">Search</span>
    <input
      v-model="model"
      aria-label="搜索标题、标签或内容"
      class="w-full bg-transparent text-base text-white outline-none placeholder:text-white/35"
      placeholder="搜索标题、标签或内容..."
    />
  </div>
</template>
