<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DiscoveryResultCard from './DiscoveryResultCard.vue'
import FrontUpdatePanel from './FrontUpdatePanel.vue'
import FrontendAdminSettings from './FrontendAdminSettings.vue'
import StateBlock from './StateBlock.vue'
import { contentApi } from '@/api/content'
import { themes, useUiStore } from '@/stores/ui'
import { usePlayerStore } from '@/stores/player'
import { useSessionStore } from '@/stores/session'
import type { DiscoveryType, SearchResponse, SiteSettings, TagItem } from '@/types'

type ToolPanel = 'calculator' | 'search' | 'settings' | 'update'
type Token = number | string

const props = defineProps<{ settings?: SiteSettings | null; activePanel?: ToolPanel | null }>()
const emit = defineEmits<{
  'update:activePanel': [panel: ToolPanel | null]
  settingsSaved: []
}>()

const ui = useUiStore()
const player = usePlayerStore()
const session = useSessionStore()

const activePanel = computed<ToolPanel | null>({
  get: () => props.activePanel ?? null,
  set: (panel) => emit('update:activePanel', panel)
})
const calculatorExpr = ref('')
const calculatorResult = ref('')
const calculatorError = ref('')

const searchQ = ref('')
const searchType = ref<DiscoveryType>('all')
const searchTag = ref('')
const searchLoading = ref(false)
const searchError = ref('')
const searchResult = ref<SearchResponse>({ items: [], total: 0, limit: 20, offset: 0 })
const tags = ref<TagItem[]>([])

const typeOptions: { label: string; value: DiscoveryType }[] = [
  { label: '全部', value: 'all' },
  { label: '文章', value: 'posts' },
  { label: '说说', value: 'moments' },
  { label: '杂谈', value: 'chatters' },
  { label: '项目', value: 'projects' },
  { label: '相册', value: 'photos' },
  { label: '友链', value: 'friends' },
  { label: '音乐', value: 'music' }
]

function countBackgrounds(value: unknown) {
  const list = Array.isArray(value) ? value : value ? [value] : []
  return list.filter((item: unknown) => {
    if (typeof item === 'string') return item.trim()
    if (item && typeof item === 'object') {
      const entry = item as { url?: string; enabled?: boolean }
      return entry.enabled !== false && typeof entry.url === 'string' && entry.url.trim()
    }
    return false
  }).length
}

const bgCount = computed(() => {
  const config = props.settings?.themeConfig
  const activeTheme = config?.activeTheme || props.settings?.theme || 'shrink-red-glass'
  const activePackage = config?.themePackages?.[activeTheme]
  const localTokens = config?.night
  const packageTokens = activePackage?.modes?.night
  const modeTokens = { ...(packageTokens || {}), ...(localTokens || {}) } as { bgImages?: unknown; bgImage?: unknown }
  const modeCount = countBackgrounds(modeTokens.bgImages) || countBackgrounds(modeTokens.bgImage)
  const legacyCount = countBackgrounds(props.settings?.bgImages)
  return Math.max(modeCount || legacyCount, themes.length)
})
const siteBgSlideshowEnabled = computed(() => props.settings?.themeConfig?.backgroundSlideshowEnabled !== false)
const themeLabel = (theme: string) => theme === 'shrink-red-glass' ? 'Shrink 红白黑玻璃主题' : theme
const modalTitle = computed(() => {
  if (activePanel.value === 'search') return '全局搜索'
  if (activePanel.value === 'settings') return '设置'
  if (activePanel.value === 'update') return '版本更新'
  return ''
})

function notifySettingsSaved() {
  emit('settingsSaved')
}

function closeAll() {
  activePanel.value = null
}

function closePanel() {
  activePanel.value = null
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeAll()
}

function appendCalc(value: string) {
  calculatorExpr.value += value
  calculatorError.value = ''
}

function backspaceCalc() {
  calculatorExpr.value = calculatorExpr.value.slice(0, -1)
}

function clearCalc() {
  calculatorExpr.value = ''
  calculatorResult.value = ''
  calculatorError.value = ''
}

function tokenize(input: string): Token[] {
  if (!/^[\d+\-*/().\s]+$/.test(input)) throw new Error('表达式包含不支持的字符')
  const tokens: Token[] = []
  let i = 0
  while (i < input.length) {
    const char = input[i]
    const previous = tokens[tokens.length - 1]
    const unaryMinus = char === '-' && (tokens.length === 0 || ['+', '-', '*', '/', '('].includes(String(previous))) && /[\d.]/.test(input[i + 1] || '')
    if (/\s/.test(char)) {
      i += 1
    } else if (/\d|\./.test(char) || unaryMinus) {
      let value = unaryMinus ? '-' : ''
      if (unaryMinus) i += 1
      while (i < input.length && /[\d.]/.test(input[i])) {
        value += input[i]
        i += 1
      }
      const number = Number(value)
      if (!Number.isFinite(number)) throw new Error('数字格式不正确')
      tokens.push(number)
    } else if ('+-*/()'.includes(char)) {
      tokens.push(char)
      i += 1
    } else {
      throw new Error('表达式包含不支持的字符')
    }
  }
  return tokens
}

function evaluateExpression(input: string) {
  const precedence: Record<string, number> = { '+': 1, '-': 1, '*': 2, '/': 2 }
  const values: number[] = []
  const operators: string[] = []
  function applyOperator() {
    const op = operators.pop()
    const b = values.pop()
    const a = values.pop()
    if (!op || a === undefined || b === undefined) throw new Error('表达式不完整')
    if (op === '+') values.push(a + b)
    if (op === '-') values.push(a - b)
    if (op === '*') values.push(a * b)
    if (op === '/') {
      if (b === 0) throw new Error('除数不能为 0')
      values.push(a / b)
    }
  }
  tokenize(input).forEach((token) => {
    if (typeof token === 'number') values.push(token)
    else if (token === '(') operators.push(token)
    else if (token === ')') {
      while (operators.length && operators[operators.length - 1] !== '(') applyOperator()
      if (operators.pop() !== '(') throw new Error('括号不匹配')
    } else {
      while (operators.length && operators[operators.length - 1] !== '(' && precedence[operators[operators.length - 1]] >= precedence[token]) {
        applyOperator()
      }
      operators.push(token)
    }
  })
  while (operators.length) applyOperator()
  if (values.length !== 1 || !Number.isFinite(values[0])) throw new Error('表达式不完整')
  return Number(values[0].toFixed(10)).toString()
}

function calculate() {
  try {
    calculatorError.value = ''
    calculatorResult.value = evaluateExpression(calculatorExpr.value)
  } catch (exc) {
    calculatorResult.value = ''
    calculatorError.value = exc instanceof Error ? exc.message : '表达式错误'
  }
}

async function loadTags() {
  try {
    tags.value = await contentApi.tags()
  } catch {
    tags.value = []
  }
}

async function runSearch() {
  searchLoading.value = true
  searchError.value = ''
  try {
    searchResult.value = await contentApi.search({
      q: searchQ.value.trim(),
      type: searchType.value,
      tag: searchTag.value.trim(),
      limit: 30
    })
  } catch (exc) {
    searchError.value = exc instanceof Error ? exc.message : '搜索失败'
  } finally {
    searchLoading.value = false
  }
}

watch(activePanel, (panel) => {
  if (panel === 'search') {
    if (!tags.value.length) loadTags()
    if (!searchResult.value.items.length) runSearch()
  }
})

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <section
      v-if="activePanel === 'calculator'"
      data-toolbox-modal
      class="toolbox-calculator-panel fixed bottom-24 left-5 z-[92] grid w-[min(22rem,calc(100vw-2rem))] gap-3 rounded-[28px] border p-4 shadow-2xl toolbox-night"
      role="dialog"
      aria-label="计算器"
      @click.stop
    >
      <header class="flex items-center justify-between gap-3">
        <div>
          <p class="text-xs font-bold uppercase tracking-[.22em] text-cyan-100/45">calculator</p>
          <h2 class="text-xl font-black">计算器</h2>
        </div>
        <button type="button" data-clickable="true" class="rounded-full bg-white px-4 py-1.5 text-sm font-black text-black" @click="closePanel">关闭</button>
      </header>
      <div class="rounded-[22px] border border-white/12 bg-white/[0.09] p-3">
        <p class="min-h-6 break-all text-base text-white/80">{{ calculatorExpr || '0' }}</p>
        <p class="mt-1 min-h-8 text-2xl font-black text-cyan-100">{{ calculatorResult }}</p>
        <p v-if="calculatorError" class="mt-2 text-sm text-red-200">{{ calculatorError }}</p>
      </div>
      <div class="grid grid-cols-4 gap-2">
        <button v-for="key in ['7','8','9','/','4','5','6','*','1','2','3','-','0','.','(',')']" :key="key" type="button" data-clickable="true" class="toolbox-key" @click="appendCalc(key)">{{ key }}</button>
        <button type="button" data-clickable="true" class="toolbox-key" @click="backspaceCalc">退格</button>
        <button type="button" data-clickable="true" class="toolbox-key" @click="appendCalc('+')">+</button>
        <button type="button" data-clickable="true" class="toolbox-key" @click="clearCalc">清空</button>
        <button type="button" data-clickable="true" class="toolbox-key toolbox-key-main" @click="calculate">=</button>
      </div>
    </section>

    <div
      v-if="activePanel === 'search' || activePanel === 'settings' || activePanel === 'update'"
      data-toolbox-modal
      class="toolbox-modal-overlay fixed inset-0 z-[90] grid place-items-center p-4"
      :class="'toolbox-night'"
      role="dialog"
      aria-modal="true"
      @click.self="closePanel"
    >
      <section class="toolbox-modal toolbox-modal-panel max-h-[88vh] w-full max-w-5xl overflow-hidden rounded-[32px] border shadow-2xl" :class="[activePanel === 'search' ? 'toolbox-modal-panel-search' : 'toolbox-modal-panel-settings', 'toolbox-night']">
        <header class="flex items-center justify-between gap-3 border-b border-white/10 px-5 py-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-[.28em] text-cyan-100/45">toolbox</p>
            <h2 class="text-2xl font-black">{{ modalTitle }}</h2>
          </div>
          <button type="button" data-clickable="true" class="rounded-full bg-white px-4 py-2 text-sm font-black text-black" @click="closePanel">关闭</button>
        </header>

        <div class="max-h-[calc(88vh-5.5rem)] overflow-y-auto p-5">
          <div v-if="activePanel === 'search'" class="grid gap-4">
            <form class="mx-auto flex w-full max-w-3xl items-center gap-2 rounded-[22px] border border-white/14 bg-white/[0.38] px-3 py-2" @submit.prevent="runSearch">
              <input v-model="searchQ" class="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/52" placeholder="搜索标题、标签或内容..." aria-label="全局搜索关键词" />
              <button type="submit" class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950/90 text-cyan-100" aria-label="搜索">
                <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <circle cx="11" cy="11" r="7" />
                  <path d="m20 20-3.6-3.6" />
                </svg>
              </button>
            </form>
            <div class="flex flex-wrap justify-center gap-2">
              <button v-for="option in typeOptions" :key="option.value" type="button" class="rounded-full border px-3 py-1 text-sm" :class="searchType === option.value ? 'border-cyan-200/50 bg-cyan-200/[0.16] text-cyan-100' : 'border-white/10 text-white/60 hover:bg-white/10'" @click="searchType = option.value; runSearch()">{{ option.label }}</button>
            </div>
            <div v-if="tags.length" class="flex flex-wrap justify-center gap-2">
              <button v-for="item in tags.slice(0, 14)" :key="item.tag" type="button" class="rounded-full border px-3 py-1 text-xs" :class="searchTag === item.tag ? 'border-fuchsia-200/50 bg-fuchsia-200/[0.16] text-fuchsia-100' : 'border-white/10 text-white/55 hover:bg-white/10'" @click="searchTag = searchTag === item.tag ? '' : item.tag; runSearch()"># {{ item.tag }} / {{ item.count }}</button>
            </div>
            <StateBlock v-if="searchLoading" message="搜索中..." />
            <StateBlock v-else-if="searchError" title="搜索失败" :message="searchError" @retry="runSearch" />
            <div v-else-if="searchResult.items.length" class="grid gap-4 md:grid-cols-2">
              <div v-for="item in searchResult.items" :key="`${item.type}-${item.url}-${item.title}`" @click.capture="closePanel">
                <DiscoveryResultCard :item="item" />
              </div>
            </div>
            <div v-else class="rounded-[24px] border border-white/12 bg-white/[0.09] p-5 text-center text-white/64">没有匹配内容。</div>
          </div>

          <FrontUpdatePanel v-else-if="activePanel === 'update' && session.isAdmin" />
          <div v-else-if="activePanel === 'update'" class="rounded-[24px] border border-white/12 bg-white/[0.06] p-6 text-center text-white/64">
            请先使用管理员账号登录后再检查或执行更新。
          </div>

          <FrontendAdminSettings v-else-if="session.isAdmin" @saved="notifySettingsSaved" />

          <div v-else class="grid gap-5 md:grid-cols-2">
            <label class="toolbox-setting">
              <span>主题</span>
              <select :value="ui.theme" @change="ui.setTheme(($event.target as HTMLSelectElement).value)">
                <option v-for="theme in themes" :key="theme" :value="theme">{{ themeLabel(theme) }}</option>
              </select>
            </label>
            <label class="toolbox-setting">
              <span>背景</span>
              <select :value="ui.bgIndex" @change="ui.setBgIndex(Number(($event.target as HTMLSelectElement).value))">
                <option v-for="i in bgCount" :key="i" :value="i - 1">背景 {{ i }}</option>
              </select>
            </label>
            <label class="toolbox-setting toolbox-switch">
              <span>背景轮播</span>
              <input
                type="checkbox"
                :checked="siteBgSlideshowEnabled && ui.bgSlideshow"
                :disabled="!siteBgSlideshowEnabled"
                @change="ui.setBgSlideshow(($event.target as HTMLInputElement).checked)"
              />
            </label>
            <label class="toolbox-setting">
              <span>字体大小</span>
              <select :value="ui.fontScale" @change="ui.setFontScale(($event.target as HTMLSelectElement).value as 'small' | 'medium' | 'large')">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
              </select>
            </label>
            <label class="toolbox-setting toolbox-switch">
              <span>氛围效果</span>
              <input type="checkbox" :checked="ui.ambience" @change="ui.toggleAmbience" />
            </label>
            <label class="toolbox-setting toolbox-switch">
              <span>弹幕背景</span>
              <input type="checkbox" :checked="ui.danmaku" @change="ui.toggleDanmaku" />
            </label>
            <label v-if="ui.clickSoundAllowed" class="toolbox-setting toolbox-switch">
              <span>点击音效</span>
              <input type="checkbox" :checked="ui.clickSound" @change="ui.toggleClickSound" />
            </label>
            <div v-else class="toolbox-setting">
              <span>点击音效</span>
              <p class="text-sm text-white/55">站点已关闭，游客设置不可覆盖。</p>
            </div>
            <label v-if="ui.clickEffectAllowed" class="toolbox-setting toolbox-switch">
              <span>鼠标点击特效</span>
              <input type="checkbox" :checked="ui.clickEffect" @change="ui.toggleClickEffect" />
            </label>
            <div v-else class="toolbox-setting">
              <span>鼠标点击特效</span>
              <p class="text-sm text-white/55">站点已关闭，游客设置不可覆盖。</p>
            </div>
            <label v-if="ui.clickSoundAllowed" class="toolbox-setting">
              <span>点击音量</span>
              <input type="range" min="0" max="1" step="0.01" :value="ui.clickSoundVolume" @input="ui.setClickSoundVolume(Number(($event.target as HTMLInputElement).value))" />
            </label>
            <label class="toolbox-setting">
              <span>音乐音量</span>
              <input type="range" min="0" max="1" step="0.01" :value="player.volume" @input="player.setVolume(Number(($event.target as HTMLInputElement).value))" />
            </label>
            <label class="toolbox-setting toolbox-switch">
              <span>音乐静音</span>
              <input type="checkbox" :checked="player.muted" @change="player.toggleMuted" />
            </label>
          </div>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.toolbox-menu-item {
  border-radius: 1rem;
  padding: .65rem .85rem;
  text-align: left;
  transition: transform .2s var(--motion-ease), background .2s var(--motion-ease), color .2s var(--motion-ease);
}
.toolbox-menu {
  background: var(--ct-toolbox-menu-bg, #191A1B) !important;
  color: var(--ct-toolbox-menu-text, rgba(255,255,255,.78));
  border-color: var(--ct-toolbox-menu-border, rgba(255,255,255,.15));
  transform-origin: bottom left;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
.toolbox-fab {
  background: var(--ct-toolbox-fab-bg, #191A1B) !important;
  color: var(--ct-toolbox-fab-text, rgb(207 250 254));
  border-color: var(--ct-toolbox-fab-border, rgba(103,232,249,.25));
  transform: scale(var(--ct-toolbox-fab-size, 1));
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
.toolbox-menu-item {
  color: var(--ct-toolbox-menu-text, rgba(255,255,255,.78));
}
.toolbox-menu-item:hover {
  background: rgb(31 41 55);
  color: white;
  transform: scale(1.02);
}
.toolbox-key {
  min-height: 2.55rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, .14);
  background: white;
  color: black;
  font-weight: 900;
  transition: transform .18s var(--motion-ease), background .18s var(--motion-ease);
}
.toolbox-key:hover {
  transform: scale(1.025);
  background: rgba(255, 255, 255, .88);
}
.toolbox-key-main {
  background: #86efac;
  color: black;
}
.toolbox-setting {
  display: grid;
  gap: .55rem;
  border-radius: 1.25rem;
  border: 1px solid rgba(255, 255, 255, .12);
  background: #202123;
  padding: 1rem;
  color: rgb(248 250 252);
  font-size: .9rem;
}
.toolbox-calculator-panel {
  background: var(--ct-toolbox-calculator-panel-bg, #191A1B) !important;
  color: var(--ct-toolbox-calculator-panel-text, currentColor);
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
.toolbox-modal-panel-settings {
  background: var(--ct-toolbox-settings-panel-bg, #191A1B) !important;
  color: var(--ct-toolbox-settings-panel-text, currentColor);
}
.toolbox-modal-panel-search {
  background: var(--ct-toolbox-search-panel-bg, #191A1B) !important;
  color: var(--ct-toolbox-search-panel-text, currentColor);
}
.toolbox-modal-panel,
.toolbox-modal-overlay {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
.toolbox-modal-overlay {
  background: rgb(0 0 0 / .62);
}
:global(:root[data-color-mode='day']) .toolbox-modal-overlay {
  background: rgb(0 0 0 / .62);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel,
:global(:root[data-color-mode='day']) .toolbox-calculator-panel {
  color: rgb(15, 23, 42);
}
:global(:root[data-color-mode='day']) .toolbox-menu {
  background: var(--ct-toolbox-menu-bg, rgb(255 255 255)) !important;
  border-color: rgba(15, 23, 42, .14);
  color: rgb(17, 24, 39);
  box-shadow: 0 18px 48px rgba(15, 23, 42, .18);
}
:global(:root[data-color-mode='day']) .toolbox-menu-item {
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-menu-item:hover {
  background: rgb(254 226 226);
  color: rgb(127, 29, 29);
}
:global(:root[data-color-mode='day']) .toolbox-fab {
  background: var(--ct-toolbox-fab-bg, rgb(255 255 255)) !important;
  border-color: rgba(244, 0, 2, .28);
  color: #f40002;
  box-shadow: 0 18px 48px rgba(15, 23, 42, .18), 0 0 24px rgba(244, 0, 2, .16);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel header {
  border-color: rgba(15, 23, 42, .1);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel :where(h1,h2,h3,p,span,label,small) {
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel :where(input, select, textarea) {
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel header p {
  color: #f40002;
}
:global(:root[data-color-mode='day']) .toolbox-setting {
  background: var(--bg-card-elevated, rgb(255 255 255));
  border-color: rgba(15, 23, 42, .1);
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-setting :where(span,p,label) {
  color: rgb(17, 24, 39) !important;
}
:global(:root[data-color-mode='day']) .toolbox-setting select,
:global(:root[data-color-mode='day']) .toolbox-setting input[type='range'] {
  background: var(--bg-card-elevated, rgb(255 255 255));
  border-color: rgba(15, 23, 42, .18);
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-setting select option {
  background: rgb(255, 255, 255);
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='night']) .toolbox-setting select option {
  background: #191A1B;
  color: rgb(248, 250, 252);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel button:not(.toolbox-key) {
  color: rgb(17, 24, 39);
}
:global(:root[data-color-mode='day']) .toolbox-modal-panel button:hover {
  background: rgb(254 226 226);
}
.toolbox-setting select,
.toolbox-setting input[type='range'] {
  min-width: 0;
  border-radius: .9rem;
  border: 1px solid rgb(55 65 81);
  background: #191A1B;
  padding: .55rem .7rem;
  color: white;
}
.toolbox-switch {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}
.toolbox-switch input {
  width: 1.15rem;
  height: 1.15rem;
  accent-color: var(--accent);
}

.toolbox-day.toolbox-modal-panel,
.toolbox-day.toolbox-calculator-panel {
  color: rgb(17, 24, 39) !important;
  background: rgb(248 250 252) !important;
  border-color: rgba(15, 23, 42, .12) !important;
}

.toolbox-night.toolbox-modal-panel,
.toolbox-night.toolbox-calculator-panel {
  color: rgb(248, 250, 252) !important;
  background: #191A1B !important;
  border-color: rgba(255, 255, 255, .14) !important;
}

.toolbox-day .toolbox-menu {
  background: rgb(255 255 255) !important;
  border-color: rgba(15, 23, 42, .14) !important;
  color: rgb(17, 24, 39) !important;
}

.toolbox-night .toolbox-menu {
  background: rgba(25, 26, 27, .94) !important;
  border-color: rgba(255, 255, 255, .18) !important;
  color: rgb(248, 250, 252) !important;
  box-shadow: 0 22px 60px rgba(0, 0, 0, .46), 0 0 0 1px rgba(244, 0, 2, .10) inset !important;
}

.toolbox-day .toolbox-menu-item {
  color: rgb(17, 24, 39) !important;
}

.toolbox-night .toolbox-menu-item {
  color: rgb(248, 250, 252) !important;
}

.toolbox-day .toolbox-menu-item:hover {
  background: rgb(254 226 226) !important;
  color: rgb(127, 29, 29) !important;
}

.toolbox-night .toolbox-menu-item:hover {
  background: rgba(244, 0, 2, .16) !important;
  color: rgb(255, 255, 255) !important;
}

.toolbox-day .toolbox-fab {
  background: rgb(255 255 255) !important;
  border-color: rgba(244, 0, 2, .32) !important;
  color: #f40002 !important;
}

.toolbox-night .toolbox-fab {
  background: rgba(25, 26, 27, .94) !important;
  border-color: rgba(244, 0, 2, .34) !important;
  color: #fb7185 !important;
  box-shadow: 0 18px 48px rgba(0, 0, 0, .42), 0 0 26px rgba(244, 0, 2, .14) !important;
}

.toolbox-day.toolbox-modal-panel :where(h1,h2,h3,p,span,label,small),
.toolbox-day.toolbox-calculator-panel :where(h1,h2,h3,p,span,label,small),
.toolbox-day .toolbox-setting :where(span,p,label,small) {
  color: rgb(17, 24, 39) !important;
}

.toolbox-night.toolbox-modal-panel :where(h1,h2,h3,p,span,label,small),
.toolbox-night.toolbox-calculator-panel :where(h1,h2,h3,p,span,label,small),
.toolbox-night .toolbox-setting :where(span,p,label,small) {
  color: rgb(248, 250, 252) !important;
}

.toolbox-day .toolbox-setting {
  background: rgb(255, 255, 255) !important;
  border-color: rgba(15, 23, 42, .1) !important;
  color: rgb(17, 24, 39) !important;
}

.toolbox-night .toolbox-setting {
  background: #202123 !important;
  border-color: rgba(255, 255, 255, .12) !important;
  color: rgb(248, 250, 252) !important;
}

.toolbox-day .toolbox-setting :where(select, input[type='range'], textarea) {
  background-color: rgb(255, 255, 255) !important;
  border-color: rgba(15, 23, 42, .18) !important;
  color: rgb(17, 24, 39) !important;
}

.toolbox-night .toolbox-setting :where(select, input[type='range'], textarea) {
  background-color: #191A1B !important;
  border-color: rgba(255, 255, 255, .16) !important;
  color: rgb(248, 250, 252) !important;
}

.toolbox-day .toolbox-setting select option {
  background: rgb(255, 255, 255) !important;
  color: rgb(17, 24, 39) !important;
}

.toolbox-night .toolbox-setting select option {
  background: #191A1B !important;
  color: rgb(248, 250, 252) !important;
}
</style>
