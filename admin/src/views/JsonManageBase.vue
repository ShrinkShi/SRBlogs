<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
const props = defineProps<{ title: string; path: string }>()
const ui = useUiStore(); const text = ref('[]')
onMounted(async()=>{ text.value = JSON.stringify(await adminApi.json(props.path), null, 2) })
async function save(){ await adminApi.putJson(props.path, JSON.parse(text.value)); ui.show('已保存') }
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><h1 class="text-4xl font-black text-white">{{ title }}</h1><p class="mt-2 text-white/50">直接编辑 JSON。生产化可继续拆成表单。</p></GlassCard>
    <textarea v-model="text" rows="24" class="glass rounded-[28px] p-5 font-mono text-sm outline-none focus:border-cyan-300/60"></textarea>
    <button class="w-fit rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950" @click="save">保存</button>
  </section>
</template>
