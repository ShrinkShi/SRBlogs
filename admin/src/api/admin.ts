import { http } from './http'
import type { ContentItem, Stats } from '@/types'

export const adminApi = {
  login: async (username: string, password: string) => {
    const { data } = await http.post<{ access_token: string }>('/auth/login', { username, password })
    return data
  },
  stats: async () => {
    const { data } = await http.get<Stats>('/dashboard/stats')
    return data
  },
  list: async (section: 'posts' | 'moments' | 'chatters') => {
    const { data } = await http.get<ContentItem[]>(`/${section}`, { params: { include_drafts: true } })
    return data
  },
  detail: async (section: 'posts' | 'moments' | 'chatters', slug: string) => {
    const { data } = await http.get<ContentItem>(`/${section}/${slug}`)
    return data
  },
  save: async (section: 'posts' | 'moments' | 'chatters', payload: ContentItem, oldSlug?: string) => {
    const method = oldSlug ? http.put : http.post
    const url = oldSlug ? `/${section}/${oldSlug}` : `/${section}`
    const { data } = await method<ContentItem>(url, payload)
    return data
  },
  remove: async (section: 'posts' | 'moments' | 'chatters', slug: string) => {
    const { data } = await http.delete(`/${section}/${slug}`)
    return data
  },
  json: async <T>(path: string) => {
    const { data } = await http.get<T>(path)
    return data
  },
  putJson: async (path: string, dataValue: unknown) => {
    const { data } = await http.put(path, { data: dataValue })
    return data
  },
  upload: async (file: File, onProgress?: (percent: number) => void) => {
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post<{ url: string; filename: string; size: number }>('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) onProgress(Math.round((event.loaded / event.total) * 100))
      }
    })
    return data
  },
  chat: async (messages: { role: string; content: string }[], provider = 'a') => {
    const { data } = await http.post('/chat', { provider, messages, stream: false })
    return data
  }
}
