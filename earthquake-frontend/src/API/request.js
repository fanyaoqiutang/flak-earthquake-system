//axios 请求工具封装（前端接口统一的请求配置）
import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 10000,
  withCredentials: true // 携带 Cookie
})

// 请求拦截器
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

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    return res
  },
  error => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
