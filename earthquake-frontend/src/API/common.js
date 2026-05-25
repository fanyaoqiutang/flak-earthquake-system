//前端common接口文件
import request from './request'

// 获取地震列表
export function getEarthquakeList(params) {
  return request({
    url: '/api/earthquake/list',
    method: 'get',
    params
  })
}

// 获取所有省份
export function getProvinces() {
  return request({
    url: '/api/provinces',
    method: 'get'
  })
}
