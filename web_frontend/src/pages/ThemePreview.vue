<template>
  <div class="theme-preview-container">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <div>
        <h2>主题预览</h2>
        <div class="theme-info">
          <span class="theme-name">{{ currentTheme.name || '未找到主题' }}</span>
          <span v-if="currentTheme.description" class="theme-desc">({{ currentTheme.description }})</span>
        </div>
      </div>
      <el-button @click="handleBack">
        <el-icon><Back /></el-icon>
        返回列表
      </el-button>
    </div>

    <!-- 预览内容 -->
    <div class="preview-content">
      <!-- 主题CSS动态注入 -->
      <style scoped>
        {{ currentTheme.css_styles }}
      </style>

      <!-- 主题预览区域 -->
      <div class="theme-preview-area" v-html="renderedContent"></div>

      <!-- 主题信息 -->
      <div class="theme-details">
        <h3>主题详情</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="主题ID">{{ currentTheme.id }}</el-descriptions-item>
          <el-descriptions-item label="主题名称">{{ currentTheme.name }}</el-descriptions-item>
          <el-descriptions-item label="主题描述">{{ currentTheme.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="CSS样式">
            <div class="code-block">
              <pre>{{ currentTheme.css_styles || '无CSS样式' }}</pre>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="HTML模板">
            <div class="code-block">
              <pre>{{ currentTheme.template || '无HTML模板' }}</pre>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { Back } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 当前主题
const currentTheme = ref({
  id: '',
  name: '',
  description: '',
  css_styles: '',
  template: ''
})

// 示例文章内容
const sampleArticle = {
  title: '示例文章标题',
  content: '<h2>这是一个二级标题</h2><p>这是一段示例文章内容，用于展示主题的渲染效果。</p><p>主题预览功能可以帮助您直观地查看主题的实际效果，包括字体、颜色、布局等样式。</p><ul><li>列表项1</li><li>列表项2</li><li>列表项3</li></ul><blockquote>这是一段引用内容，用于测试主题的引用样式。</blockquote>',
  author: '测试作者',
  date: new Date().toLocaleDateString()
}

// 模拟主题数据
const mockThemes = {
  'default': {
    id: 'default',
    name: '默认主题',
    description: '简洁大方的默认样式',
    css_styles: '.article { max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; } .article h1 { color: #333; font-size: 24px; border-bottom: 1px solid #eee; padding-bottom: 10px; } .article h2 { color: #555; font-size: 20px; margin-top: 20px; } .article p { line-height: 1.6; color: #666; margin: 10px 0; } .article ul { padding-left: 20px; } .article li { margin: 5px 0; } .article blockquote { background-color: #f5f5f5; padding: 10px 15px; border-left: 4px solid #ddd; margin: 15px 0; color: #666; }',
    template: '<div class="article"><h1>{{ title }}</h1><div class="content">{{ content }}</div><div class="meta">作者：{{ author }} | 日期：{{ date }}</div></div>'
  },
  'orangeheart': {
    id: 'orangeheart',
    name: '橙心主题',
    description: '温暖的橙色主题',
    css_styles: '.article { background-color: #fff3e0; border: 1px solid #ffcc80; border-radius: 8px; padding: 20px; font-family: "Microsoft YaHei", sans-serif; } .article h1 { color: #e65100; font-size: 28px; text-align: center; margin-bottom: 20px; } .article h2 { color: #f57c00; font-size: 22px; margin-top: 25px; } .article p { line-height: 1.8; color: #333; margin: 15px 0; } .article ul { padding-left: 25px; } .article li { margin: 8px 0; color: #555; } .article blockquote { background-color: #fff8e1; padding: 15px; border-left: 4px solid #ffb74d; margin: 20px 0; color: #ff6f00; }',
    template: '<div class="article orangeheart"><h1>{{ title }}</h1><div class="content">{{ content }}</div><div class="meta">作者：{{ author }} | 日期：{{ date }}</div></div>'
  },
  'rainbow': {
    id: 'rainbow',
    name: '彩虹主题',
    description: '多彩的彩虹主题',
    css_styles: '.article { max-width: 900px; margin: 0 auto; padding: 30px; font-family: "Comic Sans MS", cursive; background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%); border-radius: 15px; } .article h1 { color: #ff6b6b; font-size: 32px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); text-align: center; margin-bottom: 25px; } .article h2 { color: #4ecdc4; font-size: 26px; margin-top: 30px; } .article p { line-height: 1.9; color: #2d3436; margin: 18px 0; font-size: 16px; } .article ul { padding-left: 30px; } .article li { margin: 10px 0; color: #6c5ce7; font-weight: bold; } .article blockquote { background-color: rgba(255,255,255,0.8); padding: 20px; border-left: 4px solid #a29bfe; margin: 25px 0; color: #636e72; border-radius: 10px; }',
    template: '<div class="article rainbow"><h1>{{ title }}</h1><div class="content">{{ content }}</div><div class="meta">作者：{{ author }} | 日期：{{ date }}</div></div>'
  }
}

// 渲染内容
const renderedContent = computed(() => {
  if (!currentTheme.value.template) {
    return `<div class="article"><h1>${sampleArticle.title}</h1><div class="content">${sampleArticle.content}</div></div>`
  }
  
  // 简单的模板替换
  let template = currentTheme.value.template
  template = template.replace(/{{\s*title\s*}}/g, sampleArticle.title)
  template = template.replace(/{{\s*content\s*}}/g, sampleArticle.content)
  template = template.replace(/{{\s*author\s*}}/g, sampleArticle.author)
  template = template.replace(/{{\s*date\s*}}/g, sampleArticle.date)
  
  return template
})

// 加载主题数据
const loadThemeData = async () => {
  const themeId = route.params.themeId
  if (!themeId) {
    ElMessage.error('主题ID无效')
    handleBack()
    return
  }

  const loading = ElLoading.service({
    lock: true,
    text: '加载主题数据中...',
    background: 'rgba(255, 255, 255, 0.7)'
  })

  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 从模拟数据中获取主题
    const theme = mockThemes[themeId]
    if (theme) {
      currentTheme.value = { ...theme }
    } else {
      ElMessage.error('主题不存在')
      handleBack()
    }
  } catch (error) {
    ElMessage.error('加载主题数据失败：' + error.message)
    handleBack()
  } finally {
    loading.close()
  }
}

// 返回列表
const handleBack = () => {
  router.push('/theme/list')
}

// 组件挂载时加载主题数据
onMounted(() => {
  loadThemeData()
})
</script>

<style scoped>
.theme-preview-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.page-header h2 {
  margin: 0 0 5px 0;
  font-size: 20px;
  color: #303133;
}

.theme-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-name {
  font-weight: bold;
  color: #409eff;
}

.theme-desc {
  color: #909399;
  font-size: 14px;
}

.preview-content {
  margin-top: 20px;
}

.theme-preview-area {
  background-color: #fafafa;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 30px;
  min-height: 300px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}

.theme-details {
  margin-top: 30px;
}

.theme-details h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.code-block {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .theme-preview-area {
    padding: 15px;
  }
  
  .code-block {
    padding: 10px;
  }
}
</style>