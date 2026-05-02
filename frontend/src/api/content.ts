import { http } from './http'
import type { ArchiveResponse, CommentItem, ContentItem, DiscoveryType, SearchResponse, TagItem } from '@/types'

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
  comments: async (resource: 'posts' | 'moments' | 'chatters', slug: string) => {
    const { data } = await http.get<CommentItem[]>(`/comments/${resource}/${slug}`)
    return data
  },
  createComment: async (resource: 'posts' | 'moments' | 'chatters', slug: string, payload: { author: string; email?: string; content: string }) => {
    const { data } = await http.post<CommentItem>(`/comments/${resource}/${slug}`, payload)
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
  }
}
