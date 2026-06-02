//前端common接口文件
import request from './request'

// 获取地震列表
export function getEarthquakeList(params) {
  return request({
    url: '/earthquake/list',
    method: 'get',
    params
  })
}

// 获取所有省份
export function getProvinces() {
  return request({
    url: '/provinces',
    method: 'get'
  })
}

// 获取省份分组（按地区）
export function getProvincesGroupByRegion() {
  return request({
    url: '/province/group',
    method: 'get'
  })
}

// 获取地震统计数据（综合统计）
export function getEarthquakeStatistics(params) {
  return request({
    url: '/statistics',
    method: 'get',
    params
  })
}

// 获取省份地震统计（饼图）
export function getEarthquakeStatsProvince(params) {
  return request({
    url: '/earthquake/stats/province',
    method: 'get',
    params
  })
}

// 获取时间趋势统计（折线图）
export function getEarthquakeStatsTrend(params) {
  return request({
    url: '/earthquake/stats/trend',
    method: 'get',
    params
  })
}

// 获取震级分布统计（柱状图）
export function getEarthquakeStatsMagnitude(params) {
  return request({
    url: '/earthquake/stats/magnitude',
    method: 'get',
    params
  })
}

// 获取地震频次TOP5排名
export function getEarthquakeRank(params) {
  return request({
    url: '/earthquake/rank',
    method: 'get',
    params
  })
}
