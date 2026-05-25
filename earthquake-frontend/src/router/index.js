import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/HomeView.vue'
import Subscribe from '../views/Subscribe.vue'
import Science from '../views/Science.vue'
import Chat from '../views/Chat.vue'
import Profile from '../views/Profile.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', name: '首页', component: Home },
  { path: '/login', name: '登录', component: Login },
  { path: '/subscribe', name: '订阅预警', component: Subscribe },
  { path: '/science', name: '科普知识', component: Science },
  { path: '/chat', name: '交流区', component: Chat },
  { path: '/profile', name: '个人中心', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
