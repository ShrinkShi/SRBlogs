<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
const ui = useUiStore(); const content = ref('')
onMounted(async()=>{ content.value = (await adminApi.json<{content:string}>('/about')).content })
async function save(){ await adminApi.putJson('/about', { content: content.value }); ui.show('关于页已保存') }
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><div class="flex items-center justify-between"><h1 class="text-4xl font-black">关于页面</h1><button class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="save">保存</button></div></GlassCard>
    <MarkdownEditor v-model="content" />
  </section>
</template>
