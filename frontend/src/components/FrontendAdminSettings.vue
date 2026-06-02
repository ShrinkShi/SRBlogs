<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { contentApi } from '@/api/content'
import { useUiStore } from '@/stores/ui'

type AnyRecord = Record<string, any>
type SettingsTab = 'site' | 'profile' | 'theme' | 'comments'

const emit = defineEmits<{ saved: [] }>()
const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const activeTab = ref<SettingsTab>('site')
const rawSettings = ref<AnyRecord>({})
const aboutPage = ref<AnyRecord>({})
const pageConfig = ref<AnyRecord>({})
const avatarFile = ref<File | null>(null)
const soundFile = ref<File | null>(null)

const tabs: Array<{ key: SettingsTab; label: string }> = [
  { key: 'site', label: '站点信息' },
  { key: 'profile', label: '我的信息' },
  { key: 'theme', label: '主题外观' },
  { key: 'comments', label: '评论设置' }
]

const form = ref({
  site: { title: '', subtitle: '', description: '', icp: '' },
  profile: { name: '', avatar: '', intro: '', github: '', email: '', qq: '', wechat: '' },
  theme: {
    clickSoundEnabled: true,
    clickEffectEnabled: true,
    clickSoundVolume: 0.05,
    clickSoundUrl: '',
    nightWallpapers: '',
    nightActiveIndex: 0,
    nightSlideshowEnabled: true,
    nightSlideshowInterval: 8.5,
    nightSlideshowEffect: 'fade'
  },
  comments: {
    enabled: true,
    maxLength: 1000,
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

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value || {}))
}

function defaultAboutPage(): AnyRecord {
  return {
    hero: { name: '', avatar: '', description: '' },
    contact: { github: '', githubUrl: '', email: '', qq: '', wechat: '' }
  }
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

function normalizeInterval(value: unknown) {
  const number = Number(value)
  return Number.isFinite(number) ? Math.min(60, Math.max(3, number)) : 8.5
}

function normalizeEffect(value: unknown) {
  const effect = String(value || 'fade')
  return ['fade', 'soft-blur', 'none'].includes(effect) ? effect : 'fade'
}

function applyLoaded(settings: AnyRecord, about: AnyRecord, pages: AnyRecord) {
  rawSettings.value = clone(settings)
  aboutPage.value = { ...defaultAboutPage(), ...clone(about) }
  pageConfig.value = clone(pages)

  const themeConfig = settings.themeConfig || {}
  const activeTheme = themeConfig.activeTheme || settings.theme || 'shrink-red-glass'
  const activePackage = themeConfig.themePackages?.[activeTheme] || {}
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
      nightWallpapers: listToText(night.bgImages || night.backgrounds || settings.bgImages),
      nightActiveIndex: Number(night.activeBgIndex || 0),
      nightSlideshowEnabled: night.slideshowEnabled !== false,
      nightSlideshowInterval: normalizeInterval(night.slideshowInterval),
      nightSlideshowEffect: normalizeEffect(night.slideshowEffect)
    },
    comments: {
      enabled: comments.enabled !== false,
      maxLength: Number(comments.maxLength || 1000),
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
  try {
    const [settings, about, pages] = await Promise.all([
      contentApi.adminJson<AnyRecord>('/admin/settings'),
      contentApi.adminJson<AnyRecord>('/admin/about-page').catch(() => defaultAboutPage()),
      contentApi.adminJson<AnyRecord>('/admin/pages/config').catch(() => ({}))
    ])
    applyLoaded(settings, about, pages)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '设置加载失败'
  } finally {
    loading.value = false
  }
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  try {
    const data = await contentApi.upload(avatarFile.value)
    form.value.profile.avatar = data.url
    avatarFile.value = null
    ui.showToast('头像已上传', 'success')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '头像上传失败'
  }
}

async function uploadClickSound() {
  if (!soundFile.value) return
  try {
    const data = await contentApi.upload(soundFile.value)
    form.value.theme.clickSoundUrl = data.url
    soundFile.value = null
    ui.showToast('点击音效已上传', 'success')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '点击音效上传失败'
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
  modes.night = {
    ...(modes.night || themeConfig.night || {}),
    bgImages: textToWallpaperList(form.value.theme.nightWallpapers),
    activeBgIndex: Number(form.value.theme.nightActiveIndex || 0),
    slideshowEnabled: form.value.theme.nightSlideshowEnabled,
    slideshowInterval: normalizeInterval(form.value.theme.nightSlideshowInterval),
    slideshowEffect: normalizeEffect(form.value.theme.nightSlideshowEffect)
  }
  modes.day = { ...(modes.day || themeConfig.day || {}), ...modes.night }
  const activeTheme = String(themeConfig.activeTheme || next.theme || 'shrink-red-glass')
  const themePackages = { ...(themeConfig.themePackages || {}) }
  const activePackage = themePackages[activeTheme]
  if (activePackage && typeof activePackage === 'object') {
    themePackages[activeTheme] = {
      ...activePackage,
      modes: {
        ...(activePackage.modes || {}),
        day: { ...((activePackage.modes || {}).day || {}), ...modes.night },
        night: { ...((activePackage.modes || {}).night || {}), ...modes.night }
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
      github: { ...((next.comments || {}).providers?.github || {}), enabled: form.value.comments.githubLoginEnabled },
      qq: { ...((next.comments || {}).providers?.qq || {}), enabled: form.value.comments.qqLoginEnabled }
    }
  }
  next.gitalkConfig = { ...(next.gitalkConfig || {}), clientID: form.value.comments.githubClientId }
  delete next.gitalkConfig.clientSecret
  if (form.value.comments.githubSecret.trim()) next.gitalkConfig.clientSecret = form.value.comments.githubSecret.trim()
  next.qqOAuth = { ...(next.qqOAuth || {}), appID: form.value.comments.qqAppId }
  delete next.qqOAuth.appSecret
  if (form.value.comments.qqSecret.trim()) next.qqOAuth.appSecret = form.value.comments.qqSecret.trim()
  return next
}

function buildAboutPayload() {
  const next = { ...defaultAboutPage(), ...clone(aboutPage.value) }
  next.hero = { ...(next.hero || {}), name: form.value.profile.name, avatar: form.value.profile.avatar, description: form.value.profile.intro }
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
  try {
    await contentApi.adminPutJson('/admin/settings', buildSettingsPayload())
    await contentApi.adminPutJson('/admin/about-page', buildAboutPayload())
    await contentApi.adminPutJson('/admin/pages/config', buildPagesPayload())
    ui.showToast('设置已保存', 'success')
    emit('saved')
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
  <section class="front-admin-settings">
    <div class="front-admin-settings-head">
      <span></span>
      <button type="button" :disabled="loading" @click="load">{{ loading ? '加载中...' : '刷新' }}</button>
    </div>

    <p v-if="error" class="front-admin-error">{{ error }}</p>
    <p v-if="loading" class="front-admin-loading">设置加载中...</p>

    <template v-else>
      <nav class="front-admin-tabs" aria-label="管理员设置分类">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </nav>

      <div v-if="activeTab === 'site'" class="front-admin-form">
        <label><span>站点标题</span><input v-model="form.site.title" /></label>
        <label><span>副标题</span><input v-model="form.site.subtitle" /></label>
        <label><span>站点描述</span><textarea v-model="form.site.description"></textarea></label>
        <label><span>备案号</span><input v-model="form.site.icp" /></label>
      </div>

      <div v-else-if="activeTab === 'profile'" class="front-admin-form">
        <label><span>名称</span><input v-model="form.profile.name" /></label>
        <label>
          <span>头像</span>
          <div class="front-admin-inline">
            <input v-model="form.profile.avatar" placeholder="头像 URL 或上传后的地址" />
            <input type="file" accept="image/*" @change="avatarFile = (($event.target as HTMLInputElement).files?.[0] || null)" />
            <button type="button" :disabled="!avatarFile" @click="uploadAvatar">上传</button>
          </div>
        </label>
        <label><span>GitHub 链接</span><input v-model="form.profile.github" /></label>
        <label><span>简介</span><textarea v-model="form.profile.intro"></textarea></label>
        <label><span>Email</span><input v-model="form.profile.email" /></label>
        <label><span>QQ</span><input v-model="form.profile.qq" /></label>
        <label><span>微信</span><input v-model="form.profile.wechat" /></label>
      </div>

      <div v-else-if="activeTab === 'theme'" class="front-admin-form">
        <label class="front-admin-switch"><span>启用点击音效</span><input v-model="form.theme.clickSoundEnabled" type="checkbox" /></label>
        <label class="front-admin-switch"><span>启用点击特效</span><input v-model="form.theme.clickEffectEnabled" type="checkbox" /></label>
        <label><span>点击音量</span><input v-model.number="form.theme.clickSoundVolume" min="0" max="1" step="0.01" type="number" /></label>
        <label>
          <span>点击音效 URL</span>
          <div class="front-admin-inline">
            <input v-model="form.theme.clickSoundUrl" />
            <input type="file" accept="audio/*" @change="soundFile = (($event.target as HTMLInputElement).files?.[0] || null)" />
            <button type="button" :disabled="!soundFile" @click="uploadClickSound">上传</button>
          </div>
        </label>
        <label><span>夜间壁纸 URL（每行一个）</span><textarea v-model="form.theme.nightWallpapers"></textarea></label>
        <label><span>默认壁纸序号</span><input v-model.number="form.theme.nightActiveIndex" min="0" type="number" /></label>
        <label class="front-admin-switch"><span>背景轮播</span><input v-model="form.theme.nightSlideshowEnabled" type="checkbox" /></label>
        <label><span>轮播间隔（秒）</span><input v-model.number="form.theme.nightSlideshowInterval" min="3" max="60" step="0.5" type="number" /></label>
        <label>
          <span>轮播效果</span>
          <select v-model="form.theme.nightSlideshowEffect">
            <option value="fade">淡入淡出</option>
            <option value="soft-blur">柔焦切换</option>
            <option value="none">无动画</option>
          </select>
        </label>
      </div>

      <div v-else class="front-admin-form">
        <label class="front-admin-switch"><span>启用评论</span><input v-model="form.comments.enabled" type="checkbox" /></label>
        <label><span>留言最大长度</span><input v-model.number="form.comments.maxLength" min="1" type="number" /></label>
        <label class="front-admin-switch"><span>启用 GitHub 登录</span><input v-model="form.comments.githubLoginEnabled" type="checkbox" /></label>
        <label><span>GitHub Client ID</span><input v-model="form.comments.githubClientId" /></label>
        <label><span>新的 GitHub OAuth Secret</span><input v-model="form.comments.githubSecret" type="password" :placeholder="form.comments.githubSecretConfigured ? '已配置，留空保持旧值' : '未配置'" /></label>
        <label class="front-admin-switch"><span>启用 QQ 登录</span><input v-model="form.comments.qqLoginEnabled" type="checkbox" /></label>
        <label><span>QQ App ID</span><input v-model="form.comments.qqAppId" /></label>
        <label><span>新的 QQ App Secret</span><input v-model="form.comments.qqSecret" type="password" :placeholder="form.comments.qqSecretConfigured ? '已配置，留空保持旧值' : '未配置'" /></label>
      </div>

      <div class="front-admin-actions">
        <button type="button" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存设置' }}</button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.front-admin-settings {
  display: grid;
  gap: 1rem;
}
.front-admin-settings-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.front-admin-settings-head p {
  color: rgba(255, 255, 255, .42);
  font-size: .72rem;
  font-weight: 900;
  letter-spacing: .22em;
  text-transform: uppercase;
}
.front-admin-settings-head h3 {
  margin-top: .25rem;
  font-size: 1.3rem;
  font-weight: 900;
}
.front-admin-settings button {
  border-radius: .9rem;
  border: 1px solid rgba(255, 255, 255, .12);
  padding: .6rem .85rem;
  color: rgba(255, 255, 255, .76);
}
.front-admin-settings button:disabled {
  cursor: not-allowed;
  opacity: .45;
}
.front-admin-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: .4rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
  padding-bottom: .6rem;
}
.front-admin-tabs button {
  border: 0;
  background: transparent;
}
.front-admin-tabs button.active {
  color: #fecaca;
  box-shadow: inset 0 -2px 0 #f87171;
}
.front-admin-form {
  display: grid;
  gap: .7rem;
}
.front-admin-form label {
  display: grid;
  gap: .42rem;
}
.front-admin-form label > span {
  color: rgba(255, 255, 255, .64);
  font-size: .82rem;
  font-weight: 900;
}
.front-admin-form input,
.front-admin-form textarea,
.front-admin-form select {
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: .9rem;
  background: rgba(255, 255, 255, .075);
  padding: .7rem .8rem;
  color: white;
  outline: none;
}
.front-admin-form textarea {
  min-height: 5.5rem;
  resize: vertical;
}
.front-admin-form input:focus,
.front-admin-form textarea:focus,
.front-admin-form select:focus {
  border-color: rgba(248, 113, 113, .5);
}
.front-admin-inline {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, .85fr) auto;
  gap: .45rem;
}
.front-admin-switch {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}
.front-admin-switch input {
  width: 1.1rem;
  height: 1.1rem;
  accent-color: #f87171;
}
.front-admin-actions {
  display: flex;
  justify-content: center;
  border-top: 1px solid rgba(255, 255, 255, .1);
  padding-top: .9rem;
}
.front-admin-actions button {
  min-width: 12rem;
  border-color: rgba(34, 197, 94, .3);
  background: #dcfce7;
  color: #052e16;
  font-weight: 900;
}
.front-admin-error,
.front-admin-loading {
  border-radius: 1rem;
  padding: .8rem 1rem;
  font-size: .88rem;
}
.front-admin-error {
  border: 1px solid rgba(248, 113, 113, .32);
  background: rgba(127, 29, 29, .38);
  color: #fecaca;
}
.front-admin-loading {
  border: 1px solid rgba(255, 255, 255, .1);
  color: rgba(255, 255, 255, .58);
}
@media (max-width: 720px) {
  .front-admin-inline {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
