<template>
  <div class="location-audit-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>📍 待审核位置管理</h2>
          <div class="header-actions">
            <el-select v-model="filterStatus" @change="loadPendingLocations" style="width: 150px;">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="primary" @click="loadPendingLocations">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 批量操作 -->
      <div v-if="selectedRows.length > 0" class="batch-actions">
        <el-alert
          :title="`已选择 ${selectedRows.length} 项`"
          type="info"
          :closable="false"
        />
        <el-select v-model="batchProvinceId" placeholder="选择省份" style="width: 200px; margin-left: 10px;">
          <el-option
            v-for="province in provinces"
            :key="province.province_id"
            :label="province.province_name"
            :value="province.province_id"
          />
        </el-select>
        <el-button
          type="success"
          @click="handleBatchApprove"
          :disabled="!batchProvinceId"
          style="margin-left: 10px;"
        >
          批量通过
        </el-button>
      </div>

      <!-- 位置列表 -->
      <el-table
        :data="locationList"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="location_name" label="位置名称" min-width="200">
          <template #default="{ row }">
            <strong>{{ row.location_name }}</strong>
          </template>
        </el-table-column>

        <el-table-column label="出现次数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning">{{ row.occurrence_count }}次</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="最近震级" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.latest_magnitude" :type="getMagnitudeType(row.latest_magnitude)">
              {{ row.latest_magnitude }}级
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="最近时间" width="180">
          <template #default="{ row }">
            {{ row.latest_time || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="推测省份" width="150">
          <template #default="{ row }">
            {{ row.province_candidate || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="建议城市名" width="150">
          <template #default="{ row }">
            {{ row.city_candidate || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="showApproveDialog(row)"
            >
              审核
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
            <el-tag v-else :type="row.status === 'approved' ? 'success' : 'info'">
              {{ row.status === 'approved' ? '已通过' : '已拒绝' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="handlePageChange"
        layout="total, prev, pager, next"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="审核位置"
      width="500px"
    >
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="位置名称">
          <el-input v-model="currentLocation.location_name" disabled />
        </el-form-item>

        <el-form-item label="所属省份" required>
          <el-select v-model="approveForm.province_id" placeholder="请选择省份" style="width: 100%;">
            <el-option
              v-for="province in provinces"
              :key="province.province_id"
              :label="province.province_name"
              :value="province.province_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="城市名称" required>
          <el-input
            v-model="approveForm.city_name"
            placeholder="请输入城市名称"
          />
          <el-text size="small" type="info" style="margin-top: 5px;">
            建议使用：{{ currentLocation.city_candidate || currentLocation.location_name }}
          </el-text>
        </el-form-item>

        <el-form-item label="出现次数">
          <el-tag>{{ currentLocation.occurrence_count }}次</el-tag>
        </el-form-item>

        <el-form-item label="示例数据" v-if="currentLocation.sample_earthquakes?.length">
          <el-collapse>
            <el-collapse-item title="查看示例地震数据">
              <div
                v-for="(eq, index) in currentLocation.sample_earthquakes"
                :key="index"
                class="example-item"
              >
                <p><strong>时间：</strong>{{ eq.time }}</p>
                <p><strong>震级：</strong>{{ eq.magnitude }}级</p>
                <p><strong>位置：</strong>{{ eq.location }}</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleApprove">确认通过</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingLocations, approveLocation, rejectLocation, batchApproveLocations } from '@/API/admin'
import { getProvinces } from '@/API/common'

const locationList = ref([])
const provinces = ref([])
const filterStatus = ref('pending')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedRows = ref([])
const batchProvinceId = ref(null)
const dialogVisible = ref(false)
const currentLocation = ref({})
const approveForm = ref({
  city_name: '',
  province_id: null
})

onMounted(() => {
  loadPendingLocations()
  loadProvinces()
})

const loadProvinces = async () => {
  const response = await getProvinces()
  if (response.code === 200) {
    provinces.value = response.data
  }
}

const loadPendingLocations = async () => {
  const response = await getPendingLocations({
    page: currentPage.value,
    per_page: pageSize.value,
    status: filterStatus.value
  })

  if (response.code === 200) {
    locationList.value = response.data
    total.value = response.total
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadPendingLocations()
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const showApproveDialog = (row) => {
  currentLocation.value = row
  approveForm.value = {
    city_name: row.city_candidate || row.location_name,
    province_id: null
  }
  dialogVisible.value = true
}

const handleApprove = async () => {
  if (!approveForm.value.city_name || !approveForm.value.province_id) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    const response = await approveLocation(currentLocation.value.id, approveForm.value)

    if (response.code === 200) {
      ElMessage.success(response.message)
      dialogVisible.value = false
      loadPendingLocations()
    }
  } catch (error) {
    ElMessage.error('审核失败')
  }
}

const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要拒绝 "${row.location_name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await rejectLocation(row.id)

    if (response.code === 200) {
      ElMessage.success('已拒绝')
      loadPendingLocations()
    }
  } catch (error) {
    // 用户取消
  }
}

const handleBatchApprove = async () => {
  if (!batchProvinceId.value) {
    ElMessage.warning('请先选择省份')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要批量通过 ${selectedRows.value.length} 个位置吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const locationIds = selectedRows.value.map(row => row.id)
    const response = await batchApproveLocations({
      location_ids: locationIds,
      province_id: batchProvinceId.value
    })

    if (response.code === 200) {
      ElMessage.success(response.message)
      selectedRows.value = []
      loadPendingLocations()
    }
  } catch (error) {
    // 用户取消或错误
  }
}

const getMagnitudeType = (magnitude) => {
  if (magnitude >= 6) return 'danger'
  if (magnitude >= 5) return 'warning'
  return 'info'
}
</script>

<style scoped>
.location-audit-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.batch-actions {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.example-item {
  padding: 10px;
  margin-bottom: 10px;
  background-color: #f5f7fa;


}

.example-item p {
  margin: 5px 0;
}
</style>
