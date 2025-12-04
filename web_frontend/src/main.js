import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// 创建Vue应用
const app = createApp(App)

// 配置Element Plus
app.use(ElementPlus)

// 配置路由
app.use(router)

// 挂载应用
app.mount('#app')
