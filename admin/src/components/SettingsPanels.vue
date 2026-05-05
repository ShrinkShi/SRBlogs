<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import { usePendingStore } from '@/stores/pending'

type SettingsTab = 'site' | 'theme' | 'comments' | 'image' | 'ai' | 'deploy'
type SizeValue = 'small' | 'medium' | 'large'
type AlignValue = 'left' | 'center' | 'right'
type AnyRecord = Record<string, any>

interface ComponentThemeItem {
  label: string
  group: string
  day: Record<string, string>
  night: Record<string, string>
  opacity: number
  size: SizeValue
  fontFamily: string
  fontSize: number
  textColor: string
  textAlign: AlignValue
  fontWeight: string
  fontStyle: string
}

const route = useRoute()
const router = useRouter()
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
const raw = ref<AnyRecord>({})
const pageConfig = ref<AnyRecord>({})
const themeImportInput = ref<HTMLInputElement | null>(null)

const secretInputs = reactive({
  githubOAuthSecret: '',
  qqOAuthSecret: '',
  accessKeyId: '',
  ossSecretInput: '',
  aiKeyInput: ''
})

const tabs: { key: SettingsTab; label: string; hint: string }[] = [
  { key: 'site', label: '站点公开信息', hint: '全站标题、背景与公开音乐配置' },
  { key: 'theme', label: '主题与背景', hint: '红白黑主题包、组件样式与交互配置' },
  { key: 'comments', label: '留言设置', hint: 'GitHub / QQ 访客留言登录配置' },
  { key: 'image', label: '图床设置', hint: '本地、OSS 或自定义资源配置' },
  { key: 'ai', label: 'AI 设置', hint: '服务端 AI 配置边界' },
  { key: 'deploy', label: '部署与安全提示', hint: '上线前检查项' }
]
const tabKeys = tabs.map((item) => item.key)

const tokenLabels: Record<string, string> = {
  bgImage: '背景壁纸',
  overlayColor: '背景蒙层颜色',
  overlayOpacity: '背景蒙层透明度',
  pageBg: '页面背景',
  bgPage: '页面背景兼容字段',
  cardBg: '卡片背景',
  bgCard: '卡片背景兼容字段',
  bgCardElevated: '高层卡片背景',
  cardOpacity: '卡片透明度',
  textPrimary: '主文字',
  textSecondary: '次文字',
  accent: '重点红色',
  accentHover: '重点红色悬停',
  accentSoft: '柔和重点色',
  border: '边框',
  borderGlass: '玻璃边框兼容字段',
  shadow: '阴影',
  shadowGlow: '发光阴影',
  navBg: '导航背景',
  homePanelBg: '首页面板背景',
  fontFamily: '字体族',
  fontSizeBase: '基础字号',
  titleScale: '标题倍率',
  radius: '圆角',
  blur: '模糊强度'
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

const componentCatalog: { key: string; label: string; group: string }[] = [
  { key: 'topNav', label: '顶部导航栏', group: '全局组件' },
  { key: 'toolboxFab', label: '左下角工具箱悬浮球', group: '工具箱' },
  { key: 'toolboxMenu', label: '工具箱菜单', group: '工具箱' },
  { key: 'toolboxSettingsPanel', label: '工具箱设置弹窗', group: '工具箱' },
  { key: 'toolboxSearchPanel', label: '工具箱全局搜索弹窗', group: '工具箱' },
  { key: 'toolboxCalculatorPanel', label: '工具箱计算器弹窗', group: '工具箱' },
  { key: 'toast', label: 'Toast 提示', group: '全局组件' },
  { key: 'homeProfileCard', label: '首页名片', group: '首页组件' },
  { key: 'homeMusicPlayer', label: '首页音乐播放器', group: '首页组件' },
  { key: 'homeLyrics', label: '首页歌词区', group: '首页组件' },
  { key: 'homeLatestPostsCarousel', label: '首页最新文章轮播', group: '首页组件' },
  { key: 'homePhotoCarousel', label: '首页图片轮播', group: '首页组件' },
  { key: 'homeUpdatesCarousel', label: '首页更新内容轮播', group: '首页组件' },
  { key: 'homeThemeToggle', label: '首页昼夜切换卡片', group: '首页组件' },
  { key: 'homeStatusBar', label: '首页底部状态区', group: '首页组件' },
  { key: 'sectionSwitch', label: '正经 / 杂谈切换按钮', group: '搜索与切换组件' },
  { key: 'viewModeSwitch', label: '矩阵网格 / 中枢链路切换按钮', group: '搜索与切换组件' },
  { key: 'postCard', label: '文章卡片', group: '内容列表组件' },
  { key: 'chatterCard', label: '杂谈卡片', group: '内容列表组件' },
  { key: 'photoAlbumCard', label: '图片相册卡片', group: '内容列表组件' },
  { key: 'musicPlayerPanel', label: '音乐页播放器面板', group: '音乐组件' },
  { key: 'musicLyricsPanel', label: '音乐页歌词 / 歌单面板', group: '音乐组件' },
  { key: 'messageBoard', label: '留言板', group: '留言组件' },
  { key: 'searchInput', label: '搜索框', group: '搜索与切换组件' },
  { key: 'searchButton', label: '搜索按钮', group: '搜索与切换组件' },
  { key: 'tagButton', label: '标签按钮', group: '搜索与切换组件' }
]

const defaultOpacity: Record<string, number> = {
  toolboxSettingsPanel: 0.92,
  toolboxSearchPanel: 0.92,
  toolboxCalculatorPanel: 0.9,
  homeCard: 0.82,
  homeCarousel: 0.82,
  contentCard: 0.82,
  photoCard: 0.82,
  musicPanel: 0.88,
  messageBoard: 0.86,
  navBar: 0.72
}

const defaultDay = {
  bgImage: '',
  overlayColor: '#ffffff',
  overlayOpacity: '0.66',
  pageBg: '#f7f7f7',
  bgPage: '#f7f7f7',
  cardBg: 'rgba(255,255,255,.82)',
  bgCard: 'rgba(255,255,255,.82)',
  bgCardElevated: 'rgba(255,255,255,.92)',
  cardOpacity: '0.82',
  textPrimary: '#111111',
  textSecondary: '#565656',
  accent: '#e11d48',
  accentHover: '#be123c',
  accentSoft: 'rgba(225,29,72,.14)',
  border: 'rgba(17,17,17,.14)',
  borderGlass: 'rgba(17,17,17,.14)',
  shadow: 'rgba(17,17,17,.16)',
  shadowGlow: 'rgba(225,29,72,.2)',
  navBg: 'rgba(255,255,255,.84)',
  homePanelBg: 'rgba(255,255,255,.82)',
  fontFamily: '',
  fontSizeBase: '16',
  titleScale: '1.2',
  radius: '24',
  blur: '18'
}

const defaultNight = {
  bgImage: '',
  overlayColor: '#000000',
  overlayOpacity: '0.68',
  pageBg: '#050505',
  bgPage: '#050505',
  cardBg: 'rgba(16,16,18,.78)',
  bgCard: 'rgba(16,16,18,.78)',
  bgCardElevated: 'rgba(26,26,28,.86)',
  cardOpacity: '0.78',
  textPrimary: '#f5f5f5',
  textSecondary: '#b8b8b8',
  accent: '#e11d48',
  accentHover: '#fb7185',
  accentSoft: 'rgba(225,29,72,.18)',
  border: 'rgba(255,255,255,.16)',
  borderGlass: 'rgba(255,255,255,.16)',
  shadow: 'rgba(0,0,0,.45)',
  shadowGlow: 'rgba(225,29,72,.28)',
  navBg: 'rgba(8,8,10,.78)',
  homePanelBg: 'rgba(16,16,18,.78)',
  fontFamily: '',
  fontSizeBase: '16',
  titleScale: '1.2',
  radius: '24',
  blur: '18'
}

function makeComponentTheme(): Record<string, ComponentThemeItem> {
  return Object.fromEntries(componentCatalog.map((item) => [
    item.key,
    {
      label: item.label,
      group: item.group,
      day: {
        bg: item.key === 'searchButton' ? '#111827' : 'rgba(255,255,255,.86)',
        text: item.key === 'searchButton' ? '#ffffff' : '#111111',
        accent: '#e11d48',
        border: 'rgba(17,17,17,.14)'
      },
      night: {
        bg: item.key === 'searchButton' ? '#050505' : 'rgba(16,16,18,.82)',
        text: '#f5f5f5',
        accent: '#e11d48',
        border: 'rgba(255,255,255,.16)'
      },
      opacity: opacityDefaultFor(item.key),
      size: 'medium',
      fontFamily: '',
      fontSize: 16,
      textColor: '',
      textAlign: 'left',
      fontWeight: 'normal',
      fontStyle: 'normal'
    } as ComponentThemeItem
  ]))
}

function opacityDefaultFor(key: string) {
  if (key === 'topNav') return defaultOpacity.navBar
  if (key.includes('toolboxSettings')) return defaultOpacity.toolboxSettingsPanel
  if (key.includes('toolboxSearch')) return defaultOpacity.toolboxSearchPanel
  if (key.includes('toolboxCalculator')) return defaultOpacity.toolboxCalculatorPanel
  if (key.startsWith('home') && key.includes('Carousel')) return defaultOpacity.homeCarousel
  if (key.startsWith('home')) return defaultOpacity.homeCard
  if (key.includes('photo')) return defaultOpacity.photoCard
  if (key.includes('music')) return defaultOpacity.musicPanel
  if (key === 'messageBoard') return defaultOpacity.messageBoard
  if (key.includes('Card')) return defaultOpacity.contentCard
  return 0.86
}

const form = reactive({
  siteTitle: '',
  subtitle: '',
  theme: 'shrink-red-glass',
  themeConfig: {
    activeTheme: 'shrink-red-glass',
    themePackages: {} as Record<string, unknown>,
    fontFamily: '',
    fontScale: 'medium',
    day: { ...defaultDay } as Record<string, string>,
    night: { ...defaultNight } as Record<string, string>,
    opacity: { ...defaultOpacity } as Record<string, number>,
    componentTheme: makeComponentTheme()
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

const groupedComponents = computed(() => {
  const groups: Record<string, [string, ComponentThemeItem][]> = {}
  Object.entries(form.themeConfig.componentTheme).forEach(([key, item]) => {
    const group = item.group || '其他组件'
    if (!groups[group]) groups[group] = []
    groups[group].push([key, item])
  })
  return groups
})

const productionChecks = computed(() => [
  { label: '管理员密码已配置', ok: raw.value.serverSecrets?.adminPasswordConfigured === true },
  { label: 'JWT 密钥已配置', ok: raw.value.serverSecrets?.jwtSecretConfigured === true },
  { label: '公开设置不回显 Secret', ok: true },
  { label: '生产环境需要收紧 CORS 白名单', ok: false },
  { label: '部署前需要确认 backend/data 备份策略', ok: false }
])

watch(
  () => route.query.tab,
  (tab) => {
    if (typeof tab === 'string' && tabKeys.includes(tab as SettingsTab)) active.value = tab as SettingsTab
  },
  { immediate: true }
)

function changeTab(tab: SettingsTab) {
  active.value = tab
  router.replace({ query: { ...route.query, tab } })
}

function statusText(value: unknown) {
  return value ? '已配置' : '未配置'
}

function parseLines(value: string) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function commaToArray(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function normalizeOpacity(value: unknown) {
  const number = Number(value)
  if (!Number.isFinite(number)) return 0.9
  return Math.min(1, Math.max(0, number))
}

function colorPickerValue(value: unknown) {
  const text = String(value || '').trim()
  return /^#[0-9a-fA-F]{6}$/.test(text) ? text : '#e11d48'
}

function tokenLabel(key: string) {
  return tokenLabels[key] || key
}

function opacityLabel(key: string) {
  return opacityLabels[key] || key
}

function mergeComponentTheme(value: unknown) {
  const defaults = makeComponentTheme()
  const source = value && typeof value === 'object' ? (value as Record<string, Partial<ComponentThemeItem>>) : {}
  Object.entries(source).forEach(([key, incoming]) => {
    if (!defaults[key] || !incoming) return
    defaults[key] = {
      ...defaults[key],
      ...incoming,
      day: { ...defaults[key].day, ...(incoming.day || {}) },
      night: { ...defaults[key].night, ...(incoming.night || {}) },
      opacity: normalizeOpacity(incoming.opacity ?? defaults[key].opacity),
      size: ['small', 'medium', 'large'].includes(String(incoming.size)) ? (incoming.size as SizeValue) : defaults[key].size,
      textAlign: ['left', 'center', 'right'].includes(String(incoming.textAlign)) ? (incoming.textAlign as AlignValue) : defaults[key].textAlign
    }
  })
  return defaults
}

function redComponentTheme(item: ComponentThemeItem) {
  return {
    ...item,
    day: {
      ...item.day,
      bg: item.day?.bg || 'rgba(255,255,255,.86)',
      text: item.day?.text || '#111111',
      accent: '#e11d48',
      border: item.day?.border || 'rgba(17,17,17,.14)'
    },
    night: {
      ...item.night,
      bg: item.night?.bg || 'rgba(16,16,18,.82)',
      text: item.night?.text || '#f5f5f5',
      accent: '#e11d48',
      border: item.night?.border || 'rgba(255,255,255,.16)'
    },
    opacity: normalizeOpacity(item.opacity ?? 0.86)
  }
}

function buildThemePackage(includeLayouts = true) {
  return {
    id: 'shrink-red-glass',
    name: 'Shrink 红白黑玻璃主题',
    description: '白天白灰红、夜间黑灰红的毛玻璃主题。',
    version: 1,
    author: 'Shrink',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    modes: {
      day: { ...form.themeConfig.day },
      night: { ...form.themeConfig.night }
    },
    componentTheme: JSON.parse(JSON.stringify(form.themeConfig.componentTheme)),
    pageLayouts: includeLayouts ? (pageConfig.value.pageLayouts || pageConfig.value || {}) : {}
  }
}

function applyRedThemeToForm() {
  form.theme = 'shrink-red-glass'
  form.themeConfig.activeTheme = 'shrink-red-glass'
  form.themeConfig.day = { ...form.themeConfig.day, ...defaultDay }
  form.themeConfig.night = { ...form.themeConfig.night, ...defaultNight }
  form.themeConfig.opacity = { ...form.themeConfig.opacity, ...defaultOpacity }
  form.themeConfig.componentTheme = Object.fromEntries(
    Object.entries(form.themeConfig.componentTheme).map(([key, item]) => [key, redComponentTheme(item)])
  )
  form.themeConfig.themePackages = {
    'shrink-red-glass': buildThemePackage()
  }
}

async function applyRedThemeNow(includeLayout = false) {
  applyRedThemeToForm()
  if (includeLayout) {
    form.themeConfig.themePackages['shrink-red-glass'] = buildThemePackage(true)
  }
  await save()
}

function exportCurrentTheme() {
  const blob = new Blob([JSON.stringify(buildThemePackage(true), null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'shrink-red-glass-theme.json'
  link.click()
  URL.revokeObjectURL(url)
  success.value = '主题已导出，导出文件不包含 Secret。'
}

function triggerThemeImport() {
  themeImportInput.value?.click()
}

async function importThemeFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    const text = await file.text()
    const imported = JSON.parse(text)
    if (!imported || typeof imported !== 'object' || !imported.modes?.day || !imported.modes?.night) {
      throw new Error('主题文件缺少 day/night 配置。')
    }
    const applyLayout = window.confirm('是否同时导入主题包中的页面布局？取消则只导入配色和组件样式。')
    form.theme = String(imported.id || 'shrink-red-glass')
    form.themeConfig.activeTheme = form.theme
    form.themeConfig.day = { ...form.themeConfig.day, ...(imported.modes.day || {}) }
    form.themeConfig.night = { ...form.themeConfig.night, ...(imported.modes.night || {}) }
    if (imported.componentTheme) form.themeConfig.componentTheme = mergeComponentTheme(imported.componentTheme)
    form.themeConfig.themePackages = {
      ...(form.themeConfig.themePackages || {}),
      [form.theme]: imported
    }
    if (applyLayout && imported.pageLayouts) {
      const current = pageConfig.value || {}
      await adminApi.putJson('/admin/pages/config', { ...current, pageLayouts: imported.pageLayouts })
      pageConfig.value = await adminApi.json<AnyRecord>('/admin/pages/config')
    }
    await save()
    success.value = '主题导入并应用成功。'
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '主题导入失败。'
  }
}

function applySettings(data: AnyRecord) {
  raw.value = data || {}
  form.siteTitle = data.siteTitle || data.title || ''
  form.subtitle = data.subtitle || ''
  form.theme = 'shrink-red-glass'
  form.bgImagesText = Array.isArray(data.bgImages) ? data.bgImages.join('\n') : ''
  form.cloudMusicIdsText = Array.isArray(data.cloudMusicIds) ? data.cloudMusicIds.join('\n') : ''

  const themeConfig = data.themeConfig || {}
  form.themeConfig.activeTheme = themeConfig.activeTheme || 'shrink-red-glass'
  form.themeConfig.themePackages = themeConfig.themePackages || {}
  form.themeConfig.fontFamily = themeConfig.fontFamily || ''
  form.themeConfig.fontScale = themeConfig.fontScale || 'medium'
  form.themeConfig.day = { ...defaultDay, ...(themeConfig.day || {}) }
  form.themeConfig.night = { ...defaultNight, ...(themeConfig.night || {}) }
  form.themeConfig.opacity = { ...defaultOpacity, ...(themeConfig.opacity || {}) }
  Object.keys(form.themeConfig.opacity).forEach((key) => {
    form.themeConfig.opacity[key] = normalizeOpacity(form.themeConfig.opacity[key])
  })
  form.themeConfig.componentTheme = mergeComponentTheme(themeConfig.componentTheme)
  if (!form.themeConfig.themePackages['shrink-red-glass']) {
    form.themeConfig.themePackages['shrink-red-glass'] = buildThemePackage(false)
  }

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
  form.ai.provider = ai.provider || 'a'
  form.ai.baseUrl = ai.baseUrl || ''
  form.ai.model = ai.model || ''
  form.ai.enableChat = ai.enableChat !== false
  form.ai.aiKeyConfigured = ai.aiKeyConfigured === true

  const interaction = data.interaction || {}
  form.interaction.clickSoundEnabled = interaction.clickSoundEnabled !== false
  form.interaction.clickSoundVolume = Number(interaction.clickSoundVolume ?? 0.05)
  form.interaction.clickSoundUrl = interaction.clickSoundUrl || ''
  form.interaction.clickEffectEnabled = interaction.clickEffectEnabled !== false

  secretInputs.githubOAuthSecret = ''
  secretInputs.qqOAuthSecret = ''
  secretInputs.accessKeyId = ''
  secretInputs.ossSecretInput = ''
  secretInputs.aiKeyInput = ''
  jsonText.value = JSON.stringify(data, null, 2)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [settings, pages] = await Promise.all([
      adminApi.json<AnyRecord>('/admin/settings'),
      adminApi.json<AnyRecord>('/admin/pages/config').catch(() => ({}))
    ])
    pageConfig.value = pages || {}
    applySettings(settings)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置加载失败。'
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  const payload: AnyRecord = {
    ...raw.value,
    siteTitle: form.siteTitle,
    subtitle: form.subtitle,
    theme: 'shrink-red-glass',
    themeConfig: {
      ...(raw.value.themeConfig || {}),
      activeTheme: form.themeConfig.activeTheme || 'shrink-red-glass',
      themePackages: {
        ...(form.themeConfig.themePackages || {}),
        'shrink-red-glass': buildThemePackage(true)
      },
      fontFamily: form.themeConfig.fontFamily,
      fontScale: form.themeConfig.fontScale,
      day: { ...form.themeConfig.day },
      night: { ...form.themeConfig.night },
      opacity: Object.fromEntries(Object.entries(form.themeConfig.opacity).map(([key, value]) => [key, normalizeOpacity(value)])),
      componentTheme: JSON.parse(JSON.stringify(form.themeConfig.componentTheme))
    },
    bgImages: parseLines(form.bgImagesText),
    cloudMusicIds: parseLines(form.cloudMusicIdsText),
    comments: {
      ...(raw.value.comments || {}),
      enabled: form.comments.enabled,
      provider: 'multi',
      githubLoginEnabled: form.comments.githubLoginEnabled,
      qqLoginEnabled: form.comments.qqLoginEnabled,
      maxLength: Number(form.comments.maxLength || 1000)
    },
    gitalkConfig: {
      ...(raw.value.gitalkConfig || {}),
      clientID: form.comments.gitalkClientID,
      repo: form.comments.gitalkRepo,
      owner: form.comments.gitalkOwner,
      admin: commaToArray(form.comments.gitalkAdminText),
      clientSecret: secretInputs.githubOAuthSecret
    },
    qqOAuth: {
      ...(raw.value.qqOAuth || {}),
      appID: form.comments.qqAppID,
      appSecret: secretInputs.qqOAuthSecret
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
      accessKeySecret: secretInputs.ossSecretInput
    },
    ai: {
      ...(raw.value.ai || {}),
      provider: form.ai.provider,
      baseUrl: form.ai.baseUrl,
      model: form.ai.model,
      enableChat: form.ai.enableChat,
      apiKey: secretInputs.aiKeyInput
    },
    interaction: {
      ...(raw.value.interaction || {}),
      clickSoundEnabled: form.interaction.clickSoundEnabled,
      clickSoundVolume: Number(form.interaction.clickSoundVolume || 0),
      clickSoundUrl: form.interaction.clickSoundUrl,
      clickEffectEnabled: form.interaction.clickEffectEnabled
    }
  }
  return payload
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/settings', buildPayload())
    applySettings(await adminApi.json<AnyRecord>('/admin/settings'))
    success.value = '设置已保存。'
    ui.show('设置已保存')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置保存失败。'
  } finally {
    saving.value = false
  }
}

function stageSettings() {
  pendingStore.add({
    kind: 'updateSettings',
    title: '设置中心修改',
    slug: 'settings',
    settingsPayload: buildPayload()
  })
  ui.show('已加入操作暂存区')
}

function saveAdvancedJson() {
  jsonError.value = ''
  try {
    const parsed = JSON.parse(jsonText.value)
    applySettings(parsed)
    success.value = '高级 JSON 已应用到表单，保存后写入。'
  } catch (exc) {
    jsonError.value = exc instanceof Error ? exc.message : 'JSON 格式错误。'
  }
}

async function uploadInto(target: 'clickSoundUrl') {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'audio/*'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    try {
      const result = await adminApi.upload(file)
      form.interaction[target] = result.url
      success.value = '音效文件已上传并填入 URL。'
    } catch (exc) {
      error.value = exc instanceof Error ? exc.message : '上传失败。'
    }
  }
  input.click()
}

function resetComponent(key: string) {
  const defaults = makeComponentTheme()
  if (defaults[key]) form.themeConfig.componentTheme[key] = defaults[key]
}

function resetAllComponents() {
  form.themeConfig.componentTheme = makeComponentTheme()
}

onMounted(load)
</script>

<template>
  <div class="settings-shell">
    <header class="settings-header">
      <div>
        <p class="admin-section-title">settings</p>
        <h1>设置中心</h1>
        <p>公开配置、主题包、留言、图床、AI 和部署提示集中管理。Secret 不会回显明文。</p>
      </div>
      <div class="settings-actions">
        <button class="admin-btn admin-btn-ghost" type="button" @click="stageSettings">加入暂存</button>
        <button class="admin-btn admin-btn-primary" type="button" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存设置' }}</button>
      </div>
    </header>

    <p v-if="loading" class="status-box">设置加载中...</p>
    <p v-if="error" class="status-box status-error">{{ error }}</p>
    <p v-if="success" class="status-box status-success">{{ success }}</p>

    <nav class="settings-tabs" aria-label="设置分区">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="settings-tab"
        :class="{ active: active === tab.key }"
        @click="changeTab(tab.key)"
      >
        <span>{{ tab.label }}</span>
        <small>{{ tab.hint }}</small>
      </button>
    </nav>

    <section v-if="active === 'site'" class="settings-panel">
      <h2>站点公开信息</h2>
      <p class="panel-note">作者、头像、首页简介等首页字段已迁移到“页面编辑 > 首页”。这里保留全站级字段。</p>
      <div class="settings-grid">
        <label class="field">站点标题<input v-model="form.siteTitle" class="admin-input" /></label>
        <label class="field">副标题<input v-model="form.subtitle" class="admin-input" /></label>
        <label class="field md:col-span-2">背景图列表<textarea v-model="form.bgImagesText" rows="4" class="admin-input" placeholder="每行一个 URL" /></label>
        <label class="field md:col-span-2">公开音乐 ID / 配置<textarea v-model="form.cloudMusicIdsText" rows="3" class="admin-input" placeholder="每行一个 ID 或公开配置" /></label>
      </div>
    </section>

    <section v-else-if="active === 'theme'" class="settings-panel">
      <h2>主题与背景</h2>
      <p class="panel-note">当前只保留红白黑玻璃主题；组件仍可单独微调颜色、透明度、字体和大小。</p>

      <div class="theme-manager">
        <div class="settings-grid">
          <label class="field">当前主题
            <select v-model="form.theme" class="admin-input">
              <option value="shrink-red-glass">Shrink 红白黑玻璃主题</option>
            </select>
          </label>
          <label class="field">字体族<input v-model="form.themeConfig.fontFamily" class="admin-input" placeholder="留空则使用默认字体" /></label>
          <label class="field">前台字号档位
            <select v-model="form.themeConfig.fontScale" class="admin-input">
              <option value="small">小</option>
              <option value="medium">中</option>
              <option value="large">大</option>
            </select>
          </label>
        </div>
        <div class="settings-actions compact">
          <button class="admin-btn admin-btn-primary" type="button" @click="applyRedThemeNow(false)">一键应用颜色和字体</button>
          <button class="admin-btn admin-btn-ghost" type="button" @click="applyRedThemeNow(true)">一键应用颜色、字体和布局</button>
          <button class="admin-btn admin-btn-ghost" type="button" @click="exportCurrentTheme">导出当前主题</button>
          <button class="admin-btn admin-btn-ghost" type="button" @click="triggerThemeImport">导入主题 JSON</button>
          <input ref="themeImportInput" class="hidden" type="file" accept="application/json,.json" @change="importThemeFile" />
        </div>
      </div>

      <details class="settings-details" open>
        <summary>白天模式 token</summary>
        <div class="token-grid">
          <label v-for="(_, key) in form.themeConfig.day" :key="String(key)" class="token-row">
            <span>{{ tokenLabel(String(key)) }}</span>
            <input type="color" class="color-input" :value="colorPickerValue(form.themeConfig.day[key])" @input="form.themeConfig.day[key] = ($event.target as HTMLInputElement).value" />
            <input v-model="form.themeConfig.day[key]" class="admin-input" />
          </label>
        </div>
      </details>

      <details class="settings-details">
        <summary>夜间模式 token</summary>
        <div class="token-grid">
          <label v-for="(_, key) in form.themeConfig.night" :key="String(key)" class="token-row">
            <span>{{ tokenLabel(String(key)) }}</span>
            <input type="color" class="color-input" :value="colorPickerValue(form.themeConfig.night[key])" @input="form.themeConfig.night[key] = ($event.target as HTMLInputElement).value" />
            <input v-model="form.themeConfig.night[key]" class="admin-input" />
          </label>
        </div>
      </details>

      <details class="settings-details" open>
        <summary>前台透明度设置</summary>
        <p class="panel-note">范围 0 到 1。0 表示完全透明，可能导致组件不可见。</p>
        <div class="opacity-grid">
          <label v-for="(_, key) in form.themeConfig.opacity" :key="String(key)" class="opacity-row">
            <span>{{ opacityLabel(String(key)) }}</span>
            <input v-model.number="form.themeConfig.opacity[key]" type="range" min="0" max="1" step="0.01" />
            <input v-model.number="form.themeConfig.opacity[key]" type="number" min="0" max="1" step="0.01" class="admin-input compact-input" />
          </label>
        </div>
      </details>

      <details class="settings-details">
        <summary>交互设置</summary>
        <div class="settings-grid">
          <label class="setting-check"><input v-model="form.interaction.clickSoundEnabled" type="checkbox" />启用点击音效</label>
          <label class="setting-check"><input v-model="form.interaction.clickEffectEnabled" type="checkbox" />启用鼠标点击特效</label>
          <label class="field">点击音效音量<input v-model.number="form.interaction.clickSoundVolume" type="range" min="0" max="1" step="0.01" /></label>
          <label class="field">点击音效 URL<input v-model="form.interaction.clickSoundUrl" class="admin-input" /></label>
          <button class="admin-btn admin-btn-ghost" type="button" @click="uploadInto('clickSoundUrl')">上传点击音效</button>
        </div>
      </details>

      <details class="settings-details">
        <summary>组件级样式</summary>
        <div class="component-groups">
          <details v-for="(items, group) in groupedComponents" :key="group" class="component-group">
            <summary>{{ group }}</summary>
            <article v-for="[key, item] in items" :key="key" class="component-theme-card">
              <header>
                <div>
                  <strong>{{ item.label }}</strong>
                  <small>{{ key }}</small>
                </div>
                <button class="admin-btn admin-btn-ghost small" type="button" @click="resetComponent(key)">恢复默认</button>
              </header>
              <div class="settings-grid dense">
                <label class="field">大小档位
                  <select v-model="item.size" class="admin-input">
                    <option value="small">小</option>
                    <option value="medium">中</option>
                    <option value="large">大</option>
                  </select>
                </label>
                <label class="field">透明度
                  <input v-model.number="item.opacity" type="range" min="0" max="1" step="0.01" />
                  <input v-model.number="item.opacity" type="number" min="0" max="1" step="0.01" class="admin-input compact-input" />
                </label>
                <label class="field">字体族<input v-model="item.fontFamily" class="admin-input" /></label>
                <label class="field">字号<input v-model.number="item.fontSize" type="number" min="8" max="64" class="admin-input" /></label>
                <label class="field">文字对齐
                  <select v-model="item.textAlign" class="admin-input">
                    <option value="left">靠左</option>
                    <option value="center">居中</option>
                    <option value="right">靠右</option>
                  </select>
                </label>
                <label class="field">字体颜色
                  <input type="color" class="color-input" :value="colorPickerValue(item.textColor)" @input="item.textColor = ($event.target as HTMLInputElement).value" />
                  <input v-model="item.textColor" class="admin-input" />
                </label>
                <label class="setting-check"><input v-model="item.fontWeight" true-value="700" false-value="normal" type="checkbox" />加粗</label>
                <label class="setting-check"><input v-model="item.fontStyle" true-value="italic" false-value="normal" type="checkbox" />斜体</label>
              </div>
              <div class="mode-columns">
                <div>
                  <h4>日间</h4>
                  <label class="mini-field">背景<input type="color" class="color-input" :value="colorPickerValue(item.day.bg)" @input="item.day.bg = ($event.target as HTMLInputElement).value" /><input v-model="item.day.bg" class="admin-input" /></label>
                  <label class="mini-field">文字<input type="color" class="color-input" :value="colorPickerValue(item.day.text)" @input="item.day.text = ($event.target as HTMLInputElement).value" /><input v-model="item.day.text" class="admin-input" /></label>
                  <label class="mini-field">重点<input type="color" class="color-input" :value="colorPickerValue(item.day.accent)" @input="item.day.accent = ($event.target as HTMLInputElement).value" /><input v-model="item.day.accent" class="admin-input" /></label>
                  <label class="mini-field">边框<input v-model="item.day.border" class="admin-input" /></label>
                </div>
                <div>
                  <h4>夜间</h4>
                  <label class="mini-field">背景<input type="color" class="color-input" :value="colorPickerValue(item.night.bg)" @input="item.night.bg = ($event.target as HTMLInputElement).value" /><input v-model="item.night.bg" class="admin-input" /></label>
                  <label class="mini-field">文字<input type="color" class="color-input" :value="colorPickerValue(item.night.text)" @input="item.night.text = ($event.target as HTMLInputElement).value" /><input v-model="item.night.text" class="admin-input" /></label>
                  <label class="mini-field">重点<input type="color" class="color-input" :value="colorPickerValue(item.night.accent)" @input="item.night.accent = ($event.target as HTMLInputElement).value" /><input v-model="item.night.accent" class="admin-input" /></label>
                  <label class="mini-field">边框<input v-model="item.night.border" class="admin-input" /></label>
                </div>
              </div>
            </article>
          </details>
          <button class="admin-btn admin-btn-ghost" type="button" @click="resetAllComponents">恢复全部组件默认样式</button>
        </div>
      </details>
    </section>

    <section v-else-if="active === 'comments'" class="settings-panel">
      <h2>留言设置</h2>
      <p class="panel-note">前台留言仅支持访客通过 GitHub 或 QQ 登录后留言。Secret 仅保存于服务端，不回显明文。</p>
      <div class="settings-grid">
        <label class="setting-check"><input v-model="form.comments.enabled" type="checkbox" />开启留言板</label>
        <label class="setting-check"><input v-model="form.comments.githubLoginEnabled" type="checkbox" />启用 GitHub 登录留言</label>
        <label class="setting-check"><input v-model="form.comments.qqLoginEnabled" type="checkbox" />启用 QQ 登录留言</label>
        <label class="field">留言最大长度<input v-model.number="form.comments.maxLength" type="number" min="1" max="5000" class="admin-input" /></label>
        <label class="field">GitHub Client ID<input v-model="form.comments.gitalkClientID" class="admin-input" /></label>
        <label class="field">GitHub 仓库<input v-model="form.comments.gitalkRepo" class="admin-input" /></label>
        <label class="field">GitHub Owner<input v-model="form.comments.gitalkOwner" class="admin-input" /></label>
        <label class="field">GitHub 管理员 CSV<input v-model="form.comments.gitalkAdminText" class="admin-input" /></label>
        <div class="status-box">GitHub OAuth Secret 状态：{{ statusText(raw.serverSecrets?.githubOAuthSecretConfigured || raw.gitalkConfig?.clientSecretConfigured) }}</div>
        <label class="field md:col-span-2">新的 GitHub OAuth Secret<input v-model="secretInputs.githubOAuthSecret" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
        <label class="field">QQ App ID<input v-model="form.comments.qqAppID" class="admin-input" /></label>
        <div class="status-box">QQ App Secret 状态：{{ statusText(raw.serverSecrets?.qqOAuthSecretConfigured || raw.qqOAuth?.appSecretConfigured) }}</div>
        <label class="field md:col-span-2">新的 QQ App Secret<input v-model="secretInputs.qqOAuthSecret" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
      </div>
    </section>

    <section v-else-if="active === 'image'" class="settings-panel">
      <h2>图床设置</h2>
      <div class="settings-grid">
        <label class="field">存储类型
          <select v-model="form.imageBed.provider" class="admin-input">
            <option value="local">local</option>
            <option value="oss">oss</option>
            <option value="custom">custom</option>
          </select>
        </label>
        <label class="field">公开访问基础 URL<input v-model="form.imageBed.publicBaseUrl" class="admin-input" /></label>
        <label class="field">Bucket<input v-model="form.imageBed.bucket" class="admin-input" /></label>
        <label class="field">Region<input v-model="form.imageBed.region" class="admin-input" /></label>
        <label class="field">Endpoint<input v-model="form.imageBed.endpoint" class="admin-input" /></label>
        <div class="status-box">AccessKey 状态：{{ statusText(form.imageBed.accessKeyConfigured) }}<br />Secret 状态：{{ statusText(form.imageBed.ossSecretConfigured) }}</div>
        <label class="field">新的 AccessKey<input v-model="secretInputs.accessKeyId" type="password" class="admin-input" placeholder="留空则保持旧值" /></label>
        <label class="field">新的 Secret<input v-model="secretInputs.ossSecretInput" type="password" class="admin-input" placeholder="留空则保持旧值" /></label>
      </div>
    </section>

    <section v-else-if="active === 'ai'" class="settings-panel">
      <h2>AI 设置</h2>
      <div class="settings-grid">
        <label class="field">Provider<input v-model="form.ai.provider" class="admin-input" /></label>
        <label class="field">Base URL<input v-model="form.ai.baseUrl" class="admin-input" /></label>
        <label class="field">Model<input v-model="form.ai.model" class="admin-input" /></label>
        <label class="setting-check"><input v-model="form.ai.enableChat" type="checkbox" />启用后台聊天入口</label>
        <div class="status-box">API Key 状态：{{ statusText(form.ai.aiKeyConfigured) }}</div>
        <label class="field md:col-span-2">新的 API Key<input v-model="secretInputs.aiKeyInput" type="password" autocomplete="new-password" class="admin-input" placeholder="留空则保持旧值，不回显明文" /></label>
      </div>
    </section>

    <section v-else class="settings-panel">
      <h2>部署与安全提示</h2>
      <div class="deploy-checks">
        <article v-for="item in productionChecks" :key="item.label" class="deploy-check" :class="{ ok: item.ok }">
          <span>{{ item.ok ? '通过' : '待确认' }}</span>
          <strong>{{ item.label }}</strong>
        </article>
      </div>
    </section>

    <details class="settings-details">
      <summary>高级 JSON 编辑</summary>
      <p class="panel-note">这是兜底入口。JSON 格式错误会阻止应用；Secret 不会在后台响应中回显。</p>
      <textarea v-model="jsonText" class="admin-input json-editor" rows="12"></textarea>
      <p v-if="jsonError" class="status-box status-error">{{ jsonError }}</p>
      <button class="admin-btn admin-btn-ghost" type="button" @click="saveAdvancedJson">应用 JSON 到表单</button>
    </details>
  </div>
</template>

<style scoped>
.settings-shell {
  display: grid;
  gap: 1rem;
}

.settings-header,
.settings-panel,
.settings-details {
  border: 1px solid var(--admin-border);
  border-radius: .85rem;
  background: var(--admin-surface);
  padding: 1rem;
}

.settings-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.settings-header h1,
.settings-panel h2 {
  margin: .15rem 0;
  color: var(--admin-text);
  font-size: 1.35rem;
  font-weight: 900;
}

.settings-header p,
.panel-note {
  margin: 0;
  color: var(--admin-muted);
  font-size: .9rem;
}

.settings-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .55rem;
}

.settings-actions.compact {
  margin-top: .8rem;
}

.settings-tabs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: .6rem;
}

.settings-tab {
  border: 1px solid var(--admin-border);
  border-radius: .7rem;
  background: var(--admin-surface);
  padding: .75rem;
  color: var(--admin-text);
  text-align: left;
}

.settings-tab span {
  display: block;
  font-weight: 900;
}

.settings-tab small {
  display: block;
  margin-top: .2rem;
  color: var(--admin-muted);
  font-size: .72rem;
}

.settings-tab.active {
  border-color: var(--admin-black);
  background: #f3f4f6;
  box-shadow: inset 3px 0 0 var(--admin-black);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: .85rem;
  margin-top: .9rem;
}

.settings-grid.dense {
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: .65rem;
}

.setting-check {
  display: flex;
  align-items: center;
  gap: .5rem;
  color: #374151;
  font-size: .9rem;
  font-weight: 800;
}

.status-box {
  border: 1px solid var(--admin-border);
  border-radius: .7rem;
  background: #f9fafb;
  padding: .75rem;
  color: var(--admin-muted);
  font-weight: 800;
}

.status-error {
  border-color: #fecaca;
  background: #fff1f2;
  color: #dc2626;
}

.status-success {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
}

.settings-details summary {
  cursor: pointer;
  color: var(--admin-text);
  font-weight: 900;
}

.token-grid,
.opacity-grid {
  display: grid;
  gap: .65rem;
  margin-top: .85rem;
}

.token-row,
.opacity-row {
  display: grid;
  grid-template-columns: minmax(130px, .7fr) auto minmax(0, 1fr);
  align-items: center;
  gap: .6rem;
  color: #374151;
  font-size: .85rem;
  font-weight: 800;
}

.opacity-row {
  grid-template-columns: minmax(150px, .7fr) minmax(120px, 1fr) 5.5rem;
}

.color-input {
  width: 2.5rem;
  height: 2.25rem;
  border: 1px solid var(--admin-border-strong);
  border-radius: .55rem;
  background: white;
}

.compact-input {
  max-width: 6rem;
}

.component-groups {
  display: grid;
  gap: .85rem;
  margin-top: .85rem;
}

.component-group {
  border: 1px solid var(--admin-border);
  border-radius: .75rem;
  background: #f9fafb;
  padding: .75rem;
}

.component-theme-card {
  display: grid;
  gap: .75rem;
  margin-top: .75rem;
  border: 1px solid var(--admin-border);
  border-radius: .75rem;
  background: white;
  padding: .85rem;
}

.component-theme-card header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .75rem;
}

.component-theme-card strong {
  display: block;
  color: var(--admin-text);
}

.component-theme-card small {
  display: block;
  color: var(--admin-muted);
}

.admin-btn.small {
  padding: .45rem .65rem;
  font-size: .78rem;
}

.mode-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: .75rem;
}

.mode-columns h4 {
  margin: 0 0 .5rem;
  color: var(--admin-text);
}

.mini-field {
  display: grid;
  grid-template-columns: 3rem auto minmax(0, 1fr);
  align-items: center;
  gap: .45rem;
  margin-top: .45rem;
  color: #374151;
  font-size: .82rem;
  font-weight: 800;
}

.deploy-checks {
  display: grid;
  gap: .65rem;
  margin-top: .9rem;
}

.deploy-check {
  border: 1px solid var(--admin-border);
  border-radius: .7rem;
  background: #f9fafb;
  padding: .8rem;
}

.deploy-check span {
  color: #b45309;
  font-size: .75rem;
  font-weight: 900;
}

.deploy-check.ok span {
  color: #15803d;
}

.deploy-check strong {
  display: block;
  margin-top: .15rem;
}

.json-editor {
  margin: .85rem 0;
  font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
  font-size: .85rem;
}

@media (max-width: 640px) {
  .settings-header {
    display: grid;
  }

  .token-row,
  .opacity-row,
  .mini-field {
    grid-template-columns: 1fr;
  }
}
</style>
