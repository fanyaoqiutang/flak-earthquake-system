<template>
  <div id="app">
    <el-config-provider :locale="zhCn">
      <!-- 导航栏 -->
      <el-header v-if="showHeader" class="app-header">
        <div class="header-content">
          <div class="logo">地震预警平台</div>
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            router
            class="main-menu"
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
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </el-menu>

          <div class="user-info">
            <el-dropdown trigger="click">
              <span class="user-name">
                <el-avatar :size="32">{{ userInitial }}</el-avatar>
                {{ displayUsername }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="isAdmin" @click="goToAdmin">
                    <el-icon><Setting /></el-icon>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <router-view />

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
  ArrowDown, SwitchButton, Setting
} from '@element-plus/icons-vue'
import EarthquakeAlert from './components/EarthquakeAlert.vue'
import AiFloatBall from './components/AiFloatBall.vue'
import { userLogout, getUnreadAlertsCount } from './API/user'
import { adminLogout } from './API/admin'

const router = useRouter()
const route = useRoute()

// 用户信息
const isLoggedIn = ref(false)
const isAdmin = ref(false)
const username = ref('')
const userId = ref(null)

// 计算属性
const showHeader = computed(() => {
  // 只在登录页隐藏头部
  return !route.path.includes('/login')
})

const activeMenu = computed(() => {
  return route.path
})

const displayUsername = computed(() => {
  return username.value || '未登录'
})

const userInitial = computed(() => {
  return username.value ? username.value.charAt(0).toUpperCase() : '?'
})

// 方法
const handleMenuSelect = (index) => {
  // 菜单选择处理
}

const goToAdmin = () => {
  router.push('/admin/profile')
}

const handleLogout = async () => {
  try {
    if (isAdmin.value) {
      await adminLogout()
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_account')
      localStorage.removeItem('admin_id')
      isAdmin.value = false
    } else {
      await userLogout()
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_account')
      localStorage.removeItem('user_id')
    }

    localStorage.removeItem('user_role')
    isLoggedIn.value = false
    username.value = ''
    userId.value = null

    ElMessage.success('退出成功')
    router.push('/login')
  } catch (error) {
    console.error('退出失败:', error)
    ElMessage.error('退出失败')
  }
}

// 检查登录状态
const checkLoginStatus = () => {
  const userRole = localStorage.getItem('user_role')

  if (userRole === 'admin') {
    const adminToken = localStorage.getItem('admin_token')
    const adminAccount = localStorage.getItem('admin_account')

    if (adminToken && adminAccount) {
      isLoggedIn.value = true
      isAdmin.value = true
      username.value = adminAccount
      userId.value = localStorage.getItem('admin_id')
    } else {
      isLoggedIn.value = false
      isAdmin.value = false
    }
  } else if (userRole === 'user') {
    const userToken = localStorage.getItem('user_token')
    const userAccount = localStorage.getItem('user_account')

    if (userToken && userAccount) {
      isLoggedIn.value = true
      isAdmin.value = false
      username.value = userAccount
      userId.value = localStorage.getItem('user_id')
    } else {
      isLoggedIn.value = false
      isAdmin.value = false
    }
  } else {
    isLoggedIn.value = false
    isAdmin.value = false
  }
}

// 监听路由变化，重新检查登录状态
watch(() => route.path, () => {
  checkLoginStatus()
}, { immediate: true })

// 组件挂载时检查登录状态
onMounted(() => {
  checkLoginStatus()

  // 定期检查登录状态（每30秒）
  const interval = setInterval(checkLoginStatus, 30000)

  onBeforeUnmount(() => {
    clearInterval(interval)
  })
})

// 暴露方法供子组件调用
defineExpose({
  checkLoginStatus
})
</script>

<style scoped>
.app-header {
  background: #409eff;
  color: white;
  padding: 0;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  margin-right: 40px;
  letter-spacing: 2px;
}

.main-menu {
  flex: 1;
  background: transparent;
  border-bottom: none;
}

.main-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.main-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

.main-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-bottom-color: white;
}

.user-info {
  margin-left: 20px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: background 0.3s;
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>