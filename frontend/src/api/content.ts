import { http } from './http'
import type { ArchiveResponse, CommentItem, ContentItem, DiscoveryType, SearchResponse, TagItem } from '@/types'

export type CommentResource = 'posts' | 'moments' | 'chatters' | 'music' | 'photos'
export type VisitorUser = { provider: 'github' | 'qq'; id: string; login?: string; name?: string; avatar?: string; html_url?: string }

export const contentApi = {
  list: async (section: 'posts' | 'moments' | 'chatters') => {
    const { data } = await http.get<ContentItem[]>(`/${section}`)
    return data
  },
  detail: async (section: 'posts' | 'moments' | 'chatters', slug: string) => {
    const { data } = await http.get<ContentItem>(`/${section}/${slug}`)
    return data
  },
  json: async <T>(path: string) => {
    const { data } = await http.get<T>(path)
    return data
  },
  about: async () => {
    const { data } = await http.get<{ content: string }>('/about')
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
