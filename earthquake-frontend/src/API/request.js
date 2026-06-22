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

    // 如果是管理员接口，优先使用 admin_token
    if (config.url && config.url.includes('/admin/')) {
      if (adminToken) {
        config.headers['X-Admin-Token'] = adminToken
        console.log(`🔑 [Admin Request] ${config.method?.toUpperCase()} ${config.url}`)
        console.log(`   Token: ${adminToken.substring(0, 8)}...`)
      } else {
        console.warn(`⚠️ [Admin Request] 缺少 admin_token: ${config.url}`)
      }
    } else {
      // 普通用户接口
      if (userToken) {
        config.headers['Authorization'] = `Bearer ${userToken}`
        console.log(`🔑 [User Request] ${config.method?.toUpperCase()} ${config.url}`)
      }
    }

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
    const url = response.config.url

    // 只在非 GET 请求或重要接口打印响应日志
    if (response.config.method !== 'get' || url.includes('/info') || url.includes('/stats')) {
      console.log(`✅ [Response] ${url}`, { code: res.code, msg: res.msg })
    }

    if (res.code !== 200) {
      // 特殊处理 401 和 403 错误
      if (res.code === 401) {
        console.warn(`⚠️ [401 Unauthorized] ${url}`)

        // 只清除对应用户的 token
        const isAdminRoute = url.includes('/admin/')

        if (isAdminRoute) {
          console.log('   → 清除管理员登录信息')
          localStorage.removeItem('admin_token')
          localStorage.removeItem('admin_account')
          localStorage.removeItem('admin_id')

          // 显示友好的提示信息（但不强制跳转）
          ElMessage.warning({
            message: '管理员登录已过期，请重新登录',
            duration: 3000
          })

          // 如果在管理员页面，延迟跳转到登录页
          if (router.currentRoute.value.path.includes('/admin')) {
            setTimeout(() => {
              router.push('/login')
            }, 1000)
          }
        } else {
          console.log('   → 清除用户登录信息')
          localStorage.removeItem('user_token')
          localStorage.removeItem('user_account')
          localStorage.removeItem('user_id')

          ElMessage.warning({
            message: '用户登录已过期，请重新登录',
            duration: 3000
          })
        }
      } else if (res.code === 403) {
        console.error(`❌ [403 Forbidden] ${url}`)
        ElMessage.error('权限不足，无法访问该资源')
      } else {
        // 其他错误才显示详细消息
        if (res.msg && !res.msg.includes('成功')) {
          ElMessage.error(res.msg)
        }
      }

      return Promise.reject(new Error(res.msg || '请求失败'))
    }

    return res
  },
  error => {
    console.error('❌ [Network Error]', error)

    if (error.message.includes('timeout') || error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message.includes('Network Error')) {
      ElMessage.error('网络错误：无法连接到服务器，请确保后端服务正在运行')
    } else if (error.response) {
      const status = error.response.status
      const url = error.config.url

      if (status === 401) {
        console.warn(`⚠️ [HTTP 401] ${url}`)

        const isAdminRoute = url.includes('/admin/')

        if (isAdminRoute) {
          localStorage.removeItem('admin_token')
          localStorage.removeItem('admin_account')
          localStorage.removeItem('admin_id')

          ElMessage.warning({
            message: '认证失败，请重新登录',
            duration: 3000
          })

          if (router.currentRoute.value.path.includes('/admin')) {
            setTimeout(() => {
              router.push('/login')
            }, 1000)
          }
        } else {
          localStorage.removeItem('user_token')
          localStorage.removeItem('user_account')
          localStorage.removeItem('user_id')

          ElMessage.warning('认证失败，请重新登录')
        }
      } else if (status === 403) {
        ElMessage.error('权限不足，无法访问')
      } else {
        const msg = error.response.data?.msg || `请求失败 (${status})`
        if (!msg.includes('成功')) {
          ElMessage.error(msg)
        }
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务是否运行')
    }

    return Promise.reject(error)
  }
)

export default request
