<script setup lang="ts">
import { ref } from 'vue'

const model = defineModel<string>({ default: '' })
const inputRef = ref<HTMLInputElement | null>(null)
</script>

<template>
  <div class="search-input-theme flex items-center gap-2 rounded-[22px] border border-white/12 bg-white/[0.32] px-3 py-2 shadow-inner shadow-white/[0.04] transition focus-within:border-cyan-200/55 focus-within:bg-white/[0.38]">
    <input
      ref="inputRef"
      v-model="model"
      aria-label="搜索标题、标签或内容"
      class="w-full bg-transparent text-sm outline-none"
      placeholder="搜索标题、标签或内容..."
    />
    <button
      type="button"
      aria-label="搜索"
      class="search-button-theme grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950/88 shadow-[0_8px_18px_rgba(0,0,0,.22)] transition hover:scale-105"
      @click="inputRef?.focus()"
    >
      <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.6-3.6" />
      </svg>
    </button>
  </div>
</template>
