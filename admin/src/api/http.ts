import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('srblogs-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('srblogs-token')
    }
    const message = error?.response?.status === 401
      ? '登录已失效，请重新登录后再操作。'
      : error?.response?.status === 403
        ? '权限不足，请确认当前账号是否具备管理员权限。'
        : error?.response?.data?.message || error?.response?.data?.detail || error?.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)
