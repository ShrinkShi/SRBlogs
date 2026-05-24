<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { adminApi, type UpdateStatus, type UpdateTask } from '@/api/admin'

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
const ui = useUiStore()
const route = useRoute()
const updateStatus = ref<UpdateStatus | null>(null)
const updateLoading = ref(false)
const updateActionLoading = ref(false)
const updateError = ref('')
const localDebugLogs = ref<string[]>([])
const versionModalOpen = ref(false)
const versionDebugOpen = ref(false)
const updateTask = ref<UpdateTask | null>(null)
const updateLogLines = ref<string[]>([])
const updatePollingTimer = ref<number | null>(null)
const updateReconnectHint = ref(false)
const updateHadRunningTask = ref(false)

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
const latestTag = computed(() => updateStatus.value?.latestVersion || updateStatus.value?.latest?.tag || '')
const currentVersion = computed(() => {
  const version = updateStatus.value?.currentVersion || updateStatus.value?.current?.version || ''
  if (!version) return updateError.value ? '后端未返回' : 'unknown'
  return version === 'unknown' || version.startsWith('v') ? version : `v${version}`
})
const latestVersionLabel = computed(() => {
  const version = updateStatus.value?.latestVersion || updateStatus.value?.latest?.tag || ''
  if (version) return version.startsWith('v') ? version : `v${version}`
  if (updateError.value || updateStatus.value?.status === 'error' || updateStatus.value?.errorCode || updateStatus.value?.latest?.error) return '检测失败'
  return '未检测'
})
const versionState = computed<'latest' | 'available' | 'unknown'>(() => {
  if (!updateStatus.value || updateError.value || updateStatus.value.status === 'error') return 'unknown'
  return updateStatus.value.hasUpdate || updateStatus.value.updateAvailable ? 'available' : 'latest'
})
const versionStateLabel = computed(() => {
  if (versionState.value === 'available') return '发现新版本'
  if (versionState.value === 'latest') return '已是最新版'
  return '状态未知'
})
const detectionStatusLabel = computed(() => {
  if (updateError.value) return updateError.value
  const code = updateStatus.value?.errorCode || updateStatus.value?.latest?.errorCode || updateStatus.value?.latest?.errorType || ''
  const labels: Record<string, string> = {
    github_release_not_found: '未找到 GitHub Release',
    github_network_error: '无法访问 GitHub',
    github_timeout: '请求 GitHub 超时',
    github_rate_limited: 'GitHub API 限流',
    unsupported_platform: '当前环境不支持一键更新',
    update_script_missing: '未找到更新脚本',
    sudo_password_required: '当前服务器未配置免密码 sudo，无法通过 WebUI 一键更新。',
    stale_task: '更新进程已经退出，任务状态已自动修复。',
    version_constant_missing: '当前版本常量缺失',
    unknown_error: updateStatus.value?.errorMessage || updateStatus.value?.message || '未知错误'
  }
  if (code && labels[code]) return labels[code]
  return updateStatus.value?.errorMessage || updateStatus.value?.latest?.error || versionStateLabel.value
})
const updateSupportMessage = computed(() => {
  if (!updateStatus.value || updateStatus.value.updateSupported) return ''
  return updateStatus.value.updateErrorMessage || updateStatus.value.message || '当前环境不支持一键更新，请在 Linux 服务器执行'
})
const versionDebugLogs = computed(() => {
  const logs = updateStatus.value?.debugLogs?.length ? updateStatus.value.debugLogs : localDebugLogs.value
  return logs.filter(Boolean)
})
const shouldShowDebugToggle = computed(() => {
  return Boolean(
    versionDebugLogs.value.length &&
      (updateError.value ||
        updateStatus.value?.errorCode ||
        updateStatus.value?.status === 'error' ||
        currentVersion.value === 'unknown' ||
        currentVersion.value === '后端未返回' ||
        !updateStatus.value?.updateSupported)
  )
})
const activeUpdateTask = computed(() => updateTask.value || updateStatus.value?.task || null)
const taskStatusLabel = computed(() => {
  const status = activeUpdateTask.value?.status || 'idle'
  const labels: Record<string, string> = {
    idle: '空闲',
    running: updateReconnectHint.value ? '后端重启中，正在重连' : '更新中',
    success: '更新完成',
    failed: '更新失败'
  }
  return labels[status] || status
})
const taskStepLabel = computed(() => {
  const step = activeUpdateTask.value?.currentStep || 'idle'
  const labels: Record<string, string> = {
    idle: '等待开始',
    preparing: '准备更新',
    download: '下载 Release',
    backup: '备份旧版本',
    extract: '解压更新包',
    build: '安装依赖与构建',
    install: '切换版本',
    nginx: '检查 Nginx',
    systemd: '重启后端服务',
    healthcheck: '健康检查',
    cleanup: '清理临时文件',
    done: '完成'
  }
  return labels[step] || step || '运行中'
})
const taskProgress = computed(() => {
  const value = Number(activeUpdateTask.value?.progress ?? 0)
  if (!Number.isFinite(value)) return 0
  return Math.max(0, Math.min(100, value))
})
const displayedUpdateLogs = computed(() => {
  if (updateLogLines.value.length) return updateLogLines.value
  return activeUpdateTask.value?.lastLines || []
})
const taskIsRunning = computed(() => activeUpdateTask.value?.status === 'running')
const showTaskProgress = computed(() => Boolean(activeUpdateTask.value && activeUpdateTask.value.status !== 'idle'))
const taskPossiblyStuck = computed(() => {
  if (!taskIsRunning.value) return false
  const stamp = activeUpdateTask.value?.lastLogAt || activeUpdateTask.value?.updatedAt
  if (!stamp) return false
  const value = new Date(stamp).getTime()
  if (!Number.isFinite(value)) return false
  return Date.now() - value > 5 * 60 * 1000
})
const canRunUpdate = computed(() => {
  return Boolean(
    updateStatus.value?.updateSupported &&
      !updateStatus.value.errorCode &&
      !taskIsRunning.value &&
      (updateStatus.value.hasUpdate || updateStatus.value.updateAvailable)
  )
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
  localDebugLogs.value = []
  try {
    updateStatus.value = await adminApi.updateStatus()
    if (updateStatus.value.task) {
      updateTask.value = updateStatus.value.task
    }
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '版本状态加载失败'
    localDebugLogs.value = [`前端请求 /api/admin/update/status 失败: ${updateError.value}`]
    ui.error('版本状态加载失败')
  } finally {
    updateLoading.value = false
  }
}

function stopUpdatePolling() {
  if (updatePollingTimer.value) {
    window.clearInterval(updatePollingTimer.value)
    updatePollingTimer.value = null
  }
}

function startUpdatePolling() {
  if (updatePollingTimer.value) return
  updatePollingTimer.value = window.setInterval(() => {
    void loadUpdateTask({ silent: true })
  }, 2000)
}

async function loadUpdateTask(options: { silent?: boolean } = {}) {
  try {
    const [task, progress] = await Promise.all([adminApi.updateTask(), adminApi.updateProgress(100)])
    updateTask.value = {
      ...task,
      status: progress.status || task.status,
      currentStep: progress.currentStep || task.currentStep,
      progress: Number.isFinite(progress.progress) ? progress.progress : task.progress,
      lastLines: progress.lastLines || task.lastLines || [],
      updatedAt: progress.updatedAt || task.updatedAt,
      lastLogAt: progress.lastLogAt || task.lastLogAt,
      errorCode: progress.errorCode || task.errorCode,
      errorMessage: progress.errorMessage || task.errorMessage,
      exitCode: progress.exitCode ?? task.exitCode,
      finishedAt: progress.finishedAt || task.finishedAt,
      logPath: progress.logPath || task.logPath
    }
    updateLogLines.value = updateTask.value.lastLines || []
    updateReconnectHint.value = false
    if (updateTask.value.status === 'running') {
      updateHadRunningTask.value = true
      startUpdatePolling()
      return
    }
    stopUpdatePolling()
    if (updateHadRunningTask.value) {
      if (updateTask.value.status === 'success') ui.show('更新完成')
      if (updateTask.value.status === 'failed') ui.error(updateTask.value.errorCode === 'stale_task' ? '更新进程已经退出，任务状态已自动修复。' : '更新失败，请查看日志')
      updateHadRunningTask.value = false
    }
  } catch (exc) {
    if (updateHadRunningTask.value || taskIsRunning.value) {
      updateReconnectHint.value = true
      startUpdatePolling()
      return
    }
    if (!options.silent) {
      updateError.value = exc instanceof Error ? exc.message : '更新任务状态加载失败'
      ui.error('更新任务状态加载失败')
    }
  }
}

async function openVersionModal() {
  versionModalOpen.value = true
  versionDebugOpen.value = false
  await loadUpdateStatus()
  await loadUpdateTask({ silent: true })
  if (taskIsRunning.value) startUpdatePolling()
}

function closeVersionModal() {
  versionModalOpen.value = false
  stopUpdatePolling()
}

async function checkRelease() {
  updateLoading.value = true
  updateError.value = ''
  localDebugLogs.value = []
  try {
    updateStatus.value = await adminApi.checkUpdate()
    if (updateStatus.value.errorCode) {
      ui.error(detectionStatusLabel.value)
    } else {
      ui.show('版本检测完成')
    }
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '检查更新失败'
    localDebugLogs.value = [`前端请求 /api/admin/update/check 失败: ${updateError.value}`]
    ui.error('检查更新失败')
  } finally {
    updateLoading.value = false
  }
}

async function runReleaseUpdate() {
  if (!updateStatus.value?.updateSupported) {
    updateError.value = updateSupportMessage.value || '当前环境不支持一键更新，请在 Linux 服务器执行'
    ui.error(updateError.value)
    return
  }
  updateActionLoading.value = true
  updateError.value = ''
  try {
    updateStatus.value = await adminApi.runUpdate(latestTag.value)
    if (updateStatus.value.task) updateTask.value = updateStatus.value.task
    const runErrorCode = updateStatus.value.updateErrorCode || updateStatus.value.run?.errorCode || updateStatus.value.task?.errorCode || ''
    if (
      updateStatus.value.status === 'unsupported' ||
      updateStatus.value.status === 'unsupported_platform' ||
      updateStatus.value.status === 'failed' ||
      runErrorCode === 'sudo_password_required'
    ) {
      updateError.value =
        runErrorCode === 'sudo_password_required'
          ? '当前服务器未配置免密码 sudo，无法通过 WebUI 一键更新。'
          : updateStatus.value.message || updateStatus.value.updateErrorMessage || '当前环境不支持一键更新，请在 Linux 服务器执行'
      ui.error(updateError.value)
    } else {
      updateHadRunningTask.value = true
      await loadUpdateTask({ silent: true })
      startUpdatePolling()
      ui.show('更新任务已启动')
    }
  } catch (exc) {
    updateError.value = exc instanceof Error ? exc.message : '启动更新失败'
    localDebugLogs.value = [`前端请求 /api/admin/update/run 失败: ${updateError.value}`]
    ui.error('启动更新失败')
  } finally {
    updateActionLoading.value = false
  }
}

function refreshAdminPage() {
  window.location.reload()
}

onMounted(loadUpdateStatus)
onBeforeUnmount(stopUpdatePolling)
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
            @click="openVersionModal"
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
          <button type="button" class="admin-btn admin-btn-ghost" @click="closeVersionModal">关闭</button>
        </div>

        <div class="mt-5 grid gap-3">
          <div class="version-info-row">
            <span>当前版本</span>
            <b>{{ currentVersion }}</b>
          </div>
          <div class="version-info-row">
            <span>最新版本</span>
            <b>{{ latestVersionLabel }}</b>
          </div>
          <div class="version-info-row">
            <span>发布时间</span>
            <b>{{ updateStatus?.publishedAt || updateStatus?.latest?.publishedAt || '-' }}</b>
          </div>
          <div class="version-info-row">
            <span>检测状态</span>
            <b>{{ detectionStatusLabel }}</b>
          </div>
          <div class="version-info-row">
            <span>运行平台</span>
            <b>{{ updateStatus?.platform || '-' }}</b>
          </div>
        </div>

        <div v-if="shouldShowDebugToggle" class="mt-4">
          <button type="button" class="admin-btn admin-btn-ghost" @click="versionDebugOpen = !versionDebugOpen">
            {{ versionDebugOpen ? '隐藏日志' : '查看日志' }}
          </button>
          <pre
            v-if="versionDebugOpen"
            class="mt-3 max-h-64 overflow-auto rounded-xl border border-slate-200 bg-slate-950 p-4 text-xs leading-5 text-slate-100"
          >{{ versionDebugLogs.join('\n') }}</pre>
        </div>

        <div class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <h3 class="text-sm font-black text-slate-950">更新摘要</h3>
          <p class="mt-2 max-h-56 overflow-auto whitespace-pre-wrap text-sm leading-6 text-slate-600">
            {{ updateStatus?.notes || updateStatus?.latest?.body || updateStatus?.latest?.name || '暂无 release notes。' }}
          </p>
        </div>

        <div v-if="showTaskProgress" class="mt-4 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h3 class="text-sm font-black text-slate-950">更新进度</h3>
            <span
              class="rounded-full px-3 py-1 text-xs font-black"
              :class="{
                'bg-emerald-100 text-emerald-700': activeUpdateTask?.status === 'success',
                'bg-red-100 text-red-700': activeUpdateTask?.status === 'failed',
                'bg-slate-900 text-white': activeUpdateTask?.status === 'running',
                'bg-slate-100 text-slate-600': !activeUpdateTask || activeUpdateTask.status === 'idle'
              }"
            >
              {{ taskStatusLabel }}
            </span>
          </div>

          <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              class="h-full rounded-full transition-all"
              :class="activeUpdateTask?.status === 'failed' ? 'bg-red-500' : 'bg-emerald-500'"
              :style="{ width: `${taskProgress || (taskIsRunning ? 12 : 0)}%` }"
            ></div>
          </div>

          <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <p><b>当前步骤：</b>{{ taskStepLabel }}</p>
            <p><b>进度：</b>{{ taskProgress ? `${taskProgress}%` : (taskIsRunning ? '运行中' : '-') }}</p>
            <p><b>开始时间：</b>{{ activeUpdateTask?.startedAt || '-' }}</p>
            <p><b>结束时间：</b>{{ activeUpdateTask?.finishedAt || '-' }}</p>
            <p><b>PID：</b>{{ activeUpdateTask?.pid || '-' }}</p>
            <p><b>exitCode：</b>{{ activeUpdateTask?.exitCode ?? '-' }}</p>
            <p class="sm:col-span-2"><b>日志文件：</b>{{ activeUpdateTask?.logPath || '-' }}</p>
            <p v-if="activeUpdateTask?.errorMessage" class="sm:col-span-2 text-red-600">
              <b>错误：</b>{{ activeUpdateTask.errorMessage }}
            </p>
          </div>

          <p v-if="updateReconnectHint" class="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700">
            后端重启中，正在重连...
          </p>
          <p v-if="taskPossiblyStuck" class="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700">
            最近 5 分钟没有新的日志输出，任务可能已卡住，请查看日志文件。
          </p>

          <pre class="mt-3 max-h-72 overflow-auto rounded-xl bg-slate-950 p-4 text-xs leading-5 text-slate-100">{{ displayedUpdateLogs.length ? displayedUpdateLogs.join('\n') : '暂无更新日志。' }}</pre>

          <div v-if="activeUpdateTask?.status === 'success'" class="mt-4 flex flex-wrap justify-end gap-2">
            <button type="button" class="admin-btn admin-btn-ghost" @click="closeVersionModal">关闭</button>
            <button type="button" class="admin-btn admin-btn-primary" @click="refreshAdminPage">刷新后台</button>
          </div>
        </div>

        <p v-if="updateStatus && !updateStatus.updateSupported" class="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
          {{ updateSupportMessage }}
        </p>

        <div class="mt-5 flex flex-wrap justify-end gap-2">
          <button class="admin-btn admin-btn-ghost" type="button" :disabled="updateLoading" @click="checkRelease">
            {{ updateLoading ? '检测中...' : '重新检测' }}
          </button>
          <button
            class="admin-btn admin-btn-primary"
            type="button"
            :disabled="!canRunUpdate || updateActionLoading || taskIsRunning"
            @click="runReleaseUpdate"
          >
            {{ updateActionLoading ? '启动中...' : taskIsRunning ? '更新中' : '立即更新' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
