//路由管理文件（页面跳转、权限控制）
// 引入路由
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',      // 网址：localhost:8080/
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '地震数据' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { title: '管理员后台', requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '地震预警平台'

  const userToken = localStorage.getItem('user_token')
  const adminToken = localStorage.getItem('admin_token')

  if (to.meta.requiresAuth && !userToken) {
    next('/login')
  } else if (to.meta.requiresAdmin && !adminToken) {
    next('/login')
  } else {
    next()
  }
})

export default router
