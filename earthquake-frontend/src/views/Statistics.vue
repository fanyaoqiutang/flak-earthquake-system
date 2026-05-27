<template>
  <div class="statistics-container">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计筛选条件</span>
        </div>
      </template>

      <el-form :model="filterForm" label-width="100px" inline>
        <el-form-item label="地区选择">
          <el-select
            v-model="filterForm.province"
            placeholder="选择省份（全国则留空）"
            clearable
            @change="handleProvinceChange"
          >
            <el-option
              v-for="province in provinces"
              :key="province.id"
              :label="province.province_name"
              :value="province.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-radio-group v-model="filterForm.timeRange" @change="handleTimeRangeChange">
            <el-radio-button label="24h">24小时</el-radio-button>
            <el-radio-button label="7d">7天</el-radio-button>
            <el-radio-button label="30d">30天</el-radio-button>
            <el-radio-button label="1y">1年</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="filterForm.timeRange === 'custom'" label="自定义时间">
          <el-date-picker
            v-model="filterForm.customTimeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="震级范围">
          <el-select v-model="filterForm.magMin" placeholder="最小震级">
            <el-option label="3.0+" :value="3.0" />
            <el-option label="4.0+" :value="4.0" />
            <el-option label="5.0+" :value="5.0" />
            <el-option label="6.0+" :value="6.0" />
            <el-option label="不限" :value="0" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery" :loading="loading">
            <el-icon><Search /></el-icon>
            查询统计
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="handleExport" :disabled="!statisticsData.trend.length">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="charts-container">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>地震发生趋势（时间序列）</span>
              </div>
            </template>
            <div ref="trendChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>震级分布统计</span>
              </div>
            </template>
            <div ref="magnitudeChartRef" class="chart"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>省份地震占比</span>
              </div>
            </template>
            <div ref="provinceChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="data-card">
            <template #header>
              <div class="card-header">
                <span>统计概览</span>
              </div>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="地震总数" :value="summary.total" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="最大震级" :value="summary.maxMagnitude" :precision="1" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="平均震级" :value="summary.avgMagnitude" :precision="2" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="覆盖省份" :value="summary.provinceCount" />
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const API_BASE = 'http://127.0.0.1:5000'
const loading = ref(false)

const provinces = ref([])

const filterForm = reactive({
  province: '',
  timeRange: '7d',
  customTimeRange: [],
  magMin: 0
})

const statisticsData = reactive({
  trend: [],
  magnitude: [],
  province: []
})

const summary = reactive({
  total: 0,
  maxMagnitude: 0,
  avgMagnitude: 0,
  provinceCount: 0
})

const trendChartRef = ref(null)
const magnitudeChartRef = ref(null)
const provinceChartRef = ref(null)

let trendChart = null
let magnitudeChart = null
let provinceChart = null

onMounted(() => {
  loadProvinces()
  initCharts()
  handleQuery()
})

onBeforeUnmount(() => {
  if (trendChart) trendChart.dispose()
  if (magnitudeChart) magnitudeChart.dispose()
  if (provinceChart) provinceChart.dispose()
})

const loadProvinces = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/provinces`)
    const data = await response.json()
    if (data.code === 200) {
      provinces.value = data.data.map(item => ({
        id: item.province_id,
        province_name: item.province_name
      }))
    }
  } catch (error) {
    console.error('加载省份失败:', error)
    ElMessage.error('加载省份列表失败')
  }
}

const initCharts = () => {
  trendChart = echarts.init(trendChartRef.value)
  magnitudeChart = echarts.init(magnitudeChartRef.value)
  provinceChart = echarts.init(provinceChartRef.value)

  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  trendChart?.resize()
  magnitudeChart?.resize()
  provinceChart?.resize()
}

const handleProvinceChange = () => {
  handleQuery()
}

const handleTimeRangeChange = () => {
  if (filterForm.timeRange !== 'custom') {
    handleQuery()
  }
}

const getTimeRange = () => {
  const now = new Date()
  let startTime

  switch (filterForm.timeRange) {
    case '24h':
      startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      break
    case '7d':
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '30d':
      startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case '1y':
      startTime = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
      break
    case 'custom':
      if (filterForm.customTimeRange && filterForm.customTimeRange.length === 2) {
        return {
          start_time: filterForm.customTimeRange[0],
          end_time: filterForm.customTimeRange[1]
        }
      }
      return null
    default:
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  }

  return {
    start_time: startTime.toISOString().slice(0, 19).replace('T', ' '),
    end_time: now.toISOString().slice(0, 19).replace('T', ' ')
  }
}

const handleQuery = async () => {
  loading.value = true
  try {
    const timeRange = getTimeRange()
    if (!timeRange) {
      ElMessage.warning('请选择自定义时间范围')
      return
    }

    const params = new URLSearchParams()
    if (filterForm.province) {
      params.append('province_id', filterForm.province)
    }
    params.append('start_time', timeRange.start_time)
    params.append('end_time', timeRange.end_time)
    params.append('mag_min', filterForm.magMin || 0)

    const url = `${API_BASE}/api/statistics?${params.toString()}`
    console.log('请求URL:', url)

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    console.log('响应状态:', response.status)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log('响应数据:', data)

    if (data.code === 200) {
      statisticsData.trend = data.data.trend || []
      statisticsData.magnitude = data.data.magnitude || []
      statisticsData.province = data.data.province || []

      updateSummary()
      renderCharts()
      ElMessage.success('统计数据加载成功')
    } else {
      ElMessage.error(data.msg || '获取统计数据失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error(`查询失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const updateSummary = () => {
  const allData = statisticsData.magnitude
  summary.total = allData.reduce((sum, item) => sum + item.count, 0)
  summary.maxMagnitude = allData.length > 0 ? Math.max(...allData.map(item => item.max_mag || 0)) : 0

  let totalMag = 0
  let totalCount = 0
  allData.forEach(item => {
    totalMag += (item.avg_mag || 0) * item.count
    totalCount += item.count
  })
  summary.avgMagnitude = totalCount > 0 ? totalMag / totalCount : 0
  summary.provinceCount = statisticsData.province.length
}

const renderCharts = () => {
  renderTrendChart()
  renderMagnitudeChart()
  renderProvinceChart()
}

const renderTrendChart = () => {
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: statisticsData.trend.map(item => item.date),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '地震次数'
    },
    series: [
      {
        name: '地震次数',
        type: 'line',
        data: statisticsData.trend.map(item => item.count),
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#1890ff' },
        lineStyle: { width: 3 }
      }
    ]
  }
  trendChart.setOption(option)
}

const renderMagnitudeChart = () => {
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: statisticsData.magnitude.map(item => item.range)
    },
    yAxis: {
      type: 'value',
      name: '地震数量'
    },
    series: [
      {
        name: '地震数量',
        type: 'bar',
        data: statisticsData.magnitude.map(item => item.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ff6b6b' },
            { offset: 1, color: '#ee5a24' }
          ])
        },
        barWidth: '50%'
      }
    ]
  }
  magnitudeChart.setOption(option)
}

const renderProvinceChart = () => {
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '省份分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: statisticsData.province.map((item, index) => ({
          value: item.count,
          name: item.province_name
        }))
      }
    ]
  }
  provinceChart.setOption(option)
}

const handleReset = () => {
  filterForm.province = ''
  filterForm.timeRange = '7d'
  filterForm.customTimeRange = []
  filterForm.magMin = 0
  handleQuery()
}

const handleExport = () => {
  if (!statisticsData.trend.length) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  let csvContent = '时间,地震次数\n'
  statisticsData.trend.forEach(item => {
    csvContent += `${item.date},${item.count}\n`
  })

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `地震统计数据_${new Date().toLocaleDateString()}.csv`
  link.click()

  ElMessage.success('数据导出成功')
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart {
  height: 400px;
  width: 100%;
}

.chart-row {
  margin-top: 0;
}

.data-card {
  padding: 20px;
}

:deep(.el-statistic) {
  text-align: center;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>
