<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import GlassCard from '@/components/GlassCard.vue'
import type { BackupItem } from '@/types'

const backups = ref<BackupItem[]>([])
const loading = ref(false)
const working = ref('')
const error = ref('')
const success = ref('')

function formatSize(size: number) {
  if (size > 1024 * 1024) return `${(size / 1024 / 1024).toFixed(2)} MB`
  if (size > 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function downloadBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = name
  link.click()
  URL.revokeObjectURL(url)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    backups.value = await adminApi.backups()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '备份列表加载失败'
  } finally {
    loading.value = false
  }
}

async function createBackup() {
  working.value = 'create'
  error.value = ''
  success.value = ''
  try {
    const item = await adminApi.createBackup()
    success.value = `已创建备份：${item.name}`
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '创建备份失败'
  } finally {
    working.value = ''
  }
}

async function exportData() {
  working.value = 'export'
  error.value = ''
  success.value = ''
  try {
    const blob = await adminApi.exportData()
    downloadBlob(blob, `srblogs-export-${Date.now()}.zip`)
    success.value = '已导出当前内容数据。'
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '导出数据失败'
  } finally {
    working.value = ''
  }
}

async function importData(files: FileList | null) {
  if (!files?.length) return
  const message = '导入会覆盖当前 backend/data 内容，系统会先创建导入前备份。确认继续？'
  if (!window.confirm(message)) return
  working.value = 'import'
  error.value = ''
  success.value = ''
  try {
    const result = await adminApi.importData(files[0])
    success.value = `导入完成，恢复前备份：${result.preRestoreBackup}`
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '导入数据失败'
  } finally {
    working.value = ''
  }
}

async function download(item: BackupItem) {
  working.value = `download:${item.name}`
  error.value = ''
  try {
    const blob = await adminApi.downloadBackup(item.name)
    downloadBlob(blob, item.name)
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '下载备份失败'
  } finally {
    working.value = ''
  }
}

async function restore(item: BackupItem) {
  const message = '恢复会覆盖当前 backend/data 内容，系统会先创建恢复前备份。确认继续？'
  if (!window.confirm(message)) return
  working.value = `restore:${item.name}`
  error.value = ''
  success.value = ''
  try {
    const result = await adminApi.restoreBackup(item.name)
    success.value = `已恢复 ${result.restored}，恢复前备份：${result.preRestoreBackup}`
    await load()
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '恢复备份失败'
  } finally {
    working.value = ''
  }
}

onMounted(load)
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1] flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-4xl font-black text-white">备份恢复</h1>
          <p class="mt-2 max-w-3xl text-white/50">手动备份会写入 backend/data/.manual_backups。恢复和导入前会自动创建恢复前备份。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" :disabled="!!working" class="admin-btn admin-btn-primary" @click="createBackup">
            {{ working === 'create' ? '创建中...' : '创建手动备份' }}
          </button>
          <button type="button" :disabled="!!working" class="admin-btn admin-btn-ghost" @click="exportData">
            {{ working === 'export' ? '导出中...' : '导出数据' }}
          </button>
          <label class="admin-btn admin-btn-ghost cursor-pointer" :class="working ? 'pointer-events-none opacity-50' : ''">
            {{ working === 'import' ? '导入中...' : '导入 zip' }}
            <input type="file" accept=".zip,application/zip" class="hidden" @change="importData(($event.target as HTMLInputElement).files)" />
          </label>
        </div>
      </div>
      <p v-if="success" class="relative z-[1] mt-4 text-sm text-emerald-200/85">{{ success }}</p>
      <p v-if="error" class="relative z-[1] mt-4 text-sm text-red-200/85">{{ error }}</p>
    </GlassCard>

    <GlassCard v-if="loading"><p class="relative z-[1] text-white/60">备份列表加载中...</p></GlassCard>
    <GlassCard v-else-if="!backups.length">
      <p class="relative z-[1] text-white/60">暂无手动备份。</p>
      <button type="button" class="admin-btn admin-btn-ghost relative z-[1] mt-4" @click="load">刷新</button>
    </GlassCard>

    <div v-else class="grid gap-3">
      <GlassCard v-for="item in backups" :key="item.name">
        <div class="relative z-[1] grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
          <div class="min-w-0">
            <b class="break-all font-mono text-white">{{ item.name }}</b>
            <p class="mt-2 text-sm text-white/48">{{ item.createdAt }} · {{ formatSize(item.size) }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button type="button" :disabled="!!working" class="admin-btn admin-btn-ghost" @click="download(item)">
              {{ working === `download:${item.name}` ? '下载中...' : '下载' }}
            </button>
            <button type="button" :disabled="!!working" class="rounded-2xl border border-red-200/25 px-5 py-3 font-bold text-red-100 hover:bg-red-300/10 disabled:opacity-50" @click="restore(item)">
              {{ working === `restore:${item.name}` ? '恢复中...' : '恢复' }}
            </button>
          </div>
        </div>
      </GlassCard>
    </div>
  </section>
</template>
