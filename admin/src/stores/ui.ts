import { defineStore } from 'pinia'
export const useUiStore = defineStore('ui', {
  state: () => ({ toast: '', loading: false }),
  actions: {
    show(message: string) {
      this.toast = message
      setTimeout(() => (this.toast = ''), 2200)
    }
  }
})
