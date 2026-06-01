<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="menu-card">
          <el-menu :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item index="basic">
              <el-icon><User /></el-icon>
              <span>基础信息</span>
            </el-menu-item>
            <el-menu-item index="security">
              <el-icon><Lock /></el-icon>
              <span>账号安全</span>
            </el-menu-item>
            <el-menu-item index="subscription">
              <el-icon><Bell /></el-icon>
              <span>订阅管理</span>
            </el-menu-item>
            <el-menu-item index="messages">
              <el-icon><ChatDotRound /></el-icon>
              <span>消息中心</span>
            </el-menu-item>
            <el-menu-item index="history">
              <el-icon><Document /></el-icon>
              <span>历史消息</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <h2>{{ menuTitle }}</h2>
            </div>
          </template>

          <div v-show="activeMenu === 'basic'" class="content-section">
            <el-form :model="basicForm" label-width="100px">
              <el-form-item label="头像">
                <el-upload
                  class="avatar-uploader"
                  action="#"
                  :show-file-list="false"
                  :auto-upload="false"
                  @change="handleAvatarChange"
                >
                  <el-avatar :size="100" :src="basicForm.avatar || '/default-avatar.png'">
                    {{ basicForm.nickname?.charAt(0) || 'U' }}
                  </el-avatar>
                </el-upload>
              </el-form-item>

              <el-form-item label="昵称">
                <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
              </el-form-item>

              <el-form-item label="手机号">
                <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
              </el-form-item>

              <el-form-item label="邮箱">
                <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="saveBasicInfo">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-show="activeMenu === 'security'" class="content-section">
            <el-form :model="securityForm" label-width="120px">
              <el-form-item label="当前密码">
                <el-input v-model="securityForm.oldPassword" type="password" show-password />
              </el-form-item>

              <el-form-item label="新密码">
                <el-input v-model="securityForm.newPassword" type="password" show-password />
              </el-form-item>

              <el-form-item label="确认密码">
                <el-input v-model="securityForm.confirmPassword" type="password" show-password />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="changePassword">修改密码</el-button>
                <el-button type="danger" @click="showDeleteConfirm">注销账号</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-show="activeMenu === 'subscription'" class="content-section">
            <h3>订阅的省份</h3>
            <el-table :data="subscriptions" style="width: 100%">
              <el-table-column prop="province_name" label="省份" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="cancelSubscription(row.id)">
                    取消订阅
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-divider />

            <h3>预警设置</h3>
            <el-form label-width="120px">
              <el-form-item label="预警频率">
                <el-radio-group v-model="alertSettings.frequency">
                  <el-radio label="实时预警">实时预警</el-radio>
                  <el-radio label="每日汇总">每日汇总</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="通知方式">
                <el-checkbox-group v-model="alertSettings.methods">
                  <el-checkbox label="站内信">站内信</el-checkbox>
                  <el-checkbox label="短信通知">短信通知</el-checkbox>
                  <el-checkbox label="邮件通知">邮件通知</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="声音提醒">
                <el-switch v-model="alertSettings.soundEnabled" />
              </el-form-item>

              <el-form-item label="震级阈值">
                <el-slider v-model="alertSettings.magnitudeThreshold" :min="0" :max="10" :step="0.1" show-input />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="saveAlertSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-show="activeMenu === 'messages'" class="content-section">
            <div class="message-header">
              <span>预警通知</span>
              <el-button type="primary" size="small" @click="markAllRead">全部标记已读</el-button>
            </div>

            <el-table :data="messages" style="width: 100%">
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="content" label="内容" />
              <el-table-column prop="create_time" label="时间" width="180" />
              <el-table-column prop="is_read" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_read ? 'info' : 'danger'" size="small">
                    {{ row.is_read ? '已读' : '未读' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button v-if="!row.is_read" type="primary" size="small" @click="markRead(row.id)">
                    标记已读
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-show="activeMenu === 'history'" class="content-section">
            <el-table :data="chatHistory" style="width: 100%">
              <el-table-column prop="content" label="消息内容" />
              <el-table-column prop="create_time" label="发送时间" width="180" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="deleteChatMessage(row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Bell, ChatDotRound, Document } from '@element-plus/icons-vue'
import {
  getUserInfo,
  getSubscriptions,
  unsubscribeProvince,
  getAlerts,
  markAlertRead,
  markAllAlertsRead,
  getChatList,
  getAlertSettings,
  updateAlertSettings
} from '../API/user'

const router = useRouter()

const activeMenu = ref('basic')
const menuTitle = computed(() => {
  const titles = {
    basic: '基础信息',
    security: '账号安全',
    subscription: '订阅管理',
    messages: '消息中心',
    history: '历史消息'
  }
  return titles[activeMenu.value]
})

const basicForm = reactive({
  avatar: '',
  nickname: '',
  phone: '',
  email: ''
})

const securityForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const subscriptions = ref([])
const messages = ref([])
const chatHistory = ref([])
const alertSettings = reactive({
  frequency: '实时预警',
  methods: ['站内信'],
  soundEnabled: true,
  magnitudeThreshold: 3.0
})

onMounted(() => {
  loadUserInfo()
  loadSubscriptions()
  loadMessages()
  loadChatHistory()
  loadAlertSettings()
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const loadUserInfo = async () => {
  try {
    const response = await getUserInfo()
    if (response.code === 200) {
      basicForm.nickname = response.data.user_account
      basicForm.phone = response.data.phone || ''
      basicForm.email = response.data.email || ''
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

const loadSubscriptions = async () => {
  try {
    const response = await getSubscriptions()
    if (response.code === 200) {
      subscriptions.value = response.data
    }
  } catch (error) {
    console.error('加载订阅失败:', error)
  }
}

const loadMessages = async () => {
  try {
    const response = await getAlerts()
    if (response.code === 200) {
      messages.value = response.data
    }
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

const loadChatHistory = async () => {
  try {
    const response = await getChatList()
    if (response.code === 200) {
      chatHistory.value = response.data
    }
  } catch (error) {
    console.error('加载聊天记录失败:', error)
  }
}

const loadAlertSettings = async () => {
  try {
    const response = await getAlertSettings()
    if (response.code === 200) {
      const data = response.data
      alertSettings.frequency = data.frequency || '实时预警'
      alertSettings.methods = data.methods || ['站内信']
      alertSettings.soundEnabled = data.sound_enabled ?? true
      alertSettings.magnitudeThreshold = data.magnitude_threshold || 3.0
    }
  } catch (error) {
    console.error('加载预警设置失败:', error)
  }
}

const saveBasicInfo = () => {
  ElMessage.success('基础信息保存成功')
}

const handleAvatarChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    basicForm.avatar = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const changePassword = () => {
  if (securityForm.newPassword !== securityForm.confirmPassword) {
    ElMessage.error('两次密码输入不一致')
    return
  }
  ElMessage.success('密码修改成功')
  securityForm.oldPassword = ''
  securityForm.newPassword = ''
  securityForm.confirmPassword = ''
}

const showDeleteConfirm = () => {
  ElMessageBox.confirm('确定要注销账号吗？此操作不可恢复！', '警告', {
    confirmButtonText: '确定注销',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('账号已注销')
    localStorage.clear()
    router.push('/login')
  }).catch(() => {})
}

const cancelSubscription = async (id) => {
  try {
    const response = await unsubscribeProvince(id)
    if (response.code === 200) {
      ElMessage.success('取消订阅成功')
      loadSubscriptions()
    }
  } catch (error) {
    console.error('取消订阅失败:', error)
  }
}

const saveAlertSettings = async () => {
  try {
    const response = await updateAlertSettings({
      frequency: alertSettings.frequency,
      methods: alertSettings.methods,
      sound_enabled: alertSettings.soundEnabled,
      magnitude_threshold: alertSettings.magnitudeThreshold
    })
    if (response.code === 200) {
      ElMessage.success('预警设置保存成功')
    }
  } catch (error) {
    console.error('保存预警设置失败:', error)
  }
}

const markRead = async (id) => {
  try {
    const response = await markAlertRead(id)
    if (response.code === 200) {
      ElMessage.success('标记成功')
      loadMessages()
    }
  } catch (error) {
    console.error('标记失败:', error)
  }
}

const markAllRead = async () => {
  try {
    const response = await markAllAlertsRead()
    if (response.code === 200) {
      ElMessage.success('全部标记成功')
      loadMessages()
    }
  } catch (error) {
    console.error('标记失败:', error)
  }
}

const deleteChatMessage = async (id) => {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    ElMessage.success('删除成功')
    loadChatHistory()
  }).catch(() => {})
}
</script>
