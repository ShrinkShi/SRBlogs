<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi, type UpdateStatus } from '@/api/admin'

type NavItem = {
  label: string
  path: string
}

type NavGroup = {
  key: string
  title: string
  items: NavItem[]
}

const auth = useAuthStore()
const route = useRoute()
const updateStatus = ref<UpdateStatus | null>(null)
const updateLoading = ref(false)
const updateActionLoading = ref(false)
const updateError = ref('')
const versionModalOpen = ref(false)

const groups: NavGroup[] = [
  {
    key: 'content',
    title: '内容',
    items: [
      { label: '文章', path: '/content/articles' },
      { label: '图片', path: '/content/photos' },
      { label: '音乐', path: '/content/music' },
      { label: '项目', path: '/content/projects' },
      { label: '友链', path: '/content/friends' },
      { label: '关于', path: '/content/about' }
    ]
  },
  {
    key: 'settings',
    title: '设置',
    items: [{ label: '设置中心', path: '/settings' }]
  }
]

const activePath = computed(() => route.path)
const latestTag = computed(() => updateStatus.value?.latest?.tag || '')
const currentVersion = computed(() => {
  const version = updateStatus.value?.current?.version || 'unknown'
  return version === 'unknown' || version.startsWith('v') ? version : `v${version}`
})
const versionState = computed<'latest' | 'available' | 'unknown'>(() => {
  if (!updateStatus.value || updateError.value || updateStatus.value.latest?.error) return 'unknown'
  return updateStatus.value.updateAvailable ? 'available' : 'latest'
})
const versionStateLabel = computed(() => {
  if (versionState.value === 'available') return '发现新版本'
  if (versionState.value === 'latest') return '已是最新版'
  return '状态未知'
})

function isItemActive(item: NavItem): boolean {
  return activePath.value === item.path || activePath.value.startsWith(`${item.path}/`)
}

function logout() {
  auth.logout()
  location.href = '/admin/login'
}

async function loadUpdateStatus() {
  updateLoading.value = true
  updateError.value = ''
  try {
    updateStatus.value = await adminApi.updateStatus()
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '版本状态加载失败'
  } finally {
    updateLoading.value = false
  }
}

async function checkRelease() {
  updateLoading.value = true
  updateError.value = ''
  try {
    updateStatus.value = await adminApi.checkUpdate()
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '检查更新失败'
  } finally {
    updateLoading.value = false
  }
}

async function runReleaseUpdate() {
  if (!updateStatus.value?.updateConfigured) {
    updateError.value = '后端更新接口尚未接入或未启用。'
    return
  }
  updateActionLoading.value = true
  updateError.value = ''
  try {
    updateStatus.value = await adminApi.runUpdate(latestTag.value)
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '启动更新失败'
  } finally {
    updateActionLoading.value = false
  }
}

onMounted(loadUpdateStatus)
</script>

<template>
  <div class="admin-flat min-h-screen">
    <div class="admin-layout-grid grid min-h-screen">
      <aside class="admin-sidebar flex h-screen flex-col overflow-auto xl:sticky xl:top-0">
        <div class="admin-brand-card">
          <div class="flex items-center gap-3">
            <span class="admin-brand-mark">SR</span>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-black tracking-tight text-slate-950">SRBlogs</h1>
              <p class="text-xs font-semibold text-slate-500">后台管理系统</p>
            </div>
          </div>
        </div>

        <nav class="grid flex-1 content-start gap-3" aria-label="后台导航">
          <section v-for="group in groups" :key="group.key" class="admin-nav-group">
            <div class="admin-nav-parent">
              <b>{{ group.title }}</b>
            </div>
            <div class="admin-nav-children">
              <RouterLink
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="admin-nav-child"
                :class="isItemActive(item) ? 'admin-nav-child-active' : ''"
              >
                <span>{{ item.label }}</span>
              </RouterLink>
            </div>
          </section>
        </nav>

        <div class="mt-6 grid gap-3">
          <button
            type="button"
            class="version-card"
            :class="`version-card-${versionState}`"
            @click="versionModalOpen = true"
          >
            <span class="version-dot" aria-hidden="true"></span>
            <span class="min-w-0 text-left">
              <b>{{ currentVersion }}</b>
              <small>{{ updateLoading ? '检测中...' : versionStateLabel }}</small>
            </span>
          </button>
          <button type="button" class="admin-btn admin-btn-ghost w-full" @click="logout">退出登录</button>
        </div>
      </aside>

      <main class="admin-main min-w-0">
        <slot />
      </main>
    </div>

    <div v-if="versionModalOpen" class="admin-modal-backdrop" role="dialog" aria-modal="true" aria-label="版本更新">
      <div class="admin-modal">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-[.24em] text-slate-500">release</p>
            <h2 class="mt-2 text-2xl font-black text-slate-950">版本更新</h2>
          </div>
          <button type="button" class="admin-btn admin-btn-ghost" @click="versionModalOpen = false">关闭</button>
        </div>

        <div class="mt-5 grid gap-3">
          <div class="version-info-row">
            <span>当前版本</span>
            <b>{{ currentVersion }}</b>
          </div>
          <div class="version-info-row">
            <span>最新版本</span>
            <b>{{ updateStatus?.latest?.tag || '未检测' }}</b>
          </div>
          <div class="version-info-row">
            <span>发布时间</span>
            <b>{{ updateStatus?.latest?.publishedAt || '-' }}</b>
          </div>
          <div class="version-info-row">
            <span>检测状态</span>
            <b>{{ updateError || updateStatus?.latest?.error || versionStateLabel }}</b>
          </div>
        </div>

        <div class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <h3 class="text-sm font-black text-slate-950">更新摘要</h3>
          <p class="mt-2 max-h-56 overflow-auto whitespace-pre-wrap text-sm leading-6 text-slate-600">
            {{ updateStatus?.latest?.body || updateStatus?.latest?.name || '暂无 release notes。' }}
          </p>
        </div>

        <div v-if="updateStatus?.run?.status" class="mt-4 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
          <p><b>更新任务：</b>{{ updateStatus.run.status }}</p>
          <p v-if="updateStatus.run.pid"><b>PID：</b>{{ updateStatus.run.pid }}</p>
          <p v-if="updateStatus.run.startedAt"><b>启动时间：</b>{{ updateStatus.run.startedAt }}</p>
          <p v-if="updateStatus.run.log"><b>日志：</b>{{ updateStatus.run.log }}</p>
        </div>

        <p v-if="!updateStatus?.updateConfigured" class="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
          后端更新接口尚未接入或未启用。需要配置安全的后端更新接口后，才能执行立即更新。
        </p>

        <div class="mt-5 flex flex-wrap justify-end gap-2">
          <button class="admin-btn admin-btn-ghost" type="button" :disabled="updateLoading" @click="checkRelease">
            {{ updateLoading ? '检测中...' : '重新检测' }}
          </button>
          <button
            class="admin-btn admin-btn-primary"
            type="button"
            :disabled="!updateStatus?.updateConfigured || !updateStatus?.updateAvailable || updateActionLoading"
            @click="runReleaseUpdate"
          >
            {{ updateActionLoading ? '启动中...' : '立即更新' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
