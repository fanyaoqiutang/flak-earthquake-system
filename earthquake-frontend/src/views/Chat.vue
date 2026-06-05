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
            <div v-if="isAdmin && !msg.isAdmin" class="msg-actions">
              <el-button type="danger" size="small" text @click="deleteMessage(msg)">删除</el-button>
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
          :disabled="!canChat"
          @keyup.enter="sendMessage"
        />
        <div class="input-footer">
          <el-button type="primary" @click="sendMessage" :disabled="!canChat || !newMessage.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sendChatMessage, getChatList } from '../API/user'
import { deleteChatMessage, sendAdminChatMessage } from '../API/admin'

const router = useRouter()
const newMessage = ref('')
const messageListRef = ref(null)

// 判断是否为管理员
const isAdmin = computed(() => {
  return !!localStorage.getItem('admin_token')
})

// 判断登录
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('user_token') || isAdmin.value
})

const canChat = computed(() => {
  return isLoggedIn.value
})

// 当前登录用户名
const currentUser = computed(() => {
  if (isAdmin.value) {
    return localStorage.getItem('admin_account') || '管理员'
  }
  return localStorage.getItem('user_account') || '匿名用户'
})

const messages = ref([])

// 页面加载 → 获取聊天记录
onMounted(() => {
  loadChatMessages()
})

// ====================== 加载消息（完全对照后端返回结构） ======================
const loadChatMessages = async () => {
  try {
    const response = await getChatList()
    if (response.code === 200) {
      messages.value = response.data.map(item => ({
        id: item.id,
        user: item.username,       // 后端返回：username ✅
        text: item.content,         // 后端返回：content ✅
        time: item.create_time,     // 后端已格式化好 ✅
        isAdmin: item.username === '管理员', // 后端写死管理员名称 ✅
        isSelf: (isAdmin.value && item.username === '管理员') ||
                (!isAdmin.value && item.user_id == getCurrentUserId()) // 对比 user_id ✅
      }))

      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('加载聊天记录失败:', error)
  }
}

// 获取当前登录用户ID
const getCurrentUserId = () => {
  if (isAdmin.value) {
    return null // 管理员没有user_id
  }
  return localStorage.getItem('user_id')
}

// ====================== 发送消息（完全匹配后端接收字段） ======================
const sendMessage = async () => {
  if (!canChat.value) {
    ElMessage.warning('请先以用户身份登录')
    return
  }

  if (!newMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  try {
    let response
    // 如果是管理员，使用管理员接口发送
    if (isAdmin.value) {
      response = await sendAdminChatMessage({
        content: newMessage.value
      })
    } else {
      response = await sendChatMessage({
        content: newMessage.value  // 后端接收：content ✅
      })
    }

    if (response.code === 200) {
      ElMessage.success('发送成功')
      newMessage.value = ''
      loadChatMessages() // 重新拉取最新消息
    } else {
      ElMessage.error(response.msg || '发送失败')
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请检查登录状态')
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 删除消息（仅管理员可用）
const deleteMessage = (msg) => {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteChatMessage(msg.id)
      ElMessage.success('删除成功')
      loadChatMessages() // 重新加载消息列表
    } catch (error) {
      console.error('删除消息失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
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