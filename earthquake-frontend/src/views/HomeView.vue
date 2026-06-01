<template>
  <div class="home-container">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-num">{{ earthquakeData.length }}</div>
        <div class="stat-text">今日地震次数</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{{ maxMagnitude }}</div>
        <div class="stat-text">最大震级（级）</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{{ filteredEarthquakes.length }}</div>
        <div class="stat-text">筛选结果</div>
      </div>
      <div class="stat-item">
        <div class="stat-num status-normal">正常</div>
        <div class="stat-text">系统状态</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
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
    </div>

    <!-- 两栏布局 -->
    <div class="two-columns">
      <!-- 左侧：地图 -->
      <div class="left-col">
        <div class="section-title">📍 地震分布地图</div>
        <div id="mapContainer" class="map-box" ref="mapContainer"></div>
      </div>

      <!-- 右侧：地震列表 -->
      <div class="right-col">
        <div class="quake-list-card">
          <div class="card-title">近期地震信息</div>
          <div class="simple-quake-list">
            <div v-for="item in filteredEarthquakes.slice(0, 5)" :key="item.id" class="simple-quake-item">
              <div class="simple-location">
                <span class="loc-name">{{ item.location }}</span>
                <span :class="['simple-mag', getMagClass(item.magnitude)]">M{{ item.magnitude }}</span>
              </div>
              <div class="simple-time">{{ item.time }}</div>
              <div class="simple-info">深度：{{ item.depth }}km | 坐标：{{ item.lat }}°N, {{ item.lng }}°E</div>
              <a href="#" class="detail-link">查看详情 ></a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getEarthquakeList } from '../API/common'

const timeFilter = ref('1y')
const magFilter = ref('0')
const mapContainer = ref(null)

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
    const itemTime = new Date(item.earthquake_time || item.time)
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
}

// API数据到前端格式的转换
const loadEarthquakeData = async () => {
  try {
    const response = await getEarthquakeList()
    if (response.code === 200) {
      earthquakeData.value = response.data.map(item => ({
        id: item.earthquake_id,
        location: item.province_name || item.location,
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

onMounted(() => {
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

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 1px;
  background: #E8ECF0;
  margin: 20px 40px;
  border-radius: 8px;
  overflow: hidden;
}

.stat-item {
  background: white;
  flex: 1;
  padding: 12px 16px;
  text-align: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.stat-text {
  font-size: 12px;
  color: #8A99B0;
}

.status-normal {
  color: #10B981;
}

/* 筛选栏 */
.filter-bar {
  background: white;
  border: 1px solid #E8ECF0;
  border-radius: 8px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 32px;
  margin: 0 40px 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 16px;
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
  margin-left: auto;
  background: none;
  border: none;
  font-size: 13px;
  color: #64748B;
  cursor: pointer;
}

/* 两栏布局（地图占比更大，侧边栏更窄） */
.two-columns {
  display: flex;
  gap: 20px;
  padding: 0 40px 40px;
}

.left-col {
  flex: 4;
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
  height: 600px;
  background: #F0F4FA;
  border-radius: 8px;
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
}

/* 响应式 */
@media (max-width: 1200px) {
  .two-columns {
    flex-direction: column;
  }
  .map-box {
    height: 450px;
  }
}
</style>