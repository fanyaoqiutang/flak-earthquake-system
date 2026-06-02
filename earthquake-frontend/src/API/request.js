import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

request.interceptors.request.use(
  config => {
    const userToken = localStorage.getItem('user_token')
    const adminToken = localStorage.getItem('admin_token')

    if (userToken) {
      config.headers['Authorization'] = `Bearer ${userToken}`
    }

    if (adminToken) {
      config.headers['X-Admin-Token'] = adminToken
    }

    console.log(`📤 请求: ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data || '')

    return config
  },
  error => {
    console.error('❌ 请求错误:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data

    console.log(`✅ 响应: ${response.config.url}`, res)

    if (res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')

      if (res.code === 401) {
        localStorage.clear()
        router.push('/login')
      }

      return Promise.reject(new Error(res.msg || '请求失败'))
    }

    return res
  },
  error => {
    console.error('❌ 响应错误:', error)

    if (error.message.includes('timeout') || error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message.includes('Network Error')) {
      ElMessage.error('网络错误：无法连接到服务器，请确保后端服务正在运行')
    } else if (error.response) {
      const status = error.response.status

      if (status === 401) {
        ElMessage.error('认证失败，请重新登录')
        localStorage.clear()
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error('权限不足，无法访问')
      } else {
        ElMessage.error(error.response.data?.msg || `请求失败: ${status}`)
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务是否运行')
    }

    return Promise.reject(error)
  }
)

export default request
