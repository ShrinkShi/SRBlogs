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
  tags?: string[]
}

export interface ProjectItem {
  name: string
  url?: string
  description: string
  tags?: string[]
  cover?: string
  status?: string
  repo?: string
}

export interface MusicItem {
  title: string
  artist: string
  url?: string
  cover?: string
  id?: string
  sort?: number
  lyrics?: string
  lyricUrl?: string
}

export interface ThemeTokens {
  bgPage?: string
  bgCard?: string
  bgCardElevated?: string
  borderGlass?: string
  textPrimary?: string
  textSecondary?: string
  accent?: string
  accentSoft?: string
  navBg?: string
  homePanelBg?: string
  shadowGlow?: string
}

export interface ThemeConfig {
  mode?: 'day' | 'night'
  fontFamily?: string
  fontScale?: 'small' | 'medium' | 'large'
  day?: ThemeTokens
  night?: ThemeTokens
}

export interface PhotoItem {
  url: string
  title?: string
  description?: string
  date?: string
  tags?: string[]
}

export interface PhotoAlbum {
  title: string
  description?: string
  cover?: string
  date?: string
  tags?: string[]
  photos: PhotoItem[]
}

export interface CommentItem {
  id: string
  author: string
  email?: string
  content: string
  created_at: string
  avatar?: string
  githubLogin?: string
}

export interface SiteSettings {
  siteTitle?: string
  subtitle?: string
  author?: string
  avatar?: string
  description?: string
  socialLinks?: Record<string, string>
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
  themeConfig?: ThemeConfig
  gitalkConfig?: {
    clientID?: string
    repo?: string
    owner?: string
    admin?: string[]
  }
  imageBed?: Record<string, unknown>
  ai?: Record<string, unknown>
  comments?: {
    enabled?: boolean
    requireEmail?: boolean
    maxLength?: number
    showEmail?: boolean
    localEnabled?: boolean
    gitalk?: Record<string, unknown>
  }
  interaction?: {
    clickSoundEnabled?: boolean
    clickSoundVolume?: number
    clickSoundUrl?: string
  }
  githubOAuth?: {
    configured?: boolean
  }
}

export type DiscoveryType = 'all' | 'posts' | 'moments' | 'chatters' | 'projects' | 'photos' | 'friends' | 'music'

export interface SearchResultItem {
  type: Exclude<DiscoveryType, 'all'>
  title: string
  slug?: string
  summary?: string
  url: string
  tags: string[]
  date?: string
  score: number
}

export interface SearchResponse {
  items: SearchResultItem[]
  total: number
  limit: number
  offset: number
}

export interface TagItem {
  tag: string
  count: number
  types: string[]
  latestDate?: string
}

export interface ArchiveItem {
  type: 'posts' | 'moments' | 'chatters'
  title: string
  slug: string
  url: string
  date: string
  tags: string[]
}

export interface ArchiveMonth {
  month: string
  items: ArchiveItem[]
}

export interface ArchiveYear {
  year: string
  months: ArchiveMonth[]
}

export interface ArchiveResponse {
  years: ArchiveYear[]
}
