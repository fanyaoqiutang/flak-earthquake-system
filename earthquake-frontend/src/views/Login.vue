<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>地震预警与科普平台</h1>
        <p>登录后即可使用完整功能</p>
      </div>

      <div class="login-tabs">
        <div
          :class="['tab', { active: loginType === 'user' }]"
          @click="loginType = 'user'"
        >
          <el-icon><User /></el-icon>
          <span>普通用户</span>
        </div>
        <div
          :class="['tab', { active: loginType === 'admin' }]"
          @click="loginType = 'admin'"
        >
          <el-icon><Setting /></el-icon>
          <span>管理员</span>
        </div>
      </div>

      <el-form :model="form" class="login-form">
        <el-form-item>
          <el-input
            v-model="form.account"
            placeholder="请输入用户名(3-20位)"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码(至少6位)"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="loginType === 'admin'">
          <el-input
            v-model="form.adminKey"
            placeholder="请输入管理密钥"
            prefix-icon="Key"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            @click="handleLogin"
            :loading="loading"
          >
            登 录
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button
            size="large"
            class="register-btn"
            @click="handleRegister"
            :loading="loading"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="test-accounts">
        <p class="test-title">📌 测试账号 (直接点击使用)</p>
        <div class="account-item" @click="quickLogin('testuser', '123456', 'user')">
          <span class="badge user-badge">用户</span>
          <span class="account-text">testuser / 123456</span>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
        <div class="account-item" @click="quickLogin('admin', '123456', 'admin')">
          <span class="badge admin-badge">管理</span>
          <span class="account-text">admin / 123456</span>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="tips">
        <el-icon><InfoFilled /></el-icon>
        <span>不登录也可以浏览所有页面，登录后才能使用交互功能</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Key, Setting, ArrowRight, InfoFilled } from '@element-plus/icons-vue'
import { userLogin as userLoginAPI, userRegister as userRegisterAPI } from '../API/user'
import { adminLogin as adminLoginAPI, adminRegister as adminRegisterAPI } from '../API/admin'

const router = useRouter()
const loginType = ref('user')
const loading = ref(false)

const form = reactive({
  account: '',
  password: '',
  adminKey: ''
})

const quickLogin = async (account, password, type) => {
  loginType.value = type
  form.account = account
  form.password = password
  await handleLogin()
}

const handleLogin = async () => {
  if (!form.account || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  if (loginType.value === 'admin' && !form.adminKey) {
    ElMessage.warning('请输入管理密钥')
    return
  }

  loading.value = true

  try {
    let response

    if (loginType.value === 'user') {
      response = await userLoginAPI({
        user_account: form.account,
        password: form.password
      })
    } else {
      response = await adminLoginAPI({
        admin_account: form.account,
        password: form.password,
        admin_key: form.adminKey
      })
    }

    if (response.code === 200) {
      const tokenKey = loginType.value === 'user' ? 'user_token' : 'admin_token'
      const accountKey = loginType.value === 'user' ? 'user_account' : 'admin_account'
      const idKey = loginType.value === 'user' ? 'user_id' : 'admin_id'

      // 保存登录信息
      localStorage.setItem(tokenKey, response.data[tokenKey])
      localStorage.setItem(accountKey, response.data[accountKey])
      if (response.data[idKey]) {
        localStorage.setItem(idKey, response.data[idKey])
      }
      localStorage.setItem('user_role', loginType.value)

      console.log(`✅ 登录成功 - 角色: ${loginType.value}, Token: ${response.data[tokenKey].substring(0, 8)}...`)

      ElMessage.success('登录成功')

      // 根据角色跳转到不同页面
      const redirectPath = localStorage.getItem('redirect_path') ||
                          (loginType.value === 'admin' ? '/admin/profile' : '/')
      localStorage.removeItem('redirect_path')

      // 延迟跳转，确保 token 已保存
      setTimeout(() => {
        router.push(redirectPath)
      }, 300)
    }
  } catch (error) {
    console.error('登录错误:', error)
    // 错误信息已在 request.js 中显示
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!form.account || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  if (form.account.length < 3 || form.account.length > 20) {
    ElMessage.warning('账号长度必须是3-20位')
    return
  }

  if (form.password.length < 6) {
    ElMessage.warning('密码长度至少6位')
    return
  }

  if (loginType.value === 'admin' && !form.adminKey) {
    ElMessage.warning('请输入管理密钥')
    return
  }

  loading.value = true

  try {
    let response

    if (loginType.value === 'user') {
      response = await userRegisterAPI({
        user_account: form.account,
        password: form.password
      })
    } else {
      response = await adminRegisterAPI({
        admin_account: form.account,
        password: form.password,
        admin_key: form.adminKey
      })
    }

    if (response.code === 200) {
      ElMessage.success(response.msg)
      form.account = ''
      form.password = ''
      form.adminKey = ''
    }
  } catch (error) {
    console.error('注册错误:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 背景更换：极简干净浅灰，去掉渐变 */
.login-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 16px;
}

/* 登录卡片加宽，最大宽度620，左右留白减少，内容区域更大 */
.login-box {
  background: #ffffff;
  padding: 44px 48px;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 620px;
}

/* 头部标题区域 */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-header h1 {
  color: #1f2937;
  margin: 0 0 10px;
  font-size: 28px;
  font-weight: 650;
  letter-spacing: 1px;
}

.login-header p {
  color: #6b7280;
  font-size: 14px;
}

/* 身份切换标签美化 */
.login-tabs {
  display: flex;
  margin-bottom: 32px;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 16px 0;
  cursor: pointer;
  color: #6b7280;
  font-size: 15px;
  transition: all 0.26s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tab:hover:not(.active) {
  background: #f9fafb;
}

.tab.active {
  background: #1f2937;
  color: #ffffff;
  font-weight: 600;
}

/* 表单整体间距 */
.login-form {
  margin-top: 4px;
}

/* 登录按钮主样式 深色匹配简约风格 */
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 2px;
  border-radius: 10px;
  background: #1f2937;
  border: none;
}

.login-btn:hover {
  background: #111827 !important;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  height: 48px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 2px;
  background: #ffffff;
  border: 1.8px solid #1f2937;
  color: #1f2937;
  border-radius: 10px;
}

.register-btn:hover {
  background: #f3f4f6 !important;
}

/* 测试账号区域 */
.test-accounts {
  margin-top: 28px;
  padding: 18px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.test-title {
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 14px;
  font-size: 14px;
}

.account-item {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  margin: 10px 0 0;
  background: #ffffff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.24s ease;
  border: 1px solid #e2e8f0;
}

.account-item:hover {
  background: #f3f4f6;
  border-color: #1f2937;
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.badge {
  padding: 5px 11px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 14px;
}

.user-badge {
  background: #eff6ff;
  color: #1d4ed8;
}

.admin-badge {
  background: #fef2f2;
  color: #dc2626;
}

.account-text {
  flex: 1;
  font-family: 'Consolas', monospace;
  color: #374151;
  font-size: 14px;
}

.arrow-icon {
  color: #4b5563;
  font-size: 17px;
  transition: transform 0.2s;
}

.account-item:hover .arrow-icon {
  transform: translateX(3px);
}

/* 底部提示文字 */
.tips {
  margin-top: 24px;
  padding: 13px 16px;
  background: #f0fdf4;
  border-radius: 10px;
  text-align: center;
  color: #16a34a;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 输入框全局微调 */
:deep(.el-input__inner) {
  height: 48px;
  border-radius: 10px;
  font-size: 15px;
}
</style>