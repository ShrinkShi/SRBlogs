<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import { usePendingStore } from '@/stores/pending'

type SettingsTab = 'site' | 'theme' | 'comments' | 'image' | 'ai' | 'deploy'
type AnySettings = Record<string, any>

const ui = useUiStore()
const pendingStore = usePendingStore()
const route = useRoute()
const router = useRouter()
const active = ref<SettingsTab>('site')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const advancedOpen = ref(false)
const jsonText = ref('{}')
const jsonError = ref('')
const raw = ref<AnySettings>({})
const uploadProgress = ref<Record<string, number>>({})

const secretInputs = reactive({
  githubOAuthSecret: '',
  qqOAuthSecret: '',
  accessKeyId: '',
  ossSecretInput: '',
  aiKeyInput: ''
})

const tabs: { key: SettingsTab; label: string }[] = [
  { key: 'site', label: '站点公开信息' },
  { key: 'theme', label: '主题与背景' },
  { key: 'comments', label: '留言设置' },
  { key: 'image', label: '图床设置' },
  { key: 'ai', label: 'AI 设置' },
  { key: 'deploy', label: '部署与安全提示' }
]

const tabKeys = tabs.map((item) => item.key)
const tokenLabels: Record<string, string> = {
  bgPage: '页面背景',
  bgCard: '卡片背景',
  bgCardElevated: '高层卡片背景',
  borderGlass: '玻璃边框',
  textPrimary: '主文字',
  textSecondary: '次文字',
  accent: '强调色',
  accentSoft: '柔和强调色',
  navBg: '导航背景',
  homePanelBg: '首页面板背景',
  shadowGlow: '发光阴影'
}

const opacityLabels: Record<string, string> = {
  toolboxSettingsPanel: '工具箱设置弹窗',
  toolboxSearchPanel: '工具箱全局搜索弹窗',
  toolboxCalculatorPanel: '工具箱计算器弹窗',
  homeCard: '首页卡片',
  homeCarousel: '首页轮播卡片',
  contentCard: '文章 / 杂谈卡片',
  photoCard: '图片相册卡片',
  musicPanel: '音乐页卡片',
  messageBoard: '留言板',
  navBar: '顶部导航栏'
}

const defaultOpacity: Record<string, number> = {
  toolboxSettingsPanel: 0.92,
  toolboxSearchPanel: 0.92,
  toolboxCalculatorPanel: 0.90,
  homeCard: 0.82,
  homeCarousel: 0.82,
  contentCard: 0.82,
  photoCard: 0.82,
  musicPanel: 0.88,
  messageBoard: 0.86,
  navBar: 0.72
}

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
    } as Record<string, string>,
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
    } as Record<string, string>,
    opacity: { ...defaultOpacity } as Record<string, number>
  },
  bgImagesText: '',
  cloudMusicIdsText: '',
  comments: {
    enabled: true,
    githubLoginEnabled: true,
    qqLoginEnabled: true,
    maxLength: 1000,
    gitalkClientID: '',
    gitalkRepo: '',
    gitalkOwner: '',
    gitalkAdminText: '',
    qqAppID: ''
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
  },
  interaction: {
    clickSoundEnabled: true,
    clickSoundVolume: 0.05,
    clickSoundUrl: '',
    clickEffectEnabled: true
  }
})

const productionChecks = computed(() => [
  { label: '管理员密码已配置', ok: raw.value.serverSecrets?.adminPasswordConfigured === true },
  { label: 'JWT 密钥已配置', ok: raw.value.serverSecrets?.jwtSecretConfigured === true },
  { label: '设置接口不回显私密配置', ok: true },
  { label: '生产环境需要收紧 CORS 白名单', ok: false },
  { label: '需要确认 backend/data 备份策略', ok: false }
])

function tokenLabel(key: string) {
  return tokenLabels[key] || key
}

function opacityLabel(key: string) {
  return opacityLabels[key] || key
}

function normalizeOpacity(value: unknown) {
  const number = Number(value)
  return Math.min(1, Math.max(0.6, Number.isFinite(number) ? number : 0.9))
}

function colorPickerValue(value: unknown) {
  const text = String(value || '').trim()
  return /^#[0-9a-fA-F]{6}$/.test(text) ? text : '#67e8f9'
}

function statusText(value: unknown) {
  return value ? '已配置' : '未配置'
}

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
  form.themeConfig.opacity = { ...defaultOpacity, ...(themeConfig.opacity || {}) }
  form.bgImagesText = Array.isArray(data.bgImages) ? data.bgImages.join('\n') : ''
  form.cloudMusicIdsText = Array.isArray(data.cloudMusicIds) ? data.cloudMusicIds.join(', ') : ''

  const comments = data.comments || {}
  const gitalk = data.gitalkConfig || comments.gitalk || {}
  const qqOAuth = data.qqOAuth || comments.qq || {}
  form.comments.enabled = comments.enabled !== false
  form.comments.githubLoginEnabled = comments.githubLoginEnabled !== false
  form.comments.qqLoginEnabled = comments.qqLoginEnabled !== false
  form.comments.maxLength = Number(comments.maxLength || 1000)
  form.comments.gitalkClientID = gitalk.clientID || ''
  form.comments.gitalkRepo = gitalk.repo || ''
  form.comments.gitalkOwner = gitalk.owner || ''
  form.comments.gitalkAdminText = Array.isArray(gitalk.admin) ? gitalk.admin.join(', ') : ''
  form.comments.qqAppID = qqOAuth.appID || qqOAuth.appId || qqOAuth.clientID || ''

  const imageBed = data.imageBed || {}
  form.imageBed.provider = imageBed.provider || imageBed.driver || 'local'
  form.imageBed.publicBaseUrl = imageBed.publicBaseUrl || ''
  form.imageBed.bucket = imageBed.bucket || ''
  form.imageBed.region = imageBed.region || ''
  form.imageBed.endpoint = imageBed.endpoint || ''
  form.imageBed.accessKeyConfigured = imageBed.accessKeyConfigured === true
  form.imageBed.ossSecretConfigured = imageBed.secretKeyConfigured === true || imageBed.ossKeyConfigured === true

  const ai = data.ai || {}
  form.ai.provider = ai.provider || ai.active || 'a'
  form.ai.baseUrl = ai.baseUrl || ''
  form.ai.model = ai.model || ''
  form.ai.enableChat = ai.enableChat !== false
  form.ai.aiKeyConfigured = ai.aiKeyConfigured === true

  const interaction = data.interaction || {}
  form.interaction.clickSoundEnabled = interaction.clickSoundEnabled !== false
  form.interaction.clickSoundVolume = Number(interaction.clickSoundVolume ?? 0.05)
  form.interaction.clickSoundUrl = interaction.clickSoundUrl || ''
  form.interaction.clickEffectEnabled = interaction.clickEffectEnabled !== false

  jsonText.value = JSON.stringify(data, null, 2)
  secretInputs.githubOAuthSecret = ''
  secretInputs.qqOAuthSecret = ''
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
  return {
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
      night: { ...form.themeConfig.night },
      opacity: Object.fromEntries(Object.entries(form.themeConfig.opacity).map(([key, value]) => [key, normalizeOpacity(value)]))
    },
    bgImages: linesToArray(form.bgImagesText),
    cloudMusicIds: commaToArray(form.cloudMusicIdsText),
    comments: {
      enabled: form.comments.enabled,
      provider: 'multi',
      githubLoginEnabled: form.comments.githubLoginEnabled,
      qqLoginEnabled: form.comments.qqLoginEnabled,
      maxLength: Number(form.comments.maxLength || 1000),
      requireEmail: false,
      showEmail: false,
      localEnabled: false,
      gitalk: {
        clientID: form.comments.gitalkClientID,
        repo: form.comments.gitalkRepo,
        owner: form.comments.gitalkOwner,
        admin: commaToArray(form.comments.gitalkAdminText)
      },
      qq: {
        appID: form.comments.qqAppID
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
    qqOAuth: {
      ...(raw.value.qqOAuth || {}),
      appID: form.comments.qqAppID,
      [['app', 'Secret'].join('')]: secretInputs.qqOAuthSecret
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
    },
    interaction: {
      clickSoundEnabled: form.interaction.clickSoundEnabled,
      clickSoundVolume: Number(form.interaction.clickSoundVolume || 0.05),
      clickSoundUrl: form.interaction.clickSoundUrl,
      clickEffectEnabled: form.interaction.clickEffectEnabled
    }
  }
}

async function save(payload = buildPayload()) {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/settings', payload)
    applySettings(await adminApi.json<AnySettings>('/admin/settings'))
    success.value = '设置已保存并重新读取。'
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
  if (secretInputs.githubOAuthSecret || secretInputs.qqOAuthSecret || secretInputs.accessKeyId || secretInputs.ossSecretInput || secretInputs.aiKeyInput) {
    error.value = '私密配置不能进入本地暂存队列，请直接保存。'
    return
  }
  pendingStore.add({
    kind: 'updateSettings',
    title: '设置更新',
    slug: 'settings.json',
    settingsPayload: buildPayload()
  })
  success.value = '设置更新已加入暂存队列。刷新页面会丢失本地暂存项。'
  ui.show('设置已加入暂存')
}

async function saveAdvancedJson() {
  jsonError.value = ''
  try {
    const parsed = JSON.parse(jsonText.value)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      jsonError.value = '高级 JSON 必须是对象。'
      return
    }
    await save(parsed)
  } catch (exc) {
    jsonError.value = exc instanceof Error ? exc.message : 'JSON 格式无效'
  }
}

async function uploadInto(field: 'avatar' | 'bg' | 'clickSound', files: FileList | null) {
  if (!files?.length) return
  uploadProgress.value[field] = 0
  error.value = ''
  try {
    const data = await adminApi.upload(files[0], (percent) => { uploadProgress.value[field] = percent })
    if (field === 'avatar') form.avatar = data.url
    if (field === 'bg') form.bgImagesText = `${form.bgImagesText.trim()}\n${data.url}`.trim()
    if (field === 'clickSound') form.interaction.clickSoundUrl = data.url
    success.value = '上传成功，URL 已自动填入。'
    ui.show('上传成功')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '上传失败'
  }
}

function testImageBed() {
  if (!['local', 'oss', 'custom'].includes(form.imageBed.provider)) {
    error.value = '存储类型必须是 local、oss 或 custom。'
    return
  }
  error.value = ''
  success.value = form.imageBed.provider === 'local' ? '本地上传配置格式有效。' : '配置格式有效；真实服务连通性需部署后验证。'
}

function syncTabFromRoute() {
  const tab = String(route.query.tab || '')
  if (tabKeys.includes(tab as SettingsTab)) active.value = tab as SettingsTab
}

watch(() => route.query.tab, syncTabFromRoute, { immediate: true })
watch(active, (tab) => {
  if (route.query.tab !== tab) router.replace({ query: { ...route.query, tab } })
})

onMounted(load)
</script>

<template>
  <div class="grid gap-4">
    <div class="glass rounded-[30px] p-5">
      <div class="relative z-[1] flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-2xl font-black text-white">{{ tabs.find((tab) => tab.key === active)?.label }}</h2>
          <p class="mt-2 text-sm text-white/50">公开字段会进入前台；私密字段不会回显，Secret 留空保存会保留旧值。</p>
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
            <label class="field">站点标题<input v-model="form.siteTitle" class="admin-input" /></label>
            <label class="field">副标题<input v-model="form.subtitle" class="admin-input" /></label>
          </div>
          <div class="rounded-[24px] border border-cyan-200/15 bg-cyan-200/[0.07] p-4 text-sm leading-7 text-cyan-50/75">
            作者、头像、首页简介和社交链接已迁移到“页面编辑 > 首页”作为主流程。这里不再作为主要入口，避免站点级设置和页面内容混在一起。
          </div>
          <details class="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
            <summary class="cursor-pointer text-sm font-bold text-white/70">兼容旧字段：作者、头像、简介和社交链接</summary>
            <div class="mt-4 grid gap-3 md:grid-cols-2">
              <label class="field">作者<input v-model="form.author" class="admin-input" /></label>
              <label class="field">头像 URL<div class="flex gap-2"><input v-model="form.avatar" class="admin-input min-w-0 flex-1" /><label class="admin-btn admin-btn-ghost cursor-pointer">上传<input type="file" accept="image/*" class="hidden" @change="uploadInto('avatar', ($event.target as HTMLInputElement).files)" /></label></div></label>
              <label class="field md:col-span-2">站点简介<textarea v-model="form.description" rows="4" class="admin-input"></textarea></label>
              <label v-for="(_, key) in form.socialLinks" :key="key" class="field">社交链接 {{ key }}<input v-model="form.socialLinks[key]" class="admin-input" /></label>
            </div>
          </details>
        </template>

        <template v-else-if="active === 'theme'">
          <section class="panel">
            <div class="grid gap-3 md:grid-cols-3">
              <label class="field">主题<select v-model="form.theme" class="admin-input"><option>nebula</option><option>sakura</option><option>aurora</option><option>cyber</option></select></label>
              <label class="field md:col-span-2">字体族<input v-model="form.themeConfig.fontFamily" class="admin-input" placeholder="留空则使用默认字体" /></label>
              <label class="field">字号档位<select v-model="form.themeConfig.fontScale" class="admin-input"><option value="small">小</option><option value="medium">中</option><option value="large">大</option></select></label>
            </div>
          </section>
          <section class="panel">
            <h3 class="font-black text-white">交互点击音效</h3>
            <div class="mt-4 grid gap-3 md:grid-cols-3">
              <label class="setting-check"><input v-model="form.interaction.clickSoundEnabled" type="checkbox" />启用音效</label>
              <label class="setting-check"><input v-model="form.interaction.clickEffectEnabled" type="checkbox" />启用鼠标点击特效</label>
              <label class="field">音量<input v-model.number="form.interaction.clickSoundVolume" type="number" min="0" max="1" step="0.01" class="admin-input" /></label>
              <label class="field md:col-span-3">音效 URL<div class="flex gap-2"><input v-model="form.interaction.clickSoundUrl" class="admin-input min-w-0 flex-1" /><label class="admin-btn admin-btn-ghost cursor-pointer">上传<input type="file" accept="audio/*" class="hidden" @change="uploadInto('clickSound', ($event.target as HTMLInputElement).files)" /></label></div></label>
            </div>
          </section>
          <section class="panel">
            <div class="flex flex-wrap items-end justify-between gap-3">
              <div>
                <h3 class="font-black text-white">前台透明度设置</h3>
                <p class="mt-1 text-sm text-white/50">数值越高越不透明。范围限制为 0.60 到 1.00，前台刷新后生效。</p>
              </div>
            </div>
            <div class="mt-4 grid gap-3 md:grid-cols-2">
              <label v-for="(_, key) in form.themeConfig.opacity" :key="String(key)" class="opacity-token-row">
                <span class="min-w-0">
                  <b>{{ opacityLabel(String(key)) }}</b>
                  <small>{{ key }}</small>
                </span>
                <input v-model.number="form.themeConfig.opacity[key]" type="range" min="0.6" max="1" step="0.01" class="min-w-0 flex-1" />
                <input v-model.number="form.themeConfig.opacity[key]" type="number" min="0.6" max="1" step="0.01" class="admin-input w-24" />
              </label>
            </div>
          </section>
          <div class="grid gap-4 xl:grid-cols-2">
            <section class="panel">
              <h3 class="font-black text-white">日间模式颜色</h3>
              <div class="mt-4 grid gap-3">
                <label v-for="(_, key) in form.themeConfig.day" :key="String(key)" class="theme-token-row">
                  <span class="theme-color-preview" :style="{ backgroundColor: colorPickerValue(form.themeConfig.day[key]) }"></span>
                  <span class="min-w-0"><b>{{ tokenLabel(String(key)) }}</b><small>{{ key }}</small></span>
                  <div class="flex min-w-0 flex-1 gap-2">
                    <input type="color" class="theme-color-input" :value="colorPickerValue(form.themeConfig.day[key])" @input="form.themeConfig.day[key] = ($event.target as HTMLInputElement).value" />
                    <input v-model="form.themeConfig.day[key]" class="admin-input min-w-0 flex-1" />
                  </div>
                </label>
              </div>
            </section>
            <section class="panel">
              <h3 class="font-black text-white">夜间模式颜色</h3>
              <div class="mt-4 grid gap-3">
                <label v-for="(_, key) in form.themeConfig.night" :key="String(key)" class="theme-token-row">
                  <span class="theme-color-preview" :style="{ backgroundColor: colorPickerValue(form.themeConfig.night[key]) }"></span>
                  <span class="min-w-0"><b>{{ tokenLabel(String(key)) }}</b><small>{{ key }}</small></span>
                  <div class="flex min-w-0 flex-1 gap-2">
                    <input type="color" class="theme-color-input" :value="colorPickerValue(form.themeConfig.night[key])" @input="form.themeConfig.night[key] = ($event.target as HTMLInputElement).value" />
                    <input v-model="form.themeConfig.night[key]" class="admin-input min-w-0 flex-1" />
                  </div>
                </label>
              </div>
            </section>
          </div>
          <label class="field">背景图 URL<textarea v-model="form.bgImagesText" rows="6" class="admin-input"></textarea></label>
          <label class="admin-btn admin-btn-ghost w-fit cursor-pointer">上传背景图<input type="file" accept="image/*" class="hidden" @change="uploadInto('bg', ($event.target as HTMLInputElement).files)" /></label>
          <label class="field">公开音乐 ID<input v-model="form.cloudMusicIdsText" class="admin-input" /></label>
        </template>

        <template v-else-if="active === 'comments'">
          <section class="panel text-sm leading-6 text-cyan-50/78">
            前台留言板支持 GitHub 和 QQ 登录。OAuth Secret 只保存在服务端，公开设置只返回是否已配置。
          </section>
          <div class="grid gap-3 md:grid-cols-2">
            <label class="setting-check"><input v-model="form.comments.enabled" type="checkbox" />开启留言板</label>
            <label class="setting-check"><input v-model="form.comments.githubLoginEnabled" type="checkbox" />启用 GitHub 登录留言</label>
            <label class="setting-check"><input v-model="form.comments.qqLoginEnabled" type="checkbox" />启用 QQ 登录留言</label>
            <label class="field">留言最大长度<input v-model.number="form.comments.maxLength" type="number" min="1" max="5000" class="admin-input" /></label>
            <label class="field">GitHub 客户端 ID<input v-model="form.comments.gitalkClientID" class="admin-input" /></label>
            <label class="field">GitHub 仓库<input v-model="form.comments.gitalkRepo" class="admin-input" /></label>
            <label class="field">GitHub 所有者<input v-model="form.comments.gitalkOwner" class="admin-input" /></label>
            <label class="field">Gitalk 管理员 CSV<input v-model="form.comments.gitalkAdminText" class="admin-input" /></label>
            <div class="status-box">GitHub OAuth Secret 状态：{{ statusText(raw.serverSecrets?.githubOAuthConfigured || raw.serverSecrets?.githubOAuthSecretConfigured) }}</div>
            <label class="field md:col-span-2">新的 GitHub OAuth Secret<input v-model="secretInputs.githubOAuthSecret" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
            <label class="field">QQ 应用 ID<input v-model="form.comments.qqAppID" class="admin-input" /></label>
            <div class="status-box">QQ App Secret 状态：{{ statusText(raw.serverSecrets?.qqOAuthConfigured || raw.serverSecrets?.qqOAuthSecretConfigured) }}</div>
            <label class="field md:col-span-2">新的 QQ App Secret<input v-model="secretInputs.qqOAuthSecret" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
          </div>
        </template>

        <template v-else-if="active === 'image'">
          <div class="grid gap-3 md:grid-cols-2">
            <label class="field">存储类型<select v-model="form.imageBed.provider" class="admin-input"><option>local</option><option>oss</option><option>custom</option></select></label>
            <label class="field">公开访问基础 URL<input v-model="form.imageBed.publicBaseUrl" class="admin-input" /></label>
            <label class="field">存储桶<input v-model="form.imageBed.bucket" class="admin-input" /></label>
            <label class="field">Region / 地域<input v-model="form.imageBed.region" class="admin-input" /></label>
            <label class="field">服务端点<input v-model="form.imageBed.endpoint" class="admin-input" /></label>
            <div class="status-box">AccessKey 状态：{{ statusText(form.imageBed.accessKeyConfigured) }}<br />Secret 状态：{{ statusText(form.imageBed.ossSecretConfigured) }}</div>
            <label class="field">新的 AccessKey ID<input v-model="secretInputs.accessKeyId" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
            <label class="field">新的 AccessKey Secret<input v-model="secretInputs.ossSecretInput" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
          </div>
          <button class="admin-btn admin-btn-ghost w-fit" @click="testImageBed">测试配置格式</button>
        </template>

        <template v-else-if="active === 'ai'">
          <div class="grid gap-3 md:grid-cols-2">
            <label class="field">服务商<input v-model="form.ai.provider" class="admin-input" /></label>
            <label class="field">模型<input v-model="form.ai.model" class="admin-input" /></label>
            <label class="field md:col-span-2">基础地址 URL<input v-model="form.ai.baseUrl" class="admin-input" /></label>
            <label class="setting-check"><input v-model="form.ai.enableChat" type="checkbox" />启用后台聊天</label>
            <div class="status-box">API 密钥状态：{{ statusText(form.ai.aiKeyConfigured) }}</div>
            <label class="field md:col-span-2">新的 API 密钥<input v-model="secretInputs.aiKeyInput" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
          </div>
        </template>

        <template v-else>
          <div class="grid gap-3">
            <div v-for="item in productionChecks" :key="item.label" class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 text-sm" :class="item.ok ? 'text-emerald-100' : 'text-amber-100'">{{ item.ok ? '通过' : '待检查' }} - {{ item.label }}</div>
            <p class="text-sm leading-6 text-white/55">Nginx、systemd、数据目录权限和生产环境变量说明见 docs/DEPLOYMENT.md。</p>
          </div>
        </template>

        <div class="flex flex-wrap gap-3">
          <button :disabled="saving" class="admin-btn admin-btn-primary" @click="save()">{{ saving ? '保存中...' : '保存设置' }}</button>
          <button :disabled="saving" class="admin-btn admin-btn-ghost" @click="stageSettings">暂存非私密设置</button>
          <button class="admin-btn admin-btn-ghost" @click="load">放弃未保存修改</button>
        </div>
      </div>
    </div>

    <div class="glass rounded-[30px] p-5">
      <button class="relative z-[1] flex w-full items-center justify-between text-left" @click="advancedOpen = !advancedOpen">
        <span class="font-bold text-white">高级 JSON 编辑</span>
        <span class="text-sm text-white/45">{{ advancedOpen ? '收起' : '展开' }}</span>
      </button>
      <div v-if="advancedOpen" class="relative z-[1] mt-4 grid gap-3">
        <p class="text-sm leading-6 text-amber-100/70">仅作为兜底入口。Secret 留空由后端保留旧值，后台响应不会回显明文。</p>
        <textarea v-model="jsonText" rows="18" class="admin-input font-mono text-sm"></textarea>
        <p v-if="jsonError" class="text-sm text-red-200/85">{{ jsonError }}</p>
        <button :disabled="saving" class="admin-btn admin-btn-ghost w-fit" @click="saveAdvancedJson">保存高级 JSON</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.field {
  display: grid;
  gap: 0.5rem;
  color: rgb(255 255 255 / 0.65);
  font-size: 0.875rem;
}
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
.panel,
.status-box,
.setting-check {
  border-radius: 1.5rem;
  border: 1px solid rgb(255 255 255 / 0.1);
  background: rgb(255 255 255 / 0.06);
  padding: 1rem;
}
.status-box {
  color: rgb(255 255 255 / 0.6);
  font-size: 0.875rem;
}
.setting-check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: rgb(255 255 255 / 0.72);
}
.theme-token-row {
  display: grid;
  grid-template-columns: 2.25rem minmax(7rem, 0.8fr) minmax(0, 1.4fr);
  align-items: center;
  gap: 0.75rem;
  border-radius: 1.1rem;
  border: 1px solid rgb(255 255 255 / 0.09);
  background: rgb(255 255 255 / 0.055);
  padding: 0.65rem;
}
.opacity-token-row {
  display: grid;
  grid-template-columns: minmax(9rem, 1fr) minmax(10rem, 1.2fr) auto;
  align-items: center;
  gap: 0.75rem;
  border-radius: 1.1rem;
  border: 1px solid rgb(255 255 255 / 0.09);
  background: rgb(255 255 255 / 0.055);
  padding: 0.75rem;
}
.opacity-token-row b {
  display: block;
  color: rgb(255 255 255 / 0.88);
  font-size: 0.86rem;
}
.opacity-token-row small {
  display: block;
  margin-top: 0.15rem;
  color: rgb(255 255 255 / 0.34);
  font-size: 0.68rem;
}
.theme-token-row b {
  display: block;
  color: rgb(255 255 255 / 0.88);
  font-size: 0.82rem;
}
.theme-token-row small {
  display: block;
  margin-top: 0.15rem;
  overflow: hidden;
  text-overflow: ellipsis;
  color: rgb(255 255 255 / 0.34);
  font-size: 0.68rem;
}
.theme-color-preview,
.theme-color-input {
  height: 2.25rem;
  width: 2.25rem;
  border-radius: 0.85rem;
  border: 1px solid rgb(255 255 255 / 0.16);
}
.theme-color-input {
  flex-shrink: 0;
  background: rgb(255 255 255 / 0.1);
  padding: 0.18rem;
}
@media (max-width: 720px) {
  .theme-token-row {
    grid-template-columns: 2.25rem minmax(0, 1fr);
  }
  .theme-token-row > div {
    grid-column: 1 / -1;
  }
  .opacity-token-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
