<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="6">
        <el-card class="menu-card" shadow="hover">
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
            <el-menu-item index="feedback">
              <el-icon><Document /></el-icon>
              <span>意见反馈</span>
            </el-menu-item>
            <el-menu-item index="messages">
              <el-icon><ChatDotRound /></el-icon>
              <span>消息中心</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="18">
        <el-card class="content-card" shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <h2>{{ menuTitle }}</h2>
            </div>
          </template>

          <div v-if="loadError" class="error-state">
            <el-empty description="加载个人信息失败，请刷新重试">
              <el-button type="primary" @click="loadUserInfo">刷新重试</el-button>
            </el-empty>
          </div>

          <!-- ============ 基础信息 ============ -->
          <div v-show="activeMenu === 'basic' && !loadError" class="content-section">
            <el-alert
              title="为保障预警账号安全，建议绑定常用邮箱，接收地震紧急推送。"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 20px;"
            />

            <el-form :model="basicForm" label-width="100px" class="basic-form" ref="basicFormRef" :rules="basicRules">
              <el-form-item label="头像" prop="avatar">
                <div class="avatar-wrapper">
                  <el-avatar :size="100" :src="basicForm.avatar || defaultAvatarUrl">
                    {{ avatarInitial }}
                  </el-avatar>
                  <div class="avatar-actions">
                    <el-upload
                      class="avatar-uploader"
                      action="#"
                      :show-file-list="false"
                      :auto-upload="false"
                      :before-upload="beforeAvatarUpload"
                      @change="handleAvatarChange"
                      accept=".jpg,.jpeg,.png"
                    >
                      <el-button size="small" type="primary">
                        <el-icon><Camera /></el-icon>
                        更换头像
                      </el-button>
                    </el-upload>
                    <el-button size="small" @click="resetAvatar" v-if="originalAvatar">重置默认</el-button>
                  </div>
                </div>
              </el-form-item>

              <el-form-item label="昵称" prop="nickname">
                <el-input
                  v-model="basicForm.nickname"
                  placeholder="请输入昵称（1-12个字符）"
                  maxlength="12"
                  show-word-limit
                  @blur="validateNickname"
                />
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="basicForm.email"
                  placeholder="请输入邮箱（用于接收预警通知）"
                />
              </el-form-item>

              <el-form-item label="预警接收方式">
                <el-checkbox-group v-model="basicForm.alertMethods">
                  <el-checkbox label="弹窗提醒">弹窗提醒</el-checkbox>
                  <el-checkbox label="邮件通知">邮件通知</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="saveBasicInfo"
                  :disabled="!hasBasicChanges"
                  :loading="savingBasic"
                >
                  保存修改
                </el-button>
                <el-button @click="resetBasicForm">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- ============ 账号安全 ============ -->
          <div v-show="activeMenu === 'security' && !loadError" class="content-section">
            <el-alert
              title="为保障预警账号安全，建议定期更换密码，绑定常用邮箱，接收地震紧急推送。"
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 20px;"
            />

            <el-form :model="securityForm" label-width="120px" class="security-form" ref="securityFormRef" :rules="securityRules">
              <el-form-item label="当前密码" prop="oldPassword">
                <el-input
                  v-model="securityForm.oldPassword"
                  type="password"
                  show-password
                  placeholder="请输入当前密码"
                />
              </el-form-item>

              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="securityForm.newPassword"
                  type="password"
                  show-password
                  placeholder="至少6位，字母+数字组合"
                  @input="checkPasswordStrength"
                />
                <div class="password-strength" v-if="securityForm.newPassword">
                  <span>密码强度：</span>
                  <el-tag :type="passwordStrengthType" size="small">{{ passwordStrengthText }}</el-tag>
                </div>
              </el-form-item>

              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="securityForm.confirmPassword"
                  type="password"
                  show-password
                  placeholder="请再次输入新密码"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleChangePassword"
                  :disabled="!canChangePassword"
                  :loading="changingPassword"
                >
                  修改密码
                </el-button>
                <el-button type="danger" @click="showDeleteConfirm">注销账号</el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3 class="section-title">绑定/解绑邮箱</h3>
            <el-form :model="emailForm" label-width="120px">
              <el-form-item label="邮箱地址">
                <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" />
              </el-form-item>
              <el-form-item label="验证码">
                <el-input v-model="emailForm.code" placeholder="请输入验证码" style="width: 200px;">
                  <template #append>
                    <el-button @click="sendEmailCode" :disabled="emailCountdown > 0">
                      {{ emailCountdown > 0 ? `${emailCountdown}s` : '获取验证码' }}
                    </el-button>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="bindEmail">绑定/解绑</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- ============ 订阅管理 ============ -->
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
                  <el-checkbox label="弹窗提醒">弹窗提醒</el-checkbox>
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

          <!-- ============ 意见反馈 ============ -->
          <div v-show="activeMenu === 'feedback'" class="content-section">
            <el-alert
              title="若遇到地震预警异常、订阅故障、功能BUG可提交反馈，工作人员会尽快处理"
              type="info"
              show-icon
              :closable="false"
              style="margin-bottom:20px"
            />

            <el-form :model="feedbackForm" label-width="100px" ref="feedbackRef" :rules="feedbackRules">
              <el-form-item label="反馈类型" prop="feedback_type">
                <el-select v-model="feedbackForm.feedback_type" placeholder="请选择反馈类型">
                  <el-option label="功能BUG" value="BUG"/>
                  <el-option label="功能建议" value="建议"/>
                  <el-option label="预警异常" value="预警问题"/>
                  <el-option label="其他问题" value="其他"/>
                </el-select>
              </el-form-item>

              <el-form-item label="紧急程度" prop="priority">
                <el-radio-group v-model="feedbackForm.priority">
                  <el-radio label="低"/>
                  <el-radio label="中"/>
                  <el-radio label="高"/>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="详细描述" prop="content">
                <el-input v-model="feedbackForm.content" type="textarea" :rows="5" placeholder="请详细描述你遇到的问题或建议"/>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="handleSubmitFeedback" :loading="feedbackLoading">提交反馈</el-button>
                <el-button @click="resetFeedback">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- ============ 消息中心 ============ -->
          <div v-show="activeMenu === 'messages'" class="content-section">
            <el-tabs v-model="messageTab" class="message-tabs">
              <!-- 历史地震预警记录 -->
              <el-tab-pane label="历史地震预警记录" name="alerts">
                <div class="message-header">
                  <span></span>
                  <el-button type="primary" size="small" @click="markAllRead">全部标记已读</el-button>
                </div>

                <el-table :data="alertMessages" style="width: 100%" v-if="alertMessages.length > 0">
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="content" label="内容" show-overflow-tooltip />
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

                <el-empty v-else description="暂无预警通知" />
              </el-tab-pane>

              <!-- 我的消息 -->
              <el-tab-pane label="我的消息" name="my-messages">
                <div class="message-header">
                  <span></span>
                </div>

                <el-table :data="myChatMessages" style="width: 100%" v-if="myChatMessages.length > 0">
                  <el-table-column prop="content" label="消息内容" show-overflow-tooltip />
                  <el-table-column prop="send_time" label="发送时间" width="180" />
                  <el-table-column label="操作" width="100">
                    <template #default="{ row }">
                      <el-button type="danger" size="small" @click="deleteMyMessage(row.id)">
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>

                <el-empty v-else description="暂无发送的消息" />
              </el-tab-pane>
            </el-tabs>
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
import { User, Lock, Bell, ChatDotRound, Camera, Document } from '@element-plus/icons-vue'

import {
  getUserInfo,
  updateUserInfo,
  changePassword as apiChangePassword,
  deleteAccount,
  getSubscriptions,
  unsubscribeProvince,
  getAlerts,
  markAlertRead,
  markAllAlertsRead,
  getAlertSettings,
  updateAlertSettings,
  submitFeedback,
  getUserChatMessages,
  deleteUserChatMessage
} from '../API/user'

const router = useRouter()

// ===================== 基础状态 =====================
const activeMenu = ref('basic')
const loading = ref(false)
const loadError = ref(false)
const savingBasic = ref(false)
const changingPassword = ref(false)
const feedbackLoading = ref(false)
const emailCountdown = ref(0)
const messageTab = ref('alerts')

const menuTitle = computed(() => {
  const titles = {
    basic: '基础信息',
    security: '账号安全',
    subscription: '订阅管理',
    feedback: '意见反馈',
    messages: '消息中心'
  }
  return titles[activeMenu.value]
})

// ===================== 基础信息 =====================
const originalData = reactive({
  avatar: '',
  nickname: '',
  email: '',
  alertMethods: []
})

const basicForm = reactive({
  avatar: '',
  nickname: '',
  email: '',
  alertMethods: ['弹窗提醒']
})

const basicFormRef = ref(null)

const basicRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 1, max: 12, message: '昵称长度1-12个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const hasBasicChanges = computed(() => {
  return (
    basicForm.avatar !== originalData.avatar ||
    basicForm.nickname !== originalData.nickname ||
    basicForm.email !== originalData.email ||
    JSON.stringify(basicForm.alertMethods) !== JSON.stringify(originalData.alertMethods)
  )
})

const avatarInitial = computed(() => {
  if (basicForm.nickname) {
    return basicForm.nickname.charAt(0).toUpperCase()
  }
  return 'U'
})

const defaultAvatarUrl = computed(() => '/default-avatar.png')
const originalAvatar = computed(() => originalData.avatar)

// ===================== 账号安全 =====================
const securityForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const securityFormRef = ref(null)

const securityRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== securityForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const passwordStrength = ref('weak')
const passwordStrengthType = computed(() => {
  const types = { weak: 'danger', medium: 'warning', strong: 'success' }
  return types[passwordStrength.value]
})
const passwordStrengthText = computed(() => {
  const texts = { weak: '弱', medium: '中', strong: '强' }
  return texts[passwordStrength.value]
})

const canChangePassword = computed(() => {
  return securityForm.oldPassword &&
         securityForm.newPassword &&
         securityForm.confirmPassword &&
         securityForm.newPassword === securityForm.confirmPassword &&
         passwordStrength.value !== 'weak'
})

// ===================== 邮箱绑定 =====================
const emailForm = reactive({
  email: '',
  code: ''
})

// ===================== 订阅管理 =====================
const subscriptions = ref([])

const alertSettings = reactive({
  frequency: '实时预警',
  methods: ['弹窗提醒'],
  soundEnabled: true,
  magnitudeThreshold: 3.0
})

// ===================== 消息中心 =====================
const alertMessages = ref([])
const myChatMessages = ref([])

// ===================== 意见反馈 =====================
const feedbackRef = ref(null)
const feedbackForm = reactive({
  feedback_type: '',
  priority: '中',
  content: ''
})

const feedbackRules = {
  feedback_type: [{ required: true, message: '请选择反馈类型', trigger: 'change' }],
  content: [{ required: true, message: '请填写反馈内容', trigger: 'blur' }]
}

// ===================== 生命周期 =====================
onMounted(() => {
  loadUserInfo()
  loadSubscriptions()
  loadAlertMessages()
  loadMyChatMessages()
  loadAlertSettings()
})

// ===================== 菜单切换 =====================
const handleMenuSelect = (index) => {
  activeMenu.value = index
}

// ===================== 基础信息方法 =====================
const loadUserInfo = async () => {
  loading.value = true
  loadError.value = false
  try {
    const response = await getUserInfo()
    if (response.code === 200) {
      const data = response.data
      basicForm.nickname = data.nickname || data.user_account
      basicForm.email = data.email || ''
      basicForm.avatar = data.avatar || ''
      basicForm.alertMethods = data.alert_methods || ['弹窗提醒']

      Object.assign(originalData, {
        avatar: basicForm.avatar,
        nickname: basicForm.nickname,
        email: basicForm.email,
        alertMethods: [...basicForm.alertMethods]
      })
    } else {
      loadError.value = true
      ElMessage.error(response.msg || '加载用户信息失败')
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    loadError.value = true
    ElMessage.error('加载用户信息失败，请检查网络')
  } finally {
    loading.value = false
  }
}

const validateNickname = () => {
  const nickname = basicForm.nickname.trim()
  if (!nickname) {
    ElMessage.warning('昵称不能为空')
    return false
  }
  if (nickname.length > 12) {
    ElMessage.warning('昵称不能超过12个字符')
    return false
  }
  return true
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG 格式的图片！')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }
  return true
}

const handleAvatarChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    basicForm.avatar = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const resetAvatar = () => {
  basicForm.avatar = ''
}

const saveBasicInfo = async () => {
  if (!validateNickname()) return

  savingBasic.value = true
  try {
    const updateData = {}

    if (basicForm.nickname !== originalData.nickname) {
      updateData.nickname = basicForm.nickname
    }
    if (basicForm.email !== originalData.email) {
      updateData.email = basicForm.email
    }
    if (basicForm.avatar !== originalData.avatar) {
      updateData.avatar = basicForm.avatar
    }
    if (JSON.stringify(basicForm.alertMethods) !== JSON.stringify(originalData.alertMethods)) {
      updateData.alert_methods = basicForm.alertMethods
    }

    if (Object.keys(updateData).length === 0) {
      ElMessage.info('没有修改的内容')
      return
    }

    const response = await updateUserInfo(updateData)
    if (response.code === 200) {
      ElMessage.success('个人信息更新成功')
      Object.assign(originalData, {
        avatar: basicForm.avatar,
        nickname: basicForm.nickname,
        email: basicForm.email,
        alertMethods: [...basicForm.alertMethods]
      })
      if (basicForm.nickname) {
        localStorage.setItem('user_account', basicForm.nickname)
      }
    } else {
      ElMessage.error(response.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存基础信息失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingBasic.value = false
  }
}

const resetBasicForm = () => {
  basicForm.avatar = originalData.avatar
  basicForm.nickname = originalData.nickname
  basicForm.email = originalData.email
  basicForm.alertMethods = [...originalData.alertMethods]
  ElMessage.info('已重置为原始数据')
}

// ===================== 账号安全方法 =====================
const checkPasswordStrength = () => {
  const password = securityForm.newPassword
  if (!password) {
    passwordStrength.value = 'weak'
    return
  }

  const hasDigit = /\d/.test(password)
  const hasLetter = /[a-zA-Z]/.test(password)
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)

  const score = [hasDigit, hasLetter, hasSpecial].filter(Boolean).length

  if (score <= 1 || password.length < 8) {
    passwordStrength.value = 'weak'
  } else if (score === 2) {
    passwordStrength.value = 'medium'
  } else {
    passwordStrength.value = 'strong'
  }
}

const handleChangePassword = async () => {
  if (!securityFormRef.value) return

  await securityFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await ElMessageBox.confirm(
        '确认修改登录密码？修改后需要重新登录',
        '确认修改',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      changingPassword.value = true
      const response = await apiChangePassword({
        old_password: securityForm.oldPassword,
        new_password: securityForm.newPassword
      })

      if (response.code === 200) {
        ElMessage.success('密码修改成功，即将跳转到登录页')
        setTimeout(() => {
          localStorage.clear()
          router.push('/login')
        }, 1500)
      } else {
        ElMessage.error(response.msg || '密码修改失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('修改密码失败:', error)
        ElMessage.error(error.response?.data?.msg || '密码修改失败')
      }
    } finally {
      changingPassword.value = false
    }
  })
}

const showDeleteConfirm = () => {
  ElMessageBox.prompt('注销账号会清空订阅、聊天记录、预警消息，数据无法恢复。请输入密码确认注销：', '警告', {
    confirmButtonText: '确定注销',
    cancelButtonText: '取消',
    inputType: 'password',
    inputPlaceholder: '请输入当前密码',
    type: 'warning'
  }).then(async ({ value: password }) => {
    if (!password) {
      ElMessage.error('请输入密码')
      return
    }

    try {
      const response = await deleteAccount({ password })
      if (response.code === 200) {
        ElMessage.success('账号已注销')
        localStorage.clear()
        router.push('/')
      } else {
        ElMessage.error(response.msg || '注销失败')
      }
    } catch (error) {
      console.error('注销账号失败:', error)
      ElMessage.error(error.response?.data?.msg || '注销失败')
    }
  }).catch(() => {})
}

// ===================== 邮箱绑定方法 =====================
const sendEmailCode = () => {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailForm.email)) {
    ElMessage.error('邮箱格式不正确')
    return
  }

  emailCountdown.value = 60
  const timer = setInterval(() => {
    emailCountdown.value--
    if (emailCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)

  ElMessage.success('验证码已发送（演示）')
}

const bindEmail = () => {
  if (!emailForm.code) {
    ElMessage.error('请输入验证码')
    return
  }

  basicForm.email = emailForm.email
  ElMessage.success('邮箱绑定成功')
  emailForm.email = ''
  emailForm.code = ''
}

// ===================== 订阅管理方法 =====================
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

// ===================== 预警设置方法 =====================
const loadAlertSettings = async () => {
  try {
    const response = await getAlertSettings()
    if (response.code === 200) {
      const data = response.data
      alertSettings.frequency = data.frequency || '实时预警'
      alertSettings.methods = data.methods || ['弹窗提醒']
      alertSettings.soundEnabled = data.sound_enabled ?? true
      alertSettings.magnitudeThreshold = data.magnitude_threshold || 3.0
    }
  } catch (error) {
    console.error('加载预警设置失败:', error)
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

// ===================== 消息中心方法 =====================
const loadAlertMessages = async () => {
  try {
    const response = await getAlerts()
    if (response.code === 200) {
      alertMessages.value = response.data.map(item => ({
        id: item.alert_id,
        title: `地震预警 - M${item.magnitude || '未知'}`,
        content: `${item.province_name || ''}${item.city_name || ''}发生${item.magnitude || ''}级地震`,
        create_time: item.earthquake_time,
        is_read: item.is_read
      }))
    }
  } catch (error) {
    console.error('加载预警消息失败:', error)
  }
}

const loadMyChatMessages = async () => {
  try {
    const response = await getUserChatMessages()
    if (response.code === 200) {
      myChatMessages.value = response.data || []
    } else {
      console.error('加载我的消息失败:', response.msg)
    }
  } catch (error) {
    console.error('加载我的消息失败:', error)
  }
}

const deleteMyMessage = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确认删除这条消息吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await deleteUserChatMessage(id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      loadMyChatMessages()
    } else {
      ElMessage.error(response.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const markRead = async (id) => {
  try {
    const response = await markAlertRead(id)
    if (response.code === 200) {
      ElMessage.success('标记成功')
      loadAlertMessages()
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
      loadAlertMessages()
    }
  } catch (error) {
    console.error('标记失败:', error)
  }
}

// ===================== 意见反馈方法 =====================
const resetFeedback = () => {
  feedbackForm.feedback_type = ''
  feedbackForm.priority = '中'
  feedbackForm.content = ''
}

const handleSubmitFeedback = async () => {
  if (!feedbackRef.value) return

  await feedbackRef.value.validate(async (valid) => {
    if (!valid) return

    feedbackLoading.value = true
    try {
      const res = await submitFeedback(feedbackForm)
      if (res.code === 200) {
        ElMessage.success('反馈提交成功，管理员将尽快处理')
        resetFeedback()
      } else {
        ElMessage.error(res.msg)
      }
    } catch (err) {
      console.error('提交反馈报错：', err)
      ElMessage.error('提交失败，请稍后重试')
    } finally {
      feedbackLoading.value = false
    }
  })
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.menu-card {
  position: sticky;
  top: 20px;
  border-radius: 8px;
}

.content-card {
  min-height: 500px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.content-section {
  padding: 10px 0;
}

.basic-form,
.security-form {
  max-width: 600px;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 15px 0;
  color: #303133;
}

.password-strength {
  margin-top: 8px;
  font-size: 12px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.message-tabs {
  min-height: 400px;
}

.message-tabs :deep(.el-tabs__header) {
  font-size: 16px;
}

.message-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  padding: 0 30px;
  height: 50px;
  line-height: 50px;
}

.message-tabs :deep(.el-tabs__content) {
  padding-top: 10px;
}

.error-state {
  padding: 40px 0;
  text-align: center;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input:hover .el-input__wrapper),
:deep(.el-input:focus-within .el-input__wrapper) {
  box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 0;
  border-radius: 4px;
}

:deep(.el-menu-item:hover) {
  background-color: #ecf5ff;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .menu-card {
    position: static;
    margin-bottom: 20px;
  }

  .avatar-wrapper {
    flex-direction: column;
    align-items: flex-start;
  }

  .basic-form,
  .security-form {
    max-width: 100%;
  }
}
</style>