<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '@/api/admin'
import GlassCard from '@/components/GlassCard.vue'
import type { AuditLogItem } from '@/types'

const items = ref<AuditLogItem[]>([])
const total = ref(0)
const limit = 30
const offset = ref(0)
const action = ref('')
const resource = ref('')
const q = ref('')
const loading = ref(false)
const error = ref('')

const canLoadMore = computed(() => offset.value + items.value.length < total.value)

async function load(reset = true) {
  loading.value = true
  error.value = ''
  if (reset) offset.value = 0
  try {
    const data = await adminApi.auditLogs({ limit, offset: offset.value, action: action.value, resource: resource.value, q: q.value })
    items.value = reset ? data.items : [...items.value, ...data.items]
    total.value = data.total
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '审计日志加载失败'
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  offset.value += limit
  await load(false)
}

onMounted(() => load())
</script>

<template>
  <section class="grid gap-5">
    <GlassCard>
      <div class="relative z-[1] flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-4xl font-black text-white">审计日志</h1>
          <p class="mt-2 text-white/50">记录后台高风险操作、登录、上传、备份恢复和数据修改。</p>
        </div>
        <button type="button" :disabled="loading" class="admin-btn admin-btn-ghost" @click="load()">{{ loading ? '加载中...' : '刷新' }}</button>
      </div>
    </GlassCard>

    <GlassCard>
      <div class="relative z-[1] grid gap-3 lg:grid-cols-[1fr_180px_180px_auto]">
        <input v-model="q" aria-label="审计关键词" class="admin-input" placeholder="搜索操作者、动作、资源、目标或说明" @keyup.enter="load()" />
        <input v-model="action" aria-label="动作筛选" class="admin-input" placeholder="action，例如 post.create" @keyup.enter="load()" />
        <input v-model="resource" aria-label="资源筛选" class="admin-input" placeholder="resource，例如 posts" @keyup.enter="load()" />
        <button type="button" :disabled="loading" class="admin-btn admin-btn-primary" @click="load()">筛选</button>
      </div>
    </GlassCard>

    <GlassCard v-if="loading && !items.length"><p class="relative z-[1] text-white/60">审计日志加载中...</p></GlassCard>
    <GlassCard v-else-if="error">
      <p class="relative z-[1] text-red-200/85">{{ error }}</p>
      <button type="button" class="admin-btn admin-btn-ghost relative z-[1] mt-4" @click="load()">重试</button>
    </GlassCard>
    <GlassCard v-else-if="!items.length"><p class="relative z-[1] text-white/60">暂无审计日志。</p></GlassCard>

    <div v-else class="grid gap-3">
      <GlassCard v-for="item in items" :key="item.id">
        <div class="relative z-[1] grid gap-3 lg:grid-cols-[170px_1fr_auto]">
          <div class="text-sm text-white/45">{{ item.time }}</div>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded-full border border-white/10 px-2 py-1 text-xs text-white/60">{{ item.actor || 'system' }}</span>
              <b class="break-all text-white">{{ item.action }}</b>
              <span class="rounded-full bg-white/8 px-2 py-1 font-mono text-xs text-cyan-100/70">{{ item.resource || '-' }}</span>
            </div>
            <p class="mt-2 break-all font-mono text-xs text-white/45">{{ item.target || '-' }}</p>
            <p class="mt-2 break-words text-sm text-white/68">{{ item.message }}</p>
          </div>
          <span class="h-fit rounded-full px-3 py-1 text-xs font-bold" :class="item.result === 'failed' ? 'bg-red-300/15 text-red-100' : 'bg-emerald-300/15 text-emerald-100'">
            {{ item.result }}
          </span>
        </div>
      </GlassCard>
      <button v-if="canLoadMore" type="button" :disabled="loading" class="admin-btn admin-btn-ghost justify-self-center" @click="loadMore">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </section>
</template>
