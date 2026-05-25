<template>
  <div class="chat-container">
    <!-- 消息列表区域 -->
    <div class="message-area">
      <div class="message-list">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-item"
          :class="{ self: msg.isSelf, admin: msg.isAdmin }"
        >
          <div class="avatar">
            <el-avatar :size="40" :style="{ background: msg.isAdmin ? '#f56c6c' : '#409eff' }">
              {{ msg.isAdmin ? '管' : msg.user.charAt(0) }}
            </el-avatar>
          </div>
          <div class="msg-bubble">
            <div class="msg-header">
              <span class="username">{{ msg.user }}</span>
              <span class="time">{{ msg.time }}</span>
            </div>
            <div class="msg-content">{{ msg.text }}</div>
            <!-- 管理员操作按钮 -->
            <div v-if="isAdmin" class="msg-actions">
              <el-button type="danger" size="small" text @click="reportMessage(msg)">举报</el-button>
              <el-button type="warning" size="small" text @click="muteUser(msg.user)">禁言</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 未登录提示（居中显示） -->
      <div v-if="!isLoggedIn" class="login-tip">
        <div class="tip-box">
          <p>请登录后再发言</p>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="input-area">
      <div class="input-wrapper">
        <el-input
          v-model="newMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入消息..."
          :disabled="!isLoggedIn"
        />
        <div class="input-footer">
          <el-button type="primary" @click="sendMessage" :disabled="!isLoggedIn || !newMessage.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const newMessage = ref('')
const messageListRef = ref(null)

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('user_token') || !!localStorage.getItem('admin_token')
})

const isAdmin = computed(() => {
  return !!localStorage.getItem('admin_token')
})

const currentUser = computed(() => {
  return localStorage.getItem('user_account') || localStorage.getItem('admin_account') || '匿名用户'
})

const messages = ref([
  {
    id: 1,
    user: '地震小助手',
    text: '欢迎来到地震科普交流平台！请大家理性发言，分享防震知识。',
    time: '10:00',
    isAdmin: true,
    isSelf: false
  },
  {
    id: 2,
    user: '热心网友',
    text: '今天新疆那边又有地震了，大家注意安全！',
    time: '10:15',
    isAdmin: false,
    isSelf: false
  },
  {
    id: 3,
    user: '科普达人',
    text: '地震发生时如果在室内，应该立即躲在坚固的家具下面，保护头部。',
    time: '10:20',
    isAdmin: false,
    isSelf: false
  }
])

const sendMessage = () => {
  if (!newMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  messages.value.push({
    id: Date.now(),
    user: currentUser.value,
    text: newMessage.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    isAdmin: isAdmin.value,
    isSelf: true
  })

  ElMessage.success('发送成功')
  newMessage.value = ''

  nextTick(() => {
    scrollToBottom()
  })
}

const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const reportMessage = (msg) => {
  ElMessage.success(`已举报 ${msg.user} 的消息`)
}

const muteUser = (user) => {
  ElMessage.warning(`已禁言用户: ${user}`)
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: #f5f7fa;
}

/* 消息列表区域 */
.message-area {
  flex: 1;
  position: relative;
  overflow-y: auto;
  padding: 20px;
}

.message-list {
  max-width: 1000px;
  margin: 0 auto;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

/* 自己的消息靠右 */
.message-item.self {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
}

.msg-bubble {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  max-width: 70%;
}

/* 管理员消息样式 */
.message-item.admin .msg-bubble {
  border-left: 3px solid #f56c6c;
}

/* 自己的消息气泡 */
.message-item.self .msg-bubble {
  background: #e6f7ff;
}

.msg-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.time {
  font-size: 12px;
  color: #909399;
}

.msg-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

/* 管理员操作按钮 */
.msg-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

/* 未登录提示 */
.login-tip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.tip-box {
  background: #f0f0f0;
  padding: 16px 32px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tip-box p {
  margin: 0;
  font-size: 16px;
  color: #666;
}

/* 底部输入区 */
.input-area {
  background: white;
  border-top: 1px solid #e8e8e8;
  padding: 16px 20px;
}

.input-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

.input-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>