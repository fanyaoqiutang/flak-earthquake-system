//路由管理文件（页面跳转、权限控制）
// 引入路由
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '地震数据' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '数据统计' }
  },
 {
    path: '/science',
    name: 'Science',
    component: () => import('@/views/Science.vue'),
    meta: { title: '科普中心' }
  },
   {
    path: '/science/category/:categoryId',
    name: 'ScienceCategory',
    component: () => import('@/views/ScienceCategory.vue'),
    meta: { title: '分类详情' }
  },
  {
    path: '/science/article/:articleId',
    name: 'ScienceDetail',
    component: () => import('@/views/ScienceDetail.vue'),
    meta: { title: '文章详情' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { title: '智能问答' }
  },
  {
    path: '/subscribe',
    name: 'Subscribe',
    component: () => import('@/views/Subscribe.vue'),
    meta: { title: '订阅服务', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: () => import('@/views/AdminProfile.vue'),
    meta: { title: '管理员中心', requiresAdmin: true }
  },
  {
    path: '/admin/location-audit',
    name: 'LocationAudit',
    component: () => import('@/views/LocationAudit.vue'),
    meta: { title: '位置审核管理', requiresAdmin: true }
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
  const isLoggedIn = userToken || adminToken

  // 管理员后台只能管理员访问
  if (to.meta.requiresAdmin && !adminToken) {
    next('/login')
    return
  }

  // 如果管理员访问普通用户页面，重定向到管理员页面
  if (adminToken && to.path === '/profile') {
    next('/admin/profile')
    return
  }

  // 如果普通用户访问管理员页面，重定向到普通用户页面
  if (userToken && to.path === '/admin/profile') {
    next('/profile')
    return
  }

  // 需要登录的页面，普通用户或管理员都可以访问
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  // 如果已登录但访问登录页，重定向到首页
  if (to.path === '/login' && isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
