import { defineStore } from 'pinia'

export const themes = ['shrink-red-glass'] as const
export type ThemeName = (typeof themes)[number]

function normalizeTheme(value: string | null): ThemeName {
  return themes.includes(value as ThemeName) ? value as ThemeName : 'shrink-red-glass'
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    theme: normalizeTheme(localStorage.getItem('sr-theme')),
    colorMode: (localStorage.getItem('sr-color-mode') || 'night') as 'day' | 'night',
    bgIndex: Number(localStorage.getItem('sr-bg-index') || '0'),
    danmaku: localStorage.getItem('sr-danmaku') !== 'off',
    ambience: localStorage.getItem('sr-ambience') !== 'off',
    clickSound: localStorage.getItem('sr-click-sound') !== 'off',
    clickSoundAllowed: true,
    clickSoundVolume: Number(localStorage.getItem('sr-click-volume') || '0.05'),
    clickSoundUrl: localStorage.getItem('sr-click-url') || '',
    clickEffectAllowed: true,
    clickEffect: localStorage.getItem('sr-click-effect') !== 'off',
    fontScale: (localStorage.getItem('sr-font-scale') || 'medium') as 'small' | 'medium' | 'large',
    toast: '',
    toastKind: 'info' as 'info' | 'success' | 'error'
  }),
  actions: {
    setTheme(theme: ThemeName | string) {
      const normalized = normalizeTheme(theme)
      this.theme = normalized
      localStorage.setItem('sr-theme', normalized)
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
    toggleClickSound() {
      if (!this.clickSoundAllowed) return
      this.clickSound = !this.clickSound
      localStorage.setItem('sr-click-sound', this.clickSound ? 'on' : 'off')
    },
    toggleClickEffect() {
      if (!this.clickEffectAllowed) return
      this.clickEffect = !this.clickEffect
      localStorage.setItem('sr-click-effect', this.clickEffect ? 'on' : 'off')
    },
    setClickEffect(enabled: boolean) {
      if (!this.clickEffectAllowed && enabled) return
      this.clickEffect = enabled
      localStorage.setItem('sr-click-effect', enabled ? 'on' : 'off')
    },
    applyInteraction(config?: { clickSoundEnabled?: boolean; clickSoundVolume?: number; clickSoundUrl?: string; clickEffectEnabled?: boolean }) {
      if (!config) return
      this.clickSoundAllowed = config.clickSoundEnabled !== false
      this.clickSound = this.clickSoundAllowed ? localStorage.getItem('sr-click-sound') !== 'off' : false
      this.clickSoundVolume = Math.max(0, Math.min(1, Number(config.clickSoundVolume ?? 0.05)))
      this.clickSoundUrl = config.clickSoundUrl || ''
      this.clickEffectAllowed = config.clickEffectEnabled !== false
      this.clickEffect = this.clickEffectAllowed ? localStorage.getItem('sr-click-effect') !== 'off' : false
      localStorage.setItem('sr-click-sound', this.clickSound ? 'on' : 'off')
      localStorage.setItem('sr-click-volume', String(this.clickSoundVolume))
      localStorage.setItem('sr-click-url', this.clickSoundUrl)
      localStorage.setItem('sr-click-effect', this.clickEffect ? 'on' : 'off')
    },
    setClickSoundVolume(volume: number) {
      if (!this.clickSoundAllowed) return
      this.clickSoundVolume = Math.max(0, Math.min(1, Number.isFinite(volume) ? volume : this.clickSoundVolume))
      localStorage.setItem('sr-click-volume', String(this.clickSoundVolume))
    },
    setFontScale(scale: 'small' | 'medium' | 'large') {
      this.fontScale = scale
      localStorage.setItem('sr-font-scale', scale)
    },
    showToast(message: string, kind: 'info' | 'success' | 'error' = 'info') {
      this.toast = message
      this.toastKind = kind
      window.setTimeout(() => (this.toast = ''), 2200)
    }
  }
})
