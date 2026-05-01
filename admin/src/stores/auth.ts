import { defineStore } from 'pinia'
import { adminApi } from '@/api/admin'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('srblogs-token') || '' }),
  getters: { isAuthed: (state) => Boolean(state.token) },
  actions: {
    async login(username: string, password: string) {
      const data = await adminApi.login(username, password)
      this.token = data.access_token
      localStorage.setItem('srblogs-token', this.token)
    },
    logout() {
      this.token = ''
      localStorage.removeItem('srblogs-token')
    }
  }
})
