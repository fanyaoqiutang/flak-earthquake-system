<template>
  <div class="subscribe-page">
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧预警列表 -->
      <div class="left-panel">
        <div class="warning-item" v-for="i in 4" :key="i">
          <div class="warning-header">
            <span class="warning-time">2026-05-25 10:30:00</span>
            <el-tag type="danger" size="small">M5.2</el-tag>
          </div>
          <div class="warning-content">
            <h4>四川省雅安市发生5.2级地震</h4>
            <p>震源深度: 10KM | 经纬度: 30.05°N, 103.00°E</p>
            <p class="warning-tip">⚠️ 请当地居民注意防范,做好应急准备</p>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- 我的订阅省份 -->
        <div class="panel-card">
          <h3 class="card-title">我的订阅省份</h3>

          <div class="subscribe-list">
            <div v-if="!isLoggedIn" class="login-tip">
              <el-icon><Lock /></el-icon>
              <span>请先登录后查看订阅</span>
            </div>
            <template v-else>
              <div
                v-for="sub in subscriptions"
                :key="sub"
                class="subscribe-item"
              >
                <span class="province-name">{{ sub }}</span>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="removeSubscription(sub)"
                >
                  取消
                </el-button>
              </div>
              <div v-if="subscriptions.length === 0" class="empty-tip">
                暂未订阅任何省份
              </div>
            </template>
          </div>

          <el-button
            type="primary"
            class="manage-btn"
            @click="showSubscribeDialog"
            :disabled="!isLoggedIn"
          >
            管理订阅省份
          </el-button>
        </div>

        <!-- 预警设置 -->
        <div class="panel-card alert-settings">
          <h3 class="card-title">预警设置</h3>

          <div class="setting-item">
            <div class="setting-label">
              <el-icon><Bell /></el-icon>
              推送通知
            </div>
            <el-switch v-model="settings.pushNotify" :disabled="!isLoggedIn" />
          </div>

          <div class="setting-item">
            <div class="setting-label">
              <el-icon><VideoCamera /></el-icon>
              声音提醒
            </div>
            <el-switch v-model="settings.soundAlert" :disabled="!isLoggedIn" />
          </div>

          <div class="setting-divider"></div>

          <div class="setting-item">
            <div class="setting-label">预警震级阈值选择</div>
            <el-select
              v-model="settings.threshold"
              placeholder="选择震级"
              class="threshold-select"
              :disabled="!isLoggedIn"
            >
              <el-option label="3.0级以上" value="3" />
              <el-option label="4.0级以上" value="4" />
              <el-option label="5.0级以上" value="5" />
              <el-option label="6.0级以上" value="6" />
              <el-option label="7.0级以上" value="7" />
            </el-select>
          </div>
        </div>
      </div>
    </div>

    <!-- 订阅管理对话框 -->
    <el-dialog v-model="dialogVisible" title="管理订阅省份" width="600px">
      <div class="province-grid">
        <div
          v-for="province in allProvinces"
          :key="province"
          :class="['province-chip', { selected: subscriptions.includes(province) }]"
          @click="toggleSubscribe(province)"
        >
          {{ province }}
          <el-icon v-if="subscriptions.includes(province)" class="check-icon"><Check /></el-icon>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSubscriptions">保存</el-button>
      </template>
    </el-dialog>

    <!-- 地震预警弹窗 -->
    <el-dialog
      v-model="alertDialogVisible"
      title="⚠️ 紧急地震预警"
      width="500px"
      :close-on-click-modal="false"
      :before-close="handleAlertClose"
    >
      <div class="alert-content">
        <div class="alert-main">
          <div class="alert-title">
            {{ currentAlert.province }} 发生 {{ currentAlert.magnitude }} 级地震
          </div>
          <div class="alert-details">
            <p>🕒 时间: {{ currentAlert.time }}</p>
            <p>📍 位置: {{ currentAlert.location }}</p>
            <p>💡 提示: {{ currentAlert.tip }}</p>
          </div>
        </div>
        <div class="alert-countdown">
          <div class="countdown-text">预计到达时间</div>
          <div class="countdown-num">{{ countdownSeconds }}秒</div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="confirmAlert">我已知晓</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Bell, VideoCamera, Check } from '@element-plus/icons-vue'

const router = useRouter()
const dialogVisible = ref(false)
const alertDialogVisible = ref(false)
const countdownSeconds = ref(25)

const currentUser = ref('')
const userRole = ref('')

const isLoggedIn = computed(() => {
  return localStorage.getItem('user_token') || localStorage.getItem('admin_token')
})

const subscriptions = ref(['四川省', '云南省'])
const allProvinces = ref([
  '四川省', '云南省', '新疆', '西藏', '青海', '甘肃',
  '陕西', '山西', '河北', '山东', '河南', '湖北',
  '湖南', '广西', '贵州', '重庆', '内蒙古', '宁夏'
])

const settings = ref({
  pushNotify: true,
  soundAlert: true,
  threshold: '5'
})

const currentAlert = ref({
  province: '',
  magnitude: '',
  time: '',
  location: '',
  tip: ''
})

onMounted(() => {
  loadUserInfo()
  loadSubscriptions()
  // 模拟订阅省份地震预警
  setTimeout(() => {
    simulateEarthquakeAlert()
  }, 3000)
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
  }
}

const loadSubscriptions = () => {
  if (!isLoggedIn.value) return

  fetch('http://127.0.0.1:5000/api/user/subscriptions', {
    credentials: 'include'
  })
  .then(res => res.json())
  .then(data => {
    if (data.code === 200) {
      subscriptions.value = data.data.map(item => item.province_name)
    }
  })
  .catch(err => console.error('加载订阅失败:', err))
}

const showSubscribeDialog = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再管理订阅')
    router.push('/login')
    return
  }
  dialogVisible.value = true
}

const toggleSubscribe = (province) => {
  const index = subscriptions.value.indexOf(province)
  if (index > -1) {
    subscriptions.value.splice(index, 1)
  } else {
    subscriptions.value.push(province)
  }
}

const removeSubscription = (province) => {
  subscriptions.value = subscriptions.value.filter(p => p !== province)
  ElMessage.success(`已取消订阅: ${province}`)
}

const saveSubscriptions = () => {
  ElMessage.success('订阅设置已保存')
  dialogVisible.value = false
}

// 模拟订阅省份地震预警弹窗
const simulateEarthquakeAlert = () => {
  // 随机选择一个订阅的省份作为预警目标
  const randomProvince = subscriptions.value[Math.floor(Math.random() * subscriptions.value.length)]

  currentAlert.value = {
    province: randomProvince,
    magnitude: '5.2',
    time: new Date().toLocaleString('zh-CN'),
    location: `${randomProvince}雅安市`,
    tip: '请当地居民注意防范，做好应急准备'
  }

  alertDialogVisible.value = true
  startCountdown()
}

// 预警弹窗倒计时
const startCountdown = () => {
  countdownSeconds.value = 25
  const timer = setInterval(() => {
    countdownSeconds.value--
    if (countdownSeconds.value <= 0) {
      clearInterval(timer)
      alertDialogVisible.value = false
      ElMessage.warning('预警时间已到，请尽快避险！')
    }
  }, 1000)
}

const handleAlertClose = () => {
  ElMessage.info('请确认已了解预警信息')
}

const confirmAlert = () => {
  alertDialogVisible.value = false
  ElMessage.success('感谢确认，请做好防范措施')
}
</script>

<style scoped>
.subscribe-page {
  min-height: calc(100vh - 60px);
  background: #f5f5f5;
}

.main-content {
  display: flex;
  gap: 20px;
  padding: 20px;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.warning-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #1890ff;
  transition: all 0.3s;
}

.warning-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateX(5px);
}

.warning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.warning-time {
  color: #909399;
  font-size: 13px;
}

.warning-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.warning-content p {
  margin: 6px 0;
  color: #606266;
  font-size: 14px;
}

.warning-tip {
  color: #f56c6c !important;
  font-weight: 500;
}

.right-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.subscribe-list {
  min-height: 120px;
  margin-bottom: 15px;
}

.subscribe-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.province-name {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
}

.manage-btn {
  width: 100%;
  height: 40px;
  font-size: 15px;
}

.login-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 30px;
  color: #909399;
  background: #f5f7fa;
  border-radius: 8px;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 30px;
}

.alert-settings {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border: 2px solid #91d5ff;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-size: 15px;
}

.setting-divider {
  height: 1px;
  background: #91d5ff;
  margin: 10px 0;
}

.threshold-select {
  width: 180px;
}

.province-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.province-chip {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  position: relative;
}

.province-chip:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}

.province-chip.selected {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 16px;
}

/* 预警弹窗样式 */
.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.alert-main {
  flex: 1;
}

.alert-title {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 15px;
}

.alert-details p {
  margin: 8px 0;
  color: #606266;
}

.alert-countdown {
  text-align: center;
  background: #fff2f0;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #ffccc7;
}

.countdown-text {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.countdown-num {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}
</style>