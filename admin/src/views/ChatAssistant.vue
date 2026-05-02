<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
const provider = ref('a')
const input = ref('')
const messages = ref<{ role:string; content:string }[]>([{ role: 'system', content: '你是 SRBlogs 后台写作助手。' }])
const loading = ref(false)
const settingsLoading = ref(false)
const settingsError = ref('')
const enableChat = ref(true)
const aiConfigured = ref(false)
const disabled = computed(() => !enableChat.value)
async function loadSettings() {
  settingsLoading.value = true
  settingsError.value = ''
  try {
    const data = await adminApi.json<any>('/admin/settings')
    enableChat.value = data.ai?.enableChat !== false
    aiConfigured.value = data.ai?.aiKeyConfigured === true
  } catch (exc) {
    settingsError.value = exc instanceof Error ? exc.message : 'AI 设置读取失败'
  } finally {
    settingsLoading.value = false
  }
}
async function send(){
  if(disabled.value || !input.value.trim()) return
  messages.value.push({ role: 'user', content: input.value })
  input.value = ''; loading.value = true
  try { const data = await adminApi.chat(messages.value, provider.value); messages.value.push({ role: 'assistant', content: data.content || JSON.stringify(data) }) }
  finally { loading.value = false }
}
onMounted(loadSettings)
</script>
<template>
  <section class="grid gap-5">
    <GlassCard>
      <h1 class="text-4xl font-black">AI 聊天助手</h1>
      <p class="mt-2 text-white/50">支持 A/B 端点切换。API Key 只从服务端配置读取，后台不回显明文。</p>
      <p v-if="settingsLoading" class="mt-3 text-sm text-white/50">AI 设置读取中...</p>
      <p v-if="settingsError" class="mt-3 text-sm text-red-200/80">{{ settingsError }}</p>
      <p v-if="disabled" class="mt-3 rounded-2xl border border-amber-200/20 bg-amber-300/10 p-3 text-sm text-amber-50/80">AI 聊天已在设置中心关闭。</p>
      <p v-else-if="!aiConfigured" class="mt-3 rounded-2xl border border-white/10 bg-white/[0.06] p-3 text-sm text-white/55">AI Key 未配置或仅存在于服务端环境占位，发送时将返回未配置提示。</p>
    </GlassCard>
    <GlassCard>
      <select v-model="provider" class="mb-4 rounded-2xl border border-white/10 bg-white/10 px-4 py-2"><option value="a">线路 A</option><option value="b">线路 B</option></select>
      <div class="grid max-h-[520px] gap-3 overflow-auto">
        <div v-for="(m,i) in messages.filter(x=>x.role!=='system')" :key="i" class="rounded-2xl p-4" :class="m.role==='user' ? 'bg-cyan-300/15' : 'bg-white/[0.08]'"><b>{{ m.role }}</b><p class="mt-2 whitespace-pre-wrap text-white/70">{{ m.content }}</p></div>
      </div>
      <form class="mt-4 flex gap-3" @submit.prevent="send"><input v-model="input" :disabled="disabled" class="flex-1 rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none disabled:cursor-not-allowed disabled:opacity-50" placeholder="输入问题"/><button :disabled="loading || disabled" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50">发送</button></form>
    </GlassCard>
  </section>
</template>
