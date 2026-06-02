//前端用户接口文件
import request from './request'

// 用户注册
export function userRegister(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

// 用户登录
export function userLogin(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

// 用户登出
export function userLogout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

// 订阅省份
export function subscribeProvince(data) {
  return request({
    url: '/user/subscribe',
    method: 'post',
    data
  })
}

// 批量订阅省份
export function subscribeBatch(data) {
  return request({
    url: '/user/subscribe/batch',
    method: 'post',
    data
  })
}

// 取消订阅
export function unsubscribeProvince(subscribeId) {
  return request({
    url: `/user/subscribe/${subscribeId}`,
    method: 'delete'
  })
}

// 获取订阅列表
export function getSubscriptions() {
  return request({
    url: '/user/subscriptions',
    method: 'get'
  })
}

// 获取我的订阅ID列表
export function getMySubscribeIds() {
  return request({
    url: '/user/subscribe/my',
    method: 'get'
  })
}

// 获取预警列表
export function getAlerts() {
  return request({
    url: '/user/alerts',
    method: 'get'
  })
}

// 获取预警设置
export function getAlertSettings() {
  return request({
    url: '/user/alert/settings',
    method: 'get'
  })
}

// 更新预警设置
export function updateAlertSettings(data) {
  return request({
    url: '/user/alert/settings',
    method: 'post',
    data
  })
}

// 标记预警已读
export function markAlertRead(alertId) {
  return request({
    url: `/user/alerts/${alertId}/read`,
    method: 'post'
  })
}

// 全部标记已读
export function markAllAlertsRead() {
  return request({
    url: '/user/alerts/read-all',
    method: 'post'
  })
}

// 获取未读预警数量
export function getUnreadAlertsCount() {
  return request({
    url: '/user/alerts/unread',
    method: 'get'
  })
}

// 提交反馈
export function submitFeedback(data) {
  return request({
    url: '/user/feedback',
    method: 'post',
    data
  })
}

// 发送聊天消息
export function sendChatMessage(data) {
  return request({
    url: '/user/chat',
    method: 'post',
    data
  })
}

// 获取聊天记录
export function getChatList() {
  return request({
    url: '/user/chat/list',
    method: 'get'
  })
}
