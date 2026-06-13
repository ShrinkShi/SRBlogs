<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { contentApi, type UpdateProgress, type UpdateStatus } from '@/api/content'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const status = ref<UpdateStatus | null>(null)
const progress = ref<UpdateProgress | null>(null)
const loading = ref(false)
const checking = ref(false)
const running = ref(false)
const error = ref('')
const showLogs = ref(false)
let timer: number | undefined
let notifiedTaskId = ''

function displayVersion(value = '') {
  const trimmed = value.trim()
  if (!trimmed || trimmed === 'unknown') return '未知'
  return trimmed.startsWith('v') || trimmed.startsWith('V') ? trimmed : `v${trimmed}`
}

const currentVersion = computed(() => displayVersion(status.value?.currentVersion || ''))
const latestVersion = computed(() => status.value?.latestVersion ? displayVersion(status.value.latestVersion) : (status.value?.errorCode ? '检测失败' : '未知'))
const hasUpdate = computed(() => status.value?.hasUpdate || status.value?.updateAvailable || false)
const taskStatus = computed(() => progress.value?.status || status.value?.task?.status || 'idle')
const isTaskRunning = computed(() => taskStatus.value === 'running')
const canRunUpdate = computed(() => Boolean(status.value?.updateSupported && hasUpdate.value && !isTaskRunning.value))
const taskProgress = computed(() => {
  const value = Number(progress.value?.progress ?? status.value?.task?.progress ?? 0)
  return Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0))
})
const currentStep = computed(() => progress.value?.currentStep || status.value?.task?.currentStep || status.value?.message || '等待操作')
const lastLines = computed(() => progress.value?.lastLines || status.value?.task?.lastLines || [])
const exitCode = computed(() => progress.value?.exitCode ?? status.value?.task?.exitCode ?? null)
const statusText = computed(() => {
  if (isTaskRunning.value) return '更新中'
  if (taskStatus.value === 'success') return '更新完成'
  if (taskStatus.value === 'failed') return '更新失败'
  if (status.value?.errorCode) return errorMessage(status.value.errorCode, status.value.errorMessage)
  if (!status.value?.updateSupported) return '当前环境不支持一键更新'
  if (hasUpdate.value) return '检测到新版本'
  return '已经是最新版本'
})

function errorMessage(code = '', message = '') {
  const map: Record<string, string> = {
    sudo_password_required: '当前服务器未配置免密码 sudo，无法通过 WebUI 一键更新。',
    stale_task: '更新进程已经退出，任务状态已自动修复。',
    unsupported_platform: '当前环境不支持一键更新，请在 Linux 服务器执行。',
    updater_service_missing: '当前环境未安装受限 updater，请执行 deploy/install-updater.sh。',
    updater_service_unavailable: 'updater service 当前不可用，请检查 systemd 状态。',
    updater_request_write_failed: '无法写入 updater 请求文件，请检查 /var/lib/srblogs/update 权限。',
    update_script_missing: '当前环境未安装受限 updater，请执行 deploy/install-updater.sh。',
    github_release_not_found: '未找到 GitHub Release。',
    github_network_error: '无法访问 GitHub。',
    github_timeout: '请求 GitHub 超时。',
    github_rate_limited: 'GitHub API 限流。'
  }
  return map[code] || message || '检测状态未知'
}

function stopPolling() {
  if (timer) window.clearInterval(timer)
  timer = undefined
}

async function loadStatus(silent = false) {
  if (!silent) loading.value = true
  error.value = ''
  try {
    status.value = await contentApi.updateStatus()
    if (status.value.task?.status === 'running') startPolling()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '版本状态读取失败'
  } finally {
    loading.value = false
  }
}

async function checkUpdate() {
  checking.value = true
  error.value = ''
  try {
    status.value = await contentApi.checkUpdate()
    ui.showToast(status.value.hasUpdate ? '检测到新版本' : '已经是最新版本', status.value.hasUpdate ? 'info' : 'success')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '检测失败'
    ui.showToast(error.value, 'error')
  } finally {
    checking.value = false
  }
}

async function pollProgress() {
  try {
    progress.value = await contentApi.updateProgress(100)
    if (progress.value.status === 'running') return
    stopPolling()
    const taskId = progress.value.taskId || ''
    if (taskId && notifiedTaskId !== taskId) {
      notifiedTaskId = taskId
      ui.showToast(progress.value.status === 'success' ? '更新完成，请刷新后台。' : '更新失败，请查看日志。', progress.value.status === 'success' ? 'success' : 'error')
    }
    await loadStatus(true)
  } catch {
    error.value = '后端重启中，正在重连...'
  }
}

function startPolling() {
  if (timer) return
  showLogs.value = true
  pollProgress()
  timer = window.setInterval(pollProgress, 2000)
}

function reloadPage() {
  window.location.reload()
}

async function runUpdate() {
  if (!canRunUpdate.value) return
  running.value = true
  error.value = ''
  try {
    status.value = await contentApi.runUpdate(status.value?.latestVersion || '')
    if (status.value.errorCode === 'sudo_password_required') {
      error.value = errorMessage(status.value.errorCode, status.value.errorMessage)
      ui.showToast(error.value, 'error')
      return
    }
    if (status.value.task?.status === 'running' || status.value.status === 'running') {
      startPolling()
      ui.showToast('更新任务已启动', 'info')
    } else if (status.value.errorCode || status.value.updateErrorCode) {
      error.value = errorMessage(status.value.errorCode || status.value.updateErrorCode, status.value.errorMessage || status.value.updateErrorMessage)
      ui.showToast(error.value, 'error')
    }
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '更新启动失败'
    ui.showToast(error.value, 'error')
  } finally {
    running.value = false
  }
}

onMounted(loadStatus)
onBeforeUnmount(stopPolling)
</script>

<template>
  <section class="front-update-panel">
    <header class="front-update-summary">
      <div>
        <span>当前版本</span>
        <strong>{{ currentVersion }}</strong>
      </div>
      <div>
        <span>最新版本</span>
        <strong>{{ latestVersion }}</strong>
      </div>
      <div>
        <span>检测状态</span>
        <strong>{{ statusText }}</strong>
      </div>
    </header>

    <div v-if="loading" class="front-update-empty">正在读取版本状态...</div>
    <div v-else class="front-update-body">
      <p v-if="status?.publishedAt" class="front-update-muted">发布时间：{{ status.publishedAt }}</p>
      <a v-if="status?.releaseUrl" :href="status.releaseUrl" target="_blank" rel="noreferrer" class="front-update-link">查看 GitHub Release</a>
      <pre v-if="status?.notes" class="front-update-notes">{{ status.notes }}</pre>
      <p v-if="error" class="front-update-error">{{ error }}</p>

      <section v-if="isTaskRunning || progress || status?.task" class="front-update-progress">
        <div class="front-update-progress-head">
          <b>更新进度</b>
          <span>{{ taskProgress }}%</span>
        </div>
        <div class="front-update-bar"><i :style="{ width: `${taskProgress}%` }"></i></div>
        <dl>
          <div><dt>状态</dt><dd>{{ taskStatus }}</dd></div>
          <div><dt>步骤</dt><dd>{{ currentStep }}</dd></div>
          <div><dt>退出码</dt><dd>{{ exitCode ?? '-' }}</dd></div>
        </dl>
        <button type="button" class="front-update-small-btn" @click="showLogs = !showLogs">{{ showLogs ? '收起日志' : '查看日志' }}</button>
        <pre v-if="showLogs" class="front-update-log">{{ lastLines.join('\n') || '暂无日志。' }}</pre>
      </section>
    </div>

    <footer class="front-update-actions">
      <button type="button" class="front-btn front-btn-white" :disabled="checking" @click="checkUpdate">{{ checking ? '检测中...' : '重新检测' }}</button>
      <button type="button" class="front-btn front-btn-green" :disabled="running || !canRunUpdate" @click="runUpdate">{{ running || isTaskRunning ? '更新中...' : '立即更新' }}</button>
      <button v-if="taskStatus === 'success'" type="button" class="front-btn front-btn-black" @click="reloadPage">刷新后台</button>
    </footer>
  </section>
</template>

<style scoped>
.front-update-panel {
  display: grid;
  gap: 1rem;
  color: rgba(255, 255, 255, .86);
}
.front-update-summary {
  display: grid;
  gap: .75rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.front-update-summary > div,
.front-update-progress,
.front-update-empty,
.front-update-notes {
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 1.25rem;
  background: #202123;
  padding: .9rem;
}
.front-update-summary span,
.front-update-muted,
.front-update-progress dt {
  color: rgba(255, 255, 255, .48);
  font-size: .78rem;
}
.front-update-summary strong {
  display: block;
  margin-top: .25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 1rem;
  color: white;
}
.front-update-link {
  color: #bbf7d0;
  text-decoration: underline;
  text-underline-offset: .25em;
}
.front-update-notes {
  max-height: 11rem;
  overflow: auto;
  white-space: pre-wrap;
  color: rgba(255, 255, 255, .68);
}
.front-update-error {
  border-radius: 999px;
  background: rgba(239, 68, 68, .18);
  padding: .65rem .9rem;
  color: #fecaca;
  font-weight: 800;
}
.front-update-progress {
  display: grid;
  gap: .75rem;
}
.front-update-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.front-update-bar {
  height: .55rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, .08);
}
.front-update-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #86efac;
  transition: width .25s ease;
}
.front-update-progress dl {
  display: grid;
  gap: .55rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.front-update-progress dd {
  overflow: hidden;
  margin: .1rem 0 0;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(255, 255, 255, .78);
}
.front-update-small-btn {
  justify-self: start;
  border-radius: 999px;
  background: white;
  padding: .45rem .8rem;
  color: black;
  font-weight: 900;
}
.front-update-log {
  max-height: 15rem;
  overflow: auto;
  border-radius: 1rem;
  background: #0d0e0f;
  padding: .9rem;
  color: #d1d5db;
  font-size: .78rem;
  line-height: 1.65;
  white-space: pre-wrap;
}
.front-update-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem;
  justify-content: flex-end;
}
.front-btn {
  border-radius: 999px;
  padding: .68rem 1.1rem;
  font-weight: 900;
}
.front-btn:disabled {
  cursor: not-allowed;
  opacity: .48;
}
.front-btn-white {
  background: white;
  color: black;
}
.front-btn-green {
  background: #86efac;
  color: black;
}
.front-btn-black {
  background: black;
  color: white;
}
@media (max-width: 720px) {
  .front-update-summary,
  .front-update-progress dl {
    grid-template-columns: 1fr;
  }
}
</style>
