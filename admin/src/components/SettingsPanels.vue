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
  { key: 'ai', label: 'AI 猫猫助理' },
  { key: 'deploy', label: '部署同步' }
]
const parsed = computed(() => {
  try { return JSON.parse(text.value) as Record<string, unknown> } catch { return {} }
})
onMounted(async () => { text.value = JSON.stringify(await adminApi.json('/settings'), null, 2) })
async function save(){ await adminApi.putJson('/settings', JSON.parse(text.value)); ui.show('设置已保存') }
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
            <p class="mt-2 text-sm leading-6 text-white/50">对应前台的站点标题、头像、背景图、弹幕、社交链接、建站日期。这里直接编辑 JSON，保存后前台刷新即可读取。</p>
            <div class="mt-4 grid gap-3 md:grid-cols-2">
              <button class="admin-btn admin-btn-ghost" @click="patch('theme', 'nebula')">切换默认星云主题</button>
              <button class="admin-btn admin-btn-ghost" @click="patch('theme', 'sakura')">切换樱花主题</button>
            </div>
          </template>
          <template v-else-if="active === 'image'">
            <h2 class="text-2xl font-black text-white">图床配置</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">生产环境不要把 OSS AccessKey 明文存到前端仓库。建议写入后端 .env，再由上传接口读取。</p>
          </template>
          <template v-else-if="active === 'ai'">
            <h2 class="text-2xl font-black text-white">AI 猫猫助理</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">保留 A/B 双线配置入口。真实 API Key 仍建议放在后端环境变量里。</p>
          </template>
          <template v-else>
            <h2 class="text-2xl font-black text-white">部署同步</h2>
            <p class="mt-2 text-sm leading-6 text-white/50">当前版本以阿里云轻量服务器 + Nginx + Systemd 为主，不再使用原项目 Vercel/本地控制台一键脚本路线。</p>
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
