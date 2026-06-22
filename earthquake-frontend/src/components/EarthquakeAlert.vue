<template>
  <el-dialog
    v-model="visible"
    title=""
    width="700px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    custom-class="earthquake-alert-dialog"
    z-index="9999"
  >
    <div class="alert-content">
      <!-- 顶部警告标题区 -->
      <div class="alert-header">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <h2 class="alert-title">紧急地震预警</h2>
      </div>

      <div class="alert-body">
        <!-- 左侧地震信息 -->
        <div class="info-section">
          <div class="magnitude-display">
            <span class="mag-label">本次地震震级</span>
            <span class="mag-value" :class="{ 'high-risk': alertData.magnitude >= 5.0 }">
              M {{ alertData.magnitude }}
            </span>
            <span class="mag-desc" v-if="alertData.magnitude >=5.0">强震风险，请立即避险</span>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="label">发生地区</span>
              <span class="value">{{ alertData.province_name }} {{ alertData.city_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">发生时间</span>
              <span class="value">{{ alertData.earthquake_time }}</span>
            </div>
            <div class="info-item">
              <span class="label">坐标位置</span>
              <span class="value">{{ alertData.latitude }}°N, {{ alertData.longitude }}°E</span>
            </div>
            <div class="info-item">
              <span class="label">震源深度</span>
              <span class="value">{{ alertData.depth }} 千米</span>
            </div>
          </div>

          <div class="tip-box">
            <el-icon class="tip-icon"><InfoFilled /></el-icon>
            <p class="tip-text">{{ alertData.tip }}</p>
          </div>
        </div>

        <!-- 右侧倒计时卡片 -->
        <div class="countdown-section">
          <p class="countdown-label">横波预计到达倒计时</p>
          <div class="countdown-display">
            <span class="countdown-number">{{ countdown }}</span>
            <span class="countdown-unit">秒</span>
          </div>
          <p class="countdown-hint" v-if="countdown <= 10">
            剩余时间紧张，立刻避险！
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button
        type="primary"
        size="large"
        @click="confirmAlert"
        class="confirm-btn"
      >
        <el-icon><CircleCheck /></el-icon>
        我已知晓，做好应急防范
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled, InfoFilled, CircleCheck } from '@element-plus/icons-vue'
import { markAlertRead } from '../API/user'

const visible = ref(false)
// 标记当前是否已有预警弹窗展示，防止重复弹出双弹窗
const isAlertShowing = ref(false)

const alertData = ref({
  alert_id: null,
  earthquake_id: null,
  province_name: '',
  city_name: '',
  magnitude: 0,
  latitude: 0,
  longitude: 0,
  depth: 0,
  earthquake_time: '',
  message: '',
  tip: ''
})

const countdown = ref(25)
let countdownTimer = null
let audioContext = null

const show = (data) => {
  // 关键拦截：已有弹窗则直接返回，不再创建第二个弹窗
  if (isAlertShowing.value) {
    console.log('已有预警弹窗正在展示，忽略本次推送')
    return
  }

  // 先清空上一轮残留定时器、音频，杜绝多计时器、音频报错
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }

  alertData.value = data
  countdown.value = 25
  visible.value = true
  isAlertShowing.value = true

  playAlertSound()
  startCountdown()
}

const startCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }

  countdownTimer = setInterval(() => {
    countdown.value--

    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
      autoCloseAlert()
    }
  }, 1000)
}

const playAlertSound = () => {
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.value = 800
    oscillator.type = 'square'

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  } catch (error) {
    console.warn('播放提示音失败:', error)
  }
}

const confirmAlert = async () => {
  // 清空定时器
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }

  // 标记预警已读
  if (alertData.value.alert_id) {
    try {
      await markAlertRead(alertData.value.alert_id)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 关闭弹窗、释放资源、重置状态
  visible.value = false
  isAlertShowing.value = false

  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
}

const autoCloseAlert = () => {
  ElMessage.warning('倒计时结束，请尽快采取避险措施！')
  confirmAlert()
}

// 组件销毁强制清理资源
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  isAlertShowing.value = false
})

defineExpose({
  show
})
</script>

<style scoped>
/* 弹窗外层全局美化 */
:deep(.earthquake-alert-dialog .el-dialog__wrapper) {
  background: rgba(0,0,0,0.55);
}
:deep(.earthquake-alert-dialog .el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 14px 52px rgba(220, 38, 38, 0.16);
  border: none;
}
:deep(.earthquake-alert-dialog .el-dialog__header) {
  display: none;
}
/* 加大弹窗内边距，左右上下宽松 */
:deep(.earthquake-alert-dialog .el-dialog__body) {
  padding: 32px 36px 20px;
}
:deep(.earthquake-alert-dialog .el-dialog__footer) {
  padding: 16px 36px 32px;
}

.alert-content {
  width: 100%;
}

/* 头部预警标题 加大间距 */
.alert-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #fee2e2;
}

.warning-icon {
  font-size: 36px;
  color: #dc2626;
  animation: softPulse 1.6s ease-in-out infinite;
}
@keyframes softPulse {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.08); opacity: 1; }
}

.alert-title {
  margin: 0;
  font-size: 28px;
  color: #1f2937;
  font-weight: 700;
}

/* 主体左右分栏 加宽间隙 */
.alert-body {
  display: flex;
  gap: 30px;
}
.info-section {
  flex: 1;
}

/* 震级卡片 加大内边距，更宽松 */
.magnitude-display {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, #fef2f2 0%, #fef0f0 100%);
  border-radius: 16px;
  margin-bottom: 22px;
}
.mag-label {
  display: block;
  font-size: 15px;
  color: #6b7280;
  margin-bottom: 8px;
}
.mag-value {
  display: block;
  font-size: 56px;
  font-weight: 700;
  color: #dc2626;
  line-height: 1;
}
.mag-value.high-risk {
  color: #b91c1c;
}
.mag-desc {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: #dc2626;
  font-weight: 500;
}

/* 信息网格 加大单项间距与内边距 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.info-item {
  display: flex;
  flex-direction: column;
  padding: 14px 16px;
  background: #f9fafb;
  border-radius: 12px;
}
.info-item .label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 6px;
}
.info-item .value {
  color: #1f2937;
  font-weight: 500;
  font-size: 15px;
}

/* 避险提示框 宽松内边距 */
.tip-box {
  margin-top: 22px;
  padding: 18px 20px;
  background: #fffbeb;
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border-left: 4px solid #f59e0b;
}
.tip-icon {
  color: #f59e0b;
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 2px;
}
.tip-text {
  margin: 0;
  color: #92400e;
  font-size: 15px;
  line-height: 1.7;
}

/* 右侧倒计时独立卡片 加宽加高 */
.countdown-section {
  width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  background: linear-gradient(145deg, #fef2f2, #fee2e2);
  border-radius: 16px;
  border: 1px solid #fecdd3;
}
.countdown-label {
  margin: 0 0 24px 0;
  font-size: 15px;
  color: #4b5563;
  text-align: center;
}
.countdown-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.countdown-number {
  font-size: 72px;
  font-weight: 700;
  color: #dc2626;
  line-height: 1;
  font-family: 'Consolas', monospace;
}
.countdown-unit {
  font-size: 22px;
  color: #dc2626;
}
.countdown-hint {
  margin-top: 18px;
  font-size: 14px;
  color: #b91c1c;
  font-weight: 600;
  text-align: center;
  line-height: 1.6;
}

/* 底部确认按钮 */
.confirm-btn {
  width: 100%;
  height: 54px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 14px;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border: none;
}
.confirm-btn:hover {
  background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .alert-body {
    flex-direction: column;
  }
  .countdown-section {
    width: 100%;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>