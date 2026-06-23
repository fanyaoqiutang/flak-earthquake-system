<template>
  <el-dialog
    v-model="visible"
    title=""
    width="650px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    custom-class="earthquake-alert-dialog"
    z-index="9999"
  >
    <div class="alert-content">
      <!-- 顶部警告标题区 -->
      <div class="alert-header">
        <div class="header-left">
          <div class="icon-wrapper">
            <el-icon class="warning-icon"><WarningFilled /></el-icon>
          </div>
          <div class="title-wrapper">
            <h2 class="alert-title">紧急地震预警</h2>
            <p class="alert-subtitle">EMERGENCY EARTHQUAKE WARNING</p>
          </div>
        </div>
        <div class="header-right">
          <span class="risk-badge" :class="{ 'high-risk': alertData.magnitude >= 5.0 }">
            {{ alertData.magnitude >= 5.0 ? '高风险' : '中风险' }}
          </span>
        </div>
      </div>

      <div class="alert-body">
        <!-- 左侧地震信息 -->
        <div class="info-section">
          <div class="magnitude-card">
            <div class="mag-circle" :class="{ 'pulse': countdown <= 10 }">
              <span class="mag-prefix">M</span>
              <span class="mag-number">{{ alertData.magnitude }}</span>
            </div>
            <div class="mag-info">
              <span class="mag-label">震级</span>
              <span class="mag-desc" v-if="alertData.magnitude >=5.0">强震风险 · 立即避险</span>
              <span class="mag-desc" v-else>中等强度 · 注意防范</span>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item" v-for="(item, index) in infoItems" :key="index">
              <div class="item-icon">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <div class="item-content">
                <span class="label">{{ item.label }}</span>
                <span class="value">{{ item.value }}</span>
              </div>
            </div>
          </div>

          <div class="tip-box">
            <div class="tip-icon-wrapper">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
            </div>
            <div class="tip-content">
              <h4 class="tip-title">安全提示</h4>
              <p class="tip-text">{{ alertData.tip }}</p>
            </div>
          </div>
        </div>

        <!-- 右侧倒计时卡片 -->
        <div class="countdown-section">
          <div class="countdown-wrapper">
            <p class="countdown-label">横波预计到达</p>
            <div class="countdown-ring" :class="{ 'urgent': countdown <= 10 }">
              <svg class="progress-ring" width="150" height="150">
                <circle
                  class="ring-bg"
                  cx="75"
                  cy="75"
                  r="65"
                />
                <circle
                  class="ring-progress"
                  cx="75"
                  cy="75"
                  r="65"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="dashoffset"
                />
              </svg>
              <div class="countdown-center">
                <span class="countdown-number">{{ countdown }}</span>
                <span class="countdown-unit">秒</span>
              </div>
            </div>
            <p class="countdown-hint" v-if="countdown <= 10">
              ️ 时间紧迫，立刻避险！
            </p>
            <p class="countdown-hint normal" v-else>
              保持冷静，准备撤离
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="footer-actions">
        <el-button
          size="large"
          @click="confirmAlert"
          class="confirm-btn"
        >
          <el-icon><CircleCheck /></el-icon>
          我已知晓，做好应急防范
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  WarningFilled,
  InfoFilled,
  CircleCheck,
  Location,
  Clock,
  MapLocation,
  Compass
} from '@element-plus/icons-vue'
import { markAlertRead } from '../API/user'

const visible = ref(false)
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

const circumference = 2 * Math.PI * 65
const dashoffset = computed(() => {
  return circumference * (1 - countdown.value / 25)
})

const infoItems = computed(() => [
  {
    icon: 'Location',
    label: '发生地区',
    value: `${alertData.value.province_name} ${alertData.value.city_name}`
  },
  {
    icon: 'Clock',
    label: '发生时间',
    value: alertData.value.earthquake_time
  },
  {
    icon: 'MapLocation',
    label: '坐标位置',
    value: `${Number(alertData.value.latitude).toFixed(4)}°N, ${Number(alertData.value.longitude).toFixed(4)}°E`
  },
  {
    icon: 'Compass',
    label: '震源深度',
    value: `${alertData.value.depth} km`
  }
])

const show = (data) => {
  if (isAlertShowing.value) {
    console.log('已有预警弹窗正在展示，忽略本次推送')
    return
  }

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
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }

  if (alertData.value.alert_id) {
    try {
      await markAlertRead(alertData.value.alert_id)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

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
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
}
:deep(.earthquake-alert-dialog .el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(220, 38, 38, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1);
  border: none;
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
:deep(.earthquake-alert-dialog .el-dialog__header) {
  display: none;
}
:deep(.earthquake-alert-dialog .el-dialog__body) {
  padding: 0;
  background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
}
:deep(.earthquake-alert-dialog .el-dialog__footer) {
  padding: 16px 28px 24px;
  background: #f9fafb;
}

.alert-content {
  width: 100%;
}

/* 头部预警标题 */
.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px 18px;
  background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%);
  border-bottom: 2px solid #fecdd3;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);
}

.warning-icon {
  font-size: 28px;
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 0 rgba(255, 255, 255, 0));
  }
  50% {
    transform: scale(1.1);
    filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.6));
  }
}

.title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.alert-title {
  margin: 0;
  font-size: 22px;
  color: #1f2937;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.alert-subtitle {
  margin: 0;
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.risk-badge {
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  background: #fef3c7;
  color: #92400e;
  border: 2px solid #fde68a;
  transition: all 0.3s ease;
}
.risk-badge.high-risk {
  background: linear-gradient(135deg, #fee2e2, #fecdd3);
  color: #b91c1c;
  border-color: #fca5a5;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
  animation: glow 2s ease-in-out infinite;
}
@keyframes glow {
  0%, 100% { box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2); }
  50% { box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4); }
}

/* 主体左右分栏 */
.alert-body {
  display: flex;
  gap: 24px;
  padding: 24px 28px;
}
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 震级卡片 */
.magnitude-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 18px;
  background: linear-gradient(135deg, #fef2f2 0%, #fff5f5 100%);
  border-radius: 16px;
  border: 2px solid #fecdd3;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.08);
}

.mag-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.3);
  position: relative;
  overflow: hidden;
}
.mag-circle::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  animation: rotate 3s linear infinite;
}
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.mag-circle.pulse {
  animation: magPulse 1s ease-in-out infinite;
}
@keyframes magPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 6px 20px rgba(220, 38, 38, 0.3); }
  50% { transform: scale(1.05); box-shadow: 0 10px 28px rgba(220, 38, 38, 0.5); }
}

.mag-prefix {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  line-height: 1;
}
.mag-number {
  font-size: 40px;
  color: white;
  font-weight: 700;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.mag-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.mag-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 600;
}
.mag-desc {
  font-size: 13px;
  color: #dc2626;
  font-weight: 600;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: white;
  border-radius: 14px;
  border: 2px solid #f3f4f6;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.info-item:hover {
  border-color: #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.item-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.item-icon .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.item-content .label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}
.item-content .value {
  color: #1f2937;
  font-weight: 600;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 避险提示框 */
.tip-box {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border-radius: 14px;
  border: 2px solid #fde68a;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1);
}

.tip-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}
.tip-icon {
  color: white;
  font-size: 20px;
}

.tip-content {
  flex: 1;
}
.tip-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: #92400e;
  font-weight: 700;
}
.tip-text {
  margin: 0;
  color: #78350f;
  font-size: 14px;
  line-height: 1.6;
}

/* 右侧倒计时独立卡片 */
.countdown-section {
  width: 200px;
  flex-shrink: 0;
}

.countdown-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 20px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 20px;
  border: 2px solid #fecdd3;
  box-shadow: 0 6px 20px rgba(220, 38, 38, 0.12);
}

.countdown-label {
  margin: 0 0 18px 0;
  font-size: 14px;
  color: #4b5563;
  font-weight: 600;
  text-align: center;
}

.countdown-ring {
  position: relative;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-ring {
  position: absolute;
  top: 0;
  left: 0;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #fecdd3;
  stroke-width: 10;
}

.ring-progress {
  fill: none;
  stroke: #dc2626;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s linear;
  filter: drop-shadow(0 0 8px rgba(220, 38, 38, 0.4));
}
.urgent .ring-progress {
  stroke: #b91c1c;
  filter: drop-shadow(0 0 12px rgba(185, 28, 28, 0.6));
}

.countdown-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  z-index: 1;
}

.countdown-number {
  font-size: 52px;
  font-weight: 700;
  color: #dc2626;
  line-height: 1;
  font-family: 'Consolas', 'Courier New', monospace;
  text-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}
.urgent .countdown-number {
  color: #b91c1c;
  animation: numberPulse 0.5s ease-in-out infinite;
}
@keyframes numberPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.countdown-unit {
  font-size: 18px;
  color: #dc2626;
  font-weight: 600;
}

.countdown-hint {
  margin-top: 16px;
  font-size: 13px;
  color: #b91c1c;
  font-weight: 600;
  text-align: center;
  line-height: 1.5;
  padding: 10px 14px;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 10px;
  border: 1px solid #fca5a5;
}
.countdown-hint.normal {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
  border-color: #d1d5db;
}

/* 底部确认按钮 */
.footer-actions {
  display: flex;
  justify-content: center;
}

.confirm-btn {
  width: 100%;
  max-width: 360px;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 14px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  color: white;
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.3);
  transition: all 0.3s ease;
}
.confirm-btn:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.4);
  transform: translateY(-2px);
}
.confirm-btn:active {
  transform: translateY(0);
}

/* 移动端适配 */
@media (max-width: 768px) {
  :deep(.earthquake-alert-dialog .el-dialog) {
    width: 90% !important;
    margin: 20px auto;
  }

  .alert-header {
    padding: 16px 20px 14px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-left {
    gap: 12px;
  }

  .icon-wrapper {
    width: 42px;
    height: 42px;
  }

  .warning-icon {
    font-size: 24px;
  }

  .alert-title {
    font-size: 20px;
  }

  .alert-subtitle {
    font-size: 10px;
  }

  .risk-badge {
    align-self: flex-end;
    padding: 5px 14px;
    font-size: 12px;
  }

  .alert-body {
    flex-direction: column;
    padding: 20px;
    gap: 20px;
  }

  .countdown-section {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .magnitude-card {
    padding: 16px;
  }

  .mag-circle {
    width: 70px;
    height: 70px;
  }

  .mag-number {
    font-size: 32px;
  }

  .countdown-ring {
    width: 140px;
    height: 140px;
  }

  .progress-ring {
    width: 140px;
    height: 140px;
  }

  .ring-bg, .ring-progress {
    r: 60;
    cx: 70;
    cy: 70;
  }

  .countdown-number {
    font-size: 48px;
  }

  :deep(.earthquake-alert-dialog .el-dialog__footer) {
    padding: 14px 20px 20px;
  }

  .confirm-btn {
    height: 48px;
    font-size: 15px;
  }
}
</style>