<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

type SettingsTab = 'site' | 'image' | 'ai' | 'deploy'
const ui = useUiStore()
const text = ref('{}')
const active = ref<SettingsTab>('site')
const tabs: { key: SettingsTab; label: string }[] = [
  { key: 'site', label: '站点控制中心' },
  { key: 'image', label: '图床配置' },
  { key: 'ai', label: 'AI 助手' },
  { key: 'deploy', label: '部署同步' }
]
const parsed = computed(() => {
  try { return JSON.parse(text.value) as Record<string, unknown> } catch { return {} }
})
onMounted(async () => { text.value = JSON.stringify(await adminApi.json('/admin/settings'), null, 2) })
async function save(){
  text.value = JSON.stringify(await adminApi.putJson('/admin/settings', JSON.parse(text.value)), null, 2)
  ui.show('设置已保存')
}
function patch(key: string, value: unknown) {
  const data = { ...parsed.value, [key]: value }
  text.value = JSON.stringify(data, null, 2)
}
</script>
<template>
  <div class="grid gap-4 xl:grid-cols-[280px_1fr]">
    <div class="glass rounded-[30px] p-4">
      <div class="relative z-[1] grid gap-2">
        <button v-for="tab in tabs" :key="tab.key" class="rounded-2xl px-4 py-3 text-left text-sm transition" :class="active === tab.key ? 'bg-cyan-300/[0.16] text-cyan-100' : 'text-white/60 hover:bg-white/10'" @click="active = tab.key">{{ tab.label }}</button>
      </div>
    </div>
    <div class="grid gap-4">
      <div class="glass rounded-[30px] p-5">
        <div class="relative z-[1]">
          <template v-if="active === 'site'">
            <h2 class="text-2xl font-black text-white">siteConfig</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">对应前台的站点标题、头像、背景图、弹幕、社交链接和建站日期。后台接口不会返回 Secret 明文。</p>
            <div class="mt-4 grid gap-3 md:grid-cols-2">
              <button class="admin-btn admin-btn-ghost" @click="patch('theme', 'nebula')">切换默认星云主题</button>
              <button class="admin-btn admin-btn-ghost" @click="patch('theme', 'sakura')">切换樱花主题</button>
            </div>
          </template>
          <template v-else-if="active === 'image'">
            <h2 class="text-2xl font-black text-white">图床配置</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">OSS AccessKey 只能写入后端 .env 或服务端配置。此处只显示配置状态，不显示密钥明文。</p>
          </template>
          <template v-else-if="active === 'ai'">
            <h2 class="text-2xl font-black text-white">AI 助手</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">AI Key 由后端代理读取环境变量，前台和后台构建产物都不能包含密钥。</p>
          </template>
          <template v-else>
            <h2 class="text-2xl font-black text-white">部署同步</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">当前版本保留服务器部署路线：Nginx + Systemd + FastAPI，不复刻 GitHub/Vercel 双轨同步。</p>
          </template>
        </div>
      </div>
      <textarea v-model="text" rows="20" class="glass rounded-[30px] p-5 font-mono text-sm leading-6 text-white outline-none focus:border-cyan-300/60"></textarea>
      <div class="flex flex-wrap gap-3">
        <button class="admin-btn admin-btn-primary" @click="save">保存设置</button>
        <button class="admin-btn admin-btn-ghost" @click="text = JSON.stringify(parsed, null, 2)">格式化 JSON</button>
      </div>
    </div>
  </div>
</template>
