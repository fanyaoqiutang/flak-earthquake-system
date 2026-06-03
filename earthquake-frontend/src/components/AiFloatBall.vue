<template>
  <!-- 只在非登录页面显示 -->
  <div v-if="!isLoginPage" class="ai-float-ball" @click="openDialog">
    <div class="float-icon">AI</div>
  </div>

  <!-- AI 问答弹窗 -->
  <el-dialog v-model="visible" title="地震科普智能助手" width="540px" append-to-body>
    <template #header>
      <div class="dialog-header">
        <span>地震科普智能助手</span>
        <el-button size="small" type="danger" @click="clearChat">清空记录</el-button>
      </div>
    </template>

    <div class="chat-box">
      <div class="msg-wrap" v-for="(item, index) in msgList" :key="index">
        <!-- 用户消息 -->
        <div v-if="item.role === 'user'" class="user-row">
          <div class="user-bubble">{{ item.content }}</div>
        </div>
        <!-- AI 回复 -->
        <div v-else class="ai-row">
          <div class="ai-bubble">{{ item.content }}</div>
        </div>
      </div>
      <div v-if="loading" class="loading">AI正在思考中...</div>
    </div>

    <template #footer>
      <div class="input-area">
        <el-input
          v-model="inputText"
          placeholder="输入地震相关问题，回车快速发送"
          @keyup.enter.prevent="sendMessage"
        />
        <el-button type="primary" @click="sendMessage" style="margin-left:10px">发送</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { aiChat } from '@/API/common'

const route = useRoute()
const visible = ref(false)
const inputText = ref('')
const msgList = ref([])
const loading = ref(false)

// 判断是否是登录页面
const isLoginPage = computed(() => {
  return route.path === '/login'
})

// 打开弹窗
const openDialog = () => {
  visible.value = true
}

// 发送消息给 AI（通过后端代理）
const sendMessage = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入内容')
    return
  }

  const userMessage = inputText.value.trim()
  msgList.value.push({
    role: 'user',
    content: userMessage
  })

  inputText.value = ''
  loading.value = true

  try {
    const res = await aiChat({
      messages: msgList.value,
      model: 'deepseek-chat'
    })

    loading.value = false

    if (res.data && res.data.content) {
      msgList.value.push({
        role: 'assistant',
        content: res.data.content
      })
    } else {
      ElMessage.error('AI 回复失败')
    }
  } catch (err) {
    loading.value = false
    console.error('AI 聊天错误:', err)
    if (err.response) {
      const status = err.response.status
      if (status === 502) {
        ElMessage.error('AI 服务暂时不可用，请稍后重试')
      } else if (status === 404) {
        ElMessage.error('AI 接口未配置，请联系管理员')
      } else {
        ElMessage.error(`请求失败 (${status})`)
      }
    } else {
      ElMessage.error('网络连接失败')
    }
  }
}

// 清空聊天记录
const clearChat = () => {
  msgList.value = []
  ElMessage.success('聊天记录已清空')
}
</script>

<style scoped>
/*悬浮按钮*/
.ai-float-ball {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 9999;
  cursor: pointer;
}
.float-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg,#409EFF,#1890ff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  font-weight: bold;
  box-shadow: 0 5px 14px rgba(64,158,255,0.35);
  transition: all 0.25s ease;
}
.float-icon:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 18px rgba(64,158,255,0.45);
}

/*弹窗头部*/
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size:17px;
  font-weight:500;
}

/*聊天容器*/
.chat-box {
  max-height: 420px;
  min-height:320px;
  overflow-y: auto;
  padding:14px;
  background-color: #fafafa;
  border-radius: 10px;
}

/*单条消息外层容器，强制占满整行*/
.msg-wrap {
  width: 100%;
  margin-bottom:16px;
}
.user-row {
  width:100%;
  display:flex;
  justify-content: flex-end;
}
.ai-row {
  width:100%;
  display:flex;
  justify-content: flex-start;
}

/*气泡核心：文字自动换行，禁止横向溢出*/
.user-bubble {
  max-width:72%;
  padding:10px 14px;
  font-size:14px;
  line-height:1.6;
  border-radius:12px;
  border-bottom-right-radius:4px;
  background: #409EFF;
  color:#fff;
  /*关键：超长自动换行，不会横向溢出*/
  word-wrap: break-word;
  word-break: normal;
}
.ai-bubble {
  max-width:72%;
  padding:10px 14px;
  font-size:14px;
  line-height:1.6;
  border-radius:12px;
  border-bottom-left-radius:4px;
  background:#ffffff;
  color:#333;
  box-shadow:0 1px 6px rgba(0,0,0,0.07);
  /*关键：超长自动换行，不会横向溢出*/
  word-wrap: break-word;
  word-break: normal;
}

.loading {
  text-align:center;
  color:#999;
  padding:12px 0;
  font-size:13px;
}

/*底部输入框*/
.input-area {
  display:flex;
  align-items:center;
}
</style>