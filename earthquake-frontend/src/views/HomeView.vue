<template>
  <div class="home-container">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">地区</span>
        <div style="display: flex; gap: 10px; align-items: center;">
          <el-select
            v-model="selectedProvinceId"
            placeholder="选择省份"
            clearable
            @change="handleProvinceChange"
            style="width: 150px"
          >
            <el-option
              v-for="province in provinces"
              :key="province.province_id"
              :label="province.province_name"
              :value="province.province_id"
            />
          </el-select>
          <el-select
            v-model="selectedCityId"
            placeholder="选择城市"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="city in cities"
              :key="city.city_id"
              :label="city.city_name"
              :value="city.city_id"
            />
          </el-select>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-label">时间</span>
        <div class="filter-btns">
          <button @click="timeFilter = '24h'" :class="{ active: timeFilter === '24h' }">24小时</button>
          <button @click="timeFilter = '7d'" :class="{ active: timeFilter === '7d' }">7天</button>
          <button @click="timeFilter = '30d'" :class="{ active: timeFilter === '30d' }">30天</button>
          <button @click="timeFilter = '1y'" :class="{ active: timeFilter === '1y' }">1年</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-label">震级</span>
        <div class="filter-btns">
          <button @click="magFilter = '0'" :class="{ active: magFilter === '0' }">全部</button>
          <button @click="magFilter = '3'" :class="{ active: magFilter === '3' }">3.0+</button>
          <button @click="magFilter = '5'" :class="{ active: magFilter === '5' }">5.0+</button>
        </div>
      </div>
      <button class="reset-btn" @click="resetFilter">重置筛选</button>

      <!-- 统计信息内联显示 -->
      <div class="stats-inline">
        <div class="stat-item-inline">
          <span class="stat-value">{{ earthquakeData.length }}</span>
          <span class="stat-label">今日地震次数</span>
        </div>
        <div class="divider"></div>
        <div class="stat-item-inline">
          <span class="stat-value">{{ maxMagnitude }}</span>
          <span class="stat-label">最大震级（级）</span>
        </div>
        <div class="divider"></div>
        <div class="stat-item-inline">
          <span class="stat-value">{{ filteredEarthquakes.length }}</span>
          <span class="stat-label">筛选结果</span>
        </div>
        <div class="divider"></div>
        <div class="stat-item-inline">
          <span class="stat-value status-normal">正常</span>
          <span class="stat-label">系统状态</span>
        </div>
      </div>
    </div>

    <!-- 两栏布局 -->
    <div class="two-columns">
      <!-- 左侧：地图 -->
      <div class="left-col">
        <div class="section-title"> 地震分布地图</div>
        <div id="mapContainer" class="map-box" ref="mapContainer"></div>
      </div>

      <!-- 右侧：地震列表 -->
      <div class="right-col">
        <div class="quake-list-card">
          <div class="card-title">近期地震信息</div>
          <div class="simple-quake-list">
            <div v-for="item in filteredEarthquakes.slice(0, 5)" :key="item.id" class="simple-quake-item">
              <div class="simple-location">
                <span class="loc-name">{{ item.province }} {{ item.city }}</span>
                <span :class="['simple-mag', getMagClass(item.magnitude)]">M{{ item.magnitude }}</span>
              </div>
              <div class="simple-time">{{ item.time }}</div>
              <div class="simple-info">深度：{{ item.depth }}km | 坐标：{{ item.lat }}°N, {{ item.lng }}°E</div>
              <a href="#" class="detail-link" @click.prevent="showDetail(item)">查看详情 ></a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地震详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="地震详细信息"
      width="600px"
      :close-on-click-modal="true"
    >
      <div v-if="selectedEarthquake" class="earthquake-detail">
        <div class="detail-header">
          <span class="detail-magnitude" :class="getMagClass(selectedEarthquake.magnitude)">
            M {{ selectedEarthquake.magnitude }}
          </span>
          <span class="detail-location">{{ selectedEarthquake.province }} {{ selectedEarthquake.city }}</span>
        </div>

        <el-divider />

        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">发生时间：</span>
            <span class="info-value">{{ selectedEarthquake.time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">震源深度：</span>
            <span class="info-value">{{ selectedEarthquake.depth }} km</span>
          </div>
          <div class="info-row">
            <span class="info-label">震中坐标：</span>
            <span class="info-value">{{ selectedEarthquake.lat }}°N, {{ selectedEarthquake.lng }}°E</span>
          </div>
          <div class="info-row">
            <span class="info-label">震级：</span>
            <span class="info-value" :class="getMagClass(selectedEarthquake.magnitude)">
              {{ selectedEarthquake.magnitude }} 级
            </span>
          </div>
        </div>

        <el-divider />

        <div class="detail-tips">
          <el-alert
            title="防震提示"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #default>
              <ul>
                <li>保持冷静，迅速躲避到坚固的桌子下或墙角</li>
                <li>远离窗户、玻璃、吊灯等易碎物品</li>
                <li>地震停止后，有序撤离到空旷地带</li>
                <li>不要使用电梯，走楼梯撤离</li>
              </ul>
            </template>
          </el-alert>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="large" @click="detailVisible = false" class="btn-close">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
          <el-button type="primary" size="large" @click="viewOnMap" class="btn-map">
            <el-icon><Location /></el-icon>
            在地图上查看
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getEarthquakeList, getProvinces, getCities } from '../API/common'
import { Close, Location } from '@element-plus/icons-vue'

const timeFilter = ref('1y')
const magFilter = ref('0')
const mapContainer = ref(null)

// 地震详情弹窗
const detailVisible = ref(false)
const selectedEarthquake = ref(null)

// 省市筛选
const selectedProvinceId = ref(null)
const selectedCityId = ref(null)
const provinces = ref([])
const cities = ref([])

let map = null
let markers = []

const earthquakeData = ref([])

const maxMagnitude = computed(() => {
  if (earthquakeData.value.length === 0) return '0.0'
  return Math.max(...earthquakeData.value.map(e => e.magnitude)).toFixed(1)
})

const filteredEarthquakes = computed(() => {
  const now = new Date()
  let days = 365
  if (timeFilter.value === '24h') days = 1
  else if (timeFilter.value === '7d') days = 7
  else if (timeFilter.value === '30d') days = 30

  const threshold = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)

  return earthquakeData.value.filter(item => {
    const itemTime = new Date(item.time)
    const timeMatch = itemTime >= threshold

    let magMatch = true
    if (magFilter.value === '3') magMatch = item.magnitude >= 3
    else if (magFilter.value === '5') magMatch = item.magnitude >= 5

    return timeMatch && magMatch
  })
})

const getMagClass = (mag) => {
  if (mag >= 5) return 'high'
  if (mag >= 3) return 'medium'
  return 'low'
}

const resetFilter = () => {
  timeFilter.value = '1y'
  magFilter.value = '0'
  selectedProvinceId.value = null
  selectedCityId.value = null
  cities.value = []
  loadEarthquakeData()
}

// 省份变化时加载城市列表
const handleProvinceChange = async (provinceId) => {
  selectedCityId.value = null
  cities.value = []

  if (!provinceId) {
    loadEarthquakeData()
    return
  }

  try {
    const response = await getCities({ province_id: provinceId })
    if (response.code === 200) {
      cities.value = response.data
    }
  } catch (error) {
    console.error('加载城市列表失败:', error)
  }

  loadEarthquakeData()
}

// 监听城市变化
watch(selectedCityId, () => {
  loadEarthquakeData()
})

// API数据到前端格式的转换
const loadEarthquakeData = async () => {
  try {
    const params = {
      time: timeFilter.value,
      mag_min: magFilter.value === '0' ? 0 : parseFloat(magFilter.value)
    }

    if (selectedProvinceId.value) {
      params.province_id = selectedProvinceId.value
    }

    if (selectedCityId.value) {
      params.city_id = selectedCityId.value
    }

    const response = await getEarthquakeList(params)
    if (response.code === 200) {
      earthquakeData.value = response.data.map(item => ({
        id: item.earthquake_id,
        province: item.province_name || '',
        city: item.city_name || '',
        magnitude: item.magnitude,
        depth: item.depth,
        time: item.earthquake_time,
        lat: item.latitude,
        lng: item.longitude
      }))
    }
  } catch (error) {
    console.error('加载地震数据失败:', error)
  }
}

// 加载省份列表
const loadProvinces = async () => {
  try {
    const response = await getProvinces()
    if (response.code === 200) {
      provinces.value = response.data
    }
  } catch (error) {
    console.error('加载省份列表失败:', error)
  }
}

// 地图初始化
const initMap = () => {
  const script = document.createElement('script')
  script.src = `https://webapi.amap.com/maps?v=2.0&key=a93d4f6da8bb5b797ff17210a9e21fdd&plugin=AMap.Scale,AMap.ToolBar`
  script.onload = () => {
    createMap()
  }
  document.head.appendChild(script)
}

const createMap = () => {
  if (!mapContainer.value || typeof AMap === 'undefined') return

  map = new AMap.Map('mapContainer', {
    zoom: 4,
    center: [104.195, 35.8617],
    resizeEnable: true,
    viewMode: '2D',
    backgroundColor: '#F5F7FA'
  })

  map.addControl(new AMap.Scale())
  map.addControl(new AMap.ToolBar())
  addMarkers()
}

const addMarkers = () => {
  if (!map || typeof AMap === 'undefined') return

  markers.forEach(marker => map.remove(marker))
  markers = []

  filteredEarthquakes.value.forEach(item => {
    const color = item.magnitude >= 5 ? '#EF4444' : item.magnitude >= 3 ? '#F59E0B' : '#10B981'
    const size = 16 + item.magnitude * 2

    const marker = new AMap.Marker({
      position: [item.lng, item.lat],
      content: `<div style="
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: ${size * 0.4}px;
        font-weight: bold;
        color: white;
      ">${item.magnitude.toFixed(1)}</div>`,
      offset: new AMap.Pixel(-size/2, -size/2)
    })
    markers.push(marker)
    map.add(marker)
  })

  if (markers.length > 0) {
    map.setFitView(markers, false, [50, 50, 50, 50])
  }
}

watch(filteredEarthquakes, () => {
  if (map) addMarkers()
})

// 显示地震详情
const showDetail = (earthquake) => {
  selectedEarthquake.value = earthquake
  detailVisible.value = true
}

// 在地图上查看
const viewOnMap = () => {
  if (!selectedEarthquake.value || !map) return

  const { lng, lat } = selectedEarthquake.value
  map.setCenter([lng, lat])
  map.setZoom(10)
  detailVisible.value = false
}

onMounted(() => {
  loadProvinces()
  loadEarthquakeData()
  setTimeout(() => initMap(), 200)
})

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: #F5F7FB;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* 筛选栏 */
.filter-bar {
  background: white;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  margin: 20px 40px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.filter-btns {
  display: flex;
  gap: 12px;
}

.filter-btns button {
  background: none;
  border: none;
  font-size: 13px;
  color: #64748B;
  cursor: pointer;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
}

.filter-btns button.active {
  color: #1677ff;
  border-bottom-color: #1677ff;
}

.reset-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: #64748B;
  cursor: pointer;
  padding: 4px 0;
}

.reset-btn:hover {
  color: #1677ff;
}

/* 统计信息内联样式 */
.stats-inline {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
  padding-left: 20px;
  border-left: 1px solid #E8ECF0;
}

.stat-item-inline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.stat-label {
  font-size: 11px;
  color: #8A99B0;
}

.status-normal {
  color: #10B981;
}

.divider {
  width: 1px;
  height: 30px;
  background: #E8ECF0;
}

/* 两栏布局 */
.two-columns {
  display: flex;
  gap: 20px;
  padding: 0 40px 40px;
}

.left-col {
  flex: 5;
}

.right-col {
  flex: 1;
}

/* 地图 */
.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 10px;
}

.map-box {
  height: 700px;
  background: #F0F4FA;
  border-radius: 8;
  overflow: hidden;
  border: 1px solid #E8ECF0;
}

/* 地震列表 */
.quake-list-card {
  background: white;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  padding: 16px;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #F0F2F5;
}

.simple-quake-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.simple-quake-item {
  border-bottom: 1px solid #F5F7FB;
  padding-bottom: 12px;
}

.simple-quake-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.simple-location {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.loc-name {
  font-size: 13px;
  font-weight: 500;
  color: #1E293B;
}

.simple-mag {
  font-size: 13px;
  font-weight: 600;
}

.simple-mag.high { color: #DC2626; }
.simple-mag.medium { color: #F59E0B; }
.simple-mag.low { color: #10B981; }

.simple-time {
  font-size: 11px;
  color: #8A99B0;
  margin-bottom: 4px;
}

.simple-info {
  font-size: 11px;
  color: #94A3B8;
  margin-bottom: 6px;
}

.detail-link {
  font-size: 12px;
  color: #1677ff;
  text-decoration: none;
  cursor: pointer;
}

.detail-link:hover {
  text-decoration: underline;
}

/* 地震详情弹窗样式 */
.earthquake-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.detail-magnitude {
  font-size: 32px;
  font-weight: bold;
  padding: 8px 16px;
  border-radius: 8px;
  background: #f0f2f5;
}

.detail-magnitude.high {
  color: #DC2626;
  background: #FEF2F2;
}

.detail-magnitude.medium {
  color: #F59E0B;
  background: #FFFBEB;
}

.detail-magnitude.low {
  color: #10B981;
  background: #ECFDF5;
}

.detail-location {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #64748B;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
}

.info-value.high {
  color: #DC2626;
}

.info-value.medium {
  color: #F59E0B;
}

.info-value.low {
  color: #10B981;
}

.detail-tips ul {
  margin: 0;
  padding-left: 20px;
}

.detail-tips li {
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.6;
}

/* 弹窗底部按钮样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 10px;
}

.btn-close {
  min-width: 100px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-close:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
  transform: translateY(-1px);
}

.btn-map {
  min-width: 140px;
  border-radius: 6px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.btn-map:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.btn-map .el-icon {
  margin-right: 6px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .filter-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-inline {
    margin-left: 0;
    padding-left: 0;
    border-left: none;
    border-top: 1px solid #E8ECF0;
    padding-top: 12px;
    margin-top: 12px;
    width: 100%;
    justify-content: space-around;
  }

  .two-columns {
    flex-direction: column;
  }

  .map-box {
    height: 450px;
  }
}
</style>