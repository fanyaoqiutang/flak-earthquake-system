//前端管理员接口文件
import request from './request'

// 管理员注册
export function adminRegister(data) {
  return request({
    url: '/admin/register',
    method: 'post',
    data
  })
}

// 管理员登录
export function adminLogin(data) {
  return request({
    url: '/admin/login',
    method: 'post',
    data
  })
}

// 管理员登出
export function adminLogout() {
  return request({
    url: '/admin/logout',
    method: 'post'
  })
}

// 获取当前登录管理员信息
export function getAdminInfo() {
  return request({
    url: '/admin/info',
    method: 'get'
  })
}

// 获取用户列表
export function getUserList() {
  return request({
    url: '/admin/user/list',
    method: 'get'
  })
}

// 获取用户统计
export function getUserStats() {
  return request({
    url: '/admin/user/stats',
    method: 'get'
  })
}

// 切换用户状态
export function toggleUserStatus(userId) {
  return request({
    url: `/admin/user/status/${userId}`,
    method: 'post'
  })
}

// 删除用户
export function deleteUser(userId) {
  return request({
    url: `/admin/user/delete/${userId}`,
    method: 'post'
  })
}

// 获取反馈列表
export function getFeedbackList() {
  return request({
    url: '/admin/feedback/list',
    method: 'get'
  })
}

// 处理反馈
export function handleFeedback(fbId, data) {
  return request({
    url: `/admin/feedback/handle/${fbId}`,
    method: 'post',
    data
  })
}

// 获取聊天消息列表
export function getChatMessageList() {
  return request({
    url: '/admin/chat/list',
    method: 'get'
  })
}

// 删除聊天消息
export function deleteChatMessage(msgId) {
  return request({
    url: `/admin/chat/delete/${msgId}`,
    method: 'post'
  })
}

// 添加地震
export function addEarthquake(data) {
  return request({
    url: '/admin/earthquake/add',
    method: 'post',
    data
  })
}

// 更新地震
export function updateEarthquake(data) {
  return request({
    url: '/admin/earthquake/update',
    method: 'post',
    data
  })
}

// 删除地震
export function deleteEarthquake(data) {
  return request({
    url: '/admin/earthquake/delete',
    method: 'post',
    data
  })
}
