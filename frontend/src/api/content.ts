import { http } from './http'
import type { AboutPageConfig, ArchiveResponse, CommentItem, ContentItem, DiscoveryType, GithubSummary, SearchResponse, TagItem } from '@/types'

export type CommentResource = 'posts' | 'moments' | 'chatters' | 'music' | 'photos'
export type VisitorUser = { provider: 'github' | 'qq'; id: string; login?: string; name?: string; avatar?: string; html_url?: string }
export type AdminUser = { username: string; role: 'admin' }
export type InstallStatus = { installed: boolean; needsInstall: boolean; missingItems: string[] }
export type InstallPayload = {
  siteTitle: string
  author: string
  adminUsername: string
  adminPassword: string
  publicBaseUrl: string
  corsOrigins: string
  siteStartTime?: string
}

export const contentApi = {
  list: async (section: 'posts' | 'moments' | 'chatters') => {
    const { data } = await http.get<ContentItem[]>(`/${section}`)
    return data
  },
  detail: async (section: 'posts' | 'moments' | 'chatters', slug: string, includeDrafts = false) => {
    const { data } = await http.get<ContentItem>(`/${section}/${slug}`, includeDrafts ? { params: { include_drafts: true } } : undefined)
    return data
  },
  json: async <T>(path: string) => {
    const { data } = await http.get<T>(path)
    return data
  },
  publicSettings: async <T>() => {
    const { data } = await http.get<T>('/settings/public', {
      params: { _t: Date.now() },
      headers: {
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache'
      }
    })
    return data
  },
  installStatus: async () => {
    const { data } = await http.get<InstallStatus>('/install/status')
    return data
  },
  install: async (payload: InstallPayload) => {
    const { data } = await http.post<{ ok: boolean; installed: boolean; restartRequired: boolean; siteStartTime: string; loginUrl: string }>('/install', payload)
    return data
  },
  about: async () => {
    const { data } = await http.get<{ content: string }>('/about')
    return data
  },
  aboutPage: async () => {
    const { data } = await http.get<AboutPageConfig>('/about-page')
    return data
  },
  githubSummary: async (username: string) => {
    const { data } = await http.get<GithubSummary>('/github/summary', { params: { username } })
    return data
  },
  sendContact: async (payload: { name: string; email: string; message: string }) => {
    const { data } = await http.post<{ ok: boolean; message: string }>('/contact/send', payload)
    return data
  },
  comments: async (resource: CommentResource, slug: string) => {
    const { data } = await http.get<CommentItem[]>(`/comments/${resource}/${slug}`)
    return data
  },
  createComment: async (resource: CommentResource, slug: string, payload: { author?: string; email?: string; content: string }) => {
    const { data } = await http.post<CommentItem>(`/comments/${resource}/${slug}`, payload)
    return data
  },
  deleteComment: async (resource: CommentResource, slug: string, commentId: string) => {
    const { data } = await http.delete(`/comments/${resource}/${slug}/${commentId}`)
    return data
  },
  deleteContent: async (section: 'posts' | 'moments' | 'chatters', slug: string) => {
    const { data } = await http.delete(`/${section}/${slug}`)
    return data
  },
  saveContent: async (section: 'posts' | 'moments' | 'chatters', payload: ContentItem, oldSlug?: string) => {
    const method = oldSlug ? http.put : http.post
    const url = oldSlug ? `/${section}/${oldSlug}` : `/${section}`
    const { data } = await method<ContentItem>(url, payload)
    return data
  },
  githubMe: async () => {
    const { data } = await http.get<{ configured: boolean; user: null | { login: string; name?: string; avatar?: string; html_url?: string } }>('/auth/github/me')
    return data
  },
  githubLogout: async () => {
    const { data } = await http.post<{ ok: boolean }>('/auth/github/logout')
    return data
  },
  visitorMe: async () => {
    const { data } = await http.get<{ configured: { github: boolean; qq: boolean }; user: null | VisitorUser }>('/auth/visitor/me')
    return data
  },
  visitorLogout: async () => {
    const { data } = await http.post<{ ok: boolean }>('/auth/visitor/logout')
    return data
  },
  adminLogin: async (username: string, password: string) => {
    const { data } = await http.post<{ access_token: string; token_type?: string }>('/auth/login', { username, password })
    return data
  },
  adminMe: async () => {
    const { data } = await http.get<AdminUser>('/auth/admin/me')
    return data
  },
  adminJson: async <T>(path: string) => {
    const { data } = await http.get<T>(path)
    return data
  },
  adminPutJson: async <T = unknown>(path: string, dataValue: unknown) => {
    const { data } = await http.put<T>(path, { data: dataValue })
    return data
  },
  upload: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post<{ url: string; filename: string; size: number }>('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  },
  search: async (params: { q?: string; type?: DiscoveryType; tag?: string; limit?: number; offset?: number }) => {
    const { data } = await http.get<SearchResponse>('/search', { params })
    return data
  },
  tags: async () => {
    const { data } = await http.get<TagItem[]>('/tags')
    return data
  },
  archive: async () => {
    const { data } = await http.get<ArchiveResponse>('/archive')
    return data
  },
  updateMusicLike: async (songId: string, liked: boolean) => {
    const { data } = await http.post<{ id: string; likes: number; liked: boolean }>(`/music/${encodeURIComponent(songId)}/likes`, { data: { liked } })
    return data
  }
}
