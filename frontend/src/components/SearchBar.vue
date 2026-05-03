<script setup lang="ts">
import { ref } from 'vue'

const model = defineModel<string>({ default: '' })
const inputRef = ref<HTMLInputElement | null>(null)
</script>

<template>
  <div class="flex items-center gap-3 rounded-[30px] border border-white/10 bg-white/[0.08] px-5 py-4 shadow-inner shadow-white/[0.03] transition focus-within:border-cyan-200/55 focus-within:bg-white/[0.11]">
    <input
      ref="inputRef"
      v-model="model"
      aria-label="搜索标题、标签或内容"
      class="w-full bg-transparent text-base text-white outline-none placeholder:text-white/35"
      placeholder="搜索标题、标签或内容..."
    />
    <button
      type="button"
      aria-label="聚焦搜索"
      class="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-slate-950/72 text-cyan-100 shadow-[0_12px_28px_rgba(0,0,0,.22)] transition hover:scale-105 hover:text-white"
      @click="inputRef?.focus()"
    >
      <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.6-3.6" />
      </svg>
    </button>
  </div>
</template>
