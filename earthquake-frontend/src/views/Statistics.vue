<template>
  <div class="statistics-container">
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计筛选条件</span>
          <el-tag
            v-if="riskLevel.level"
            :type="riskLevel.color === '#F56C6C' ? 'danger' : riskLevel.color === '#E6A23C' ? 'warning' : 'success'"
            effect="dark"
            size="large"
            class="risk-tag"
          >
            {{ riskLevel.text }}
          </el-tag>
        </div>
      </template>

      <el-form :model="filterForm" label-width="100px" inline class="filter-form">
        <div class="filter-group">
          <el-form-item label="地区选择">
            <el-select
              v-model="filterForm.province"
              placeholder="全国（默认）"
              clearable
              style="width: 200px"
            >
              <el-option label="全国" value="" />
              <el-option-group
                v-for="group in provinceGroups"
                :key="group.region_name"
                :label="group.region_name"
              >
                <el-option
                  v-for="province in group.province_list"
                  :key="province.province_id"
                  :label="province.province_name"
                  :value="province.province_id"
                />
              </el-option-group>
            </el-select>
          </el-form-item>

          <el-form-item label="震级范围">
            <el-select v-model="filterForm.magMin" placeholder="全部" style="width: 120px">
              <el-option label="全部" :value="0" />
              <el-option label="3.0~3.9" :value="3.0" />
              <el-option label="4.0~4.9" :value="4.0" />
              <el-option label="5.0~5.9" :value="5.0" />
              <el-option label="6.0+" :value="6.0" />
            </el-select>
          </el-form-item>
        </div>

        <div class="filter-divider"></div>

        <div class="filter-group">
          <el-form-item label="时间范围">
            <el-radio-group v-model="filterForm.timeRange" @change="handleTimeRangeChange">
              <el-radio-button label="24h">24小时</el-radio-button>
              <el-radio-button label="7d">7天</el-radio-button>
              <el-radio-button label="30d">30天</el-radio-button>
              <el-radio-button label="1y">1年</el-radio-button>
              <el-radio-button label="custom">自定义</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="filterForm.timeRange === 'custom'" label="起止日期">
            <el-date-picker
              v-model="filterForm.customTimeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 380px"
            />
          </el-form-item>
        </div>

        <div class="filter-actions">
          <el-button type="primary" @click="handleQuery" :loading="loading">
            <el-icon><Search /></el-icon>
            查询统计
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="showExportDialog" :disabled="!statisticsData.trend.length">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </el-form>
    </el-card>

    <div class="charts-container">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>地震发生趋势（时间序列）</span>
                <el-tooltip content="点击节点可查看详情" placement="top">
                  <el-icon><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
            </template>
            <div v-loading="loading" ref="trendChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>震级分布统计</span>
              </div>
            </template>
            <div v-loading="loading" ref="magnitudeChartRef" class="chart"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>省份地震占比</span>
              </div>
            </template>
            <div v-loading="loading" ref="provinceChartRef" class="chart"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="summary-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>统计概览</span>
              </div>
            </template>
            <el-row :gutter="20">
              <el-col :xs="12" :sm="6">
                <div class="summary-item">
                  <div class="summary-icon" style="background: #E8F4FF;">
                    <el-icon color="#409EFF"><TrendCharts /></el-icon>
                  </div>
                  <div class="summary-content">
                    <div class="summary-label">地震总数</div>
                    <div class="summary-value">{{ summary.total }}</div>
                    <div class="summary-compare" :class="getCompareClass(summary.comparison.total_compare)">
                      {{ formatCompare(summary.comparison.total_compare) }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="summary-item">
                  <div class="summary-icon" :style="{ background: summary.maxMagnitude >= 5.0 ? '#FEF0F0' : '#F4F4F5' }">
                    <el-icon :color="summary.maxMagnitude >= 5.0 ? '#F56C6C' : '#909399'"><Warning /></el-icon>
                  </div>
                  <div class="summary-content">
                    <div class="summary-label">最大震级</div>
                    <div class="summary-value" :style="{ color: summary.maxMagnitude >= 5.0 ? '#F56C6C' : '' }">
                      {{ summary.maxMagnitude.toFixed(1) }}
                    </div>
                    <div class="summary-compare" :class="getCompareClass(summary.comparison.max_compare, true)">
                      {{ formatCompare(summary.comparison.max_compare, '级') }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="summary-item">
                  <div class="summary-icon" style="background: '#F0F9FF';">
                    <el-icon color="#67C23A"><Histogram /></el-icon>
                  </div>
                  <div class="summary-content">
                    <div class="summary-label">平均震级</div>
                    <div class="summary-value">{{ summary.avgMagnitude.toFixed(2) }}</div>
                    <div class="summary-compare" :class="getCompareClass(summary.comparison.avg_compare)">
                      {{ formatCompare(summary.comparison.avg_compare, '级') }}
                    </div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="summary-item">
                  <div class="summary-icon" style="background: '#FAF5FF';">
                    <el-icon color="#9C27B0"><MapLocation /></el-icon>
                  </div>
                  <div class="summary-content">
                    <div class="summary-label">覆盖省份</div>
                    <div class="summary-value">{{ summary.provinceCount }}</div>
                    <div class="summary-compare" :class="getCompareClass(summary.comparison.province_compare)">
                      {{ formatCompare(summary.comparison.province_compare, '个') }}
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="exportDialogVisible" title="导出数据" width="500px">
      <el-form label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportFormat">
            <el-radio label="excel">Excel（推荐）</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="exportContent">
            <el-checkbox label="raw">原始地震明细</el-checkbox>
            <el-checkbox label="charts">图表截图</el-checkbox>
            <el-checkbox label="summary">统计指标汇总</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleExport">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Search, Refresh, Download, InfoFilled,
  TrendCharts, Warning, Histogram, MapLocation
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getProvinces, getEarthquakeStatistics, getProvincesGroup } from '../API/common'

const loading = ref(false)
const exportDialogVisible = ref(false)
const exportFormat = ref('excel')
const exportContent = ref(['raw', 'summary'])

const provinces = ref([])
const provinceGroups = ref([])

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
  provinceCount: 0,
  comparison: {
    total_compare: 0,
    max_compare: 0,
    avg_compare: 0,
    province_compare: 0
  }
})

const riskLevel = reactive({
  level: 'low',
  text: '低风险',
  color: '#67C23A'
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
  window.removeEventListener('resize', handleResize)
})

const loadProvinces = async () => {
  try {
    const response = await getProvincesGroup()
    if (response.code === 200) {
      provinceGroups.value = response.data

      const allProvinces = []
      response.data.forEach(group => {
        allProvinces.push(...group.province_list)
      })
      provinces.value = allProvinces
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

  trendChart.on('click', handleTrendClick)
  magnitudeChart.on('click', handleMagnitudeClick)
  provinceChart.on('click', handleProvinceClick)
}

const handleResize = () => {
  trendChart?.resize()
  magnitudeChart?.resize()
  provinceChart?.resize()
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

    const params = {
      start_time: timeRange.start_time,
      end_time: timeRange.end_time,
      mag_min: filterForm.magMin || 0
    }

    if (filterForm.province) {
      params.province_id = filterForm.province
    }

    const response = await getEarthquakeStatistics(params)

    if (response.code === 200) {
      statisticsData.trend = response.data.trend || []
      statisticsData.magnitude = response.data.magnitude || []
      statisticsData.province = response.data.province || []

      summary.total = response.data.summary.total
      summary.maxMagnitude = response.data.summary.max_magnitude
      summary.avgMagnitude = response.data.summary.avg_magnitude
      summary.provinceCount = response.data.summary.province_count
      summary.comparison = response.data.summary.comparison

      riskLevel.level = response.data.risk_level.level
      riskLevel.text = response.data.risk_level.text
      riskLevel.color = response.data.risk_level.color

      renderCharts()

      if (statisticsData.trend.length === 0) {
        ElMessage.info('未匹配到符合条件的地震数据，请更换筛选条件')
      }
    } else {
      ElMessage.error(response.msg || '获取统计数据失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error(`查询失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderTrendChart()
  renderMagnitudeChart()
  renderProvinceChart()
}

const renderTrendChart = () => {
  if (statisticsData.trend.length === 0) {
    showEmptyChart(trendChart, '该时间段暂无地震记录')
    return
  }

  const hasHighMag = statisticsData.trend.some(item => item.max_mag >= 5.0)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: function(params) {
        const data = params[0]
        const item = statisticsData.trend[data.dataIndex]
        let html = `<div style="padding: 5px;">`
        html += `<div style="font-weight: bold; margin-bottom: 5px;">${item.date}</div>`
        html += `<div>地震次数: ${item.count} 次</div>`
        html += `<div>最大震级: ${item.max_mag.toFixed(1)} 级</div>`
        if (item.provinces && item.provinces.length > 0) {
          html += `<div>涉及省份: ${item.provinces.join(', ')}</div>`
        }
        html += `</div>`
        return html
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: statisticsData.trend.map(item => item.date),
      axisLabel: {
        rotate: 45,
        fontSize: 11,
        color: '#999'
      }
    },
    yAxis: {
      type: 'value',
      name: '地震次数',
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#E8E8E8'
        }
      }
    },
    series: [
      {
        name: '地震次数',
        type: 'line',
        data: statisticsData.trend.map((item, index) => ({
          value: item.count,
          itemStyle: {
            color: item.max_mag >= 5.0 ? '#F56C6C' : '#1890ff'
          }
        })),
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: {
            type: 'dashed',
            color: '#909399',
            width: 1.5
          },
          label: {
            position: 'end',
            formatter: '均值: {c}'
          },
          data: [{
            yAxis: statisticsData.trend.reduce((sum, item) => sum + item.count, 0) / statisticsData.trend.length
          }]
        },
        itemStyle: {
          color: '#1890ff'
        },
        lineStyle: { width: 3 }
      }
    ]
  }
  trendChart.setOption(option)
}

const renderMagnitudeChart = () => {
  if (statisticsData.magnitude.length === 0) {
    showEmptyChart(magnitudeChart, '该震级范围暂无地震记录')
    return
  }

  const getColorByRange = (range) => {
    if (range.startsWith('3.')) return '#FFA940'
    if (range.startsWith('4.')) return '#FF7A45'
    if (range.startsWith('5.')) return '#FF4D4F'
    if (range.startsWith('6.')) return '#CF1322'
    return '#A8071A'
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        const data = params[0]
        const item = statisticsData.magnitude[data.dataIndex]
        return `${item.range}<br/>数量: ${item.count} 次<br/>最大: ${item.max_mag.toFixed(1)} 级<br/>平均: ${item.avg_mag.toFixed(2)} 级`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: statisticsData.magnitude.map(item => item.range),
      axisLabel: {
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '地震数量',
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#E8E8E8'
        }
      }
    },
    series: [
      {
        name: '地震数量',
        type: 'bar',
        data: statisticsData.magnitude.map(item => ({
          value: item.count,
          itemStyle: {
            color: getColorByRange(item.range)
          }
        })),
        label: {
          show: true,
          position: 'top',
          fontSize: 12,
          fontWeight: 'bold'
        },
        barWidth: '50%'
      }
    ]
  }
  magnitudeChart.setOption(option)
}

const renderProvinceChart = () => {
  if (statisticsData.province.length === 0) {
    showEmptyChart(provinceChart, '该地区暂无地震记录')
    return
  }

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        const item = statisticsData.province[params.dataIndex]
        const percentage = ((item.count / statisticsData.province.reduce((sum, p) => sum + p.count, 0)) * 100).toFixed(1)
        return `${params.name}<br/>地震次数: ${item.count} 次<br/>占比: ${percentage}%<br/>最大震级: ${item.max_mag.toFixed(1)} 级`
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      type: 'scroll',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '省份分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}',
          fontSize: 11
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: statisticsData.province.map((item, index) => ({
          value: item.count,
          name: item.province_name,
          itemStyle: {
            opacity: item.count >= 3 ? 1 : 0.7
          }
        }))
      }
    ]
  }
  provinceChart.setOption(option)
}

const showEmptyChart = (chart, message) => {
  const option = {
    graphic: {
      elements: [{
        type: 'text',
        left: 'center',
        top: 'middle',
        style: {
          text: message,
          fill: '#999',
          fontSize: 16
        }
      }]
    }
  }
  chart.setOption(option)
}

const handleTrendClick = (params) => {
  console.log('趋势图点击:', params)
}

const handleMagnitudeClick = (params) => {
  const item = statisticsData.magnitude[params.dataIndex]
  if (item && item.count > 0) {
    ElMessage.info(`已选择震级范围: ${item.range}`)
  }
}

const handleProvinceClick = (params) => {
  const provinceName = params.name
  const province = provinces.value.find(p => p.province_name === provinceName)
  if (province) {
    filterForm.province = province.province_id
    handleQuery()
    ElMessage.success(`已锁定省份: ${provinceName}`)
  }
}

const handleReset = () => {
  filterForm.province = ''
  filterForm.timeRange = '7d'
  filterForm.customTimeRange = []
  filterForm.magMin = 0

  ElMessage.success('已重置所有筛选条件')
  handleQuery()
}

const showExportDialog = () => {
  exportDialogVisible.value = true
}

const handleExport = () => {
  if (!statisticsData.trend.length) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  const timestamp = new Date().toLocaleDateString('zh-CN').replace(/\//g, '')
  const provinceText = filterForm.province ? provinces.value.find(p => p.province_id === filterForm.province)?.province_name || '全国' : '全国'
  const magText = filterForm.magMin > 0 ? `${filterForm.magMin}级以上` : '全部震级'
  const fileName = `${filterForm.timeRange}_${provinceText}_${magText}_地震统计_${timestamp}`

  let csvContent = '时间,地震次数,最大震级\n'
  statisticsData.trend.forEach(item => {
    csvContent += `${item.date},${item.count},${item.max_mag}\n`
  })

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${fileName}.csv`
  link.click()

  exportDialogVisible.value = false
  ElMessage.success('数据导出成功')
}

const getCompareClass = (value, isMax = false) => {
  if (value === 0) return ''
  if (isMax) {
    return value > 0 ? 'compare-up-danger' : 'compare-down-success'
  }
  return value > 0 ? 'compare-up' : 'compare-down'
}

const formatCompare = (value, unit = '') => {
  if (value === 0) return '较上期持平'
  const prefix = value > 0 ? '↑' : '↓'
  return `${prefix} 较上期 ${Math.abs(value).toFixed(1)}${unit}`
}
</script>

<style scoped>
.statistics-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
}

.risk-tag {
  margin-left: auto;
}

.filter-form {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-group {
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-divider {
  width: 1px;
  height: 40px;
  background: #E8E8E8;
  margin: 0 8px;
}

.filter-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card,
.summary-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.chart-card:hover,
.summary-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart {
  height: 400px;
  width: 100%;
}

.chart-row {
  margin-top: 0;
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.summary-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.summary-icon .el-icon {
  font-size: 28px;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.summary-compare {
  font-size: 12px;
  font-weight: 500;
}

.compare-up {
  color: #F56C6C;
}

.compare-down {
  color: #67C23A;
}

.compare-up-danger {
  color: #F56C6C;
  font-weight: 600;
}

.compare-down-success {
  color: #67C23A;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .filter-form {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-divider {
    display: none;
  }

  .filter-actions {
    margin-left: 0;
    justify-content: center;
  }

  .chart {
    height: 300px;
  }

  .summary-item {
    margin-bottom: 12px;
  }
}
</style>
