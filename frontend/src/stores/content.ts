import { defineStore } from 'pinia'
import { contentApi } from '@/api/content'
import type { ContentItem } from '@/types'

export const useContentStore = defineStore('content', {
  state: () => ({
    posts: [] as ContentItem[],
    moments: [] as ContentItem[],
    chatters: [] as ContentItem[],
    loading: false,
    error: ''
  }),
  actions: {
    async load(section: 'posts' | 'moments' | 'chatters') {
      this.loading = true
      this.error = ''
      try {
        this[section] = await contentApi.list(section)
      } catch (error) {
        this.error = error instanceof Error ? error.message : '加载失败'
      } finally {
        this.loading = false
      }
    }
  }
})
