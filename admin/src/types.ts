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
  updatedAt?: string
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

export interface AuditLogItem {
  id: string
  time: string
  actor: string
  action: string
  resource: string
  target: string
  result: 'success' | 'failed'
  message: string
  ip?: string
  detail?: Record<string, unknown>
}

export interface AuditLogResponse {
  items: AuditLogItem[]
  total: number
  limit: number
  offset: number
}

export interface BackupItem {
  name: string
  createdAt: string
  size: number
}
