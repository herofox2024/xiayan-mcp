import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/article/publish'
  },
  {
    path: '/article',
    name: 'Article',
    component: () => import('../pages/Article.vue'),
    children: [
      {
        path: 'publish',
        name: 'ArticlePublish',
        component: () => import('../pages/ArticlePublish.vue')
      }
    ]
  },
  {
    path: '/theme',
    name: 'Theme',
    component: () => import('../pages/Theme.vue'),
    children: [
      {
        path: 'list',
        name: 'ThemeList',
        component: () => import('../pages/ThemeList.vue')
      },
      {
        path: 'preview/:themeId',
        name: 'ThemePreview',
        component: () => import('../pages/ThemePreview.vue')
      },
      {
        path: 'add',
        name: 'ThemeAdd',
        component: () => import('../pages/ThemeAdd.vue')
      },
      {
        path: 'edit/:themeId',
        name: 'ThemeEdit',
        component: () => import('../pages/ThemeEdit.vue')
      }
    ]
  },
  {
    path: '/media',
    name: 'Media',
    component: () => import('../pages/Media.vue'),
    children: [
      {
        path: 'list',
        name: 'MediaList',
        component: () => import('../pages/MediaList.vue')
      },
      {
        path: 'upload',
        name: 'MediaUpload',
        component: () => import('../pages/MediaUpload.vue')
      }
    ]
  },
  {
    path: '/credential',
    name: 'Credential',
    component: () => import('../pages/Credential.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
