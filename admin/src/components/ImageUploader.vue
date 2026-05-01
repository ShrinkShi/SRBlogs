<script setup lang="ts">
import { ref } from 'vue'
import { adminApi } from '@/api/admin'
const emit = defineEmits<{ uploaded: [url: string] }>()
const progress = ref(0)
const error = ref('')
async function handle(files: FileList | null){
  if (!files?.length) return
  error.value = ''; progress.value = 0
  try { const data = await adminApi.upload(files[0], p => progress.value = p); emit('uploaded', data.url) }
  catch(e){ error.value = e instanceof Error ? e.message : '上传失败' }
}
</script>
<template>
  <label class="glass block cursor-pointer rounded-[28px] border-dashed p-5 text-center hover:border-cyan-300/40">
    <input type="file" class="hidden" accept="image/*" @change="handle(($event.target as HTMLInputElement).files)" />
    <p class="font-bold text-white">拖拽/点击上传图片</p>
    <p class="mt-1 text-sm text-white/50">上传成功后自动返回图片 URL</p>
    <div v-if="progress" class="mt-4 h-2 rounded-full bg-white/10"><div class="h-full rounded-full bg-cyan-300" :style="{ width: progress + '%' }"></div></div>
    <p v-if="error" class="mt-3 text-sm text-red-300">{{ error }}</p>
  </label>
</template>
