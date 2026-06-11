<template>
  <div class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <h1>地震预警平台</h1>
        </div>

        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          router
          class="nav-menu"
          :ellipsis="false"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
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
          <template v-if="isLoggedIn">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                <el-avatar :size="36" class="user-avatar">
                  {{ userRole === 'admin' ? '管' : '用' }}
                </el-avatar>
                <span class="user-name">{{ currentUser }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleProfile">
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
          </template>
          <template v-else>
            <el-button type="primary" @click="goToLogin">登录 / 注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>
     <!-- AI 智能问答悬浮球 -->
    <AiFloatBall v-if="isLoggedIn" />
  </div>
</template>

<script setup>import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled, DataAnalysis, Reading, ChatDotRound, Location, Bell, User, ArrowDown, SwitchButton
} from '@element-plus/icons-vue'
import AiFloatBall from './components/AiFloatBall.vue'

const router = useRouter()
const route = useRoute()

const activeIndex = computed(() => {
  if (route.path === '/') return '/'
  return route.path
})

const currentUser = ref('')
const userRole = ref('')

// 改进的登录状态管理(使用响应式)
const loginState = ref(false)

const isLoggedIn = computed(() => {
  return loginState.value
})

// 封装刷新用户信息方法
const loadUserInfo = () => {
  const userToken = localStorage.getItem('user_token')
  const adminToken = localStorage.getItem('admin_token')
  const userAccount = localStorage.getItem('user_account')
  const adminAccount = localStorage.getItem('admin_account')

  // 更新登录状态
  loginState.value = !!(userToken || adminToken)

  if (userAccount) {
    currentUser.value = userAccount
    userRole.value = 'user'
  } else if (adminAccount) {
    currentUser.value = adminAccount
    userRole.value = 'admin'
  } else {
    // 没数据清空
    currentUser.value = ''
    userRole.value = ''
  }
}

onMounted(() => {
  loadUserInfo()
})

// 监听路由变化，重新加载用户信息
watch(() => route.path, () => {
  loadUserInfo()
})

const goToLogin = () => {
  router.push('/login')
}

const handleProfile = () => {
  const adminToken = localStorage.getItem('admin_token')
  console.log('点击个人中心，adminToken:', adminToken)

  if (adminToken) {
    console.log('跳转到管理员页面')
    router.push('/admin/profile')
  } else {
    console.log('跳转到普通用户页面')
    router.push('/profile')
  }
}

const handleLogout = () => {
  localStorage.clear()
  ElMessage.success('退出登录成功')
  router.push('/login')
  loadUserInfo() // 执行刷新状态
}

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'admin') {
    ElMessage.info('管理后台功能开发中')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      localStorage.clear()
      currentUser.value = ''
      userRole.value = ''
      ElMessage.success('已退出登录')
      router.push('/')
      loadUserInfo() // 关键：重新刷新登录状态
    }).catch(() => {})
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 0;
  height: 64px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo h1 {
  font-size: 22px;
  color: white;
  margin: 0;
  margin-right: 40px;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  background: transparent;
  border-bottom: none;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.95) !important;
  font-size: 15px;
  height: 64px;
  line-height: 64px;
  padding: 0 20px;
  font-weight: 500;
}

.nav-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.nav-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.25) !important;
  color: white !important;
  border-bottom: 3px solid white;
}

.nav-menu .el-icon {
  margin-right: 6px;
  font-size: 18px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: background 0.3s;
  color: white;
}

.user-dropdown:hover {
  background: rgba(255, 255, 255, 0.15);
}

.user-avatar {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.user-name {
  font-size: 14px;
  color: white;
  font-weight: 500;
}

.app-main {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: #f0f2f5;
}
</style>