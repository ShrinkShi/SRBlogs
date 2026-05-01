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

export interface FriendItem {
  name: string
  url: string
  avatar?: string
  description?: string
}

export interface ProjectItem {
  name: string
  url?: string
  description: string
  tags?: string[]
  cover?: string
  status?: string
}

export interface MusicItem {
  title: string
  artist: string
  url?: string
  cover?: string
  id?: string
}

export interface PhotoItem {
  url: string
  title?: string
  description?: string
}

export interface CommentItem {
  id: string
  author: string
  email?: string
  content: string
  created_at: string
}

export interface SiteSettings {
  title?: string
  authorName?: string
  bio?: string
  avatarUrl?: string
  defaultPostCover?: string
  photoWallImage?: string
  bgImages?: string[]
  themeColors?: string[]
  danmakuList?: string[]
  cloudMusicIds?: string[]
  buildDate?: string
  social?: Record<string, string>
  counts?: { photos?: number }
  chatterTitle?: string
  chatterDescription?: string
  theme?: string
  imageBed?: Record<string, unknown>
  ai?: Record<string, unknown>
}
