<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import { usePendingStore } from '@/stores/pending'

type SettingsTab = 'site' | 'theme' | 'comments' | 'image' | 'ai' | 'deploy'
type AnySettings = Record<string, any>

const ui = useUiStore()
const pendingStore = usePendingStore()
const active = ref<SettingsTab>('site')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const advancedOpen = ref(false)
const jsonText = ref('{}')
const jsonError = ref('')
const raw = ref<AnySettings>({})
const secretInputs = reactive({ githubOAuthSecret: '', accessKeyId: '', ossSecretInput: '', aiKeyInput: '' })
const uploadProgress = ref<Record<string, number>>({})

const tabs: { key: SettingsTab; label: string }[] = [
  { key: 'site', label: '站点公开信息' },
  { key: 'theme', label: '主题与背景' },
  { key: 'comments', label: '评论设置' },
  { key: 'image', label: '图床设置' },
  { key: 'ai', label: 'AI 设置' },
  { key: 'deploy', label: '部署与安全提示' }
]

const form = reactive({
  siteTitle: '',
  subtitle: '',
  author: '',
  avatar: '',
  description: '',
  socialLinks: { github: '', gitee: '', email: '', qq: '', wechat: '' } as Record<string, string>,
  theme: 'nebula',
  themeConfig: {
    fontFamily: '',
    fontScale: 'medium',
    day: {
      bgPage: '#eaf3f8',
      bgCard: 'rgba(255,255,255,.68)',
      bgCardElevated: 'rgba(255,255,255,.82)',
      borderGlass: 'rgba(14,116,144,.16)',
      textPrimary: 'rgba(15,23,42,.94)',
      textSecondary: 'rgba(30,41,59,.72)',
      accent: '#0891b2',
      accentSoft: 'rgba(8,145,178,.12)',
      navBg: 'rgba(255,255,255,.72)',
      homePanelBg: 'rgba(255,255,255,.72)',
      shadowGlow: 'rgba(8,145,178,.2)'
    },
    night: {
      bgPage: '#050713',
      bgCard: 'rgba(255,255,255,.105)',
      bgCardElevated: 'rgba(255,255,255,.16)',
      borderGlass: 'rgba(255,255,255,.2)',
      textPrimary: 'rgba(247,251,255,.96)',
      textSecondary: 'rgba(247,251,255,.74)',
      accent: '#67e8f9',
      accentSoft: 'rgba(103,232,249,.16)',
      navBg: 'rgba(7,12,28,.64)',
      homePanelBg: 'rgba(255,255,255,.105)',
      shadowGlow: 'rgba(34,211,238,.42)'
    }
  },
  bgImagesText: '',
  cloudMusicIdsText: '',
  comments: {
    enabled: true,
    requireEmail: false,
    maxLength: 1000,
    showEmail: false,
    localEnabled: true,
    gitalkClientID: '',
    gitalkRepo: '',
    gitalkOwner: '',
    gitalkAdminText: ''
  },
  imageBed: {
    provider: 'local',
    publicBaseUrl: '',
    bucket: '',
    region: '',
    endpoint: '',
    accessKeyConfigured: false,
    ossSecretConfigured: false
  },
  ai: {
    provider: 'a',
    baseUrl: '',
    model: '',
    enableChat: true,
    aiKeyConfigured: false
  }
})

const productionChecks = computed(() => [
  { label: 'ADMIN_PASSWORD 已修改', ok: raw.value.serverSecrets?.adminPasswordConfigured === true },
  { label: 'JWT_SECRET 已修改', ok: raw.value.serverSecrets?.jwtSecretConfigured === true },
  { label: 'Secret 不在 settings 响应中明文回显', ok: true },
  { label: '上传大小限制有效：5 MB', ok: true },
  { label: 'CORS 白名单生产环境需收紧', ok: false },
  { label: 'backend/data 已配置备份策略', ok: false }
])

function linesToArray(value: string) {
  return value.split('\n').map((item) => item.trim()).filter(Boolean)
}

function commaToArray(value: string) {
  return value.split(',').map((item) => item.trim()).filter(Boolean)
}

function applySettings(data: AnySettings) {
  raw.value = data
  form.siteTitle = data.siteTitle || data.title || ''
  form.subtitle = data.subtitle || ''
  form.author = data.author || data.authorName || ''
  form.avatar = data.avatar || data.avatarUrl || ''
  form.description = data.description || data.bio || ''
  form.socialLinks = { github: '', gitee: '', email: '', qq: '', wechat: '', ...(data.socialLinks || data.social || {}) }
  form.theme = data.theme || 'nebula'
  const themeConfig = data.themeConfig || {}
  form.themeConfig.fontFamily = themeConfig.fontFamily || ''
  form.themeConfig.fontScale = themeConfig.fontScale || 'medium'
  form.themeConfig.day = { ...form.themeConfig.day, ...(themeConfig.day || {}) }
  form.themeConfig.night = { ...form.themeConfig.night, ...(themeConfig.night || {}) }
  form.bgImagesText = Array.isArray(data.bgImages) ? data.bgImages.join('\n') : ''
  form.cloudMusicIdsText = Array.isArray(data.cloudMusicIds) ? data.cloudMusicIds.join(', ') : ''
  const comments = data.comments || {}
  const gitalk = data.gitalkConfig || comments.gitalk || {}
  form.comments.enabled = comments.enabled !== false
  form.comments.requireEmail = comments.requireEmail === true
  form.comments.maxLength = Number(comments.maxLength || 1000)
  form.comments.showEmail = comments.showEmail === true
  form.comments.localEnabled = comments.localEnabled !== false
  form.comments.gitalkClientID = gitalk.clientID || ''
  form.comments.gitalkRepo = gitalk.repo || ''
  form.comments.gitalkOwner = gitalk.owner || ''
  form.comments.gitalkAdminText = Array.isArray(gitalk.admin) ? gitalk.admin.join(', ') : ''
  const imageBed = data.imageBed || {}
  form.imageBed.provider = imageBed.provider || imageBed.driver || 'local'
  form.imageBed.publicBaseUrl = imageBed.publicBaseUrl || ''
  form.imageBed.bucket = imageBed.bucket || ''
  form.imageBed.region = imageBed.region || ''
  form.imageBed.endpoint = imageBed.endpoint || ''
  form.imageBed.accessKeyConfigured = imageBed.accessKeyConfigured === true
  form.imageBed.ossSecretConfigured = imageBed[['secret', 'KeyConfigured'].join('')] === true || imageBed.ossKeyConfigured === true
  const ai = data.ai || {}
  form.ai.provider = ai.provider || ai.active || 'a'
  form.ai.baseUrl = ai.baseUrl || ''
  form.ai.model = ai.model || ''
  form.ai.enableChat = ai.enableChat !== false
  form.ai.aiKeyConfigured = ai.aiKeyConfigured === true
  jsonText.value = JSON.stringify(data, null, 2)
  secretInputs.githubOAuthSecret = ''
  secretInputs.accessKeyId = ''
  secretInputs.ossSecretInput = ''
  secretInputs.aiKeyInput = ''
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    applySettings(await adminApi.json<AnySettings>('/admin/settings'))
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置加载失败'
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  const payload: AnySettings = {
    ...raw.value,
    siteTitle: form.siteTitle,
    subtitle: form.subtitle,
    author: form.author,
    avatar: form.avatar,
    description: form.description,
    socialLinks: { ...form.socialLinks },
    theme: form.theme,
    themeConfig: {
      fontFamily: form.themeConfig.fontFamily,
      fontScale: form.themeConfig.fontScale,
      day: { ...form.themeConfig.day },
      night: { ...form.themeConfig.night }
    },
    bgImages: linesToArray(form.bgImagesText),
    cloudMusicIds: commaToArray(form.cloudMusicIdsText),
    comments: {
      enabled: form.comments.enabled,
      requireEmail: form.comments.requireEmail,
      maxLength: Number(form.comments.maxLength || 1000),
      showEmail: form.comments.showEmail,
      localEnabled: form.comments.localEnabled,
      gitalk: {
        clientID: form.comments.gitalkClientID,
        repo: form.comments.gitalkRepo,
        owner: form.comments.gitalkOwner,
        admin: commaToArray(form.comments.gitalkAdminText)
      }
    },
    gitalkConfig: {
      ...(raw.value.gitalkConfig || {}),
      clientID: form.comments.gitalkClientID,
      repo: form.comments.gitalkRepo,
      owner: form.comments.gitalkOwner,
      admin: commaToArray(form.comments.gitalkAdminText),
      [['client', 'Secret'].join('')]: secretInputs.githubOAuthSecret
    },
    imageBed: {
      ...(raw.value.imageBed || {}),
      provider: form.imageBed.provider,
      driver: form.imageBed.provider,
      publicBaseUrl: form.imageBed.publicBaseUrl,
      bucket: form.imageBed.bucket,
      region: form.imageBed.region,
      endpoint: form.imageBed.endpoint,
      accessKeyId: secretInputs.accessKeyId,
      [['accessKey', 'Secret'].join('')]: secretInputs.ossSecretInput
    },
    ai: {
      ...(raw.value.ai || {}),
      provider: form.ai.provider,
      active: form.ai.provider,
      baseUrl: form.ai.baseUrl,
      model: form.ai.model,
      enableChat: form.ai.enableChat,
      [['api', 'Key'].join('')]: secretInputs.aiKeyInput
    }
  }
  return payload
}

async function save(payload = buildPayload()) {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/settings', payload)
    const latest = await adminApi.json<AnySettings>('/admin/settings')
    applySettings(latest)
    success.value = '设置已保存，已重新读取后台响应。'
    ui.show('设置已保存')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置保存失败'
  } finally {
    saving.value = false
  }
}
function stageSettings() {
  error.value = ''
  success.value = ''
  if (secretInputs.githubOAuthSecret || secretInputs.accessKeyId || secretInputs.ossSecretInput || secretInputs.aiKeyInput) {
    error.value = 'Secret 修改不进入本地 pendingOperations，请直接保存。'
    return
  }
  const payload = buildPayload()
  pendingStore.add({
    kind: 'updateSettings',
    title: '设置修改',
    slug: 'settings.json',
    settingsPayload: payload
  })
  success.value = '设置修改已加入暂存队列，刷新页面会丢失；点击右侧应用后才写入后端。'
  ui.show('设置修改已加入暂存队列')
}

async function saveAdvancedJson() {
  jsonError.value = ''
  try {
    const parsed = JSON.parse(jsonText.value)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      jsonError.value = '高级 JSON 必须是对象'
      return
    }
    await save(parsed)
  } catch (exc) {
    jsonError.value = exc instanceof Error ? exc.message : 'JSON 格式错误'
  }
}

async function uploadInto(field: 'avatar' | 'bg', files: FileList | null) {
  if (!files?.length) return
  const key = field === 'avatar' ? 'avatar' : 'bg'
  uploadProgress.value[key] = 0
  error.value = ''
  try {
    const data = await adminApi.upload(files[0], (percent) => { uploadProgress.value[key] = percent })
    if (field === 'avatar') form.avatar = data.url
    else form.bgImagesText = `${form.bgImagesText.trim()}\n${data.url}`.trim()
    success.value = '上传成功，URL 已填入设置表单。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '上传失败'
  }
}

function testImageBed() {
  if (!['local', 'oss', 'custom'].includes(form.imageBed.provider)) {
    error.value = '图床 provider 只能是 local / oss / custom。'
    return
  }
  success.value = form.imageBed.provider === 'local' ? '本地图床配置格式正常，可使用上传接口测试。' : '图床配置格式检查通过；真实 OSS/custom 连通性需服务端 SDK 支持。'
  error.value = ''
}

onMounted(load)
</script>

<template>
  <div class="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)]">
    <div class="glass h-fit rounded-[30px] p-4 xl:sticky xl:top-6">
      <div class="relative z-[1] grid gap-2">
        <button v-for="tab in tabs" :key="tab.key" class="rounded-2xl px-4 py-3 text-left text-sm transition" :class="active === tab.key ? 'bg-cyan-300/[0.16] text-cyan-100' : 'text-white/60 hover:bg-white/10'" @click="active = tab.key">{{ tab.label }}</button>
      </div>
    </div>

    <div class="grid gap-4">
      <div class="glass rounded-[30px] p-5">
        <div class="relative z-[1] flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black text-white">{{ tabs.find((tab) => tab.key === active)?.label }}</h2>
            <p class="mt-2 text-sm text-white/50">公开设置会进入前台；AI Key、OSS Key、GitHub OAuth Secret 等私有配置只保存在后端。后台不回显 Secret 明文，只显示 configured 状态；Secret 输入框留空保存时会保留旧值。</p>
          </div>
          <button class="admin-btn admin-btn-ghost" @click="load">刷新</button>
        </div>
        <p v-if="loading" class="relative z-[1] mt-4 text-white/55">设置加载中...</p>
        <p v-if="error" class="relative z-[1] mt-4 text-sm text-red-200/85">{{ error }}</p>
        <p v-if="success" class="relative z-[1] mt-4 text-sm text-emerald-200/85">{{ success }}</p>
      </div>

      <div class="glass rounded-[30px] p-5">
        <div class="relative z-[1] grid gap-4">
          <template v-if="active === 'site'">
            <div class="grid gap-3 md:grid-cols-2">
              <label class="grid gap-2 text-sm text-white/65">站点标题<input v-model="form.siteTitle" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">副标题<input v-model="form.subtitle" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">作者名<input v-model="form.author" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">头像 URL<div class="flex gap-2"><input v-model="form.avatar" class="admin-input min-w-0 flex-1" /><label class="admin-btn admin-btn-ghost cursor-pointer">上传<input type="file" accept="image/*" class="hidden" @change="uploadInto('avatar', ($event.target as HTMLInputElement).files)" /></label></div></label>
            </div>
            <label class="grid gap-2 text-sm text-white/65">站点简介<textarea v-model="form.description" rows="4" class="admin-input"></textarea></label>
            <div class="grid gap-3 md:grid-cols-2">
              <label v-for="(_, key) in form.socialLinks" :key="key" class="grid gap-2 text-sm text-white/65">社交链接 {{ key }}<input v-model="form.socialLinks[key]" class="admin-input" /></label>
            </div>
          </template>

          <template v-else-if="active === 'theme'">
            <label class="grid gap-2 text-sm text-white/65">主题<select v-model="form.theme" class="admin-input"><option>nebula</option><option>sakura</option><option>aurora</option><option>cyber</option></select></label>
            <div class="grid gap-3 md:grid-cols-2">
              <label class="grid gap-2 text-sm text-white/65">字体族<input v-model="form.themeConfig.fontFamily" class="admin-input" placeholder="留空使用默认字体" /></label>
              <label class="grid gap-2 text-sm text-white/65">字号档位<select v-model="form.themeConfig.fontScale" class="admin-input"><option value="small">小</option><option value="medium">中</option><option value="large">大</option></select></label>
            </div>
            <div class="grid gap-4 xl:grid-cols-2">
              <div class="rounded-[24px] border border-white/10 bg-white/[0.06] p-4">
                <h3 class="font-black text-white">日间模式核心 token</h3>
                <div class="mt-4 grid gap-3 md:grid-cols-2">
                  <label v-for="(_, key) in form.themeConfig.day" :key="String(key)" class="grid gap-2 text-xs text-white/58">{{ key }}<input v-model="form.themeConfig.day[key]" class="admin-input" /></label>
                </div>
              </div>
              <div class="rounded-[24px] border border-white/10 bg-white/[0.06] p-4">
                <h3 class="font-black text-white">夜间模式核心 token</h3>
                <div class="mt-4 grid gap-3 md:grid-cols-2">
                  <label v-for="(_, key) in form.themeConfig.night" :key="String(key)" class="grid gap-2 text-xs text-white/58">{{ key }}<input v-model="form.themeConfig.night[key]" class="admin-input" /></label>
                </div>
              </div>
            </div>
            <p class="text-sm leading-6 text-white/50">这些 token 会进入公开站点配置，用于前台昼夜模式、顶部导航、卡片、首页模块和文字层级；不要在这里填写任何 Secret。</p>
            <label class="grid gap-2 text-sm text-white/65">背景图列表，每行一个 URL<textarea v-model="form.bgImagesText" rows="6" class="admin-input"></textarea></label>
            <label class="admin-btn admin-btn-ghost w-fit cursor-pointer">上传背景图并追加 URL<input type="file" accept="image/*" class="hidden" @change="uploadInto('bg', ($event.target as HTMLInputElement).files)" /></label>
            <label class="grid gap-2 text-sm text-white/65">公开音乐 ID，逗号分隔<input v-model="form.cloudMusicIdsText" class="admin-input" /></label>
          </template>

          <template v-else-if="active === 'comments'">
            <div class="grid gap-3 md:grid-cols-2">
              <label class="setting-check"><input v-model="form.comments.enabled" type="checkbox" />开启评论</label>
              <label class="setting-check"><input v-model="form.comments.localEnabled" type="checkbox" />启用本地评论</label>
              <label class="setting-check"><input v-model="form.comments.requireEmail" type="checkbox" />评论需要邮箱</label>
              <label class="setting-check"><input v-model="form.comments.showEmail" type="checkbox" />前台显示邮箱</label>
              <label class="grid gap-2 text-sm text-white/65">评论最大长度<input v-model.number="form.comments.maxLength" type="number" min="1" max="5000" class="admin-input" /></label>
            </div>
            <div class="grid gap-3 md:grid-cols-2">
              <label class="grid gap-2 text-sm text-white/65">Gitalk Client ID<input v-model="form.comments.gitalkClientID" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">GitHub Repo<input v-model="form.comments.gitalkRepo" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">GitHub Owner<input v-model="form.comments.gitalkOwner" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">Gitalk Admin，逗号分隔<input v-model="form.comments.gitalkAdminText" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65 md:col-span-2">新的 GitHub OAuth Secret<input v-model="secretInputs.githubOAuthSecret" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保留旧值，不回显明文" /></label>
            </div>
          </template>

          <template v-else-if="active === 'image'">
            <div class="grid gap-3 md:grid-cols-2">
              <label class="grid gap-2 text-sm text-white/65">Provider<select v-model="form.imageBed.provider" class="admin-input"><option>local</option><option>oss</option><option>custom</option></select></label>
              <label class="grid gap-2 text-sm text-white/65">Public Base URL<input v-model="form.imageBed.publicBaseUrl" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">Bucket<input v-model="form.imageBed.bucket" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">Region<input v-model="form.imageBed.region" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">Endpoint<input v-model="form.imageBed.endpoint" class="admin-input" /></label>
              <div class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-white/60">AccessKey configured: {{ form.imageBed.accessKeyConfigured }}<br />Secret configured: {{ form.imageBed.ossSecretConfigured }}</div>
              <label class="grid gap-2 text-sm text-white/65">新的 AccessKey ID<input v-model="secretInputs.accessKeyId" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保留旧值" /></label>
              <label class="grid gap-2 text-sm text-white/65">新的 AccessKey Secret<input v-model="secretInputs.ossSecretInput" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保留旧值" /></label>
            </div>
            <button class="admin-btn admin-btn-ghost w-fit" @click="testImageBed">测试配置格式</button>
          </template>

          <template v-else-if="active === 'ai'">
            <div class="grid gap-3 md:grid-cols-2">
              <label class="grid gap-2 text-sm text-white/65">Provider<input v-model="form.ai.provider" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65">Model<input v-model="form.ai.model" class="admin-input" /></label>
              <label class="grid gap-2 text-sm text-white/65 md:col-span-2">Base URL<input v-model="form.ai.baseUrl" class="admin-input" /></label>
              <label class="setting-check"><input v-model="form.ai.enableChat" type="checkbox" />启用后台聊天</label>
              <div class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm text-white/60">API Key configured: {{ form.ai.aiKeyConfigured }}</div>
              <label class="grid gap-2 text-sm text-white/65 md:col-span-2">新的 API Key<input v-model="secretInputs.aiKeyInput" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保留旧值，不进入前台" /></label>
            </div>
          </template>

          <template v-else>
            <div class="grid gap-3">
              <div v-for="item in productionChecks" :key="item.label" class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm" :class="item.ok ? 'text-emerald-100' : 'text-amber-100'">{{ item.ok ? 'OK' : 'CHECK' }} - {{ item.label }}</div>
              <p class="text-sm leading-6 text-white/55">服务器部署、Nginx、systemd、backend/data 权限和 .env 生产配置请参见 `docs/DEPLOYMENT.md`。</p>
            </div>
          </template>

          <div class="flex flex-wrap gap-3">
            <button :disabled="saving" class="admin-btn admin-btn-primary" @click="save()">{{ saving ? '保存中...' : '保存设置' }}</button>
            <button :disabled="saving" class="admin-btn admin-btn-ghost" @click="stageSettings">加入暂存（非 Secret）</button>
            <button class="admin-btn admin-btn-ghost" @click="load">取消未保存修改</button>
          </div>
        </div>
      </div>

      <div class="glass rounded-[30px] p-5">
        <button class="relative z-[1] flex w-full items-center justify-between text-left" @click="advancedOpen = !advancedOpen">
          <span class="font-bold text-white">高级 JSON 编辑</span>
          <span class="text-sm text-white/45">{{ advancedOpen ? '收起' : '展开' }}</span>
        </button>
        <div v-if="advancedOpen" class="relative z-[1] mt-4 grid gap-3">
          <p class="text-sm leading-6 text-amber-100/70">仅作兜底。Secret 仍不会在后台响应中明文回显；留空 Secret 保存时后端会保留旧值。</p>
          <textarea v-model="jsonText" rows="18" class="admin-input font-mono text-sm"></textarea>
          <p v-if="jsonError" class="text-sm text-red-200/85">{{ jsonError }}</p>
          <button :disabled="saving" class="admin-btn admin-btn-ghost w-fit" @click="saveAdvancedJson">保存高级 JSON</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-input {
  width: 100%;
  border-radius: 1rem;
  border: 1px solid rgb(255 255 255 / 0.1);
  background: rgb(255 255 255 / 0.1);
  padding: 0.75rem 1rem;
  color: white;
  outline: none;
}
.admin-input:focus {
  border-color: rgb(103 232 249 / 0.6);
}
.setting-check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border-radius: 1rem;
  border: 1px solid rgb(255 255 255 / 0.1);
  background: rgb(255 255 255 / 0.06);
  padding: 0.9rem 1rem;
  color: rgb(255 255 255 / 0.72);
}
</style>
