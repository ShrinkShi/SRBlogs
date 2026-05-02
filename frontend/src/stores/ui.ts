import { defineStore } from 'pinia'

export const themes = ['nebula', 'sakura', 'aurora', 'cyber'] as const
export type ThemeName = (typeof themes)[number]

export const useUiStore = defineStore('ui', {
  state: () => ({
    theme: (localStorage.getItem('sr-theme') || 'nebula') as ThemeName,
    colorMode: (localStorage.getItem('sr-color-mode') || 'night') as 'day' | 'night',
    bgIndex: Number(localStorage.getItem('sr-bg-index') || '0'),
    danmaku: localStorage.getItem('sr-danmaku') !== 'off',
    ambience: localStorage.getItem('sr-ambience') !== 'off',
    toast: '',
    toastKind: 'info' as 'info' | 'success' | 'error'
  }),
  actions: {
    setTheme(theme: ThemeName | string) {
      this.theme = theme as ThemeName
      localStorage.setItem('sr-theme', theme)
    },
    nextTheme() {
      const i = themes.indexOf(this.theme as ThemeName)
      this.setTheme(themes[(i + 1) % themes.length])
    },
    setColorMode(mode: 'day' | 'night') {
      this.colorMode = mode
      localStorage.setItem('sr-color-mode', mode)
    },
    toggleColorMode() {
      this.setColorMode(this.colorMode === 'night' ? 'day' : 'night')
    },
    setBgIndex(index: number) {
      this.bgIndex = index
      localStorage.setItem('sr-bg-index', String(index))
    },
    toggleDanmaku() {
      this.danmaku = !this.danmaku
      localStorage.setItem('sr-danmaku', this.danmaku ? 'on' : 'off')
    },
    toggleAmbience() {
      this.ambience = !this.ambience
      localStorage.setItem('sr-ambience', this.ambience ? 'on' : 'off')
    },
    showToast(message: string, kind: 'info' | 'success' | 'error' = 'info') {
      this.toast = message
      this.toastKind = kind
      window.setTimeout(() => (this.toast = ''), 2200)
    }
  }
})
