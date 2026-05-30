export interface ContentMeta {
  title: string
  date: string
  tags: string[]
  draft: boolean
  cover?: string
  summary?: string
  images?: string[]
  location?: string
  view_count?: number
  like_count?: number
  comment_count?: number
  share_count?: number
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
  likes?: number
}

export interface ThemeTokens {
  bgImage?: string
  bgImages?: Array<string | { url: string; name?: string; enabled?: boolean }>
  activeBgIndex?: number
  slideshowEnabled?: boolean
  slideshowInterval?: number
  slideshowEffect?: 'fade' | 'soft-blur' | 'none' | string
  overlayColor?: string
  overlayOpacity?: number
  pageBg?: string
  cardBg?: string
  cardOpacity?: number
  bgPage?: string
  bgCard?: string
  bgCardElevated?: string
  border?: string
  borderGlass?: string
  textPrimary?: string
  textSecondary?: string
  accent?: string
  accentHover?: string
  accentSoft?: string
  navBg?: string
  homePanelBg?: string
  shadow?: string
  shadowGlow?: string
  fontFamily?: string
  fontSizeBase?: number
  titleScale?: number
  radius?: number
  blur?: number
}

export interface ThemePackage {
  id: string
  name: string
  description?: string
  version?: number
  author?: string
  createdAt?: string
  updatedAt?: string
  modes?: {
    day?: ThemeTokens
    night?: ThemeTokens
  }
  componentTheme?: Record<string, ComponentThemeItem>
  pageLayouts?: Record<string, unknown>
  layout?: {
    pagePadding?: {
      desktop?: number
      tablet?: number
      mobile?: number
    }
  }
}

export interface ThemeConfig {
  mode?: 'day' | 'night'
  activeTheme?: string
  backgroundSlideshowEnabled?: boolean
  themePackages?: Record<string, ThemePackage>
  fontFamily?: string
  fontScale?: 'small' | 'medium' | 'large'
  day?: ThemeTokens
  night?: ThemeTokens
  opacity?: {
    toolboxSettingsPanel?: number
    toolboxSearchPanel?: number
    toolboxCalculatorPanel?: number
    homeCard?: number
    homeCarousel?: number
    contentCard?: number
    photoCard?: number
    musicPanel?: number
    messageBoard?: number
    navBar?: number
  }
  layout?: {
    pagePadding?: {
      desktop?: number
      tablet?: number
      mobile?: number
    }
  }
  componentTheme?: Record<string, ComponentThemeItem>
}

export interface ComponentThemeItem {
  label?: string
  day?: ComponentThemeMode
  night?: ComponentThemeMode
  opacity?: number
  size?: 'small' | 'medium' | 'large'
  fontFamily?: string
  fontSize?: number
  textColor?: string
  textAlign?: 'left' | 'center' | 'right'
  fontWeight?: string
  fontStyle?: string
}

export interface ComponentThemeMode {
  bg?: string
  text?: string
  accent?: string
  border?: string
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
  provider?: 'github' | 'qq' | ''
  providerId?: string
}

export interface AboutPageConfig {
  hero: {
    status: string
    eyebrow: string
    name: string
    role: string
    description: string
    primaryButtonText: string
    primaryButtonUrl: string
    secondaryButtonText: string
    stats: Array<{ value: string; suffix: string; label: string }>
  }
  about: {
    badge: string
    title: string
    paragraphs: string[]
    highlightWords: string[]
    skills: Array<{ icon: string; title: string; description: string }>
    codeProfile: {
      variableName: string
      name: string
      role: string
      location: string
      languages: string[]
      github: string
    }
  }
  github: {
    badge: string
    titlePrefix: string
    titleAccent: string
    stats: Array<{ icon: string; value: string; label: string }>
    contributionText: string
  }
  contact: {
    badge: string
    title: string
    headline: string
    description: string
    email: string
    github: string
    githubUrl: string
    website: string
    websiteUrl: string
    qq: string
    wechat: string
    mailTo: string
  }
}

export interface SiteSettings {
  siteTitle?: string
  subtitle?: string
  siteDescription?: string
  author?: string
  avatar?: string
  description?: string
  profileIntro?: string
  socialLinks?: Record<string, string>
  title?: string
  authorName?: string
  bio?: string
  avatarUrl?: string
  icp?: string
  beian?: string
  defaultPostCover?: string
  photoWallImage?: string
  bgImages?: string[]
  themeColors?: string[]
  danmakuList?: string[]
  cloudMusicIds?: string[]
  siteStartTime?: string
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
    provider?: 'github' | 'multi'
    providers?: {
      github?: {
        enabled?: boolean
        configured?: boolean
        clientIdConfigured?: boolean
        secretConfigured?: boolean
      }
      qq?: {
        enabled?: boolean
        configured?: boolean
        appIdConfigured?: boolean
        secretConfigured?: boolean
      }
    }
    githubLoginEnabled?: boolean
    githubLoginConfigured?: boolean
    qqLoginEnabled?: boolean
    qqLoginConfigured?: boolean
    maxLength?: number
    gitalk?: Record<string, unknown>
  }
  interaction?: {
    clickSoundEnabled?: boolean
    clickSoundVolume?: number
    clickSoundUrl?: string
    clickEffectEnabled?: boolean
  }
  pageText?: Record<string, {
    title?: string
    subtitle?: string
    description?: string
  }>
  pageLayouts?: Record<string, {
    title?: string
    subtitle?: string
    note?: string
    blocks?: Array<{ id: string; label?: string; x: number; y: number; w: number; h: number }>
  }>
  githubOAuth?: {
    configured?: boolean
  }
}

export type HomeComponentId =
  | 'profileCard'
  | 'musicPlayer'
  | 'lyrics'
  | 'latestPostsCarousel'
  | 'photoCarousel'
  | 'updatesCarousel'
  | 'themeToggle'
  | 'statusBar'

export interface HomeLayoutComponent {
  order: number
  w: number
  h: number
  rowSpan?: number
  visible?: boolean
}

export interface PageConfig {
  pageText?: Record<string, { title?: string; subtitle?: string; description?: string }>
  homeProfile?: {
    author?: string
    avatar?: string
    description?: string
    socialLinks?: Record<string, string>
  }
  homeLayout?: {
    layoutVersion?: number
    components?: Partial<Record<HomeComponentId, HomeLayoutComponent>>
  }
  pageLayouts?: Record<string, PageLayout>
  home?: {
    layoutVersion?: number
    components?: Partial<Record<HomeComponentId, HomeLayoutComponent>>
  }
}

export interface PageLayoutComponent {
  order: number
  w: number
  h: number
  rowSpan?: number
  visible?: boolean
  label?: string
  type?: string
  locked?: boolean
  props?: Record<string, unknown>
}

export interface PageLayout {
  layoutVersion?: number
  components?: Record<string, PageLayoutComponent>
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
