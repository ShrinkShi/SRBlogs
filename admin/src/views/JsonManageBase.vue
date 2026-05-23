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
    <GlassCard><h1 class="text-4xl font-black text-white">{{ title }}</h1><p class="mt-2 text-white/50">高级 JSON 编辑。当前保留直接编辑模式，后续再拆成表单化管理。</p></GlassCard>
    <textarea v-model="text" rows="24" class="glass rounded-[28px] p-5 font-mono text-sm outline-none focus:border-cyan-300/60"></textarea>
    <div class="admin-bottom-actions">
      <button class="admin-btn admin-btn-save" @click="save">保存</button>
    </div>
  </section>
</template>
