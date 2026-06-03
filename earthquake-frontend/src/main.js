// 1. 从 Vue 库里导入“创建应用”的方法
import { createApp } from 'vue'
// 2. 导入根组件 App.vue（整个项目的最外层页面）
import App from './App.vue'
// 3. 导入路由（负责页面跳转：登录页 / 首页 / 管理页）
import router from './router'
// 4. 导入 ElementPlus  UI组件库（按钮、表格、弹窗…）
import ElementPlus from 'element-plus'
// 5. 导入 ElementPlus 的样式
import 'element-plus/dist/index.css'

// 6. 创建 Vue 应用实例（项目启动！）
const app = createApp(App)
// 7. 把路由安装到项目里（页面跳转可用）
app.use(router)
app.use(ElementPlus)
// 9. 把项目挂载到页面上（显示到浏览器）
app.mount('#app')
