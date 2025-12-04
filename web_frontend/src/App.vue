<template>
  <div class="app-container">
    <!-- 侧边栏导航 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>xiayan-mcp</h1>
      </div>
      <nav class="sidebar-nav">
        <el-menu
          default-active="/article/publish"
          class="el-menu-vertical-demo"
          router
          @select="handleMenuSelect"
        >
          <el-sub-menu index="/article">
            <template #title>
              <span>
                <el-icon><Document /></el-icon>
                <span>文章管理</span>
              </span>
            </template>
            <el-menu-item index="/article/publish">发布文章</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/theme">
            <template #title>
              <span>
                <el-icon><Collection /></el-icon>
                <span>主题管理</span>
              </span>
            </template>
            <el-menu-item index="/theme/list">主题列表</el-menu-item>
            <el-menu-item index="/theme/add">添加主题</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/media">
            <template #title>
              <span>
                <el-icon><Picture /></el-icon>
                <span>媒体管理</span>
              </span>
            </template>
            <el-menu-item index="/media/list">媒体列表</el-menu-item>
            <el-menu-item index="/media/upload">上传媒体</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/credential">
            <template #title>
              <span>
                <el-icon><Key /></el-icon>
                <span>微信凭证</span>
              </span>
            </template>
          </el-menu-item>
        </el-menu>
      </nav>
    </aside>
    <!-- 主内容区域 -->
    <main class="main-content">
      <header class="content-header">
        <h2>{{ pageTitle }}</h2>
      </header>
      <div class="content-body">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Collection, Picture, Key } from '@element-plus/icons-vue'

// 页面标题
const pageTitle = ref('文章发布')
const route = useRoute()

// 监听路由变化，更新页面标题
watch(
  () => route.path,
  (newPath) => {
    switch (newPath) {
      case '/article/publish':
        pageTitle.value = '文章发布'
        break
      case '/theme/list':
        pageTitle.value = '主题列表'
        break
      case '/theme/add':
        pageTitle.value = '添加主题'
        break
      case '/theme/preview':
        pageTitle.value = '主题预览'
        break
      case '/media/list':
        pageTitle.value = '媒体列表'
        break
      case '/media/upload':
        pageTitle.value = '上传媒体'
        break
      case '/credential':
        pageTitle.value = '微信凭证配置'
        break
      default:
        pageTitle.value = 'xiayan-mcp'
    }
  },
  { immediate: true }
)

// 菜单选择处理
const handleMenuSelect = (key, keyPath) => {
  console.log('Menu selected:', key, keyPath)
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: Arial, sans-serif;
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 200px;
  background-color: #304156;
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #475669;
}

.sidebar-header h1 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.content-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.content-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
