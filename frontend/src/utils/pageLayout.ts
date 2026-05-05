import type { PageConfig, PageLayoutComponent } from '@/types'

export type PageKey = 'home' | 'posts' | 'photos' | 'music' | 'projects' | 'friends' | 'about'

export interface LayoutBlock extends PageLayoutComponent {
  id: string
  label: string
  type: string
  visible: boolean
}

function block(
  id: string,
  order: number,
  w: number,
  h: number,
  label: string,
  type = id,
  visible = true,
  rowSpan = 1
): LayoutBlock {
  return { id, order, w, h, rowSpan, label, type, visible, locked: true, props: {} }
}

export const defaultPageLayouts: Record<PageKey, LayoutBlock[]> = {
  home: [
    block('profileCard', 1, 6, 2, '名片'),
    block('musicPlayer', 2, 6, 2, '音乐播放器'),
    block('lyrics', 3, 12, 1, '歌词区'),
    block('latestPostsCarousel', 4, 4, 3, '最新文章轮播'),
    block('photoCarousel', 5, 8, 2, '图片轮播'),
    block('updatesCarousel', 6, 8, 2, '更新内容轮播'),
    block('themeToggle', 7, 4, 2, '昼夜切换卡片'),
    block('statusBar', 8, 12, 1, '底部状态区')
  ],
  posts: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('sectionSwitch', 2, 12, 0.8, '正经 / 杂谈切换'),
    block('searchBox', 3, 12, 0.8, '搜索区'),
    block('tagFilter', 4, 12, 0.8, '标签筛选区'),
    block('viewModeSwitch', 5, 12, 0.8, '显示模式切换'),
    block('contentList', 6, 12, 4, '内容列表区')
  ],
  photos: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('viewModeSwitch', 2, 12, 0.8, '显示模式切换'),
    block('albumList', 3, 12, 4, '相册列表区'),
    block('messageBoard', 4, 12, 2, '留言板区域', 'messageBoard', false)
  ],
  music: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('playerPanel', 2, 5, 4, '音乐播放器面板'),
    block('lyricsPlaylistPanel', 3, 7, 4, '歌词 / 歌单面板'),
    block('messageBoard', 4, 12, 2, '留言板')
  ],
  projects: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('projectList', 2, 12, 4, '项目列表区')
  ],
  friends: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('friendList', 2, 12, 4, '友链列表区')
  ],
  about: [
    block('pageTitle', 1, 12, 1.4, '页面标题区'),
    block('markdownContent', 2, 12, 4, 'Markdown 内容区')
  ]
}

defaultPageLayouts.home = [
  block('profileCard', 1, 6, 2, '名片'),
  block('musicPlayer', 2, 6, 2, '音乐播放器'),
  block('lyrics', 3, 12, 1, '歌词区'),
  block('latestPostsCarousel', 4, 4, 4, '最新文章轮播', 'latestPostsCarousel', true, 2),
  block('photoCarousel', 5, 8, 2, '图片轮播'),
  block('updatesCarousel', 6, 4, 2, '更新内容轮播'),
  block('themeToggle', 7, 4, 2, '昼夜切换卡片'),
  block('statusBar', 8, 12, 1, '底部状态区')
]

function clamp(value: unknown, fallback: number, min: number, max: number) {
  const next = Number(value)
  if (!Number.isFinite(next)) return fallback
  return Math.min(max, Math.max(min, next))
}

export function layoutBlocks(config: PageConfig | null | undefined, page: PageKey): LayoutBlock[] {
  const defaults = defaultPageLayouts[page] || []
  const saved = (config?.pageLayouts?.[page]?.components || (page === 'home' ? config?.homeLayout?.components : undefined) || {}) as Record<string, PageLayoutComponent>
  const byId = new Map<string, LayoutBlock>()
  for (const item of defaults) {
    const current = saved[item.id] || {}
    byId.set(item.id, {
      ...item,
      ...current,
      id: item.id,
      label: String(current.label || item.label),
      type: String(current.type || item.type),
      order: clamp(current.order, item.order, 1, 999),
      w: clamp(current.w, item.w, 1, 12),
      h: clamp(current.h, item.h, 0.5, 8),
      rowSpan: clamp(current.rowSpan, item.rowSpan || 1, 1, 4),
      visible: current.visible !== false,
      props: current.props || item.props || {}
    })
  }
  for (const [id, current] of Object.entries(saved)) {
    if (byId.has(id)) continue
    byId.set(id, {
      id,
      label: String(current.label || id),
      type: String(current.type || 'customText'),
      order: clamp(current.order, 99, 1, 999),
      w: clamp(current.w, 12, 1, 12),
      h: clamp(current.h, 1, 0.5, 8),
      rowSpan: clamp(current.rowSpan, 1, 1, 4),
      visible: current.visible !== false,
      locked: false,
      props: current.props || {}
    })
  }
  return [...byId.values()].sort((a, b) => a.order - b.order)
}

export function layoutBlock(config: PageConfig | null | undefined, page: PageKey, id: string) {
  return layoutBlocks(config, page).find((item) => item.id === id)
}

export function isVisible(config: PageConfig | null | undefined, page: PageKey, id: string) {
  return layoutBlock(config, page, id)?.visible !== false
}

export function layoutStyle(block?: PageLayoutComponent | null) {
  const w = clamp(block?.w, 12, 1, 12)
  const h = clamp(block?.h, 1, 0.5, 4)
  const rowSpan = Math.max(1, Math.min(4, Math.round(clamp(block?.rowSpan, 1, 1, 4))))
  const span = Math.max(1, Math.min(12, Math.round(w)))
  return {
    order: block?.order || 99,
    gridColumn: `span ${span} / span ${span}`,
    gridRow: `span ${rowSpan} / span ${rowSpan}`,
    minHeight: `${Math.max(2.75, h * 3.25)}rem`
  }
}

export function customBlocks(config: PageConfig | null | undefined, page: PageKey) {
  const defaultIds = new Set((defaultPageLayouts[page] || []).map((item) => item.id))
  return layoutBlocks(config, page).filter((item) => item.visible !== false && !defaultIds.has(item.id))
}
