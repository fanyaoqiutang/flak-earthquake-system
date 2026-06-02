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
            placeholder="请输入账号(3-20位)"
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

      localStorage.setItem(tokenKey, response.data[tokenKey])
      localStorage.setItem(accountKey, response.data[accountKey])
      if (response.data[idKey]) {
        localStorage.setItem(idKey, response.data[idKey])
      }
      localStorage.setItem('user_role', loginType.value)

      ElMessage.success('登录成功')

      const redirectPath = localStorage.getItem('redirect_path') || '/'
      localStorage.removeItem('redirect_path')
      router.push(redirectPath)
    }
  } catch (error) {
    console.error('登录错误:', error)
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
.login-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 480px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 26px;
  font-weight: 600;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-tabs {
  display: flex;
  margin-bottom: 30px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 14px;
  cursor: pointer;
  color: #909399;
  font-size: 15px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tab.active {
  background: #409eff;
  color: white;
  font-weight: bold;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 2px;
}

.register-btn {
  width: 100%;
  height: 46px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 2px;
  background: white;
  border: 2px solid #409eff;
  color: #409eff;
}

.register-btn:hover {
  background: #ecf5ff;
}

.test-accounts {
  margin-top: 25px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bae7ff;
}

.test-title {
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 12px;
  font-size: 14px;
}

.account-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin: 8px 0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e8e8e8;
}

.account-item:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  transform: translateX(5px);
}

.badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-right: 12px;
}

.user-badge {
  background: #e6f7ff;
  color: #1890ff;
}

.admin-badge {
  background: #fff1f0;
  color: #f5222d;
}

.account-text {
  flex: 1;
  font-family: monospace;
  color: #595959;
  font-size: 14px;
}

.arrow-icon {
  color: #1890ff;
  font-size: 16px;
}

.tips {
  margin-top: 20px;
  padding: 12px;
  background: #f6ffed;
  border-radius: 8px;
  text-align: center;
  color: #52c41a;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
