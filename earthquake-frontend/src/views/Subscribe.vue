<template>
  <div class="subscribe-page">
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧预警列表 -->
      <div class="left-panel">
        <div v-if="!isLoggedIn" class="login-hint">
          <el-alert
            title="登录后查看订阅省份的地震预警"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
        <div v-else-if="subscribedProvinceIds.length === 0" class="subscribe-hint">
          <el-alert
            title="请先订阅省份以查看地震预警"
            type="warning"
            :closable="false"
            show-icon
          />
          <el-button type="primary" @click="showSubscribeDialog" style="margin-top: 10px;">
            管理订阅省份
          </el-button>
        </div>
        <template v-else>
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else-if="earthquakeList.length === 0" class="empty-warning">
            <el-empty description="您订阅的省份暂无地震预警信息" />
          </div>
          <div
            v-else
            class="warning-item"
            v-for="eq in earthquakeList"
            :key="eq.earthquake_id || eq.time"
          >
            <div class="warning-header">
              <span class="warning-time">{{ formatTime(eq.earthquake_time) }}</span>
              <el-tag type="danger" size="small">M{{ eq.magnitude }}</el-tag>
            </div>
            <div class="warning-content">
              <h4>{{ getWarningTitle(eq) }}</h4>
              <p>震源深度: {{ eq.depth }}KM | 经纬度: {{ eq.latitude }}°N, {{ eq.longitude }}°E</p>
              <p class="warning-tip">⚠️ 请当地居民注意防范,做好应急准备</p>
            </div>
          </div>

          <!-- 分页组件 -->
          <div v-if="earthquakeList.length > 0 && total > pageSize" class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[8, 16, 24]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </template>
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
                <span class="province-name">{{ sub.province_name }}</span>
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

          <!-- 开发测试按钮 -->
          <div class="setting-divider"></div>
          <div class="setting-item" style="justify-content: center;">
            <el-button
              type="warning"
              size="small"
              @click="testAlert"
              :disabled="!isLoggedIn || subscribedProvinceIds.length === 0"
            >
              🧪 测试预警弹窗
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 订阅管理对话框 - 按地区分类 -->
    <el-dialog
      v-model="dialogVisible"
      title="省份订阅（多选）"
      width="800px"
      :z-index="3000"
      destroy-on-close
      class="subscribe-dialog"
    >
      <div class="region-list" v-loading="loadingRegions">
        <div
          v-for="region in regionData"
          :key="region.region_name"
          class="region-section"
        >
          <!-- 地区标题栏 -->
          <div class="region-header">
            <div class="region-title">
              <span class="region-name">{{ region.region_name }}</span>
              <el-checkbox
                :model-value="isRegionAllSelected(region)"
                :indeterminate="isRegionPartiallySelected(region)"
                @change="toggleRegion(region)"
                class="select-all-checkbox"
              >
                全选
              </el-checkbox>
            </div>
          </div>

          <!-- 省份网格 -->
          <div class="province-grid">
            <div
              v-for="province in region.province_list"
              :key="province.province_id"
              class="province-item"
            >
              <el-checkbox
                :model-value="selectedProvinceIds.includes(province.province_id)"
                @change="toggleProvince(province)"
              >
                {{ province.province_name }}
              </el-checkbox>
            </div>
          </div>
        </div>

        <el-empty v-if="regionData.length === 0" description="暂无地区数据" />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div class="selected-count">
            已选择 <span class="count-num">{{ selectedProvinceIds.length }}</span> 个省份
          </div>
          <div class="dialog-buttons">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveSubscriptions" :loading="saving">保存</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 全局预警弹窗组件 -->
    <EarthquakeAlert ref="alertRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Lock, Bell, VideoCamera, Check } from '@element-plus/icons-vue'
import {
  getSubscriptions,
  subscribeBatch,
  unsubscribeProvince,
  getAlertSettings,
  updateAlertSettings
} from '../API/user'
import { getEarthquakeList, simulateEarthquakeAlert } from '../API/common'
import EarthquakeAlert from '../components/EarthquakeAlert.vue'

const router = useRouter()
const dialogVisible = ref(false)
const alertDialogVisible = ref(false)
const countdownSeconds = ref(25)
const saving = ref(false)
const loadingRegions = ref(false)
const loading = ref(false)

const currentUser = ref('')
const userRole = ref('')
const earthquakeList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(8)

// 预警相关
const lastCheckTime = ref(null)
const pollingTimer = ref(null)
const hasNewAlert = ref(false)

const isLoggedIn = computed(() => {
  return localStorage.getItem('user_token') || localStorage.getItem('admin_token')
})

const subscriptions = ref([])
const subscribedProvinceIds = ref([])
const regionData = ref([])
const selectedProvinceIds = ref([])

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

// 内联省份地区数据
const defaultRegionData = [
  {
    region_name: "华北地区",
    province_list: [
      { province_id: 1, province_name: "北京市" },
      { province_id: 2, province_name: "天津市" },
      { province_id: 3, province_name: "河北省" },
      { province_id: 4, province_name: "山西省" },
      { province_id: 5, province_name: "内蒙古自治区" }
    ]
  },
  {
    region_name: "东北地区",
    province_list: [
      { province_id: 6, province_name: "辽宁省" },
      { province_id: 7, province_name: "吉林省" },
      { province_id: 8, province_name: "黑龙江省" }
    ]
  },
  {
    region_name: "华东地区",
    province_list: [
      { province_id: 9, province_name: "上海市" },
      { province_id: 10, province_name: "江苏省" },
      { province_id: 11, province_name: "浙江省" },
      { province_id: 12, province_name: "安徽省" },
      { province_id: 13, province_name: "福建省" },
      { province_id: 14, province_name: "江西省" },
      { province_id: 15, province_name: "山东省" }
    ]
  },
  {
    region_name: "华中地区",
    province_list: [
      { province_id: 16, province_name: "河南省" },
      { province_id: 17, province_name: "湖北省" },
      { province_id: 18, province_name: "湖南省" }
    ]
  },
  {
    region_name: "华南地区",
    province_list: [
      { province_id: 19, province_name: "广东省" },
      { province_id: 20, province_name: "广西壮族自治区" },
      { province_id: 21, province_name: "海南省" }
    ]
  },
  {
    region_name: "西南地区",
    province_list: [
      { province_id: 22, province_name: "重庆市" },
      { province_id: 23, province_name: "四川省" },
      { province_id: 24, province_name: "贵州省" },
      { province_id: 25, province_name: "云南省" },
      { province_id: 26, province_name: "西藏自治区" }
    ]
  },
  {
    region_name: "西北地区",
    province_list: [
      { province_id: 27, province_name: "陕西省" },
      { province_id: 28, province_name: "甘肃省" },
      { province_id: 29, province_name: "青海省" },
      { province_id: 30, province_name: "宁夏回族自治区" },
      { province_id: 31, province_name: "新疆维吾尔自治区" }
    ]
  },
  {
    region_name: "港澳台地区",
    province_list: [
      { province_id: 32, province_name: "台湾省" },
      { province_id: 33, province_name: "香港特别行政区" },
      { province_id: 34, province_name: "澳门特别行政区" }
    ]
  }
]

onMounted(() => {
  loadUserInfo()
  regionData.value = defaultRegionData
  if (isLoggedIn.value) {
    loadSubscriptions()
    loadAlertSettings()
  }
  loadEarthquakeList()

  // 启动预警轮询（每30秒检查一次）
  startAlertPolling()
})

onUnmounted(() => {
  stopAlertPolling()
})

const startAlertPolling = () => {
  if (!isLoggedIn.value || subscribedProvinceIds.value.length === 0) {
    console.log('⚠️ 未登录或未订阅，不启动预警轮询')
    return
  }

  console.log('🔔 启动预警轮询，间隔30秒')
  lastCheckTime.value = new Date()

  pollingTimer.value = setInterval(() => {
    checkForNewAlerts()
  }, 30000)
}

const stopAlertPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
    console.log('️ 停止预警轮询')
  }
}

const checkForNewAlerts = async () => {
  if (!isLoggedIn.value || subscribedProvinceIds.value.length === 0) {
    return
  }

  try {
    console.log('🔍 检查新地震预警...', new Date().toLocaleTimeString())

    const response = await getEarthquakeList({ limit: 50 })
    if (response.code === 200) {
      const allData = Array.isArray(response.data) ? response.data : []

      const subscribedEarthquakes = allData.filter(eq =>
        subscribedProvinceIds.value.includes(getProvinceIdByName(eq.province_name))
      )

      const newAlerts = subscribedEarthquakes.filter(eq => {
        if (!lastCheckTime.value) return false

        const eqTime = new Date(eq.earthquake_time)
        return eqTime > lastCheckTime.value &&
               parseFloat(eq.magnitude) >= parseFloat(settings.value.threshold)
      })

      if (newAlerts.length > 0) {
        const latestAlert = newAlerts.sort((a, b) =>
          new Date(b.earthquake_time) - new Date(a.earthquake_time)
        )[0]

        console.log('🚨 发现新预警！', latestAlert)

        showEarthquakeAlert(latestAlert)
        sendBrowserNotification(latestAlert)

        if (settings.value.soundAlert) {
          playAlertSound()
        }
      }

      lastCheckTime.value = new Date()
    }
  } catch (err) {
    console.error('检查新预警失败:', err)
  }
}

const showEarthquakeAlert = (eq) => {
  currentAlert.value = {
    province: eq.province_name,
    city: eq.city_name,
    magnitude: eq.magnitude,
    time: eq.earthquake_time,
    location: `${eq.province_name}${eq.city_name || '某地'} (${eq.latitude}°N, ${eq.longitude}°E)`,
    depth: eq.depth,
    tip: `震源深度${eq.depth}KM，请当地居民注意防范，做好应急准备`
  }

  alertDialogVisible.value = true
  startCountdown()
  hasNewAlert.value = true
}

const sendBrowserNotification = (eq) => {
  if ('Notification' in window && Notification.permission === 'granted') {
    const notification = new Notification(`⚠️ ${eq.province_name}发生${eq.magnitude}级地震`, {
      body: `时间: ${eq.earthquake_time}\n地点: ${eq.province_name}${eq.city_name || ''}\n震源深度: ${eq.depth}KM\n请立即采取避险措施！`,
      icon: '/favicon.svg',
      tag: 'earthquake-alert',
      requireInteraction: true
    })

    notification.onclick = () => {
      window.focus()
      notification.close()
    }
  } else if ('Notification' in window && Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        sendBrowserNotification(eq)
      }
    })
  }
}

const playAlertSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.value = 800
    oscillator.type = 'sine'

    gainNode.gain.setValueAtTime(0.5, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  } catch (err) {
    console.log('播放提示音失败:', err)
  }
}

const loadEarthquakeList = async () => {
  loading.value = true
  try {
    if (isLoggedIn.value && subscribedProvinceIds.value.length > 0) {
      const response = await getEarthquakeList({ limit: 100 })
      if (response.code === 200) {
        const allData = Array.isArray(response.data) ? response.data : []

        const filteredData = allData.filter(eq =>
          subscribedProvinceIds.value.includes(getProvinceIdByName(eq.province_name))
        )

        total.value = filteredData.length

        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        earthquakeList.value = filteredData.slice(start, end)

        console.log('✅ 已加载订阅省份地震列表:', earthquakeList.value)
        console.log('总数:', total.value, '当前页:', currentPage.value, '每页:', pageSize.value)
        console.log('订阅省份IDs:', subscribedProvinceIds.value)

        if (filteredData.length > 0) {
          const latestTime = new Date(filteredData[0].earthquake_time)
          if (!lastCheckTime.value || latestTime > lastCheckTime.value) {
            lastCheckTime.value = latestTime
          }
        }
      } else {
        ElMessage.error('加载地震数据失败')
      }
    } else {
      earthquakeList.value = []
      total.value = 0
    }
  } catch (err) {
    console.error('加载地震列表失败:', err)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const getProvinceIdByName = (provinceName) => {
  if (!provinceName) return null

  for (const region of defaultRegionData) {
    for (const province of region.province_list) {
      if (province.province_name === provinceName) {
        return province.province_id
      }
    }
  }
  return null
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadEarthquakeList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadEarthquakeList()
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return timeStr
}

const getWarningTitle = (eq) => {
  const provinceName = eq.province_name || ''
  const cityName = eq.city_name || ''

  if (cityName) {
    return `${provinceName}${cityName}发生${eq.magnitude}级地震`
  }
  if (provinceName) {
    return `${provinceName}发生${eq.magnitude}级地震`
  }
  return `未知地点发生${eq.magnitude}级地震`
}

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

const loadSubscriptions = async () => {
  if (!isLoggedIn.value) return

  try {
    const response = await getSubscriptions()
    if (response.code === 200) {
      subscriptions.value = Array.isArray(response.data) ? response.data : []
      selectedProvinceIds.value = subscriptions.value.map(item => item.province_id)

      subscribedProvinceIds.value = [...selectedProvinceIds.value]

      console.log('✅ 已订阅省份:', subscribedProvinceIds.value)

      stopAlertPolling()
      startAlertPolling()

      loadEarthquakeList()
    }
  } catch (err) {
    console.error('加载订阅失败:', err)
    selectedProvinceIds.value = []
    subscribedProvinceIds.value = []
  }
}

const loadAlertSettings = async () => {
  if (!isLoggedIn.value) return

  try {
    const response = await getAlertSettings()
    if (response.code === 200) {
      const data = response.data
      settings.value.pushNotify = data.alert_frequency === '实时预警'
      settings.value.soundAlert = data.alert_methods?.includes('站内信') || true
      settings.value.threshold = String(data.magnitude_threshold || 5)
      console.log('✅ 预警设置:', data)
    }
  } catch (err) {
    console.error('加载预警设置失败:', err)
  }
}

const showSubscribeDialog = async () => {
  const hasUserToken = localStorage.getItem('user_token')
  const hasAdminToken = localStorage.getItem('admin_token')

  console.log('点击管理订阅省份 - 当前登录状态:', {
    hasUserToken: !!hasUserToken,
    hasAdminToken: !!hasAdminToken
  })

  if (!hasUserToken && !hasAdminToken) {
    ElMessage.warning('请先登录后再管理订阅')
    router.push('/login')
    return
  }

  if (hasAdminToken && !hasUserToken) {
    ElMessage.warning('请使用普通用户账号登录后再管理订阅')
    return
  }

  try {
    dialogVisible.value = true
    console.log('对话框已打开')
  } catch (error) {
    console.error('打开对话框失败:', error)
    ElMessage.error('打开对话框失败')
  }
}

const isRegionAllSelected = (region) => {
  if (!Array.isArray(selectedProvinceIds.value) || region.province_list.length === 0) return false
  return region.province_list.every(p => selectedProvinceIds.value.includes(p.province_id))
}

const isRegionPartiallySelected = (region) => {
  if (!Array.isArray(selectedProvinceIds.value)) return false
  const selectedCount = region.province_list.filter(p => selectedProvinceIds.value.includes(p.province_id)).length
  return selectedCount > 0 && selectedCount < region.province_list.length
}

const toggleRegion = (region) => {
  if (!Array.isArray(selectedProvinceIds.value)) {
    selectedProvinceIds.value = []
  }

  const allSelected = isRegionAllSelected(region)

  if (allSelected) {
    region.province_list.forEach(p => {
      const index = selectedProvinceIds.value.indexOf(p.province_id)
      if (index > -1) {
        selectedProvinceIds.value.splice(index, 1)
      }
    })
  } else {
    region.province_list.forEach(p => {
      if (!selectedProvinceIds.value.includes(p.province_id)) {
        selectedProvinceIds.value.push(p.province_id)
      }
    })
  }
}

const toggleProvince = (province) => {
  if (!Array.isArray(selectedProvinceIds.value)) {
    selectedProvinceIds.value = []
  }

  const index = selectedProvinceIds.value.indexOf(province.province_id)
  if (index > -1) {
    selectedProvinceIds.value.splice(index, 1)
  } else {
    selectedProvinceIds.value.push(province.province_id)
  }
}

const removeSubscription = async (sub) => {
  try {
    await unsubscribeProvince(sub.id)
    ElMessage.success(`已取消订阅: ${sub.province_name}`)

    const index = subscribedProvinceIds.value.indexOf(sub.province_id)
    if (index > -1) {
      subscribedProvinceIds.value.splice(index, 1)
    }

    loadSubscriptions()
  } catch (err) {
    console.error('取消订阅失败:', err)
    ElMessage.error('取消订阅失败')
  }
}

const saveSubscriptions = async () => {
  try {
    saving.value = true
    await subscribeBatch({ province_ids: selectedProvinceIds.value })

    subscribedProvinceIds.value = [...selectedProvinceIds.value]

    ElMessage.success('订阅设置已保存')
    dialogVisible.value = false

    currentPage.value = 1

    stopAlertPolling()
    startAlertPolling()

    loadSubscriptions()
  } catch (err) {
    console.error('保存订阅失败:', err)
    ElMessage.error('保存订阅失败')
  } finally {
    saving.value = false
  }
}

const alertRef = ref(null)

const simulateEarthquakeAlertFn = async () => {
  if (subscriptions.value.length === 0) return

  const randomSub = subscriptions.value[Math.floor(Math.random() * subscriptions.value.length)]

  try {
    const response = await simulateEarthquakeAlert({
      province_id: randomSub.province_id,
      magnitude: 5.2,
      depth: 10,
      latitude: 30.0 + Math.random() * 5,
      longitude: 100.0 + Math.random() * 10,
      earthquake_message: `【模拟演练】${randomSub.province_name}某地发生5.2级地震`
    })

    if (response.code === 200 && response.data) {
      if (alertRef.value) {
        alertRef.value.show(response.data)
      }
    }
  } catch (error) {
    console.error('模拟预警失败:', error)
    ElMessage.error('模拟预警失败，请稍后重试')
  }
}

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
  hasNewAlert.value = false
}

// 测试预警弹窗（开发用）
const testAlert = async () => {
  if (subscriptions.value.length === 0) {
    ElMessage.warning('请先订阅省份')
    return
  }

  const randomSub = subscriptions.value[Math.floor(Math.random() * subscriptions.value.length)]

  try {
    const response = await simulateEarthquakeAlert({
      province_id: randomSub.province_id,
      magnitude: 5.2,
      depth: 10,
      latitude: 30.0 + Math.random() * 5,
      longitude: 100.0 + Math.random() * 10,
      earthquake_message: `【测试演练】${randomSub.province_name}测试市发生5.2级地震`
    })

    if (response.code === 200 && response.data) {
      if (alertRef.value) {
        alertRef.value.show(response.data)
      }
    }
  } catch (error) {
    console.error('测试预警失败:', error)
    ElMessage.error('测试预警失败，请稍后重试')
  }
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
  height: calc(100vh - 60px);
  overflow: hidden;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.left-panel::-webkit-scrollbar {
  display: none;
}

.loading-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-warning {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.login-hint, .subscribe-hint {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.subscribe-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

.right-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  flex-shrink: 0;
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

.region-list {
  max-height: 500px;
  overflow-y: auto;
  padding: 0 10px;
}

.region-section {
  margin-bottom: 24px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
}

.region-section:last-child {
  margin-bottom: 0;
}

.region-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
}

.region-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.region-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.region-name::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 16px;
  background: #409eff;
  border-radius: 2px;
}

.select-all-checkbox {
  font-size: 14px;
  color: #409eff;
}

.province-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  padding-left: 12px;
}

.province-item {
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.province-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.selected-count {
  font-size: 14px;
  color: #606266;
}

.count-num {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  margin: 0 4px;
}

.dialog-buttons {
  display: flex;
  gap: 12px;
}

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
