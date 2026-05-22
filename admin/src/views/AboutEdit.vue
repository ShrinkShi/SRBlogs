<script setup lang="ts">
import { onMounted, ref } from 'vue'
import GlassCard from '@/components/GlassCard.vue'
import { adminApi } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

type AnyRecord = Record<string, any>

const ui = useUiStore()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const section = ref<'hero' | 'about' | 'github' | 'contact'>('hero')
const aboutPage = ref<AnyRecord | null>(null)

const sections = [
  { key: 'hero', label: 'Hero 首屏' },
  { key: 'about', label: '关于我' },
  { key: 'github', label: 'GitHub 活动' },
  { key: 'contact', label: '联系我' }
] as const

function emptyAboutPage(): AnyRecord {
  return {
    hero: {
      status: '',
      eyebrow: '',
      name: '',
      role: '',
      description: '',
      primaryButtonText: '',
      primaryButtonUrl: '',
      secondaryButtonText: '',
      stats: []
    },
    about: {
      badge: '',
      title: '',
      paragraphs: [],
      highlightWords: [],
      skills: [],
      codeProfile: {
        variableName: '',
        name: '',
        role: '',
        location: '',
        languages: [],
        github: ''
      }
    },
    github: {
      badge: '',
      titlePrefix: '',
      titleAccent: '',
      stats: [],
      contributionText: ''
    },
    contact: {
      badge: '',
      title: '',
      headline: '',
      description: '',
      email: '',
      github: '',
      githubUrl: '',
      website: '',
      websiteUrl: '',
      qq: '',
      wechat: '',
      mailTo: ''
    }
  }
}

function addHeroStat() {
  aboutPage.value?.hero.stats.push({ value: '1', suffix: '+', label: '统计项' })
}

function addParagraph() {
  aboutPage.value?.about.paragraphs.push('新的介绍段落')
}

function addSkill() {
  aboutPage.value?.about.skills.push({ icon: 'rocket', title: '能力标题', description: '能力描述' })
}

function addGithubStat() {
  aboutPage.value?.github.stats.push({ icon: 'folder', value: '0', label: '统计项' })
}

function removeAt(list: any[], index: number) {
  list.splice(index, 1)
}

function languagesText() {
  return (aboutPage.value?.about.codeProfile.languages || []).join(', ')
}

function updateLanguages(value: string) {
  if (!aboutPage.value) return
  aboutPage.value.about.codeProfile.languages = value.split(',').map((item) => item.trim()).filter(Boolean)
}

function highlightsText() {
  return (aboutPage.value?.about.highlightWords || []).join(', ')
}

function updateHighlights(value: string) {
  if (!aboutPage.value) return
  aboutPage.value.about.highlightWords = value.split(',').map((item) => item.trim()).filter(Boolean)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    aboutPage.value = await adminApi.json<AnyRecord>('/admin/about-page')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '关于页配置加载失败'
    aboutPage.value = emptyAboutPage()
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!aboutPage.value) return
  saving.value = true
  error.value = ''
  try {
    await adminApi.putJson('/admin/about-page', aboutPage.value)
    ui.show('关于页已保存')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '关于页保存失败'
    ui.show(error.value)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="about-admin grid gap-5">
    <div class="admin-card">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-2xl font-black text-slate-950">关于页结构化编辑</h2>
        <div class="flex flex-wrap gap-2">
          <button class="admin-btn admin-btn-primary" type="button" :disabled="saving || loading" @click="save">
            {{ saving ? '保存中...' : '保存关于页' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">{{ error }}</div>
    <div v-if="loading" class="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-slate-600">关于页配置加载中...</div>

    <div v-if="aboutPage && !loading" class="grid gap-5 lg:grid-cols-[14rem_minmax(0,1fr)]">
      <GlassCard>
        <nav class="grid gap-2">
          <button
            v-for="item in sections"
            :key="item.key"
            type="button"
            class="rounded-xl px-4 py-3 text-left text-sm font-bold transition"
            :class="section === item.key ? 'bg-slate-950 text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
            @click="section = item.key"
          >
            {{ item.label }}
          </button>
        </nav>
      </GlassCard>

      <GlassCard>
        <div v-if="section === 'hero'" class="form-grid">
          <label>状态胶囊<input v-model="aboutPage.hero.status" class="admin-input" /></label>
          <label>小标题<input v-model="aboutPage.hero.eyebrow" class="admin-input" /></label>
          <label>主标题<input v-model="aboutPage.hero.name" class="admin-input" /></label>
          <label>角色标题<input v-model="aboutPage.hero.role" class="admin-input" /></label>
          <label class="md:col-span-2">简介文案<textarea v-model="aboutPage.hero.description" class="admin-input" rows="4"></textarea></label>
          <label>主按钮文案<input v-model="aboutPage.hero.primaryButtonText" class="admin-input" /></label>
          <label>主按钮链接<input v-model="aboutPage.hero.primaryButtonUrl" class="admin-input" /></label>
          <label>次按钮文案<input v-model="aboutPage.hero.secondaryButtonText" class="admin-input" /></label>
          <div class="md:col-span-2 list-box">
            <div class="list-head"><strong>统计项</strong><button class="admin-btn admin-btn-ghost" type="button" @click="addHeroStat">新增统计</button></div>
            <div v-for="(stat, index) in aboutPage.hero.stats" :key="index" class="repeat-row">
              <input v-model="stat.value" class="admin-input" placeholder="数值" />
              <input v-model="stat.suffix" class="admin-input" placeholder="后缀" />
              <input v-model="stat.label" class="admin-input" placeholder="说明" />
              <button class="admin-btn admin-btn-danger" type="button" @click="removeAt(aboutPage.hero.stats, Number(index))">删除</button>
            </div>
          </div>
        </div>

        <div v-else-if="section === 'about'" class="form-grid">
          <label>顶部胶囊<input v-model="aboutPage.about.badge" class="admin-input" /></label>
          <label>标题<input v-model="aboutPage.about.title" class="admin-input" /></label>
          <label class="md:col-span-2">高亮关键词（逗号分隔）<input :value="highlightsText()" class="admin-input" @input="updateHighlights(($event.target as HTMLInputElement).value)" /></label>
          <div class="md:col-span-2 list-box">
            <div class="list-head"><strong>介绍段落</strong><button class="admin-btn admin-btn-ghost" type="button" @click="addParagraph">新增段落</button></div>
            <div v-for="(paragraph, index) in aboutPage.about.paragraphs" :key="index" class="repeat-row paragraphs-row">
              <textarea v-model="aboutPage.about.paragraphs[Number(index)]" class="admin-input" rows="3"></textarea>
              <button class="admin-btn admin-btn-danger" type="button" @click="removeAt(aboutPage.about.paragraphs, Number(index))">删除</button>
            </div>
          </div>
          <div class="md:col-span-2 list-box">
            <div class="list-head"><strong>能力卡片</strong><button class="admin-btn admin-btn-ghost" type="button" @click="addSkill">新增能力</button></div>
            <div v-for="(skill, index) in aboutPage.about.skills" :key="index" class="repeat-row">
              <input v-model="skill.icon" class="admin-input" placeholder="图标类型" />
              <input v-model="skill.title" class="admin-input" placeholder="标题" />
              <input v-model="skill.description" class="admin-input" placeholder="描述" />
              <button class="admin-btn admin-btn-danger" type="button" @click="removeAt(aboutPage.about.skills, Number(index))">删除</button>
            </div>
          </div>
          <label>变量名<input v-model="aboutPage.about.codeProfile.variableName" class="admin-input" /></label>
          <label>姓名<input v-model="aboutPage.about.codeProfile.name" class="admin-input" /></label>
          <label>角色<input v-model="aboutPage.about.codeProfile.role" class="admin-input" /></label>
          <label>位置<input v-model="aboutPage.about.codeProfile.location" class="admin-input" /></label>
          <label class="md:col-span-2">语言列表（逗号分隔）<input :value="languagesText()" class="admin-input" @input="updateLanguages(($event.target as HTMLInputElement).value)" /></label>
          <label class="md:col-span-2">GitHub<input v-model="aboutPage.about.codeProfile.github" class="admin-input" /></label>
        </div>

        <div v-else-if="section === 'github'" class="form-grid">
          <label>顶部胶囊<input v-model="aboutPage.github.badge" class="admin-input" /></label>
          <label>标题前缀<input v-model="aboutPage.github.titlePrefix" class="admin-input" /></label>
          <label>标题重点词<input v-model="aboutPage.github.titleAccent" class="admin-input" /></label>
          <label>贡献说明<input v-model="aboutPage.github.contributionText" class="admin-input" /></label>
          <div class="md:col-span-2 list-box">
            <div class="list-head"><strong>GitHub 统计</strong><button class="admin-btn admin-btn-ghost" type="button" @click="addGithubStat">新增统计</button></div>
            <div v-for="(stat, index) in aboutPage.github.stats" :key="index" class="repeat-row">
              <input v-model="stat.icon" class="admin-input" placeholder="图标" />
              <input v-model="stat.value" class="admin-input" placeholder="数值" />
              <input v-model="stat.label" class="admin-input" placeholder="说明" />
              <button class="admin-btn admin-btn-danger" type="button" @click="removeAt(aboutPage.github.stats, Number(index))">删除</button>
            </div>
          </div>
        </div>

        <div v-else-if="section === 'contact'" class="form-grid">
          <label>顶部胶囊<input v-model="aboutPage.contact.badge" class="admin-input" /></label>
          <label>标题<input v-model="aboutPage.contact.title" class="admin-input" /></label>
          <label class="md:col-span-2">大标题<input v-model="aboutPage.contact.headline" class="admin-input" /></label>
          <label class="md:col-span-2">说明<textarea v-model="aboutPage.contact.description" class="admin-input" rows="4"></textarea></label>
          <label>Email<input v-model="aboutPage.contact.email" class="admin-input" /></label>
          <label>收件邮箱<input v-model="aboutPage.contact.mailTo" class="admin-input" /></label>
          <label>GitHub 展示<input v-model="aboutPage.contact.github" class="admin-input" /></label>
          <label>GitHub 链接<input v-model="aboutPage.contact.githubUrl" class="admin-input" /></label>
          <label>Website 展示<input v-model="aboutPage.contact.website" class="admin-input" /></label>
          <label>Website 链接<input v-model="aboutPage.contact.websiteUrl" class="admin-input" /></label>
          <label>QQ<input v-model="aboutPage.contact.qq" class="admin-input" /></label>
          <label>微信<input v-model="aboutPage.contact.wechat" class="admin-input" /></label>
        </div>

        <div class="mt-6 flex flex-wrap justify-end gap-2 border-t border-slate-200 pt-4">
          <button class="admin-btn admin-btn-primary" type="button" :disabled="saving" @click="save">
            {{ saving ? '保存中...' : '保存关于页' }}
          </button>
        </div>
      </GlassCard>
    </div>
  </section>
</template>

<style scoped>
.about-admin label {
  display: grid;
  gap: .45rem;
  color: #1f2937;
  font-size: .9rem;
  font-weight: 800;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.list-box {
  display: grid;
  gap: .75rem;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background: #f8fafc;
  padding: 1rem;
}

.list-head,
.repeat-row {
  display: flex;
  align-items: center;
  gap: .6rem;
}

.list-head {
  justify-content: space-between;
}

.repeat-row {
  align-items: flex-start;
}

.repeat-row .admin-input {
  min-width: 0;
}

.paragraphs-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .repeat-row {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
