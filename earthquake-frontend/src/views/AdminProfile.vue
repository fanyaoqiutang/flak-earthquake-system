<template>
  <div class="admin-profile-page">
    <div class="sidebar">
      <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          @select="handleMenuSelect"
      >
        <el-menu-item index="dashboard">
          <el-icon><Monitor /></el-icon>
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
        <el-menu-item index="user">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="chat">
          <el-icon><ChatLineRound /></el-icon>
          <span>聊天内容管理</span>
        </el-menu-item>
        <el-menu-item index="feedback">
          <el-icon><ChatDotRound /></el-icon>
          <span>用户反馈处理</span>
        </el-menu-item>
        <el-menu-item index="location-audit">
          <el-icon><DocumentChecked /></el-icon>
          <span>位置审核管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="main-content">
      <el-card class="content-card">
        <div v-if="activeMenu === 'dashboard'">
          <h2>仪表盘</h2>
          <div class="dashboard-stats">
            <el-card class="stat-card" @click="navigateTo('user')">
              <div class="stat-content">
                <div class="stat-icon blue">
                  <el-icon :size="28"><User /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData.totalUsers || 0 }}</div>
                  <div class="stat-label">总用户数</div>
                </div>
              </div>
            </el-card>
            <el-card class="stat-card" @click="navigateTo('chat')">
              <div class="stat-content">
                <div class="stat-icon green">
                  <el-icon :size="28"><ChatLineRound /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData.todayMessages || 0 }}</div>
                  <div class="stat-label">今日新增消息</div>
                </div>
              </div>
            </el-card>
            <el-card class="stat-card" @click="navigateTo('earthquake')">
              <div class="stat-content">
                <div class="stat-icon orange">
                  <el-icon :size="28"><Warning /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData.totalEarthquakes || 0 }}</div>
                  <div class="stat-label">地震数据总数</div>
                </div>
              </div>
            </el-card>
            <el-card class="stat-card" @click="navigateTo('feedback')">
              <div class="stat-content">
                <div class="stat-icon red">
                  <el-icon :size="28"><ChatDotRound /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData.pendingFeedbacks || 0 }}</div>
                  <div class="stat-label">待处理反馈</div>
                </div>
              </div>
            </el-card>
            <el-card class="stat-card" @click="navigateTo('location-audit')">
              <div class="stat-content">
                <div class="stat-icon purple">
                  <el-icon :size="28"><DocumentChecked /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData.pendingLocations || 0 }}</div>
                  <div class="stat-label">待审核位置</div>
                </div>
              </div>
            </el-card>
          </div>
        </div>

        <div v-if="activeMenu === 'earthquake'">
          <div class="section-header">
            <h2>地震数据管理</h2>
          </div>
          <el-table :data="earthquakes" v-loading="loading" style="width: 100%">
            <el-table-column prop="city_name" label="城市" width="120" />
            <el-table-column label="日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.earthquake_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="magnitude" label="震级" width="100" />
            <el-table-column label="经纬度" width="180">
              <template #default="{ row }">
                {{ row.longitude.toFixed(2) }}, {{ row.latitude.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="depth" label="深度(km)" width="120" />
            <el-table-column prop="earthquake_message" label="地震信息" min-width="200" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteEarthquake(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination
                v-model:current-page="earthquakeCurrentPage"
                v-model:page-size="earthquakePageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="earthquakeTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="handleEarthquakeSizeChange"
                @current-change="handleEarthquakePageChange"
            />
          </div>
        </div>

        <div v-if="activeMenu === 'province'">
          <div class="section-header">
            <h2>省份管理</h2>
            <el-button type="primary" @click="handleAddProvince">添加省份</el-button>
          </div>
          <el-table :data="provinces" v-loading="loading" style="width: 100%">
            <el-table-column prop="province_id" label="ID" width="80" />
            <el-table-column prop="province_name" label="省份名称" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteProvince(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

       <div v-if="activeMenu === 'user'">
          <div class="section-header">
            <h2>用户管理</h2>
          </div>
          <el-table :data="users" v-loading="loading" style="width: 100%">
            <el-table-column prop="user_id" label="ID" width="80" />
            <el-table-column prop="user_account" label="用户名" width="150" />
            <el-table-column prop="phone" label="手机号" width="150" />
            <el-table-column label="订阅省份" width="150">
              <template #default="{ row }">
                <el-tag v-for="sub in row.subscribed_provinces" :key="sub" size="small" style="margin-right: 5px; margin-bottom: 5px;">
                  {{ sub }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="注册日期" width="150">
              <template #default="{ row }">
                {{ formatDate(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="账号状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '正常' ? 'success' : 'danger'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button
                  :type="row.status === '正常' ? 'warning' : 'success'"
                  size="small"
                  @click="handleToggleStatus(row)"
                >
                  {{ row.status === '正常' ? '禁用' : '启用' }}
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteUser(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination
                v-model:current-page="userCurrentPage"
                v-model:page-size="userPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="userTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="handleUserSizeChange"
                @current-change="handleUserPageChange"
            />
          </div>
        </div>

        <div v-if="activeMenu === 'chat'">
          <div class="section-header">
            <h2>聊天内容管理</h2>
          </div>
          <el-table :data="chatRecords" v-loading="loading" style="width: 100%">
            <el-table-column label="日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户" width="120" />
            <el-table-column prop="content" label="聊天内容" min-width="400" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteChat(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
                v-model:current-page="chatCurrentPage"
                v-model:page-size="chatPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="chatTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="handleChatSizeChange"
                @current-change="handleChatPageChange"
            />
          </div>
        </div>

        <div v-if="activeMenu === 'feedback'">
          <div class="section-header">
            <h2>用户反馈处理</h2>
          </div>
          <el-table :data="feedbacks" v-loading="loading" style="width: 100%">
            <el-table-column label="日期" width="150">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="user.username" label="用户名" width="120" />
            <el-table-column prop="feedback_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.feedback_type === 'bug' ? 'danger' : 'warning'">
                  {{ row.feedback_type === 'bug' ? 'Bug' : '功能建议' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="feedback_content" label="反馈内容" min-width="250" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'resolved' ? 'success' : 'info'">
                  {{ row.status === 'pending' ? '待处理' : row.status === 'resolved' ? '已解决' : '已忽略' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleResolveFeedback(row)">标记已解决</el-button>
                <el-button v-if="row.status === 'pending'" type="info" size="small" @click="handleIgnoreFeedback(row)">忽略</el-button>
                <el-button type="danger" size="small" @click="handleDeleteFeedback(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination
                v-model:current-page="feedbackCurrentPage"
                v-model:page-size="feedbackPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="feedbackTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="handleFeedbackSizeChange"
                @current-change="handleFeedbackPageChange"
            />
          </div>
        </div>

        <div v-if="activeMenu === 'location-audit'">
          <div class="section-header">
            <h2>位置审核管理</h2>
          </div>
          <el-card style="margin-bottom: 20px;">
            <div class="stats-bar">
              <div class="stat-item">
                <span class="stat-label">待审核：</span>
                <span class="stat-value pending">{{ pendingStats.pending }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已通过：</span>
                <span class="stat-value approved">{{ pendingStats.approved }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已拒绝：</span>
                <span class="stat-value rejected">{{ pendingStats.rejected }}</span>
              </div>
              <el-button type="primary" size="small" @click="handleBatchApprove" :disabled="selectedLocations.length === 0">
                批量通过 ({{ selectedLocations.length }})
              </el-button>
            </div>
          </el-card>

          <el-table
              :data="pendingLocations"
              v-loading="loading"
              style="width: 100%"
              @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="location_name" label="位置名称" min-width="150" />
            <el-table-column prop="province_candidate" label="推测省份" width="120" />
            <el-table-column prop="city_candidate" label="建议城市名" width="120" />
            <el-table-column prop="occurrence_count" label="出现次数" width="100" />
            <el-table-column prop="latest_magnitude" label="最近震级" width="100" />
            <el-table-column label="最近时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.latest_time) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'approved' ? 'success' : 'info'">
                  {{ row.status === 'pending' ? '待审核' : row.status === 'approved' ? '已通过' : '已拒绝' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                    v-if="row.status === 'pending'"
                    type="primary"
                    size="small"
                    @click="handleApproveLocation(row)"
                >审核通过</el-button>
                <el-button
                    v-if="row.status === 'pending'"
                    type="danger"
                    size="small"
                    @click="handleRejectLocation(row)"
                >拒绝</el-button>
                <el-button
                    type="info"
                    size="small"
                    @click="handleViewSamples(row)"
                >查看示例</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-container">
            <el-pagination
                v-model:current-page="auditCurrentPage"
                v-model:page-size="auditPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="auditTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="handleAuditSizeChange"
                @current-change="handleAuditPageChange"
            />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 省份编辑对话框 -->
    <el-dialog v-model="provinceDialogVisible" :title="provinceDialogTitle" width="400px">
      <el-form :model="editProvinceForm" label-width="100px">
        <el-form-item label="省份名称">
          <el-input v-model="editProvinceForm.province_name" placeholder="请输入省份名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="provinceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProvince">保存</el-button>
      </template>
    </el-dialog>

    <!-- 位置审核对话框 -->
    <el-dialog v-model="auditDialogVisible" title="审核位置" width="600px">
      <el-form :model="approveForm" label-width="120px">
        <el-form-item label="位置名称">
          <el-input v-model="currentLocation.location_name" disabled />
        </el-form-item>
        <el-form-item label="推测省份">
          <el-input v-model="currentLocation.province_candidate" disabled />
        </el-form-item>
        <el-form-item label="选择省份" required>
          <el-select v-model="approveForm.province_id" placeholder="选择省份" style="width: 100%">
            <el-option
                v-for="province in allProvinces"
                :key="province.province_id"
                :label="province.province_name"
                :value="province.province_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="确认城市名" required>
          <el-input v-model="approveForm.city_name" placeholder="请确认或修改城市名称" />
        </el-form-item>
        <el-form-item label="出现次数">
          <span>{{ currentLocation.occurrence_count }} 次</span>
        </el-form-item>
        <el-form-item label="最近震级">
          <span>{{ currentLocation.latest_magnitude }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmApprove">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 批量审核对话框 -->
    <el-dialog v-model="batchAuditDialogVisible" title="批量审核通过" width="500px">
      <el-form :model="batchApproveForm" label-width="100px">
        <el-form-item label="选择省份" required>
          <el-select v-model="batchApproveForm.province_id" placeholder="选择省份" style="width: 100%">
            <el-option
                v-for="province in allProvinces"
                :key="province.province_id"
                :label="province.province_name"
                :value="province.province_id"
            />
          </el-select>
        </el-form-item>
        <el-alert
            title="注意：所有选中的位置将被添加到所选省份"
            type="warning"
            :closable="false"
            style="margin-bottom: 15px;"
        />
      </el-form>
      <template #footer>
        <el-button @click="batchAuditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmBatchApprove">确认批量添加</el-button>
      </template>
    </el-dialog>

    <!-- 查看示例对话框 -->
    <el-dialog v-model="samplesDialogVisible" title="示例地震数据" width="700px">
      <el-table :data="currentLocation.sample_earthquakes || []" style="width: 100%">
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.earthquake_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="magnitude" label="震级" width="80" />
        <el-table-column prop="depth" label="深度" width="80" />
        <el-table-column prop="earthquake_message" label="地震信息" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
// 移除updateUserInfo导入
import { getDashboardStats, getAdminInfo, getAllUsers, deleteUser, toggleUserStatus, getAllProvinces, deleteProvince, updateProvinceName, addProvince, getFeedbacks, updateFeedbackStatus, getPendingLocations, approveLocation, rejectLocation, batchApproveLocations } from '@/API/admin'
import {
  Monitor,
  Warning,
  Location,
  User,
  ChatLineRound,
  ChatDotRound,
  DocumentChecked
} from '@element-plus/icons-vue'

const router = useRouter()

const activeMenu = ref('dashboard')
const loading = ref(false)

const dashboardData = reactive({
  totalUsers: 0,
  todayMessages: 0,
  totalEarthquakes: 0,
  pendingFeedbacks: 0,
  pendingLocations: 0
})
const adminInfo = ref(null)

// 用户管理（完全移除编辑相关变量）
const users = ref([])
const userCurrentPage = ref(1)
const userPageSize = ref(10)
const userTotal = ref(0)
const allProvinces = ref([])

// 省份管理
const provinces = ref([])
const provinceDialogVisible = ref(false)
const provinceDialogTitle = ref('编辑省份')
const editProvinceForm = reactive({
  province_id: null,
  province_name: ''
})

// 地震数据管理
const earthquakes = ref([])
const earthquakeCurrentPage = ref(1)
const earthquakePageSize = ref(10)
const earthquakeTotal = ref(0)

// 聊天记录数据
const chatRecords = ref([])
const chatCurrentPage = ref(1)
const chatPageSize = ref(10)
const chatTotal = ref(0)

// 反馈数据
const feedbacks = ref([])
const feedbackCurrentPage = ref(1)
const feedbackPageSize = ref(10)
const feedbackTotal = ref(0)

// 位置审核数据
const pendingLocations = ref([])
const auditCurrentPage = ref(1)
const auditPageSize = ref(20)
const auditTotal = ref(0)
const selectedLocations = ref([])
const pendingStats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0
})

const auditDialogVisible = ref(false)
const currentLocation = ref({})
const approveForm = reactive({
  province_id: null,
  city_name: ''
})

const batchAuditDialogVisible = ref(false)
const batchApproveForm = reactive({
  province_id: null
})

const samplesDialogVisible = ref(false)

// 仪表盘
const fetchDashboardStats = async () => {
  try {
    const response = await getDashboardStats()
    if (response.code === 200) {
      Object.assign(dashboardData, response.data)
      await fetchPendingLocationsCount()
    } else {
      ElMessage.error(response.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}
const fetchPendingLocationsCount = async () => {
  try {
    const response = await getPendingLocations({ page: 1, per_page: 1, status: 'pending' })
    if (response.code === 200 && response.data) {
      dashboardData.pendingLocations = response.data.total || 0
    }
  } catch (error) {
    console.error('获取待审核位置数量失败:', error)
  }
}
const fetchAdminInfo = async () => {
  try {
    const response = await getAdminInfo()
    if (response.code === 200) {
      adminInfo.value = response.data
    } else {
      ElMessage.error(response.message || '获取管理员信息失败')
    }
  } catch (error) {
    console.error('获取管理员信息失败:', error)
    ElMessage.error('获取管理员信息失败')
  }
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await getAllUsers({})
    if (response.code === 200) {
      users.value = response.data
      userTotal.value = response.data.length
    } else {
      ElMessage.error(response.message || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 切换用户启用/禁用
const handleToggleStatus = async (user) => {
  const text = user.status === "正常" ? "禁用" : "启用"
  await ElMessageBox.confirm(`确定要${text}用户「${user.user_account}」吗？`, "提示", {
    type: "warning"
  })
  const res = await toggleUserStatus(user.user_id)
  if (res.code === 200) {
    ElMessage.success(`${text}成功`)
    fetchUsers()
    fetchDashboardStats()
  } else {
    ElMessage.error(res.message)
  }
}

// 获取省份列表
const fetchProvinces = async () => {
  loading.value = true
  try {
    const response = await getAllProvinces()
    if (response.code === 200) {
      provinces.value = response.data
    } else {
      ElMessage.error(response.message || '获取省份列表失败')
    }
  } catch (error) {
    console.error('获取省份列表失败:', error)
    ElMessage.error('获取省份列表失败')
  } finally {
    loading.value = false
  }
}

// 获取地震数据列表
const fetchEarthquakes = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/admin/earthquakes?page=${earthquakeCurrentPage.value}&per_page=${earthquakePageSize.value}`)
    const data = await response.json()
    if (data.code === 200) {
      earthquakes.value = data.data.items
      earthquakeTotal.value = data.data.total
    } else {
      ElMessage.error(data.message || '获取地震数据失败')
    }
  } catch (error) {
    console.error('获取地震数据失败:', error)
    ElMessage.error('获取地震数据失败')
  } finally {
    loading.value = false
  }
}

// 获取聊天记录
const fetchChatRecords = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/admin/chat-records?page=${chatCurrentPage.value}&per_page=${chatPageSize.value}`)
    const data = await response.json()
    if (data.code === 200) {
      chatRecords.value = data.data.items
      chatTotal.value = data.data.total
    } else {
      ElMessage.error(data.message || '获取聊天记录失败')
    }
  } catch (error) {
    console.error('获取聊天记录失败:', error)
    ElMessage.error('获取聊天记录失败')
  } finally {
    loading.value = false
  }
}

// 获取反馈列表
const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const response = await getFeedbacks({
      page: feedbackCurrentPage.value,
      per_page: feedbackPageSize.value
    })
    if (response.code === 200) {
      feedbacks.value = response.data.items
      feedbackTotal.value = response.data.total
    } else {
      ElMessage.error(response.message || '获取反馈列表失败')
    }
  } catch (error) {
    console.error('获取反馈列表失败:', error)
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

// 获取待审核位置列表
const fetchPendingLocations = async () => {
  loading.value = true
  try {
    const response = await getPendingLocations({
      page: auditCurrentPage.value,
      per_page: auditPageSize.value,
      status: 'pending'
    })
    if (response.code === 200) {
      pendingLocations.value = response.data.items
      auditTotal.value = response.data.total
      pendingStats.pending = response.data.stats?.pending || 0
      pendingStats.approved = response.data.stats?.approved || 0
      pendingStats.rejected = response.data.stats?.rejected || 0
    } else {
      ElMessage.error(response.message || '获取待审核位置失败')
    }
  } catch (error) {
    console.error('获取待审核位置失败:', error)
    ElMessage.error('获取待审核位置失败')
  } finally {
    loading.value = false
  }
}

// 删除用户
const handleDeleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${user.user_account} 吗？`, '警告', {
      type: 'warning'
    })
    const response = await deleteUser(user.user_id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      fetchUsers()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

// 删除省份
const handleDeleteProvince = async (province) => {
  try {
    await ElMessageBox.confirm(`确定要删除省份 ${province.province_name} 吗？`, '警告', {
      type: 'warning'
    })
    const response = await deleteProvince(province.province_id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      fetchProvinces()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除省份失败:', error)
      ElMessage.error('删除省份失败')
    }
  }
}

// 编辑省份
const handleEditProvince = (province) => {
  provinceDialogTitle.value = '编辑省份'
  editProvinceForm.province_id = province.province_id
  editProvinceForm.province_name = province.province_name
  provinceDialogVisible.value = true
}

// 添加省份
const handleAddProvince = () => {
  provinceDialogTitle.value = '添加省份'
  editProvinceForm.province_id = null
  editProvinceForm.province_name = ''
  provinceDialogVisible.value = true
}

// 保存省份
const handleSaveProvince = async () => {
  try {
    let response
    if (editProvinceForm.province_id) {
      response = await updateProvinceName(editProvinceForm.province_id, editProvinceForm.province_name)
    } else {
      response = await addProvince(editProvinceForm.province_name)
    }
    if (response.code === 200) {
      ElMessage.success(editProvinceForm.province_id ? '更新成功' : '添加成功')
      provinceDialogVisible.value = false
      fetchProvinces()
    } else {
      ElMessage.error(response.message || (editProvinceForm.province_id ? '更新失败' : '添加失败'))
    }
  } catch (error) {
    console.error('保存省份失败:', error)
    ElMessage.error(editProvinceForm.province_id ? '更新省份失败' : '添加省份失败')
  }
}

// 删除地震数据
const handleDeleteEarthquake = async (earthquake) => {
  try {
    await ElMessageBox.confirm('确定要删除该地震数据吗？', '警告', {
      type: 'warning'
    })
    const response = await fetch(`/api/admin/earthquakes/${earthquake.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('删除成功')
      fetchEarthquakes()
      fetchDashboardStats()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除地震数据失败:', error)
      ElMessage.error('删除地震数据失败')
    }
  }
}

// 删除聊天记录
const handleDeleteChat = async (record) => {
  try {
    await ElMessageBox.confirm('确定要删除该聊天记录吗？', '警告', {
      type: 'warning'
    })
    const response = await fetch(`/api/admin/chat-records/${record.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('删除成功')
      fetchChatRecords()
      fetchDashboardStats()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除聊天记录失败:', error)
      ElMessage.error('删除聊天记录失败')
    }
  }
}

// 标记反馈已解决
const handleResolveFeedback = async (feedback) => {
  try {
    const response = await updateFeedbackStatus(feedback.id, 'resolved')
    if (response.code === 200) {
      ElMessage.success('已标记为已解决')
      fetchFeedbacks()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('更新反馈状态失败:', error)
    ElMessage.error('操作失败')
  }
}

// 忽略反馈
const handleIgnoreFeedback = async (feedback) => {
  try {
    const response = await updateFeedbackStatus(feedback.id, 'ignored')
    if (response.code === 200) {
      ElMessage.success('已忽略')
      fetchFeedbacks()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('更新反馈状态失败:', error)
    ElMessage.error('操作失败')
  }
}

// 删除反馈
const handleDeleteFeedback = async (feedback) => {
  try {
    await ElMessageBox.confirm('确定要删除该反馈吗？', '警告', {
      type: 'warning'
    })
    const response = await fetch(`/api/admin/feedbacks/${feedback.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('删除成功')
      fetchFeedbacks()
      fetchDashboardStats()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除反馈失败:', error)
      ElMessage.error('删除反馈失败')
    }
  }
}

// 审核通过位置
const handleApproveLocation = async (location) => {
  currentLocation.value = location
  approveForm.province_id = null
  approveForm.city_name = location.city_candidate || location.location_name
  const response = await getAllProvinces()
  if (response.code === 200) {
    allProvinces.value = response.data
  }
  auditDialogVisible.value = true
}

// 确认审核通过
const handleConfirmApprove = async () => {
  if (!approveForm.province_id || !approveForm.city_name) {
    ElMessage.warning('请选择省份并确认城市名称')
    return
  }
  try {
    const response = await approveLocation(currentLocation.value.id, approveForm)
    if (response.code === 200) {
      ElMessage.success('审核通过，城市已添加')
      auditDialogVisible.value = false
      fetchPendingLocations()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '审核失败')
    }
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error('审核失败')
  }
}

// 拒绝位置
const handleRejectLocation = async (location) => {
  try {
    await ElMessageBox.confirm(`确定要拒绝位置"${location.location_name}"吗？`, '警告', {
      type: 'warning'
    })
    const response = await rejectLocation(location.id)
    if (response.code === 200) {
      ElMessage.success('已拒绝')
      fetchPendingLocations()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 批量审核
const handleBatchApprove = () => {
  if (selectedLocations.value.length === 0) {
    ElMessage.warning('请先选择要审核的位置')
    return
  }
  batchAuditDialogVisible.value = true
}

// 确认批量审核
const handleConfirmBatchApprove = async () => {
  if (!batchApproveForm.province_id) {
    ElMessage.warning('请选择省份')
    return
  }
  try {
    const locationIds = selectedLocations.value.map(loc => loc.id)
    const response = await batchApproveLocations({
      location_ids: locationIds,
      province_id: batchApproveForm.province_id
    })
    if (response.code === 200) {
      ElMessage.success(`成功添加 ${response.data.added_count} 个城市`)
      batchAuditDialogVisible.value = false
      fetchPendingLocations()
      fetchDashboardStats()
    } else {
      ElMessage.error(response.message || '批量审核失败')
    }
  } catch (error) {
    console.error('批量审核失败:', error)
    ElMessage.error('批量审核失败')
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedLocations.value = selection
}

// 查看示例数据
const handleViewSamples = (location) => {
  currentLocation.value = location
  samplesDialogVisible.value = true
}

// 分页处理
const handleUserSizeChange = (size) => {
  userPageSize.value = size
  fetchUsers()
}
const handleUserPageChange = (page) => {
  userCurrentPage.value = page
  fetchUsers()
}
const handleEarthquakeSizeChange = (size) => {
  earthquakePageSize.value = size
  fetchEarthquakes()
}
const handleEarthquakePageChange = (page) => {
  earthquakeCurrentPage.value = page
  fetchEarthquakes()
}
const handleChatSizeChange = (size) => {
  chatPageSize.value = size
  fetchChatRecords()
}
const handleChatPageChange = (page) => {
  chatCurrentPage.value = page
  fetchChatRecords()
}
const handleFeedbackSizeChange = (size) => {
  feedbackPageSize.value = size
  fetchFeedbacks()
}
const handleFeedbackPageChange = (page) => {
  feedbackCurrentPage.value = page
  fetchFeedbacks()
}
const handleAuditSizeChange = (size) => {
  auditPageSize.value = size
  fetchPendingLocations()
}
const handleAuditPageChange = (page) => {
  auditCurrentPage.value = page
  fetchPendingLocations()
}

// 菜单选择处理
const handleMenuSelect = (index) => {
  activeMenu.value = index
  switch (index) {
    case 'user': fetchUsers(); break
    case 'province': fetchProvinces(); break
    case 'earthquake': fetchEarthquakes(); break
    case 'chat': fetchChatRecords(); break
    case 'feedback': fetchFeedbacks(); break
    case 'location-audit': fetchPendingLocations(); break
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 导航到指定模块
const navigateTo = (menu) => {
  activeMenu.value = menu
  switch (menu) {
    case 'user': fetchUsers(); break
    case 'province': fetchProvinces(); break
    case 'earthquake': fetchEarthquakes(); break
    case 'chat': fetchChatRecords(); break
    case 'feedback': fetchFeedbacks(); break
    case 'location-audit': fetchPendingLocations(); break
  }
}

onMounted(async () => {
  await fetchDashboardStats()
  await fetchAdminInfo()
})
</script>

<style scoped>
.admin-profile-page {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 240px;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  padding: 20px 0;
}

.admin-menu {
  border-right: none;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.content-card {
  min-height: calc(100vh - 48px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue {
  color: #409eff;
  background: #ecf5ff;
}

.stat-icon.green {
  color: #67c23a;
  background: #f0f9eb;
}

.stat-icon.orange {
  color: #e6a23c;
  background: #fdf6ec;
}

.stat-icon.red {
  color: #f56c6c;
  background: #fef0f0;
}

.stat-icon.purple {
  color: #9c27b0;
  background: #f3e5f5;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.stats-bar {
  display: flex;
  gap: 30px;
  align-items: center;
}

.stat-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.stat-value.pending {
  color: #e6a23c;
}

.stat-value.approved {
  color: #67c23a;
}

.stat-value.rejected {
  color: #909399;
}
</style>
