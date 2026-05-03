import { http } from './http'
import type { AuditLogResponse, BackupItem, CommentIndexItem, CommentItem, ContentItem, Stats } from '@/types'

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
    const { data } = await http.get<ContentItem>(`/${section}/${slug}`, { params: { include_drafts: true } })
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
  comments: async (resource: 'posts' | 'moments' | 'chatters' | 'music' | 'photos', slug: string) => {
    const { data } = await http.get<CommentItem[]>(`/comments/${resource}/${slug}`)
    return data
  },
  commentsIndex: async () => {
    const { data } = await http.get<CommentIndexItem[]>('/admin/comments/index')
    return data
  },
  deleteComment: async (resource: 'posts' | 'moments' | 'chatters' | 'music' | 'photos', slug: string, commentId: string) => {
    const { data } = await http.delete(`/comments/${resource}/${slug}/${commentId}`)
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
  },
  auditLogs: async (params: { limit?: number; offset?: number; action?: string; resource?: string; q?: string }) => {
    const { data } = await http.get<AuditLogResponse>('/admin/audit/logs', { params })
    return data
  },
  backups: async () => {
    const { data } = await http.get<BackupItem[]>('/admin/backups')
    return data
  },
  createBackup: async () => {
    const { data } = await http.post<BackupItem>('/admin/backups')
    return data
  },
  restoreBackup: async (name: string) => {
    const { data } = await http.post<{ ok: boolean; restored: string; preRestoreBackup: string }>(`/admin/backups/${encodeURIComponent(name)}/restore`)
    return data
  },
  downloadBackup: async (name: string) => {
    const { data } = await http.get<Blob>(`/admin/backups/${encodeURIComponent(name)}/download`, { responseType: 'blob' })
    return data
  },
  exportData: async () => {
    const { data } = await http.get<Blob>('/admin/export', { responseType: 'blob' })
    return data
  },
  importData: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post<{ ok: boolean; restored: string; preRestoreBackup: string }>('/admin/import', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  }
}
