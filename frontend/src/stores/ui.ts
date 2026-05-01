import { defineStore } from 'pinia'

export const themes = ['nebula', 'sakura', 'aurora', 'cyber'] as const
export type ThemeName = (typeof themes)[number]

export const useUiStore = defineStore('ui', {
  state: () => ({
    theme: (localStorage.getItem('sr-theme') || 'nebula') as ThemeName,
    bgIndex: Number(localStorage.getItem('sr-bg-index') || '0'),
    danmaku: localStorage.getItem('sr-danmaku') !== 'off',
    toast: ''
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
    setBgIndex(index: number) {
      this.bgIndex = index
      localStorage.setItem('sr-bg-index', String(index))
    },
    toggleDanmaku() {
      this.danmaku = !this.danmaku
      localStorage.setItem('sr-danmaku', this.danmaku ? 'on' : 'off')
    },
    showToast(message: string) {
      this.toast = message
      window.setTimeout(() => (this.toast = ''), 2200)
    }
  }
})
