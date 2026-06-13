<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

type AnyRecord = Record<string, any>
type SettingsTab = 'site' | 'profile' | 'theme' | 'comments'

const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const rawSettings = ref<AnyRecord>({})
const aboutPage = ref<AnyRecord>({})
const pageConfig = ref<AnyRecord>({})
const clickSoundFile = ref<File | null>(null)
const avatarFile = ref<File | null>(null)
const wallpaperUploading = ref<{ day: boolean; night: boolean }>({ day: false, night: false })
const activeTab = ref<SettingsTab>('site')

const settingTabs: Array<{ key: SettingsTab; label: string; icon: string }> = [
  { key: 'site', label: '站点信息', icon: 'M4 5h16v14H4zM8 9h8M8 13h5' },
  { key: 'profile', label: '我的信息', icon: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 8a7 7 0 0 1 14 0' },
  { key: 'theme', label: '主题外观', icon: 'M12 3a9 9 0 0 0 0 18 4.5 4.5 0 0 1 0-9 4.5 4.5 0 0 0 0-9Z' },
  { key: 'comments', label: '评论设置', icon: 'M4 5h16v10H8l-4 4V5Z' }
]

const form = ref({
  site: {
    title: '',
    subtitle: '',
    description: '',
    icp: ''
  },
  profile: {
    name: '',
    avatar: '',
    intro: '',
    github: '',
    email: '',
    qq: '',
    wechat: ''
  },
  theme: {
    clickSoundEnabled: true,
    clickEffectEnabled: true,
    clickSoundVolume: 0.05,
    clickSoundUrl: '',
    dayWallpapers: '',
    nightWallpapers: '',
    dayActiveIndex: 0,
    nightActiveIndex: 0,
    daySlideshowEnabled: true,
    daySlideshowInterval: 8.5,
    daySlideshowEffect: 'fade',
    nightSlideshowEnabled: true,
    nightSlideshowInterval: 8.5,
    nightSlideshowEffect: 'fade'
  },
  comments: {
    enabled: true,
    maxLength: 20000,
    githubLoginEnabled: true,
    githubClientId: '',
    githubSecretConfigured: false,
    githubSecret: '',
    qqLoginEnabled: true,
    qqAppId: '',
    qqSecretConfigured: false,
    qqSecret: ''
  }
})

const wallpaperHint = computed(() => '每行一个壁纸 URL。前台固定夜晚模式，会读取这里的背景配置。')

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value || {}))
}

function listToText(value: unknown) {
  if (!Array.isArray(value)) return ''
  return value.map((item) => typeof item === 'string' ? item : item?.url).filter(Boolean).join('\n')
}

function textToWallpaperList(value: string) {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((url, index) => ({ url, name: `壁纸 ${index + 1}`, enabled: true }))
}

function normalizeSlideshowInterval(value: unknown) {
  const number = Number(value)
  return Number.isFinite(number) ? Math.min(60, Math.max(3, number)) : 8.5
}

function normalizeSlideshowEffect(value: unknown) {
  const effect = String(value || 'fade')
  return ['fade', 'soft-blur', 'none'].includes(effect) ? effect : 'fade'
}

function defaultAboutPage(): AnyRecord {
  return {
    hero: { name: '', avatar: '', description: '' },
    contact: { github: '', githubUrl: '', email: '', qq: '', wechat: '' }
  }
}

function applyLoadedSettings(settings: AnyRecord, about: AnyRecord, pages: AnyRecord) {
  rawSettings.value = clone(settings)
  aboutPage.value = { ...defaultAboutPage(), ...clone(about) }
  pageConfig.value = clone(pages)
  const themeConfig = settings.themeConfig || {}
  const activeTheme = themeConfig.activeTheme || settings.theme || 'shrink-red-glass'
  const activePackage = themeConfig.themePackages?.[activeTheme] || {}
  const day = themeConfig.modes?.day || themeConfig.day || activePackage.modes?.day || {}
  const night = themeConfig.modes?.night || themeConfig.night || activePackage.modes?.night || {}
  const comments = settings.comments || {}
  const interaction = settings.interaction || {}
  const contact = aboutPage.value.contact || {}
  const hero = aboutPage.value.hero || {}
  const homeProfile = pages.homeProfile || {}
  const social = settings.socialLinks || {}
  const gitalk = settings.gitalkConfig || {}
  const qqOAuth = settings.qqOAuth || {}
  const serverSecrets = settings.serverSecrets || {}
  const legacyPersonalDescription = settings.description && settings.description !== settings.subtitle ? settings.description : ''

  form.value = {
    site: {
      title: String(settings.siteTitle || settings.title || ''),
      subtitle: String(settings.subtitle || ''),
      description: String(settings.siteDescription || legacyPersonalDescription || ''),
      icp: String(settings.icp || settings.beian || '')
    },
    profile: {
      name: String(homeProfile.author || hero.name || settings.author || settings.authorName || ''),
      avatar: String(homeProfile.avatar || hero.avatar || settings.avatar || settings.avatarUrl || ''),
      intro: String(homeProfile.description || hero.description || settings.bio || legacyPersonalDescription || ''),
      github: String(contact.githubUrl || social.github || contact.github || ''),
      email: String(contact.email || social.email || ''),
      qq: String(contact.qq || social.qq || ''),
      wechat: String(contact.wechat || social.wechat || '')
    },
    theme: {
      clickSoundEnabled: interaction.clickSoundEnabled !== false,
      clickEffectEnabled: interaction.clickEffectEnabled !== false,
      clickSoundVolume: Number(interaction.clickSoundVolume ?? 0.05),
      clickSoundUrl: String(interaction.clickSoundUrl || ''),
      dayWallpapers: listToText(day.bgImages || day.backgrounds || settings.bgImages),
      nightWallpapers: listToText(night.bgImages || night.backgrounds || settings.bgImages),
      dayActiveIndex: Number(day.activeBgIndex || 0),
      nightActiveIndex: Number(night.activeBgIndex || 0),
      daySlideshowEnabled: day.slideshowEnabled !== false,
      daySlideshowInterval: normalizeSlideshowInterval(day.slideshowInterval),
      daySlideshowEffect: normalizeSlideshowEffect(day.slideshowEffect),
      nightSlideshowEnabled: night.slideshowEnabled !== false,
      nightSlideshowInterval: normalizeSlideshowInterval(night.slideshowInterval),
      nightSlideshowEffect: normalizeSlideshowEffect(night.slideshowEffect)
    },
    comments: {
      enabled: comments.enabled !== false,
      maxLength: Number(comments.maxLength || 20000),
      githubLoginEnabled: comments.providers?.github?.enabled ?? comments.githubLoginEnabled ?? true,
      githubClientId: String(gitalk.clientID || gitalk.clientId || ''),
      githubSecretConfigured: Boolean(serverSecrets.githubOAuthSecretConfigured || comments.providers?.github?.secretConfigured),
      githubSecret: '',
      qqLoginEnabled: comments.providers?.qq?.enabled ?? comments.qqLoginEnabled ?? true,
      qqAppId: String(qqOAuth.appID || qqOAuth.appId || ''),
      qqSecretConfigured: Boolean(serverSecrets.qqAppSecretConfigured || comments.providers?.qq?.secretConfigured),
      qqSecret: ''
    }
  }
}

async function load() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const [settings, about, pages] = await Promise.all([
      adminApi.json<AnyRecord>('/admin/settings'),
      adminApi.json<AnyRecord>('/admin/about-page').catch(() => defaultAboutPage()),
      adminApi.json<AnyRecord>('/admin/pages/config').catch(() => ({}))
    ])
    applyLoadedSettings(settings, about, pages)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置加载失败'
  } finally {
    loading.value = false
  }
}

async function uploadClickSound() {
  if (!clickSoundFile.value) return
  try {
    const data = await adminApi.upload(clickSoundFile.value)
    form.value.theme.clickSoundUrl = data.url
    ui.show('点击音效已上传')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '点击音效上传失败'
  }
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  try {
    const data = await adminApi.upload(avatarFile.value)
    form.value.profile.avatar = data.url
    avatarFile.value = null
    ui.show('头像已上传')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '头像上传失败'
  }
}

function appendWallpaperUrls(mode: 'day' | 'night', urls: string[]) {
  const current = mode === 'day' ? form.value.theme.dayWallpapers : form.value.theme.nightWallpapers
  const next = [current.trim(), ...urls].filter(Boolean).join('\n')
  if (mode === 'day') form.value.theme.dayWallpapers = next
  else form.value.theme.nightWallpapers = next
}

async function uploadWallpapers(mode: 'day' | 'night', files: FileList | null) {
  const selected = Array.from(files || []).filter((file) => file.type.startsWith('image/'))
  if (!selected.length) {
    error.value = '请选择图片文件作为壁纸'
    return
  }
  wallpaperUploading.value[mode] = true
  error.value = ''
  try {
    const urls: string[] = []
    for (const file of selected) {
      const data = await adminApi.upload(file)
      urls.push(data.url)
    }
    appendWallpaperUrls(mode, urls)
    ui.show(`${mode === 'day' ? '兼容' : '背景'}壁纸已上传`)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '壁纸上传失败'
  } finally {
    wallpaperUploading.value[mode] = false
  }
}

function buildSettingsPayload() {
  const next = clone(rawSettings.value)
  next.siteTitle = form.value.site.title
  next.title = form.value.site.title
  next.subtitle = form.value.site.subtitle
  next.siteDescription = form.value.site.description
  next.description = form.value.site.description
  next.icp = form.value.site.icp
  next.beian = form.value.site.icp
  next.author = form.value.profile.name
  next.authorName = form.value.profile.name
  next.avatar = form.value.profile.avatar
  next.avatarUrl = form.value.profile.avatar
  next.bio = form.value.profile.intro
  next.profileIntro = form.value.profile.intro
  next.socialLinks = {
    ...(next.socialLinks || {}),
    github: form.value.profile.github,
    email: form.value.profile.email,
    qq: form.value.profile.qq,
    wechat: form.value.profile.wechat
  }

  next.interaction = {
    ...(next.interaction || {}),
    clickSoundEnabled: form.value.theme.clickSoundEnabled,
    clickEffectEnabled: form.value.theme.clickEffectEnabled,
    clickSoundVolume: Number(form.value.theme.clickSoundVolume),
    clickSoundUrl: form.value.theme.clickSoundUrl
  }

  const themeConfig = { ...(next.themeConfig || {}) }
  const modes = { ...(themeConfig.modes || {}) }
  modes.day = {
    ...(modes.day || themeConfig.day || {}),
    bgImages: textToWallpaperList(form.value.theme.dayWallpapers),
    activeBgIndex: Number(form.value.theme.dayActiveIndex || 0),
    slideshowEnabled: form.value.theme.daySlideshowEnabled,
    slideshowInterval: normalizeSlideshowInterval(form.value.theme.daySlideshowInterval),
    slideshowEffect: normalizeSlideshowEffect(form.value.theme.daySlideshowEffect)
  }
  modes.night = {
    ...(modes.night || themeConfig.night || {}),
    bgImages: textToWallpaperList(form.value.theme.nightWallpapers),
    activeBgIndex: Number(form.value.theme.nightActiveIndex || 0),
    slideshowEnabled: form.value.theme.nightSlideshowEnabled,
    slideshowInterval: normalizeSlideshowInterval(form.value.theme.nightSlideshowInterval),
    slideshowEffect: normalizeSlideshowEffect(form.value.theme.nightSlideshowEffect)
  }
  modes.day = { ...(modes.day || themeConfig.day || {}), ...modes.night }
  const activeTheme = String(themeConfig.activeTheme || next.theme || 'shrink-red-glass')
  const themePackages = { ...(themeConfig.themePackages || {}) }
  const activePackage = themePackages[activeTheme]
  if (activePackage && typeof activePackage === 'object') {
    const packageRecord = activePackage as AnyRecord
    themePackages[activeTheme] = {
      ...packageRecord,
      modes: {
        ...(packageRecord.modes || {}),
        day: {
          ...((packageRecord.modes || {}).day || {}),
          ...modes.night
        },
        night: {
          ...((packageRecord.modes || {}).night || {}),
          bgImages: modes.night.bgImages,
          activeBgIndex: modes.night.activeBgIndex,
          slideshowEnabled: modes.night.slideshowEnabled,
          slideshowInterval: modes.night.slideshowInterval,
          slideshowEffect: modes.night.slideshowEffect
        }
      }
    }
  }
  next.themeConfig = { ...themeConfig, activeTheme, themePackages, modes, day: modes.day, night: modes.night }

  next.comments = {
    ...(next.comments || {}),
    enabled: form.value.comments.enabled,
    maxLength: Number(form.value.comments.maxLength),
    githubLoginEnabled: form.value.comments.githubLoginEnabled,
    qqLoginEnabled: form.value.comments.qqLoginEnabled,
    providers: {
      ...((next.comments || {}).providers || {}),
      github: {
        ...((next.comments || {}).providers?.github || {}),
        enabled: form.value.comments.githubLoginEnabled
      },
      qq: {
        ...((next.comments || {}).providers?.qq || {}),
        enabled: form.value.comments.qqLoginEnabled
      }
    }
  }

  next.gitalkConfig = {
    ...(next.gitalkConfig || {}),
    clientID: form.value.comments.githubClientId
  }
  if (form.value.comments.githubSecret.trim()) {
    next.gitalkConfig.clientSecret = form.value.comments.githubSecret.trim()
  }

  next.qqOAuth = {
    ...(next.qqOAuth || {}),
    appID: form.value.comments.qqAppId
  }
  if (form.value.comments.qqSecret.trim()) {
    next.qqOAuth.appSecret = form.value.comments.qqSecret.trim()
  }

  return next
}

function buildAboutPayload() {
  const next = { ...defaultAboutPage(), ...clone(aboutPage.value) }
  next.hero = {
    ...(next.hero || {}),
    name: form.value.profile.name,
    avatar: form.value.profile.avatar,
    description: form.value.profile.intro
  }
  next.contact = {
    ...(next.contact || {}),
    github: form.value.profile.github.replace(/^https?:\/\//, ''),
    githubUrl: form.value.profile.github,
    email: form.value.profile.email,
    qq: form.value.profile.qq,
    wechat: form.value.profile.wechat
  }
  return next
}

function buildPagesPayload() {
  const next = clone(pageConfig.value || {})
  next.homeProfile = {
    ...(next.homeProfile || {}),
    author: form.value.profile.name,
    avatar: form.value.profile.avatar,
    description: form.value.profile.intro,
    socialLinks: {
      ...((next.homeProfile || {}).socialLinks || {}),
      github: form.value.profile.github,
      email: form.value.profile.email,
      qq: form.value.profile.qq,
      wechat: form.value.profile.wechat
    }
  }
  return next
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/settings', buildSettingsPayload())
    await adminApi.putJson('/admin/about-page', buildAboutPayload())
    await adminApi.putJson('/admin/pages/config', buildPagesPayload())
    success.value = '设置已保存'
    ui.show('设置已保存')
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <p v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{{ error }}</p>
    <p v-if="success" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-700">{{ success }}</p>

    <p v-if="loading" class="admin-card text-slate-500">设置加载中...</p>
    <div v-else class="grid gap-5">
      <nav class="settings-subnav" aria-label="设置中心子导航">
        <button
          v-for="tab in settingTabs"
          :key="tab.key"
          type="button"
          class="settings-subnav-item"
          :class="{ 'settings-subnav-item-active': activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path :d="tab.icon" />
          </svg>
          <span>{{ tab.label }}</span>
        </button>
      </nav>

      <div v-if="activeTab === 'site'" class="admin-card">
        <h2 class="text-xl font-black text-slate-950">站点信息</h2>
        <div class="settings-form-grid mt-4">
          <label class="settings-row"><span>站点标题</span><input v-model="form.site.title" class="admin-input" /></label>
          <label class="settings-row"><span>副标题</span><input v-model="form.site.subtitle" class="admin-input" /></label>
          <label class="settings-row settings-row-textarea"><span>站点描述</span><textarea v-model="form.site.description" class="admin-input min-h-24"></textarea></label>
          <label class="settings-row"><span>备案号</span><input v-model="form.site.icp" class="admin-input" placeholder="例如：粤 ICP 备 xxxxxxxx 号" /></label>
        </div>
      </div>

      <div v-else-if="activeTab === 'profile'" class="admin-card">
        <h2 class="text-xl font-black text-slate-950">我的信息</h2>
        <div class="settings-form-grid mt-4">
          <label class="settings-row"><span>名称</span><input v-model="form.profile.name" class="admin-input" /></label>
          <label class="settings-row settings-row-textarea">
            <span>头像</span>
            <div class="settings-inline-upload">
              <input v-model="form.profile.avatar" class="admin-input" placeholder="头像 URL 或上传后的地址" />
              <input class="admin-input" type="file" accept="image/*" @change="avatarFile = (($event.target as HTMLInputElement).files?.[0] || null)" />
              <button class="admin-btn admin-btn-ghost" type="button" :disabled="!avatarFile" @click="uploadAvatar">上传</button>
            </div>
          </label>
          <label class="settings-row"><span>GitHub 链接</span><input v-model="form.profile.github" class="admin-input" placeholder="https://github.com/ShrinkShi" /></label>
          <label class="settings-row settings-row-textarea"><span>简介</span><textarea v-model="form.profile.intro" class="admin-input min-h-28"></textarea></label>
          <label class="settings-row"><span>Email 复制内容</span><input v-model="form.profile.email" class="admin-input" /></label>
          <label class="settings-row"><span>QQ 复制内容</span><input v-model="form.profile.qq" class="admin-input" /></label>
          <label class="settings-row"><span>微信复制内容</span><input v-model="form.profile.wechat" class="admin-input" /></label>
        </div>
      </div>

      <div v-else-if="activeTab === 'theme'" class="admin-card">
        <h2 class="text-xl font-black text-slate-950">主题外观</h2>
        <div class="settings-form-grid mt-4">
          <label class="settings-row settings-switch-row">
            <span>启用点击音效</span>
            <input v-model="form.theme.clickSoundEnabled" type="checkbox" />
          </label>
          <label class="settings-row settings-switch-row">
            <span>启用鼠标点击特效</span>
            <input v-model="form.theme.clickEffectEnabled" type="checkbox" />
          </label>
          <label class="settings-row"><span>点击音效音量</span><input v-model.number="form.theme.clickSoundVolume" class="admin-input" type="number" min="0" max="1" step="0.01" /></label>
          <label class="settings-row"><span>点击音效 URL</span><input v-model="form.theme.clickSoundUrl" class="admin-input" /></label>
          <label class="settings-row settings-row-textarea">
            <span>上传点击音效</span>
            <div class="flex flex-wrap gap-2">
              <input class="admin-input min-w-0 flex-1" type="file" accept="audio/*" @change="clickSoundFile = (($event.target as HTMLInputElement).files?.[0] || null)" />
              <button class="admin-btn admin-btn-ghost" type="button" @click="uploadClickSound">上传</button>
            </div>
          </label>
        </div>

        <div class="mt-5 grid gap-4">
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 class="font-black text-slate-950">背景壁纸</h3>
            <p class="mt-1 text-xs text-slate-500">{{ wallpaperHint }} 也可以直接上传图片，上传后会自动追加 URL。</p>
            <div class="mt-3 flex flex-wrap items-center gap-2">
              <label class="admin-btn admin-btn-ghost cursor-pointer">
                {{ wallpaperUploading.night ? '上传中...' : '上传壁纸' }}
                <input
                  class="hidden"
                  type="file"
                  accept="image/*"
                  multiple
                  :disabled="wallpaperUploading.night"
                  @change="uploadWallpapers('night', ($event.target as HTMLInputElement).files); (($event.target as HTMLInputElement).value = '')"
                />
              </label>
            </div>
            <textarea v-model="form.theme.nightWallpapers" class="admin-input mt-3 min-h-36 font-mono text-sm"></textarea>
            <div class="settings-form-grid mt-3">
              <label class="settings-row"><span>默认壁纸序号</span><input v-model.number="form.theme.nightActiveIndex" class="admin-input" type="number" min="0" /></label>
              <label class="settings-row settings-switch-row">
                <span>启用壁纸轮播</span>
                <input v-model="form.theme.nightSlideshowEnabled" type="checkbox" />
              </label>
              <label class="settings-row"><span>轮播间隔（秒）</span><input v-model.number="form.theme.nightSlideshowInterval" class="admin-input" type="number" min="3" max="60" step="0.5" /></label>
              <label class="settings-row">
                <span>切换动画</span>
                <select v-model="form.theme.nightSlideshowEffect" class="admin-input">
                  <option value="fade">淡入淡出</option>
                  <option value="soft-blur">柔焦淡入</option>
                  <option value="none">无动画</option>
                </select>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'comments'" class="admin-card">
        <h2 class="text-xl font-black text-slate-950">评论设置</h2>
        <p class="mt-2 text-sm text-slate-600">前台留言支持 OAuth 登录，密钥只保存在后端，不回显明文。</p>
        <div class="settings-form-grid mt-4">
          <label class="settings-row settings-switch-row">
            <span>开启留言板</span>
            <input v-model="form.comments.enabled" type="checkbox" />
          </label>
          <label class="settings-row"><span>留言最大长度</span><input v-model.number="form.comments.maxLength" class="admin-input" type="number" min="1" /></label>

          <label class="settings-row settings-switch-row">
            <span>启用 GitHub 登录留言</span>
            <input v-model="form.comments.githubLoginEnabled" type="checkbox" />
          </label>
          <label class="settings-row"><span>GitHub Client ID</span><input v-model="form.comments.githubClientId" class="admin-input" /></label>
          <div class="settings-row">
            <span>GitHub OAuth Secret 状态</span>
            <b>{{ form.comments.githubSecretConfigured ? '已配置' : '未配置' }}</b>
          </div>
          <label class="settings-row"><span>新的 GitHub OAuth Secret</span><input v-model="form.comments.githubSecret" class="admin-input" type="password" placeholder="留空则保持旧值，不回显明文" /></label>

          <label class="settings-row settings-switch-row">
            <span>启用 QQ 登录留言</span>
            <input v-model="form.comments.qqLoginEnabled" type="checkbox" />
          </label>
          <label class="settings-row"><span>QQ App ID</span><input v-model="form.comments.qqAppId" class="admin-input" /></label>
          <div class="settings-row">
            <span>QQ App Secret 状态</span>
            <b>{{ form.comments.qqSecretConfigured ? '已配置' : '未配置' }}</b>
          </div>
          <label class="settings-row"><span>新的 QQ App Secret</span><input v-model="form.comments.qqSecret" class="admin-input" type="password" placeholder="留空则保持旧值，不回显明文" /></label>
        </div>
      </div>

      <div class="admin-card admin-bottom-actions">
        <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
        <button :disabled="saving || loading" class="admin-btn admin-btn-save" type="button" @click="save">{{ saving ? '保存中...' : '保存设置' }}</button>
      </div>
    </div>
  </section>
</template>
