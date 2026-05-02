import { defineStore } from 'pinia'
import { adminApi } from '@/api/admin'
import type { ContentItem } from '@/types'

export type PendingStatus = 'editing' | 'pending' | 'applied' | 'failed'
export type PendingKind = 'createPost' | 'editPost' | 'deletePost' | 'publishDraft'

export interface PendingOperation {
  id: string
  kind: PendingKind
  section: 'posts' | 'moments' | 'chatters'
  title: string
  slug: string
  oldSlug?: string
  status: PendingStatus
  createdAt: string
  error?: string
  payload?: ContentItem
}

function nowText() {
  return new Date().toLocaleString()
}

function labelFor(kind: PendingKind) {
  return {
    createPost: '文章新建',
    editPost: '文章编辑',
    deletePost: '文章删除',
    publishDraft: '草稿发布'
  }[kind]
}

export const usePendingStore = defineStore('pending', {
  state: () => ({ operations: [] as PendingOperation[] }),
  getters: {
    pendingCount: (state) => state.operations.filter((item) => item.status === 'pending').length,
    label: () => labelFor
  },
  actions: {
    add(operation: Omit<PendingOperation, 'id' | 'status' | 'createdAt'>) {
      const item: PendingOperation = {
        ...operation,
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        status: 'pending',
        createdAt: nowText()
      }
      this.operations.unshift(item)
      return item
    },
    remove(id: string) {
      this.operations = this.operations.filter((item) => item.id !== id)
    },
    async apply(id: string) {
      const item = this.operations.find((operation) => operation.id === id)
      if (!item || item.status !== 'pending') return
      item.error = ''
      try {
        if (item.kind === 'deletePost') {
          await adminApi.remove(item.section, item.slug)
        } else if (item.payload) {
          await adminApi.save(item.section, item.payload, item.oldSlug)
        } else {
          throw new Error('暂存操作缺少 payload')
        }
        item.status = 'applied'
      } catch (exc) {
        item.status = 'failed'
        item.error = exc instanceof Error ? exc.message : '应用暂存操作失败'
      }
    },
    retry(id: string) {
      const item = this.operations.find((operation) => operation.id === id)
      if (item && item.status === 'failed') {
        item.status = 'pending'
        item.error = ''
      }
    }
  }
})
