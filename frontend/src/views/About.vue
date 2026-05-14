<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { contentApi } from '@/api/content'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import type { AboutPageConfig } from '@/types'

const ui = useUiStore()

const defaultConfig: AboutPageConfig = {
  hero: {
    status: 'Available for opportunities',
    eyebrow: '你好，我是',
    name: 'Shrink',
    role: '全栈开发工程师',
    description: '物联网工程专业学生，热衷于 MOD、游戏引擎，热爱软件、Web 应用开发。\n致力于用技术创造价值',
    primaryButtonText: '查看作品',
    primaryButtonUrl: '/projects',
    secondaryButtonText: '联系我',
    stats: [
      { value: '4', suffix: '+', label: '年经验' },
      { value: '20', suffix: '+', label: '个项目' },
      { value: '1,000', suffix: '+', label: '次提交' }
    ]
  },
  about: {
    badge: '<about />',
    title: '关于我',
    paragraphs: [
      '我是一名充满热情的全栈开发工程师，拥有丰富的 Web 应用开发经验。',
      '在多年的开发生涯中，我参与并主导了多个企业级项目的架构设计与开发工作。从前端的交互体验到后端的系统架构，从数据库设计到云端部署，我始终追求代码的优雅性和系统的可靠性。',
      '我相信技术的力量，热爱开源社区，持续学习新技术并将其应用到实际项目中。在工作之余，我也喜欢通过技术博客和开源项目与社区分享知识。'
    ],
    highlightWords: ['全栈开发工程师'],
    skills: [
      { icon: 'rocket', title: '全栈开发', description: '前端与后端的完整技术栈' },
      { icon: 'cloud', title: '云原生架构', description: 'Docker、K8s、微服务架构' },
      { icon: 'bot', title: 'AI 应用', description: 'LLM 集成与智能应用开发' }
    ],
    codeProfile: {
      variableName: 'Shrink',
      name: 'Shrink',
      role: 'Freelance Developer',
      location: 'BeiJing, China CN',
      languages: ['python', 'Java', 'c#', 'c++', 'Vue/Nuxt'],
      github: 'github.com/ShrinkShi'
    }
  },
  github: {
    badge: '<github />',
    titlePrefix: 'GitHub',
    titleAccent: '活动',
    stats: [
      { icon: 'folder', value: '20', label: '公开仓库' },
      { icon: 'star', value: '2616', label: 'Stars' },
      { icon: 'git-branch', value: '79', label: 'Followers' },
      { icon: 'fork', value: '837', label: 'Forks' }
    ],
    contributionText: '07836246 · 2,108 contributions'
  },
  contact: {
    badge: '<contact />',
    title: '联系我',
    headline: '让我们一起创造价值',
    description: '无论是工作机会、项目合作还是技术交流，都欢迎与我联系，期待与您的交流！',
    email: '1363072460@qq.com',
    github: 'github.com/ShrinkShi',
    githubUrl: 'https://github.com/ShrinkShi',
    website: 'www.shrink.asia',
    websiteUrl: 'https://www.shrink.asia',
    qq: '1363072460',
    wechat: '请填写微信号',
    mailTo: '1363072460@qq.com'
  }
}

const config = ref<AboutPageConfig>(defaultConfig)
const loading = ref(true)
const error = ref('')
const sending = ref(false)
const form = reactive({ name: '', email: '', message: '' })

useSeo({ title: '关于 - SRBlogs', description: '关于 Shrink 的个人介绍、GitHub 活动与联系方式。' })

const roleWords = ['全栈开发工程师', '游戏开发者', 'MOD作者']
const typedRole = ref(roleWords[0])
const githubStats = ref<AboutPageConfig['github']['stats']>([])
const githubHeatmapCells = ref<number[]>([])
const githubContributionText = ref('')
const githubLoading = ref(false)
const githubError = ref('')
let typingTimer: number | undefined
let typingWordIndex = 0
let typingCharIndex = 0
let isDeleting = false

type HighlightSegment = {
  text: string
  highlighted: boolean
}

const fallbackHeatmapCells = computed(() =>
  Array.from({ length: 154 }, (_, index) => (index * 7 + Math.floor(index / 11) * 3) % 6)
)

const displayGithubStats = computed(() => (githubStats.value.length ? githubStats.value : config.value.github.stats))
const displayHeatmapCells = computed(() =>
  githubHeatmapCells.value.length ? githubHeatmapCells.value : fallbackHeatmapCells.value
)
const displayGithubContributionText = computed(() => githubContributionText.value || config.value.github.contributionText)

function formatAvailabilityStatus(value: string) {
  const normalized = (value || 'Available for opportunities').trim().toLowerCase()
  return normalized ? normalized.charAt(0).toUpperCase() + normalized.slice(1) : 'Available for opportunities'
}

function scheduleTyping(delay = 90) {
  window.clearTimeout(typingTimer)
  typingTimer = window.setTimeout(runTypingFrame, delay)
}

function runTypingFrame() {
  const word = roleWords[typingWordIndex % roleWords.length]
  if (isDeleting) {
    typingCharIndex = Math.max(0, typingCharIndex - 1)
    typedRole.value = word.slice(0, typingCharIndex)
    if (typingCharIndex === 0) {
      isDeleting = false
      typingWordIndex = (typingWordIndex + 1) % roleWords.length
      scheduleTyping(260)
      return
    }
    scheduleTyping(54)
    return
  }

  typingCharIndex = Math.min(word.length, typingCharIndex + 1)
  typedRole.value = word.slice(0, typingCharIndex)
  if (typingCharIndex === word.length) {
    isDeleting = true
    scheduleTyping(1200)
    return
  }
  scheduleTyping(92)
}

function startRoleTyping() {
  typingWordIndex = 0
  typingCharIndex = 0
  isDeleting = false
  typedRole.value = ''
  scheduleTyping(120)
}

function compactNumber(value: number) {
  if (value >= 1000) return value.toLocaleString('en-US')
  return String(value)
}

async function fetchGithubSummary() {
  githubLoading.value = true
  githubError.value = ''
  try {
    const username = 'ShrinkShi'
    const [userResponse, reposResponse, eventsResponse] = await Promise.all([
      fetch(`https://api.github.com/users/${username}`),
      fetch(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`),
      fetch(`https://api.github.com/users/${username}/events/public?per_page=100`)
    ])

    if (!userResponse.ok || !reposResponse.ok || !eventsResponse.ok) {
      throw new Error('GitHub public API unavailable')
    }

    const user = await userResponse.json()
    const repos = await reposResponse.json()
    const events = await eventsResponse.json()
    const repoList = Array.isArray(repos) ? repos : []
    const eventList = Array.isArray(events) ? events : []
    const stars = repoList.reduce((sum: number, repo: { stargazers_count?: number }) => sum + (repo.stargazers_count || 0), 0)
    const forks = repoList.reduce((sum: number, repo: { forks_count?: number }) => sum + (repo.forks_count || 0), 0)

    githubStats.value = [
      { icon: 'folder', value: compactNumber(Number(user.public_repos || repoList.length || 0)), label: '公开仓库' },
      { icon: 'star', value: compactNumber(stars), label: 'Stars' },
      { icon: 'git-branch', value: compactNumber(Number(user.followers || 0)), label: 'Followers' },
      { icon: 'fork', value: compactNumber(forks), label: 'Forks' }
    ]

    const buckets = Array.from({ length: 154 }, () => 0)
    const now = Date.now()
    for (const event of eventList) {
      const createdAt = Date.parse(event.created_at)
      if (Number.isNaN(createdAt)) continue
      const daysAgo = Math.floor((now - createdAt) / 86_400_000)
      if (daysAgo >= 0 && daysAgo < buckets.length) {
        buckets[buckets.length - 1 - daysAgo] += 1
      }
    }
    githubHeatmapCells.value = buckets.map((count) => Math.min(5, count))
    githubContributionText.value = `${user.login || username} · ${eventList.length} recent public events`
  } catch (exc) {
    githubError.value = exc instanceof Error ? exc.message : 'GitHub 数据加载失败'
  } finally {
    githubLoading.value = false
  }
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function highlightSegments(text: string): HighlightSegment[] {
  const source = String(text || '')
  const words = Array.from(new Set((config.value.about.highlightWords || [])
    .map((word) => String(word || '').trim())
    .filter(Boolean)))
    .sort((a, b) => b.length - a.length)
  if (!source || !words.length) return [{ text: source, highlighted: false }]

  const pattern = new RegExp(words.map(escapeRegExp).join('|'), 'g')
  const segments: HighlightSegment[] = []
  let lastIndex = 0
  for (const match of source.matchAll(pattern)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      segments.push({ text: source.slice(lastIndex, index), highlighted: false })
    }
    segments.push({ text: match[0], highlighted: true })
    lastIndex = index + match[0].length
  }
  if (lastIndex < source.length) {
    segments.push({ text: source.slice(lastIndex), highlighted: false })
  }
  return segments.length ? segments : [{ text: source, highlighted: false }]
}

function statIcon(icon: string) {
  const map: Record<string, string> = { folder: 'M3 7h6l2 2h10v10H3z', star: 'M12 3l2.7 5.5 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.8 1-6.1L3.2 9.4l6.1-.9z', 'git-branch': 'M6 3v6m0 0a3 3 0 100-6 3 3 0 000 6zm12 12a3 3 0 100-6 3 3 0 000 6zM6 9v3a6 6 0 006 6h3', fork: 'M7 3v6m10-6v6M7 9a3 3 0 100-6 3 3 0 000 6zm10 0a3 3 0 100-6 3 3 0 000 6zm-5 3v4' }
  return map[icon] || map.folder
}

async function copyText(label: string, text: string) {
  try {
    await navigator.clipboard.writeText(text)
    ui.showToast(`${label} 已复制`, 'success')
  } catch {
    ui.showToast(`${label} 复制失败`, 'error')
  }
}

async function submitContact() {
  sending.value = true
  try {
    const result = await contentApi.sendContact({ ...form })
    ui.showToast(result.message || '消息已发送', 'success')
    form.name = ''
    form.email = ''
    form.message = ''
  } catch (exc) {
    ui.showToast(exc instanceof Error ? exc.message : '消息发送失败', 'error')
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  startRoleTyping()
  try {
    config.value = await contentApi.aboutPage()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '关于页配置加载失败，已使用默认内容。'
  } finally {
    loading.value = false
  }
  void fetchGithubSummary()
})

onBeforeUnmount(() => {
  window.clearTimeout(typingTimer)
})
</script>

<template>
  <main class="about-page">
    <section id="about-hero" class="about-section hero-section">
      <div class="about-shell hero-centered">
        <div class="hero-content">
          <p class="status-pill hero-status"><span class="status-dot"></span>{{ formatAvailabilityStatus(config.hero.status) }}</p>
          <p class="eyebrow">{{ config.hero.eyebrow }}</p>
          <h1>{{ config.hero.name }}</h1>
          <h2 class="typed-role"><span>{{ typedRole }}</span><i aria-hidden="true"></i></h2>
          <p v-if="error" class="about-error">{{ error }}</p>
          <p class="hero-desc">{{ config.hero.description }}</p>
          <div class="hero-actions">
            <RouterLink class="about-button primary" :to="config.hero.primaryButtonUrl">{{ config.hero.primaryButtonText }}</RouterLink>
            <button class="about-button secondary" type="button" @click="scrollTo('about-contact')">{{ config.hero.secondaryButtonText }}</button>
          </div>
        </div>
      </div>
      <button class="scroll-cue" type="button" @click="scrollTo('about-profile')">
        向下滚动
        <span></span>
      </button>
    </section>

    <section id="about-profile" class="about-section">
      <div class="about-shell two-column profile-layout">
        <header class="about-section-header">
          <p class="section-badge">{{ config.about.badge }}</p>
          <h2>{{ config.about.title }}</h2>
        </header>
        <div class="section-copy profile-copy">
          <div class="paragraphs">
            <p v-for="(paragraph, index) in config.about.paragraphs" :key="index">
              <span
                v-for="(segment, segmentIndex) in highlightSegments(paragraph)"
                :key="`${index}-${segmentIndex}`"
                :class="{ 'about-accent': segment.highlighted }"
              >{{ segment.text }}</span>
            </p>
          </div>
          <div class="skills-grid">
            <article v-for="skill in config.about.skills" :key="skill.title" class="skill-card">
              <span class="skill-icon">{{ skill.icon === 'cloud' ? 'CN' : skill.icon === 'bot' ? 'AI' : 'FS' }}</span>
              <h3>{{ skill.title }}</h3>
              <p>{{ skill.description }}</p>
            </article>
          </div>
        </div>
        <aside class="code-card" aria-label="个人代码资料">
          <div class="code-window-bar">
            <div class="code-dots" aria-hidden="true"><span></span><span></span><span></span></div>
            <span class="code-filename">Shrink.json</span>
          </div>
          <pre><code><span class="code-var">{{ config.about.codeProfile.variableName }}</span> = {
  name: <span class="code-string">"{{ config.about.codeProfile.name }}"</span>,
  role: <span class="code-string">"{{ config.about.codeProfile.role }}"</span>,
  location: <span class="code-string">"{{ config.about.codeProfile.location }}"</span>,
  language: [<span class="code-string">"{{ config.about.codeProfile.languages.slice(0, 2).join('", "') }}"</span>,
             <span class="code-string">"{{ config.about.codeProfile.languages.slice(2).join('", "') }}"</span>],
  github: <span class="code-string">"{{ config.about.codeProfile.github }}"</span>
};</code></pre>
        </aside>
      </div>
    </section>

    <section id="about-github" class="about-section">
      <div class="about-shell github-shell">
        <header class="about-section-header">
          <p class="section-badge">{{ config.github.badge }}</p>
          <h2>{{ config.github.titlePrefix }} <span>{{ config.github.titleAccent }}</span></h2>
        </header>
        <div class="github-stats">
          <article v-for="stat in displayGithubStats" :key="stat.label" class="github-stat-card">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="statIcon(stat.icon)" /></svg>
            <strong>{{ stat.value }}</strong>
            <span>{{ stat.label }}</span>
          </article>
        </div>
        <div class="heatmap-card">
          <div class="heatmap-head">
            <strong>{{ displayGithubContributionText }}</strong>
            <span>{{ githubLoading ? '正在读取 GitHub 公共活动' : 'GitHub Public Activity' }}</span>
          </div>
          <div class="heatmap-grid">
            <i v-for="(level, index) in displayHeatmapCells" :key="index" :data-level="level"></i>
          </div>
          <p v-if="githubError" class="github-fallback">GitHub 公共数据暂时读取失败，已显示后台配置兜底数据。</p>
          <div class="heatmap-legend">
            <span>Less</span>
            <i v-for="level in [0, 1, 2, 3, 4]" :key="level" :data-level="level"></i>
            <span>More</span>
          </div>
        </div>
      </div>
    </section>

    <section id="about-contact" class="about-section">
      <div class="about-shell two-column contact-layout">
        <header class="about-section-header">
          <p class="section-badge">{{ config.contact.badge }}</p>
          <h2>{{ config.contact.title }}</h2>
        </header>
        <div class="section-copy contact-copy">
          <h3 class="contact-headline"><span>{{ config.contact.headline.slice(0, 1) }}</span>{{ config.contact.headline.slice(1) }}</h3>
          <p class="contact-description">{{ config.contact.description }}</p>
          <div class="contact-cards">
            <a class="contact-card" :href="`mailto:${config.contact.email}`"><strong>Email</strong><span>{{ config.contact.email }}</span></a>
            <a class="contact-card" :href="config.contact.githubUrl" target="_blank" rel="noopener noreferrer"><strong>GitHub</strong><span>{{ config.contact.github }}</span></a>
            <a class="contact-card" :href="config.contact.websiteUrl" target="_blank" rel="noopener noreferrer"><strong>Website</strong><span>{{ config.contact.website }}</span></a>
          </div>
          <div class="social-actions" aria-label="社交联系">
            <a :href="config.contact.githubUrl" target="_blank" rel="noopener noreferrer" title="GitHub">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 00-3.2 19c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.2-3.5-1.2-.5-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 0 1.6 1 1.6 1 .9 1.5 2.3 1.1 2.9.8.1-.7.4-1.1.7-1.4-2.3-.3-4.7-1.2-4.7-5A3.9 3.9 0 016.5 7c-.1-.3-.4-1.3.1-2.8 0 0 .9-.3 2.9 1.1A10 10 0 0112 5c.9 0 1.8.1 2.6.3 2-1.4 2.9-1.1 2.9-1.1.5 1.5.2 2.5.1 2.8a3.9 3.9 0 011 2.7c0 3.9-2.4 4.7-4.7 5 .4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5A10 10 0 0012 2z" /></svg>
            </a>
            <button type="button" title="复制微信" @click="copyText('微信', config.contact.wechat)">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 6A6.5 6.5 0 003 12.2a5.8 5.8 0 001.1 3.4L3.5 18l2.5-.8a7.5 7.5 0 003.5.9c3.6 0 6.5-2.7 6.5-6S13.1 6 9.5 6zm-2.3 5.2a.8.8 0 110-1.6.8.8 0 010 1.6zm4.6 0a.8.8 0 110-1.6.8.8 0 010 1.6zM17 10.5a5.7 5.7 0 014 5.3 5 5 0 01-1 3l.5 2-2-.7a6.6 6.6 0 01-3 .7 6 6 0 01-5.6-3.5 7.3 7.3 0 006.9-6.8z" /></svg>
            </button>
            <button type="button" title="复制 QQ" @click="copyText('QQ', config.contact.qq)">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c-3 0-5 2.7-5 6.8 0 1.8-.8 3-1.4 4-.4.7-.7 1.3-.5 1.9.2.6.8.8 1.4.8-.2.8-.1 1.4.4 1.8.6.4 1.5.2 2.3-.2.8.6 1.8.9 2.8.9s2-.3 2.8-.9c.8.4 1.7.6 2.3.2.5-.4.6-1 .4-1.8.6 0 1.2-.2 1.4-.8.2-.6-.1-1.2-.5-1.9-.6-1-1.4-2.2-1.4-4C17 5.7 15 3 12 3z" /></svg>
            </button>
          </div>
        </div>
        <form class="contact-form" @submit.prevent="submitContact">
          <label>姓名<input v-model.trim="form.name" required maxlength="80" placeholder="你的名字" /></label>
          <label>邮箱<input v-model.trim="form.email" required type="email" maxlength="160" placeholder="you@example.com" /></label>
          <label>留言<textarea v-model.trim="form.message" required maxlength="2000" rows="7" placeholder="想和我聊些什么？"></textarea></label>
          <button class="about-button primary" type="submit" :disabled="sending">{{ sending ? '发送中...' : '发送消息' }}</button>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
.about-page {
  position: relative;
  z-index: 1;
  --about-muted: color-mix(in srgb, var(--text-primary) 72%, transparent);
  --about-code-font: 'Consolas-with-Yahei', Consolas, 'Microsoft YaHei', '微软雅黑', 'Courier New', ui-monospace, monospace;
  color: var(--text-primary);
  font-family: var(--about-code-font);
  padding: 2rem 0 5rem;
}

.about-section {
  position: relative;
  min-height: calc(100vh - 4.5rem);
  display: grid;
  place-items: center;
  padding: clamp(4rem, 7vw, 7rem) 1rem;
  overflow: clip;
}

.hero-section {
  place-items: start center;
  overflow: visible;
  padding-top: clamp(.5rem, 1.4vh, 1rem);
}

.about-shell {
  width: min(100%, 1100px);
  margin-inline: auto;
}

.two-column {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.8fr);
  align-items: center;
  gap: clamp(2rem, 5vw, 5rem);
}

.profile-layout {
  grid-template-columns: minmax(0, 1fr) minmax(360px, .88fr);
  column-gap: clamp(1.35rem, 2.6vw, 2.5rem);
  row-gap: clamp(.55rem, 1.4vw, 1rem);
}

.section-copy,
.code-card,
.heatmap-card,
.contact-form,
.github-stat-card,
.skill-card {
  border: 1px solid var(--border-glass);
  background: var(--bg-card-elevated);
  box-shadow: 0 18px 48px color-mix(in srgb, #000 14%, transparent);
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.section-copy,
.code-card,
.heatmap-card,
.contact-form {
  border-radius: 30px;
  padding: clamp(1.5rem, 4vw, 3rem);
}

.profile-copy,
.contact-copy {
  border-color: transparent;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.hero-centered {
  display: grid;
  place-items: center;
  text-align: center;
}

.hero-section .about-shell {
  transform: translateY(-4vh);
}

.hero-content {
  display: grid;
  justify-items: center;
  width: min(100%, 860px);
}

.status-pill,
.section-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  color: var(--accent);
  font-family: var(--about-code-font);
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: none;
}

.section-badge {
  margin-inline: auto;
  background: color-mix(in srgb, var(--accent) 20%, transparent);
  border-color: color-mix(in srgb, var(--accent) 42%, transparent);
  color: var(--accent);
}

.hero-status {
  gap: .55rem;
  border-color: color-mix(in srgb, #22c55e 45%, transparent);
  color: #22c55e;
  background: color-mix(in srgb, #22c55e 20%, transparent);
}

.status-dot {
  width: .62rem;
  height: .62rem;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 16px #22c55e, 0 0 4px #22c55e;
}

.eyebrow {
  margin-top: 2.5rem;
  color: var(--about-muted);
  font-size: calc(1rem + 2px);
  font-weight: 800;
}

h1,
h2 {
  line-height: 1.05;
  color: var(--text-primary);
}

h1 {
  margin-top: 0.4rem;
  font-size: clamp(4rem, 11vw, 8rem);
  font-family: 'Microsoft YaHei', '微软雅黑', var(--about-code-font);
  color: transparent;
  background: linear-gradient(110deg, #e11d48 8%, #fb7185 52%, #be123c 96%);
  -webkit-background-clip: text;
  background-clip: text;
}

.typed-role,
.about-section-header h2 span,
.about-accent,
.contact-headline span {
  color: var(--accent);
}

.typed-role {
  display: inline-flex;
  align-items: center;
  gap: .15em;
  min-height: 1.5em;
  margin-top: .65rem;
  font-size: clamp(1.15rem, 2.3vw, 1.85rem);
  color: #fb7185;
  letter-spacing: .05em;
}

.typed-role i {
  width: 2px;
  height: 1.15em;
  border-radius: 999px;
  background: currentColor;
  animation: about-caret 1s steps(2, start) infinite;
}

@keyframes about-caret {
  50% {
    opacity: 0;
  }
}

.hero-desc,
.paragraphs,
.contact-description {
  margin-top: 1.25rem;
  white-space: pre-line;
  color: var(--about-muted);
  font-size: clamp(1rem, 1.4vw, 1.15rem);
  line-height: 1.9;
}

.hero-actions,
.social-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-top: 2rem;
}

.about-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border-radius: 999px;
  padding: 0 1.2rem;
  font-weight: 900;
  transition: transform .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease;
}

.about-button:hover {
  transform: scale(1.045);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 28%, transparent),
    0 0 24px color-mix(in srgb, var(--accent) 28%, transparent),
    0 14px 34px color-mix(in srgb, var(--shadow-glow) 20%, transparent);
}

.about-button.primary {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: white;
}

.about-button.secondary {
  border: 1px solid color-mix(in srgb, var(--text-primary) 20%, transparent);
  background: color-mix(in srgb, #9ca3af 40%, transparent);
  color: var(--text-primary);
}

.github-stats,
.skills-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.9rem;
  margin-top: 2rem;
}

.github-stat-card,
.skill-card {
  border-radius: 22px;
  padding: 1rem;
}

.github-stat-card strong {
  display: block;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 4vw, 3rem);
  line-height: 1;
}

.github-stat-card span,
.skill-card p {
  color: var(--about-muted);
}

.scroll-cue {
  position: absolute;
  bottom: clamp(16rem, 26vh, 20rem);
  left: 50%;
  display: grid;
  justify-items: center;
  gap: 0.25rem;
  transform: translateX(-50%);
  color: var(--about-muted);
  font-size: 0.85rem;
}

.scroll-cue span {
  position: relative;
  order: -1;
  width: 24px;
  height: 38px;
  border-radius: 999px;
  border: 2px solid color-mix(in srgb, var(--accent) 72%, transparent);
  background: var(--bg-card-elevated);
}

.scroll-cue span::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 8px;
  width: 3px;
  height: 8px;
  border-radius: 999px;
  background: var(--accent);
  transform: translateX(-50%);
  animation: about-mouse-wheel 1.35s ease-in-out infinite;
}

.scroll-cue span::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -18px;
  width: 1px;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(var(--accent), transparent);
  transform: translateX(-50%);
}

@keyframes about-mouse-wheel {
  0% {
    opacity: 0;
    transform: translate(-50%, 0);
  }
  35% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(-50%, 10px);
  }
}

.about-section-header {
  grid-column: 1 / -1;
  display: grid;
  justify-items: center;
  text-align: center;
  margin-bottom: clamp(1.5rem, 4vw, 3rem);
}

.profile-layout .about-section-header,
.contact-layout .about-section-header {
  margin-bottom: clamp(.35rem, 1vw, .8rem);
}

.contact-layout {
  row-gap: clamp(.55rem, 1.4vw, 1rem);
}

.about-section-header h2 {
  margin-top: 1rem;
  font-size: clamp(.9rem, calc(3vw - 10px), 1.925rem);
  line-height: 1.05;
  color: transparent;
  background: linear-gradient(110deg, #e11d48 8%, #fb7185 52%, #be123c 96%);
  -webkit-background-clip: text;
  background-clip: text;
  font-weight: 950;
}

.paragraphs {
  display: grid;
  gap: 1rem;
}

.skill-card h3 {
  margin-top: .7rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.skill-card {
  border-color: var(--border-glass);
  background: var(--bg-card-elevated);
  box-shadow: 0 12px 30px color-mix(in srgb, #000 12%, transparent);
}

.skill-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  color: var(--accent);
  font-weight: 900;
}

.code-card {
  justify-self: center;
  width: min(100%, 212px);
  min-width: 0;
  overflow: hidden;
  padding: 0;
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.code-card:hover {
  border-color: color-mix(in srgb, var(--accent) 58%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 20%, transparent),
    0 0 34px color-mix(in srgb, var(--accent) 24%, transparent),
    0 18px 48px color-mix(in srgb, var(--shadow-glow) 14%, transparent);
  transform: scale(1.025);
}

.code-window-bar {
  display: flex;
  align-items: center;
  gap: .65rem;
  min-height: 44px;
  padding: 0 1.2rem;
  border-bottom: 1px solid color-mix(in srgb, var(--border-glass) 50%, transparent);
  background: var(--bg-card);
}

.code-dots {
  display: flex;
  gap: .45rem;
  margin: 0;
}

.code-dots span {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.code-dots span:nth-child(1) {
  background: #ef4444;
}

.code-dots span:nth-child(2) {
  background: #f59e0b;
}

.code-dots span:nth-child(3) {
  background: #22c55e;
}

.code-filename {
  color: var(--about-muted);
  font-size: .86rem;
  font-weight: 800;
}

pre {
  margin: 0;
  color: var(--text-primary);
  padding: clamp(1.1rem, 2.4vw, 2rem);
  font-family: var(--about-code-font);
  font-size: .88rem;
  line-height: 1.75;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  overflow-x: hidden;
}

.code-var { color: var(--accent); font-weight: 900; }
.code-string { color: #16a34a; }

.github-shell {
  width: min(100%, 640px);
}

.github-stats {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: .55rem;
}

.github-stat-card svg,
.social-actions svg {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

.github-stat-card {
  min-width: 0;
  padding: .7rem;
  color: var(--accent);
  border-color: color-mix(in srgb, var(--border-glass) 48%, transparent);
  background: var(--bg-card-elevated);
  box-shadow: 0 12px 30px color-mix(in srgb, #000 12%, transparent);
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.github-stat-card:hover,
.heatmap-card:hover {
  border-color: color-mix(in srgb, var(--accent) 58%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 20%, transparent),
    0 0 30px color-mix(in srgb, var(--accent) 22%, transparent),
    0 16px 42px color-mix(in srgb, var(--shadow-glow) 12%, transparent);
  transform: scale(1.025);
}

.github-stat-card strong {
  font-size: clamp(1.15rem, 2.8vw, 1.7rem);
}

.github-stat-card span {
  font-size: .78rem;
}

.heatmap-card {
  margin-top: 1rem;
  padding: 1.2rem;
  border-color: color-mix(in srgb, var(--border-glass) 46%, transparent);
  background: var(--bg-card-elevated);
  box-shadow: 0 12px 30px color-mix(in srgb, #000 12%, transparent);
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.heatmap-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: var(--about-muted);
}

.github-fallback {
  margin-top: .9rem;
  color: var(--about-muted);
  font-size: .9rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(22, 1fr);
  gap: 3px;
  margin-top: 1rem;
}

.heatmap-grid i,
.heatmap-legend i {
  aspect-ratio: 1;
  border-radius: 5px;
  background: color-mix(in srgb, var(--about-muted) 18%, transparent);
}

i[data-level="1"] { background: color-mix(in srgb, var(--accent) 22%, transparent); }
i[data-level="2"] { background: color-mix(in srgb, var(--accent) 38%, transparent); }
i[data-level="3"] { background: color-mix(in srgb, var(--accent) 58%, transparent); }
i[data-level="4"],
i[data-level="5"] { background: var(--accent); }

.heatmap-legend {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: .35rem;
  margin-top: 1rem;
  color: var(--about-muted);
  font-size: .85rem;
}

.heatmap-legend i {
  width: 14px;
  height: 14px;
}

.contact-headline {
  margin-top: 1.25rem;
  color: var(--text-primary);
  font-size: clamp(.95rem, 1.65vw, 1.35rem);
}

.contact-cards {
  display: grid;
  gap: .75rem;
  margin-top: 2rem;
}

.contact-card {
  display: grid;
  gap: .2rem;
  border: 3px solid color-mix(in srgb, var(--border-glass) 96%, transparent);
  border-radius: 18px;
  background: color-mix(in srgb, #9ca3af 40%, transparent);
  padding: 1rem;
  color: var(--text-primary);
  transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease, background .2s ease;
}

.contact-card:hover {
  border-color: color-mix(in srgb, var(--accent) 72%, transparent);
  background: color-mix(in srgb, #9ca3af 40%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 28%, transparent),
    0 0 24px color-mix(in srgb, var(--accent) 30%, transparent),
    0 12px 30px color-mix(in srgb, var(--shadow-glow) 18%, transparent);
  transform: scale(1.025);
}

.contact-card span {
  color: var(--about-muted);
}

.social-actions a,
.social-actions button {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
  border-radius: 16px;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease, border-color .2s ease;
}

.social-actions a:hover,
.social-actions button:hover {
  border-color: color-mix(in srgb, var(--accent) 78%, transparent);
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 24%, transparent),
    0 0 22px color-mix(in srgb, var(--accent) 34%, transparent);
  transform: scale(1.08);
}

.contact-form {
  display: grid;
  gap: 1rem;
  border-color: color-mix(in srgb, var(--border-glass) 36%, transparent);
  background: var(--bg-card-elevated);
  box-shadow: 0 14px 34px color-mix(in srgb, #000 12%, transparent);
  transition: border-color .2s ease, box-shadow .2s ease;
}

.contact-form:hover {
  border-color: color-mix(in srgb, var(--accent) 38%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 16%, transparent),
    0 0 28px color-mix(in srgb, var(--accent) 18%, transparent),
    0 18px 42px color-mix(in srgb, var(--shadow-glow) 18%, transparent);
}

.contact-form label {
  display: grid;
  gap: .45rem;
  color: var(--text-primary);
  font-weight: 800;
  transition: color .18s ease;
}

.contact-form label:hover {
  color: var(--accent);
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--border-glass) 48%, transparent);
  border-radius: 18px;
  background: var(--bg-card);
  color: var(--text-primary);
  padding: .85rem 1rem;
  outline: none;
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}

.contact-form input:hover,
.contact-form textarea:hover {
  border-color: color-mix(in srgb, var(--accent) 42%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--accent) 16%, transparent),
    0 0 18px color-mix(in srgb, var(--accent) 18%, transparent);
}

.contact-form input:focus,
.contact-form textarea:focus {
  border-color: var(--accent);
}

.about-error {
  margin-top: 1rem;
  color: var(--accent);
  font-weight: 800;
}

@media (max-width: 900px) {
  .two-column {
    grid-template-columns: 1fr;
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .github-stats,
  .skills-grid {
    grid-template-columns: 1fr;
  }

  .about-section {
    min-height: auto;
  }
}

@media (max-width: 430px) {
  .about-page {
    padding-top: 1rem;
  }

  .about-section {
    padding-inline: .75rem;
  }

  .section-copy,
  .code-card,
  .heatmap-card,
  .contact-form {
    border-radius: 22px;
    padding: 1rem;
  }

  h1 {
    font-size: clamp(3rem, 17vw, 4rem);
  }

  .heatmap-grid {
    grid-template-columns: repeat(11, 1fr);
  }
}
</style>
