<template>
  <div class="earthquake-page">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar bg-white p-4 shadow-sm mb-4 rounded-lg">
      <div class="flex items-center flex-wrap gap-4">
        <div class="filter-group">
          <span class="mr-2 text-gray-600">按时间：</span>
          <el-radio-group v-model="timeFilter" size="small">
            <el-radio-button label="24h">最近24小时内</el-radio-button>
            <el-radio-button label="48h">最近48小时内</el-radio-button>
            <el-radio-button label="7d">最近7天内</el-radio-button>
            <el-radio-button label="30d">最近30天内</el-radio-button>
            <el-radio-button label="1y">最近一年内</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-group">
          <span class="mr-2 text-gray-600">按震级：</span>
          <el-radio-group v-model="magFilter" size="small">
            <el-radio-button label="7">7.0级以上</el-radio-button>
            <el-radio-button label="5">5.0级以上</el-radio-button>
            <el-radio-button label="3">3.0级以上</el-radio-button>
            <el-radio-button label="0">全部</el-radio-button>
          </el-radio-group>
        </div>
        <el-button @click="resetFilter" size="small">重置</el-button>
      </div>
    </div>

    <!-- 地图 + 右侧列表布局 -->
    <div class="map-container flex gap-4">
      <!-- 地图主区域 -->
      <div id="amap-container" class="map-box flex-1 rounded-lg overflow-hidden shadow-sm"></div>

      <!-- 右侧地震列表 -->
      <div class="list-box w-80 bg-white rounded-lg shadow-sm p-4 overflow-y-auto">
        <div class="space-y-4">
          <div v-for="quake in filteredEarthquakes" :key="quake.id" class="quake-item border-b pb-3">
            <div class="flex items-center justify-between">
              <span class="mag-tag bg-red-600 text-white px-2 py-1 rounded text-sm font-bold">
                M{{ quake.magnitude }}
              </span>
              <el-button type="text" size="small" @click="showDetail(quake)">详情</el-button>
            </div>
            <p class="text-gray-800 font-medium mt-1">{{ quake.location }}</p>
            <p class="text-gray-600 text-sm mt-1">震发时间：{{ quake.time }}</p>
            <p class="text-gray-500 text-sm mt-1">
              纬度{{ quake.lat }} 经度{{ quake.lng }} 深度{{ quake.depth }}KM
            </p>
          </div>
        </div>
        <div class="text-center mt-4">
          <el-button type="text" @click="loadMore">更多 »</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElRadioGroup, ElRadioButton, ElButton, ElMessage } from 'element-plus'

// 你的高德地图 Key
const AMAP_KEY = "a93d4f6da8bb5b797ff17210a9e21fdd"

// 筛选条件
const timeFilter = ref('1y')
const magFilter = ref('0')
let map = null
let markers = []

// 模拟地震数据（后续可替换为后端接口数据）
const earthquakeData = ref([
  {
    id: '1',
    location: '新疆乌鲁木齐市沙依巴克区',
    magnitude: 3.9,
    depth: 30,
    time: '2026-05-18 16:32:28',
    lat: 43.67,
    lng: 87.42,
    timestamp: new Date('2026-05-18 16:32:28').getTime()
  },
  {
    id: '2',
    location: '新疆阿克苏地区库车市',
    magnitude: 4.1,
    depth: 15,
    time: '2026-05-18 13:09:20',
    lat: 41.37,
    lng: 83.92,
    timestamp: new Date('2026-05-18 13:09:20').getTime()
  },
  {
    id: '3',
    location: '新疆阿克苏地区库车市',
    magnitude: 4.5,
    depth: 13,
    time: '2026-05-18 13:07:27',
    lat: 41.40,
    lng: 83.96,
    timestamp: new Date('2026-05-18 13:07:27').getTime()
  },
  {
    id: '4',
    location: '缅甸',
    magnitude: 5.2,
    depth: 10,
    time: '2026-05-18 10:05:24',
    lat: 16.55,
    lng: 96.25,
    timestamp: new Date('2026-05-18 10:05:24').getTime()
  },
  {
    id: '5',
    location: '广西柳州市柳南区',
    magnitude: 3.3,
    depth: 10,
    time: '2026-05-18 07:41:44',
    lat: 24.40,
    lng: 109.27,
    timestamp: new Date('2026-05-18 07:41:44').getTime()
  }
])

// 筛选后的数据
const filteredEarthquakes = ref([])

// 初始化地图
const initMap = () => {
  const script = document.createElement('script')
  script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
  script.async = true
  script.onload = () => {
    map = new AMap.Map("amap-container", {
      zoom: 4,
      center: [104.195, 35.8617] // 中国中心坐标
    })
    updateMarkers()
  }
  document.head.appendChild(script)
}

// 更新地图标记
const updateMarkers = () => {
  if (!map) return
  // 清除旧标记
  markers.forEach(marker => map.remove(marker))
  markers = []

  // 添加新标记，根据震级设置样式
  filteredEarthquakes.value.forEach(quake => {
    const marker = new AMap.Marker({
      position: [quake.lng, quake.lat],
      title: `M${quake.magnitude} ${quake.location}`
    })
    marker.on('click', () => showDetail(quake))
    map.add(marker)
    markers.push(marker)
  })
}

// 筛选逻辑
const filterData = () => {
  const now = Date.now()
  let timeThreshold = now
  switch (timeFilter.value) {
    case '24h': timeThreshold = now - 24*3600*1000; break
    case '48h': timeThreshold = now - 48*3600*1000; break
    case '7d': timeThreshold = now - 7*24*3600*1000; break
    case '30d': timeThreshold = now - 30*24*3600*1000; break
    case '1y': timeThreshold = now - 365*24*3600*1000; break
  }

  filteredEarthquakes.value = earthquakeData.value.filter(quake => {
    const timeOk = quake.timestamp >= timeThreshold
    let magOk = false
    switch (magFilter.value) {
      case '7': magOk = quake.magnitude >= 7; break
      case '5': magOk = quake.magnitude >= 5; break
      case '3': magOk = quake.magnitude >= 3; break
      case '0': magOk = true; break
    }
    return timeOk && magOk
  })
  if (map) updateMarkers()
}

// 重置筛选
const resetFilter = () => {
  timeFilter.value = '1y'
  magFilter.value = '0'
}

// 显示详情
const showDetail = (quake) => {
  ElMessage.info(`查看 ${quake.location} 地震详情`)
}

// 加载更多
const loadMore = () => {
  ElMessage.info('加载更多地震数据...')
}

// 监听筛选条件变化
watch([timeFilter, magFilter], filterData)

onMounted(() => {
  filterData()
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})
</script>

<style scoped>
.earthquake-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 16px;
}
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
.map-container {
  height: calc(100vh - 150px);
  display: flex;
  gap: 16px;
}
.map-box {
  height: 100%;
  flex: 1;
  border-radius: 10px;
  overflow: hidden;
  background: #eef2f7;
}
.list-box {
  height: 100%;
  width: 320px;
}
.mag-tag {
  font-weight: bold;
}
</style>