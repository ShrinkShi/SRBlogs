<script setup lang="ts">
import { ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
const provider = ref('a')
const input = ref('')
const messages = ref<{ role:string; content:string }[]>([{ role: 'system', content: '你是 SRBlogs 后台写作助手。' }])
const loading = ref(false)
async function send(){
  if(!input.value.trim()) return
  messages.value.push({ role: 'user', content: input.value })
  input.value = ''; loading.value = true
  try { const data = await adminApi.chat(messages.value, provider.value); messages.value.push({ role: 'assistant', content: data.content || JSON.stringify(data) }) }
  finally { loading.value = false }
}
</script>
<template>
  <section class="grid gap-5">
    <GlassCard><h1 class="text-4xl font-black">AI 聊天助手</h1><p class="mt-2 text-white/50">支持 A/B 端点切换。未配置时返回占位提示。</p></GlassCard>
    <GlassCard>
      <select v-model="provider" class="mb-4 rounded-2xl border border-white/10 bg-white/10 px-4 py-2"><option value="a">线路 A</option><option value="b">线路 B</option></select>
      <div class="grid max-h-[520px] gap-3 overflow-auto">
        <div v-for="(m,i) in messages.filter(x=>x.role!=='system')" :key="i" class="rounded-2xl p-4" :class="m.role==='user' ? 'bg-cyan-300/15' : 'bg-white/[0.08]'"><b>{{ m.role }}</b><p class="mt-2 whitespace-pre-wrap text-white/70">{{ m.content }}</p></div>
      </div>
      <form class="mt-4 flex gap-3" @submit.prevent="send"><input v-model="input" class="flex-1 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none" placeholder="输入问题"/><button :disabled="loading" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950">发送</button></form>
    </GlassCard>
  </section>
</template>
