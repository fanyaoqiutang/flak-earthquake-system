<template>
  <div class="admin-profile-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="menu-card">
          <el-menu :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item index="dashboard">
              <el-icon><DataLine /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="earthquake">
              <el-icon><Warning /></el-icon>
              <span>地震数据管理</span>
            </el-menu-item>
            <el-menu-item index="province">
              <el-icon><Location /></el-icon>
              <span>省份管理</span>
            </el-menu-item>
            <el-menu-item index="users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>聊天内容管理</span>
            </el-menu-item>
            <el-menu-item index="feedback">
              <el-icon><Comment /></el-icon>
              <span>用户反馈处理</span>
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

          <div v-show="activeMenu === 'dashboard'" class="content-section">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon" style="background: #409eff;">
                      <el-icon :size="30"><User /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ stats.totalUsers }}</div>
                      <div class="stat-label">总用户数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon" style="background: #67c23a;">
                      <el-icon :size="30"><ChatDotRound /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ stats.todayMessages }}</div>
                      <div class="stat-label">今日新增消息</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon" style="background: #e6a23c;">
                      <el-icon :size="30"><Warning /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ stats.totalEarthquakes }}</div>
                      <div class="stat-label">地震数据总数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon" style="background: #f56c6c;">
                      <el-icon :size="30"><CircleClose /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ stats.pendingFeedbacks }}</div>
                      <div class="stat-label">待处理反馈</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div v-show="activeMenu === 'earthquake'" class="content-section">
            <div class="toolbar">
              <el-button type="primary" @click="showAddEarthquakeDialog">新增地震数据</el-button>
              <el-button @click="loadEarthquakeData">刷新数据</el-button>
            </div>

            <el-table :data="earthquakeList" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="earthquake_id" label="ID" width="80" />
              <el-table-column prop="earthquake_time" label="发生时间" width="180" />
              <el-table-column prop="province_name" label="地点" />
              <el-table-column prop="magnitude" label="震级" width="100" />
              <el-table-column prop="depth" label="深度(km)" width="100" />
              <el-table-column prop="latitude" label="纬度" width="100" />
              <el-table-column prop="longitude" label="经度" width="100" />
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="editEarthquake(row)">编辑</el-button>
                  <el-button type="danger" size="small" @click="deleteEarthquake(row.earthquake_id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-show="activeMenu === 'province'" class="content-section">
            <div class="toolbar">
              <el-button type="primary" @click="showAddProvinceDialog">新增省份</el-button>
            </div>

            <el-table :data="provinceList" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="province_id" label="ID" width="80" />
              <el-table-column prop="province_name" label="省份名称" />
              <el-table-column prop="region" label="所属地区" />
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="editProvince(row)">编辑</el-button>
                  <el-button type="danger" size="small" @click="deleteProvince(row.province_id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-show="activeMenu === 'users'" class="content-section">
            <el-table :data="userList" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="user_id" label="ID" width="80" />
              <el-table-column prop="user_account" label="用户名" />
              <el-table-column prop="last_active_time" label="最后登录时间" width="180" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'normal' ? 'success' : 'danger'">
                    {{ row.status === 'normal' ? '正常' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="250">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="viewUserDetail(row)">详情</el-button>
                  <el-button :type="row.status === 'normal' ? 'warning' : 'success'" size="small" @click="toggleUserStatus(row)">
                    {{ row.status === 'normal' ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-show="activeMenu === 'chat'" class="content-section">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="8">
                <el-card>
                  <el-statistic title="总消息数" :value="chatStats.total" />
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <el-statistic title="正常消息" :value="chatStats.normal" />
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <el-statistic title="违规消息" :value="chatStats.violation" />
                </el-card>
              </el-col>
            </el-row>

            <el-table :data="chatList" style="width: 100%;">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="发送用户" width="150" />
              <el-table-column prop="content" label="聊天内容" />
              <el-table-column prop="create_time" label="发送时间" width="180" />
              <el-table-column label="操作" width="250">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="deleteChat(row.id)">删除</el-button>
                  <el-button type="warning" size="small" @click="warnUser(row.user_id)">警告</el-button>
                  <el-button type="info" size="small" @click="muteUser(row.user_id)">禁言</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-show="activeMenu === 'feedback'" class="content-section">
            <el-table :data="feedbackList" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="user_account" label="用户" width="150" />
              <el-table-column prop="feedback_type" label="类型" width="120" />
              <el-table-column prop="content" label="反馈内容" />
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.priority === '高' ? 'danger' : row.priority === '中' ? 'warning' : 'info'">
                    {{ row.priority }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="handleFeedback(row.id)">处理</el-button>
                  <el-button type="danger" size="small" @click="deleteFeedback(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="earthquakeDialogVisible" :title="isEdit ? '编辑地震数据' : '新增地震数据'" width="600px">
      <el-form :model="earthquakeForm" label-width="100px">
        <el-form-item label="发生时间">
          <el-date-picker v-model="earthquakeForm.earthquake_time" type="datetime" />
        </el-form-item>
        <el-form-item label="省份">
          <el-select v-model="earthquakeForm.province_id" placeholder="选择省份">
            <el-option
              v-for="p in provinceList"
              :key="p.province_id"
              :label="p.province_name"
              :value="p.province_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="震级">
          <el-input-number v-model="earthquakeForm.magnitude" :min="0" :max="10" :step="0.1" />
        </el-form-item>
        <el-form-item label="深度(km)">
          <el-input-number v-model="earthquakeForm.depth" :min="0" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input-number v-model="earthquakeForm.latitude" :step="0.01" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input-number v-model="earthquakeForm.longitude" :step="0.01" />
        </el-form-item>
        <el-form-item label="描述信息">
          <el-input v-model="earthquakeForm.earthquake_message" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="earthquakeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEarthquake">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataLine, Warning, Location, User, ChatDotRound, Comment, CircleClose
} from '@element-plus/icons-vue'

const API_BASE = 'http://127.0.0.1:5000'

const activeMenu = ref('dashboard')
const menuTitle = computed(() => {
  const titles = {
    dashboard: '仪表盘',
    earthquake: '地震数据管理',
    province: '省份管理',
    users: '用户管理',
    chat: '聊天内容管理',
    feedback: '用户反馈处理'
  }
  return titles[activeMenu.value]
})

const stats = reactive({
  totalUsers: 0,
  todayMessages: 0,
  totalEarthquakes: 0,
  pendingFeedbacks: 0
})

const earthquakeList = ref([])
const provinceList = ref([])
const userList = ref([])
const chatList = ref([])
const feedbackList = ref([])

const chatStats = reactive({
  total: 0,
  normal: 0,
  violation: 0
})

const earthquakeDialogVisible = ref(false)
const isEdit = ref(false)
const earthquakeForm = reactive({
  earthquake_id: null,
  earthquake_time: '',
  province_id: '',
  magnitude: 0,
  depth: 0,
  latitude: 0,
  longitude: 0,
  earthquake_message: ''
})

onMounted(() => {
  loadDashboardStats()
  loadEarthquakeData()
  loadProvinceList()
  loadUserList()
  loadChatList()
  loadFeedbackList()
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const loadDashboardStats = async () => {
  stats.totalUsers = 100
  stats.todayMessages = 256
  stats.totalEarthquakes = 50
  stats.pendingFeedbacks = 5
}

const loadEarthquakeData = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/earthquake/list`)
    const data = await response.json()
    if (data.code === 200) {
      earthquakeList.value = data.data
    }
  } catch (error) {
    console.error('加载地震数据失败:', error)
  }
}

const loadProvinceList = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/provinces`)
    const data = await response.json()
    if (data.code === 200) {
      provinceList.value = data.data
    }
  } catch (error) {
    console.error('加载省份列表失败:', error)
  }
}

const loadUserList = async () => {
  userList.value = [
    { user_id: 1, user_account: 'testuser', last_active_time: '2026-05-26 10:00:00', status: 'normal' }
  ]
}

const loadChatList = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/user/chat/list`)
    const data = await response.json()
    if (data.code === 200) {
      chatList.value = data.data
      chatStats.total = data.data.length
      chatStats.normal = data.data.length
      chatStats.violation = 0
    }
  } catch (error) {
    console.error('加载聊天列表失败:', error)
  }
}

const loadFeedbackList = async () => {
  feedbackList.value = []
}

const showAddEarthquakeDialog = () => {
  isEdit.value = false
  Object.assign(earthquakeForm, {
    earthquake_id: null,
    earthquake_time: new Date(),
    province_id: '',
    magnitude: 0,
    depth: 0,
    latitude: 0,
    longitude: 0,
    earthquake_message: ''
  })
  earthquakeDialogVisible.value = true
}

const editEarthquake = (row) => {
  isEdit.value = true
  Object.assign(earthquakeForm, row)
  earthquakeDialogVisible.value = true
}

const saveEarthquake = () => {
  ElMessage.success('保存成功')
  earthquakeDialogVisible.value = false
  loadEarthquakeData()
}

const deleteEarthquake = (id) => {
  ElMessageBox.confirm('确定要删除这条地震数据吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadEarthquakeData()
  }).catch(() => {})
}

const showAddProvinceDialog = () => {
  ElMessage.info('新增省份功能开发中')
}

const editProvince = (row) => {
  ElMessage.info('编辑省份功能开发中')
}

const deleteProvince = (id) => {
  ElMessageBox.confirm('确定要删除这个省份吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadProvinceList()
  }).catch(() => {})
}

const viewUserDetail = (row) => {
  ElMessage.info(`查看用户 ${row.user_account} 详情`)
}

const toggleUserStatus = (row) => {
  const newStatus = row.status === 'normal' ? '禁用' : '启用'
  ElMessageBox.confirm(`确定要${newStatus}该用户吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === 'normal' ? 'disabled' : 'normal'
    ElMessage.success(`${newStatus}成功`)
  }).catch(() => {})
}

const deleteChat = (id) => {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadChatList()
  }).catch(() => {})
}

const warnUser = (userId) => {
  ElMessageBox.confirm('确定要发送警告吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('警告已发送')
  }).catch(() => {})
}

const muteUser = (userId) => {
  ElMessageBox.prompt('请输入禁言时长（小时）', '禁言用户', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^[0-9]+$/,
    inputErrorMessage: '请输入有效数字'
  }).then(({ value }) => {
    ElMessage.success(`已禁言 ${value} 小时`)
  }).catch(() => {})
}

const handleFeedback = (id) => {
  ElMessage.success('反馈已处理')
  loadFeedbackList()
}

const deleteFeedback = (id) => {
  ElMessageBox.confirm('确定要删除这条反馈吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadFeedbackList()
  }).catch(() => {})
}
</script>

<style scoped>
.admin-profile-container {
  padding: 20px;
}

.menu-card {
  position: sticky;
  top: 20px;
}

.content-card {
  min-height: 600px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.content-section {
  padding: 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
