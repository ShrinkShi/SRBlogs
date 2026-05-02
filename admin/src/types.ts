export interface ContentMeta {
  title: string
  date: string
  tags: string[]
  draft: boolean
  cover?: string
  summary?: string
}
export interface ContentItem {
  slug: string
  meta: ContentMeta
  content: string
}
export interface Stats { posts: number; moments: number; chatters: number; photos: number }

export interface CommentItem {
  id: string
  author: string
  email?: string
  content: string
  created_at: string
}

export interface CommentIndexItem {
  resource: 'posts' | 'moments' | 'chatters'
  slug: string
  count: number
  updatedAt: string
  title: string
}
