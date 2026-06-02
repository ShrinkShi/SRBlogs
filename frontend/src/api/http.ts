import axios from 'axios'

const localApiBase =
  typeof window !== 'undefined' && ['5173', '5174', '5175'].includes(window.location.port)
    ? `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000/api`
    : '/api'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || localApiBase,
  timeout: 20000,
  withCredentials: true
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('srblogs-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = String(error?.config?.url || '')
    const adminRequest = requestUrl.includes('/admin') || requestUrl.includes('/auth/admin/me') || requestUrl.includes('/upload') || requestUrl.includes('/chat')
    if (error?.response?.status === 401 && adminRequest && localStorage.getItem('srblogs-token')) {
      localStorage.removeItem('srblogs-token')
    }
    const message = error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)
