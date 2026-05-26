<template>
  <div class="profile-container">
    <div class="profile-header">
      <el-avatar :size="100" class="user-avatar">
        {{ userRole === 'admin' ? '管' : '用' }}
      </el-avatar>
      <h2>{{ currentUser || '未登录' }}</h2>
      <el-tag :type="userRole === 'admin' ? 'danger' : 'success'">
        {{ userRole === 'admin' ? '管理员' : '普通用户' }}
      </el-tag>
    </div>

    <div class="profile-content">
      <el-tabs v-model="activeTab" class="profile-tabs">
        <!-- 用户信息 -->
        <el-tab-pane label="个人信息" name="info">
          <div class="info-section">
            <div class="info-item">
              <span class="label">账号:</span>
              <span class="value">{{ currentUser }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色:</span>
              <span class="value">{{ userRole === 'admin' ? '管理员' : '普通用户' }}</span>
            </div>
          </div>
        </el-tab-pane>

        <!-- 我的订阅 -->
        <el-tab-pane label="我的订阅" name="subscriptions">
          <div v-if="subscriptions.length === 0" class="empty-state">
            <el-icon :size="48" color="#909399"><Bell /></el-icon>
            <p>暂未订阅任何省份</p>
            <el-button type="primary" @click="$router.push('/subscribe')">去订阅</el-button>
          </div>
          <div v-else class="subscription-list">
            <el-tag
              v-for="sub in subscriptions"
              :key="sub"
              closable
              @close="removeSubscription(sub)"
              class="sub-tag"
            >
              {{ sub }}
            </el-tag>
          </div>
        </el-tab-pane>

        <!-- 账户设置 -->
        <el-tab-pane label="账户设置" name="settings">
          <div class="settings-section">
            <el-button type="warning" @click="changePassword">修改密码</el-button>
            <el-button type="danger" @click="logout">退出登录</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('info')
const currentUser = ref('')
const userRole = ref('')
const subscriptions = ref([])

onMounted(() => {
  loadUserInfo()
})

const loadUserInfo = () => {
  const userAccount = localStorage.getItem('user_account')
  const adminAccount = localStorage.getItem('admin_account')

  if (userAccount) {
    currentUser.value = userAccount
    userRole.value = 'user'
  } else if (adminAccount) {
    currentUser.value = adminAccount
    userRole.value = 'admin'
  } else {
    ElMessage.warning('请先登录')
    router.push('/login')
  }
}

const removeSubscription = (province) => {
  subscriptions.value = subscriptions.value.filter(p => p !== province)
  ElMessage.success(`已取消订阅: ${province}`)
}

const changePassword = () => {
  ElMessage.info('修改密码功能开发中')
}

const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.clear()
    ElMessage.success('已退出登录')
    router.push('/')
  }).catch(() => {})
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.profile-header {
  text-align: center;
  margin-bottom: 40px;
}

.user-avatar {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 36px;
  font-weight: bold;
}

.profile-header h2 {
  margin: 10px 0;
  color: #303133;
}

.profile-content {
  margin-top: 30px;
}

.info-section {
  padding: 20px;
}

.info-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  width: 100px;
  color: #909399;
  font-weight: 600;
}

.value {
  color: #303133;
  flex: 1;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state p {
  margin: 20px 0;
  font-size: 16px;
}

.subscription-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 20px;
}

.sub-tag {
  font-size: 14px;
  padding: 8px 16px;
}

.settings-section {
  display: flex;
  gap: 15px;
  padding: 20px;
}
</style>
