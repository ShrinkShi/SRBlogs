export type FloatingAppActionType = 'modal' | 'route' | 'external' | 'toggle' | 'custom'

export type FloatingAppIcon = 'settings' | 'music' | 'search' | 'calculator' | 'article'

export type FloatingAppItem = {
  id: string
  name: string
  icon: FloatingAppIcon
  actionType: FloatingAppActionType
  action: string
  enabled?: boolean
  order?: number
  tooltip?: string
}

export const floatingApps: FloatingAppItem[] = [
  {
    id: 'settings',
    name: '设置',
    icon: 'settings',
    actionType: 'modal',
    action: 'settings',
    order: 10,
    tooltip: '打开游客设置'
  },
  {
    id: 'music-player',
    name: '音乐播放器',
    icon: 'music',
    actionType: 'toggle',
    action: 'floatingMusicPlayer',
    order: 20,
    tooltip: '显示或隐藏悬浮播放器'
  },
  {
    id: 'search',
    name: '全局搜索',
    icon: 'search',
    actionType: 'modal',
    action: 'search',
    order: 30,
    tooltip: '搜索站内内容'
  },
  {
    id: 'calculator',
    name: '计算器',
    icon: 'calculator',
    actionType: 'modal',
    action: 'calculator',
    order: 40,
    tooltip: '打开轻量计算器'
  },
  {
    id: 'posts',
    name: '文章',
    icon: 'article',
    actionType: 'route',
    action: '/posts',
    order: 50,
    tooltip: '进入文章归档'
  }
]
