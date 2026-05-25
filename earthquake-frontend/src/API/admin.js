//前端管理员接口文件
import request from './request'

// 管理员注册
export function adminRegister(data) {
  return request({
    url: '/api/admin/register',
    method: 'post',
    data
  })
}

// 管理员登录
export function adminLogin(data) {
  return request({
    url: '/api/admin/login',
    method: 'post',
    data
  })
}

// 管理员登出
export function adminLogout() {
  return request({
    url: '/api/admin/logout',
    method: 'post'
  })
}

// 获取当前登录管理员信息
export function getAdminInfo() {
  return request({
    url: '/api/admin/info',
    method: 'get'             // 获取信息用 GET
  })
}
// 添加地震
export function addEarthquake(data) {
  return request({
    url: '/api/admin/earthquake/add',
    method: 'post',
    data
  })
}

// 更新地震
export function updateEarthquake(data) {
  return request({
    url: '/api/admin/earthquake/update',
    method: 'post',
    data
  })
}

// 删除地震
export function deleteEarthquake(data) {
  return request({
    url: '/api/admin/earthquake/delete',
    method: 'post',
    data
  })
}
