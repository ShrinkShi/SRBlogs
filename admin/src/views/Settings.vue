<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

type AnyRecord = Record<string, any>

const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const rawSettings = ref<AnyRecord>({})
const aboutPage = ref<AnyRecord>({})
const clickSoundFile = ref<File | null>(null)
const wallpaperUploading = ref<{ day: boolean; night: boolean }>({ day: false, night: false })

const form = ref({
  site: {
    title: '',
    subtitle: ''
  },
  profile: {
    name: '',
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

const wallpaperHint = computed(() => '每行一个壁纸 URL。保存后前台按当前主题的昼夜模式读取。')

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
    hero: { name: '', description: '' },
    contact: { github: '', githubUrl: '', email: '', qq: '', wechat: '' }
  }
}

function applyLoadedSettings(settings: AnyRecord, about: AnyRecord) {
  rawSettings.value = clone(settings)
  aboutPage.value = { ...defaultAboutPage(), ...clone(about) }
  const themeConfig = settings.themeConfig || {}
  const activeTheme = themeConfig.activeTheme || settings.theme || 'shrink-red-glass'
  const activePackage = themeConfig.themePackages?.[activeTheme] || {}
  const day = themeConfig.modes?.day || themeConfig.day || activePackage.modes?.day || {}
  const night = themeConfig.modes?.night || themeConfig.night || activePackage.modes?.night || {}
  const comments = settings.comments || {}
  const interaction = settings.interaction || {}
  const contact = aboutPage.value.contact || {}
  const hero = aboutPage.value.hero || {}
  const social = settings.socialLinks || {}
  const gitalk = settings.gitalkConfig || {}
  const qqOAuth = settings.qqOAuth || {}
  const serverSecrets = settings.serverSecrets || {}

  form.value = {
    site: {
      title: String(settings.siteTitle || settings.title || ''),
      subtitle: String(settings.subtitle || settings.description || '')
    },
    profile: {
      name: String(hero.name || settings.author || ''),
      intro: String(hero.description || settings.description || ''),
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
  success.value = ''
  try {
    const [settings, about] = await Promise.all([
      adminApi.json<AnyRecord>('/admin/settings'),
      adminApi.json<AnyRecord>('/admin/about-page').catch(() => defaultAboutPage())
    ])
    applyLoadedSettings(settings, about)
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
    ui.show(`${mode === 'day' ? '白天' : '夜晚'}壁纸已上传`)
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
  next.description = form.value.site.subtitle
  next.author = form.value.profile.name
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
          bgImages: modes.day.bgImages,
          activeBgIndex: modes.day.activeBgIndex,
          slideshowEnabled: modes.day.slideshowEnabled,
          slideshowInterval: modes.day.slideshowInterval,
          slideshowEffect: modes.day.slideshowEffect
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

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await adminApi.putJson('/admin/settings', buildSettingsPayload())
    await adminApi.putJson('/admin/about-page', buildAboutPayload())
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
    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.28em] text-slate-500">settings</p>
          <h1 class="mt-2 text-3xl font-black text-slate-950">设置</h1>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-600">只保留站点信息、我的信息、主题交互与留言授权。Secret 留空保存时保持旧值，不回显明文。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button class="admin-btn admin-btn-ghost" type="button" @click="load">刷新</button>
          <button :disabled="saving || loading" class="admin-btn admin-btn-primary" type="button" @click="save">{{ saving ? '保存中...' : '保存设置' }}</button>
        </div>
      </div>
      <p v-if="error" class="mt-3 text-sm text-red-700">{{ error }}</p>
      <p v-if="success" class="mt-3 text-sm text-emerald-700">{{ success }}</p>
    </div>

    <p v-if="loading" class="admin-card text-slate-500">设置加载中...</p>
    <div v-else class="grid gap-5">
      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">Frame1 站点信息设置</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="field">站点标题<input v-model="form.site.title" class="admin-input" /></label>
          <label class="field">副标题<input v-model="form.site.subtitle" class="admin-input" /></label>
        </div>
      </div>

      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">Frame2 我的信息设置</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="field">名称<input v-model="form.profile.name" class="admin-input" /></label>
          <label class="field">GitHub 链接<input v-model="form.profile.github" class="admin-input" placeholder="https://github.com/ShrinkShi" /></label>
          <label class="field md:col-span-2">简介<textarea v-model="form.profile.intro" class="admin-input min-h-28"></textarea></label>
          <label class="field">Email 复制内容<input v-model="form.profile.email" class="admin-input" /></label>
          <label class="field">QQ 复制内容<input v-model="form.profile.qq" class="admin-input" /></label>
          <label class="field">微信复制内容<input v-model="form.profile.wechat" class="admin-input" /></label>
        </div>
      </div>

      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">Frame3 主题设置</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="checkbox-row">
            <span>启用点击音效</span>
            <input v-model="form.theme.clickSoundEnabled" type="checkbox" />
          </label>
          <label class="checkbox-row">
            <span>启用鼠标点击特效</span>
            <input v-model="form.theme.clickEffectEnabled" type="checkbox" />
          </label>
          <label class="field">点击音效音量<input v-model.number="form.theme.clickSoundVolume" class="admin-input" type="number" min="0" max="1" step="0.01" /></label>
          <label class="field">点击音效 URL<input v-model="form.theme.clickSoundUrl" class="admin-input" /></label>
          <label class="field md:col-span-2">
            上传点击音效
            <div class="flex flex-wrap gap-2">
              <input class="admin-input min-w-0 flex-1" type="file" accept="audio/*" @change="clickSoundFile = (($event.target as HTMLInputElement).files?.[0] || null)" />
              <button class="admin-btn admin-btn-ghost" type="button" @click="uploadClickSound">上传</button>
            </div>
          </label>
        </div>

        <div class="mt-5 grid gap-4 lg:grid-cols-2">
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 class="font-black text-slate-950">子Frame 白天模式壁纸</h3>
            <p class="mt-1 text-xs text-slate-500">{{ wallpaperHint }} 也可以直接上传图片，上传后会自动追加 URL。</p>
            <div class="mt-3 flex flex-wrap items-center gap-2">
              <label class="admin-btn admin-btn-ghost cursor-pointer">
                {{ wallpaperUploading.day ? '上传中...' : '上传白天壁纸' }}
                <input
                  class="hidden"
                  type="file"
                  accept="image/*"
                  multiple
                  :disabled="wallpaperUploading.day"
                  @change="uploadWallpapers('day', ($event.target as HTMLInputElement).files); (($event.target as HTMLInputElement).value = '')"
                />
              </label>
            </div>
            <textarea v-model="form.theme.dayWallpapers" class="admin-input mt-3 min-h-36 font-mono text-sm"></textarea>
            <label class="field mt-3">默认壁纸序号<input v-model.number="form.theme.dayActiveIndex" class="admin-input" type="number" min="0" /></label>
            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <label class="checkbox-row sm:col-span-2">
                <span>启用白天壁纸轮播</span>
                <input v-model="form.theme.daySlideshowEnabled" type="checkbox" />
              </label>
              <label class="field">
                轮播间隔（秒）
                <input v-model.number="form.theme.daySlideshowInterval" class="admin-input" type="number" min="3" max="60" step="0.5" />
              </label>
              <label class="field">
                切换动画
                <select v-model="form.theme.daySlideshowEffect" class="admin-input">
                  <option value="fade">淡入淡出</option>
                  <option value="soft-blur">柔焦淡入</option>
                  <option value="none">无动画</option>
                </select>
              </label>
            </div>
          </div>
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <h3 class="font-black text-slate-950">子Frame 夜晚模式壁纸</h3>
            <p class="mt-1 text-xs text-slate-500">{{ wallpaperHint }} 也可以直接上传图片，上传后会自动追加 URL。</p>
            <div class="mt-3 flex flex-wrap items-center gap-2">
              <label class="admin-btn admin-btn-ghost cursor-pointer">
                {{ wallpaperUploading.night ? '上传中...' : '上传夜晚壁纸' }}
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
            <label class="field mt-3">默认壁纸序号<input v-model.number="form.theme.nightActiveIndex" class="admin-input" type="number" min="0" /></label>
            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <label class="checkbox-row sm:col-span-2">
                <span>启用夜晚壁纸轮播</span>
                <input v-model="form.theme.nightSlideshowEnabled" type="checkbox" />
              </label>
              <label class="field">
                轮播间隔（秒）
                <input v-model.number="form.theme.nightSlideshowInterval" class="admin-input" type="number" min="3" max="60" step="0.5" />
              </label>
              <label class="field">
                切换动画
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

      <div class="admin-card">
        <h2 class="text-xl font-black text-slate-950">Frame4 留言设置</h2>
        <p class="mt-2 text-sm text-slate-600">前台留言支持 OAuth 登录，密钥只保存在后端，不回显明文。</p>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="checkbox-row">
            <span>开启留言板</span>
            <input v-model="form.comments.enabled" type="checkbox" />
          </label>
          <label class="field">留言最大长度<input v-model.number="form.comments.maxLength" class="admin-input" type="number" min="1" /></label>

          <label class="checkbox-row">
            <span>启用 GitHub 登录留言</span>
            <input v-model="form.comments.githubLoginEnabled" type="checkbox" />
          </label>
          <label class="field">GitHub Client ID<input v-model="form.comments.githubClientId" class="admin-input" /></label>
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
            GitHub OAuth Secret 状态：<b>{{ form.comments.githubSecretConfigured ? '已配置' : '未配置' }}</b>
          </div>
          <label class="field">新的 GitHub OAuth Secret<input v-model="form.comments.githubSecret" class="admin-input" type="password" placeholder="留空则保持旧值，不回显明文" /></label>

          <label class="checkbox-row">
            <span>启用 QQ 登录留言</span>
            <input v-model="form.comments.qqLoginEnabled" type="checkbox" />
          </label>
          <label class="field">QQ App ID<input v-model="form.comments.qqAppId" class="admin-input" /></label>
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
            QQ App Secret 状态：<b>{{ form.comments.qqSecretConfigured ? '已配置' : '未配置' }}</b>
          </div>
          <label class="field">新的 QQ App Secret<input v-model="form.comments.qqSecret" class="admin-input" type="password" placeholder="留空则保持旧值，不回显明文" /></label>
        </div>
      </div>
    </div>
  </section>
</template>
