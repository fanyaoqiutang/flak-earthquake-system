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
// 获取所有省份（管理员用）
export function getAllProvinces() {
  return request({
    url: '/admin/provinces',
    method: 'get'
  })
}

// 删除省份
export function deleteProvince(provinceId) {
  return request({
    url: `/admin/provinces/${provinceId}`,
    method: 'delete'
  })
}

// 更新省份名称
export function updateProvinceName(provinceId, name) {
  return request({
    url: `/admin/provinces/${provinceId}`,
    method: 'put',
    data: { province_name: name }
  })
}

// ... existing code ...

// 添加省份
export function addProvince(name) {
  return request({
    url: '/admin/provinces',
    method: 'post',
    data: { province_name: name }
  })
}

// 获取所有用户（带分页）
export function getAllUsers(params) {
  return request({
    url: '/admin/user/list',
    method: 'get',
    params
  })
}

// 更新用户信息
export function updateUserInfo(userId, data) {
  return request({
    url: `/admin/user/update/${userId}`,
    method: 'put',
    data
  })
}

// 获取反馈列表（带分页）
export function getFeedbacks(params) {
  return request({
    url: '/admin/feedback/list',
    method: 'get',
    params
  })
}

// 更新反馈状态
export function updateFeedbackStatus(feedbackId, status) {
  return request({
    url: `/admin/feedback/status/${feedbackId}`,
    method: 'put',
    data: { status }
  })
}

/**
 * 获取待审核位置列表
 */
export function getPendingLocations(params) {
  return request({
    url: '/admin/locations/pending',
    method: 'get',
    params
  })
}

/**
 * 审核通过并添加城市
 */
export function approveLocation(locationId, data) {
  return request({
    url: `/admin/locations/approve/${locationId}`,
    method: 'post',
    data
  })
}

/**
 * 拒绝位置
 */
export function rejectLocation(locationId) {
  return request({
    url: `/admin/locations/reject/${locationId}`,
    method: 'post'
  })
}

/**
 * 批量审核通过
 */
export function batchApproveLocations(data) {
  return request({
    url: '/admin/locations/batch_approve',
    method: 'post',
    data
  })
}

// 获取仪表盘统计数据
export function getDashboardStats() {
  return request({
    url: '/admin/dashboard/stats',
    method: 'get'
  })
}

// 管理员发送聊天消息
export function sendAdminChatMessage(data) {
  const token = localStorage.getItem('admin_token')
  return request({
    url: '/user/chat/admin',
    method: 'post',
    headers: {
      'X-Admin-Token': token
    },
    data
  })
}
