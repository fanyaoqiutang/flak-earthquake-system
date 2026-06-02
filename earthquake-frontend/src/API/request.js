//axios 请求工具封装（前端接口统一的请求配置）
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 10000, // 10秒超时
  withCredentials: true, // 携带 Cookie
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求重试机制
let retryCount = 0
const MAX_RETRIES = 1

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

    // 调试信息
    console.log('发送请求:', config.method.toUpperCase(), config.url)
    console.log('请求头:', config.headers)

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    console.log('响应数据:', res)
    if (res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    return res
  },
  error => {
    console.error('响应错误:', error)

    // 检查是否是网络错误
    if (error.message.includes('timeout') || error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message.includes('Network Error')) {
      ElMessage.error('网络错误：无法连接到服务器，请确保后端服务正在运行')
    } else if (error.response) {
      // 服务器返回了错误状态码
      console.error('错误响应:', error.response.data)
      if (error.response.status === 401) {
        ElMessage.error('认证失败，请重新登录')
        // 可以选择清除token并跳转到登录页
        // localStorage.removeItem('user_token')
        // localStorage.removeItem('admin_token')
        // router.push('/login')
      } else {
        ElMessage.error(error.response.data?.msg || `请求失败: ${error.response.status}`)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('无响应:', error.request)
      ElMessage.error('网络错误：服务器无响应，请检查后端服务是否运行')
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
