//前端用户接口文件
import request from './request'

// 用户注册
export function userRegister(data) {
  return request({
    url: '/api/user/register',
    method: 'post',
    data
  })
}

// 用户登录
export function userLogin(data) {
  return request({
    url: '/api/user/login',
    method: 'post',
    data
  })
}

// 用户登出
export function userLogout() {
  return request({
    url: '/api/user/logout',
    method: 'post'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/api/user/info',
    method: 'get'
  })
}

// 订阅省份
export function subscribeProvince(data) {
  return request({
    url: '/api/user/subscribe',
    method: 'post',
    data
  })
}

// 取消订阅
export function unsubscribeProvince(subscribeId) {
  return request({
    url: `/api/user/subscribe/${subscribeId}`,
    method: 'delete'
  })
}

// 获取订阅列表
export function getSubscriptions() {
  return request({
    url: '/api/user/subscriptions',
    method: 'get'
  })
}

// 获取预警列表
export function getAlerts() {
  return request({
    url: '/api/user/alerts',
    method: 'get'
  })
}

// 标记预警已读
export function markAlertRead(alertId) {
  return request({
    url: `/api/user/alerts/${alertId}/read`,
    method: 'post'
  })
}

// 全部标记已读
export function markAllAlertsRead() {
  return request({
    url: '/api/user/alerts/read-all',
    method: 'post'
  })
}

// 提交反馈
export function submitFeedback(data) {
  return request({
    url: '/api/user/feedback',
    method: 'post',
    data
  })
}

// 发送聊天消息
export function sendChatMessage(data) {
  return request({
    url: '/api/user/chat',
    method: 'post',
    data
  })
}

// 获取聊天记录
export function getChatList() {
  return request({
    url: '/api/user/chat/list',
    method: 'get'
  })
}
