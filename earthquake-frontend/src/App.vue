<template>
  <div id="app">
    <el-config-provider :locale="zhCn">
      <!-- 顶部导航栏 -->
      <el-header class="app-header" v-if="showHeader">
        <div class="header-content">
          <div class="logo-section">
            <h1 class="logo-title">地震预警平台</h1>
          </div>

          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            router
            class="nav-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>

            <el-menu-item index="/statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据统计</span>
            </el-menu-item>

            <el-menu-item index="/science">
              <el-icon><Reading /></el-icon>
              <span>科普知识</span>
            </el-menu-item>

            <el-menu-item index="/chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>交流区</span>
            </el-menu-item>

            <el-menu-item index="/subscribe">
              <el-icon><Bell /></el-icon>
              <span>订阅预警</span>
              <el-badge v-if="unreadCount > 0" :value="unreadCount" class="badge" />
            </el-menu-item>

            <el-menu-item index="/profile" v-if="isLoggedIn">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </el-menu>

          <!-- 登录后展示头像下拉 -->
          <div class="user-section" v-if="isLoggedIn">
            <el-dropdown>
              <div class="user-info">
                <el-avatar :size="32" class="user-avatar">
                  {{ userAccount.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ userAccount }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push('/profile')">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <div class="login-btn" v-if="!isLoggedIn">
            <el-button type="primary" @click="router.push('/login')">登录</el-button>
          </div>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 全局预警弹窗 -->
      <EarthquakeAlert v-if="alertComponentReady" ref="alertRef" />

      <!-- AI智能助手悬浮球 -->
      <AiFloatBall />
    </el-config-provider>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElConfigProvider, ElMessage } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import {
  House, DataAnalysis, Reading, ChatDotRound, Bell, User,
  ArrowDown, SwitchButton
} from '@element-plus/icons-vue'
import EarthquakeAlert from './components/EarthquakeAlert.vue'
import AiFloatBall from './components/AiFloatBall.vue'
import { userLogout, getUnreadAlertsCount } from './API/user'

const router = useRouter()
const route = useRoute()

const alertRef = ref(null)
const alertComponentReady = ref(true)
const unreadCount = ref(0)
let socket = null

// 修复：同时判断用户/管理员token，登录状态统一识别
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('user_token') || !!localStorage.getItem('admin_token')
})

// 修复：区分普通用户/管理员账号读取
const userAccount = computed(() => {
  const role = localStorage.getItem('user_role')
  if (role === 'admin') {
    return localStorage.getItem('admin_account') || '管理员'
  } else {
    return localStorage.getItem('user_account') || '用户'
  }
})

const showHeader = computed(() => {
  const hideHeaderRoutes = ['/login', '/register']
  return !hideHeaderRoutes.includes(route.path)
})

const activeMenu = computed(() => {
  return route.path
})

onMounted(() => {
  initWebSocket()
  loadUnreadCount()

  setInterval(() => {
    if (isLoggedIn.value) {
      loadUnreadCount()
    }
  }, 30000)
})

onBeforeUnmount(() => {
  if (socket) {
    socket.disconnect()
  }
})

watch(isLoggedIn, (newVal) => {
  if (newVal) {
    initWebSocket()
    loadUnreadCount()
  } else {
    if (socket) {
      socket.disconnect()
      socket = null
    }
    unreadCount.value = 0
  }
})

const handleMenuSelect = (index) => {
  console.log('菜单选择:', index)
}

const handleLogout = async () => {
  try {
    await userLogout()
    localStorage.clear()
    ElMessage.success('退出成功')
    router.push('/login')

    if (socket) {
      socket.disconnect()
      socket = null
    }
  } catch (error) {
    console.error('退出失败:', error)
    localStorage.clear()
    router.push('/login')
  }
}

const loadUnreadCount = async () => {
  if (!isLoggedIn.value) return

  try {
    const response = await getUnreadAlertsCount()
    if (response.code === 200) {
      unreadCount.value = response.data.unread_count || 0
    }
  } catch (error) {
    console.error('加载未读数量失败:', error)
  }
}

const initWebSocket = () => {
  // 区分管理员/普通用户id
  const role = localStorage.getItem('user_role')
  let userId, userToken
  if (role === 'admin') {
    userId = localStorage.getItem('admin_id')
    userToken = localStorage.getItem('admin_token')
  } else {
    userId = localStorage.getItem('user_id')
    userToken = localStorage.getItem('user_token')
  }

  if (!userId || !userToken) {
    console.log('未登录，不建立WebSocket连接')
    return
  }

  try {
    import('socket.io-client').then(({ io }) => {
      socket = io('http://localhost:5000', {
        query: {
          user_id: userId,
          token: userToken
        },
        transports: ['websocket', 'polling']
      })

      socket.on('connect', () => {
        console.log('✅ WebSocket连接成功')
        socket.emit('subscribe_alert', { user_id: userId })
      })

      socket.on('earthquake_alert', (data) => {
        console.log('🚨 收到地震预警:', data)
        if (alertRef.value) {
          alertRef.value.show(data)
        }
        loadUnreadCount()
      })

      socket.on('disconnect', () => {
        console.log('❌ WebSocket连接断开')
      })

      socket.on('error', (error) => {
        console.error('⚠️ WebSocket错误:', error)
      })
    }).catch(error => {
      console.warn('⚠️ socket.io-client 加载失败，预警功能不可用:', error)
    })
  } catch (error) {
    console.warn('⚠️ WebSocket 初始化失败:', error)
  }
}
</script>

<style scoped>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

:deep(body) {
  margin: 0;
  padding: 0;
}

/* 浅蓝柔和渐变导航背景 */
.app-header {
  background: linear-gradient(to right, #4096ff 0%, #2b7de9 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  padding: 0;
  height: 64px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24px;
  gap: 48px;
}

.logo-section {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.logo-title {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 1px;
}

.nav-menu {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

:deep(.el-menu--horizontal.nav-menu) {
  background: transparent !important;
  border-bottom: none !important;
  height: 100%;
}

:deep(.nav-menu .el-menu-item) {
  color: rgba(255, 255, 255, 0.92);
  border-bottom: none !important;
  transition: all 0.24s ease;
  font-size: 16px;
  height: 64px;
  line-height: 64px;
  padding: 0 22px;
  background: transparent !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

:deep(.nav-menu .el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.22) !important;
  color: #ffffff !important;
}

:deep(.nav-menu .el-menu-item.is-active) {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.26) !important;
  border-bottom: 3px solid #fff !important;
  font-weight: 600;
}

:deep(.nav-menu .el-menu-item .el-icon) {
  margin-right: 6px;
  font-size: 18px;
}

.user-section {
  flex-shrink: 0;
  height: 100%;
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 14px;
  border-radius: 6px;
  transition: all 0.24s ease;
  color: white;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.22);
}

:deep(.user-avatar) {
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.55);
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.badge {
  margin-left: 6px;
}

.login-btn {
  flex-shrink: 0;
}

:deep(.login-btn .el-button) {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.35);
  color: white;
}

:deep(.login-btn .el-button:hover) {
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.6);
}

.app-main {
  flex: 1;
  padding: 0;
  background: #f0f2f5;
}

@media (max-width: 768px) {
  .logo-title {
    font-size: 16px;
  }

  .nav-menu {
    display: none;
  }

  .header-content {
    padding: 0 12px;
    gap: 16px;
  }
}
</style>