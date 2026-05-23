import { defineStore } from 'pinia'
export const useUiStore = defineStore('ui', {
  state: () => ({ toast: '', toastType: 'success' as 'success' | 'error', loading: false }),
  actions: {
    show(message: string, type: 'success' | 'error' = 'success') {
      this.toast = message
      this.toastType = type
      setTimeout(() => (this.toast = ''), 2200)
    },
    error(message: string) {
      this.show(message, 'error')
    }
  }
})
