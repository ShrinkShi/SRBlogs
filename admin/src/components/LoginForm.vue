<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: 'admin', password: '' })
const error = ref('')
const loading = ref(false)
async function submit(){
  loading.value = true; error.value = ''
  try { await auth.login(form.username, form.password); router.push('/') }
  catch(e){ error.value = e instanceof Error ? e.message : '登录失败' }
  finally { loading.value = false }
}
</script>
<template>
  <form class="glass w-full max-w-md rounded-[32px] p-8" @submit.prevent="submit">
    <h1 class="text-4xl font-black text-white">SRBlogs Admin</h1>
    <p class="mt-2 text-white/55">登录后管理文章、动态、图床与 AI 配置。</p>
    <div class="mt-7 grid gap-4">
      <input v-model="form.username" aria-label="用户名" autocomplete="username" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="用户名" />
      <input v-model="form.password" type="password" aria-label="密码" autocomplete="current-password" class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 outline-none focus:border-cyan-300/60" placeholder="密码" />
      <p v-if="error" class="text-sm text-red-300">{{ error }}</p>
      <button :disabled="loading" class="rounded-2xl bg-cyan-300 px-5 py-3 font-bold text-slate-950 disabled:opacity-50">登录</button>
    </div>
  </form>
</template>
