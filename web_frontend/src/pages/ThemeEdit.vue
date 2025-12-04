<template>
  <div class="theme-edit-container">
    <!-- 页面标题 -->
    <h2>编辑主题</h2>

    <!-- 主题表单 -->
    <el-form :model="themeForm" :rules="rules" ref="themeFormRef" label-width="80px" class="theme-form">
      <!-- 主题ID -->
      <el-form-item label="主题ID" prop="id">
        <el-input
          v-model="themeForm.id"
          placeholder="请输入主题ID（唯一标识符，只能包含字母、数字、下划线）"
          maxlength="50"
          show-word-limit
          :disabled="isEditing"
        ></el-input>
        <div class="form-help-text">
          主题ID用于内部标识，编辑模式下不可修改
        </div>
      </el-form-item>

      <!-- 主题名称 -->
      <el-form-item label="主题名称" prop="name">
        <el-input
          v-model="themeForm.name"
          placeholder="请输入主题名称"
          maxlength="50"
          show-word-limit
        ></el-input>
      </el-form-item>

      <!-- 主题描述 -->
      <el-form-item label="主题描述" prop="description">
        <el-input
          v-model="themeForm.description"
          placeholder="请输入主题描述"
          type="textarea"
          :rows="3"
          maxlength="200"
          show-word-limit
        ></el-input>
      </el-form-item>

      <!-- CSS样式 -->
      <el-form-item label="CSS样式">
        <el-tabs v-model="cssTab" class="css-tabs">
          <el-tab-pane label="编辑" name="edit">
            <el-input
              v-model="themeForm.css_styles"
              placeholder="请输入主题CSS样式"
              type="textarea"
              :rows="10"
              class="code-editor"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="预览" name="preview">
            <div class="css-preview">
              <pre>{{ themeForm.css_styles || '无CSS样式' }}</pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form-item>

      <!-- HTML模板 -->
      <el-form-item label="HTML模板">
        <el-tabs v-model="templateTab" class="template-tabs">
          <el-tab-pane label="编辑" name="edit">
            <el-input
              v-model="themeForm.template"
              placeholder="请输入主题HTML模板"
              type="textarea"
              :rows="15"
              class="code-editor"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="预览" name="preview">
            <div class="template-preview">
              <pre>{{ themeForm.template || '无HTML模板' }}</pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="isSubmitting">
          更新主题
        </el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="cancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 表单引用
const themeFormRef = ref()

// 提交状态
const isSubmitting = ref(false)

// 是否编辑模式
const isEditing = ref(true)

// CSS标签页
const cssTab = ref('edit')

// 模板标签页
const templateTab = ref('edit')

// 主题表单数据
const themeForm = ref({
  id: '',
  name: '',
  description: '',
  css_styles: '',
  template: ''
})

// 表单验证规则
const rules = {
  id: [
    { required: true, message: '请输入主题ID', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '主题ID只能包含字母、数字和下划线', trigger: 'blur' },
    { min: 1, max: 50, message: '主题ID长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入主题名称', trigger: 'blur' },
    { min: 1, max: 50, message: '主题名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '主题描述长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 模拟主题数据
const mockThemes = {
  'default': {
    id: 'default',
    name: '默认主题',
    description: '简洁大方的默认样式',
    css_styles: '.article { max-width: 800px; margin: 0 auto; padding: 20px; }',
    template: '<div class="article">\n  <h1>{{ title }}</h1>\n  <div class="content">{{ content }}</div>\n</div>'
  },
  'orangeheart': {
    id: 'orangeheart',
    name: '橙心主题',
    description: '温暖的橙色主题',
    css_styles: '.article { background-color: #fff3e0; border: 1px solid #ffcc80; }',
    template: '<div class="article orangeheart">\n  <h1>{{ title }}</h1>\n  <div class="content">{{ content }}</div>\n</div>'
  }
}

// 加载主题数据
const loadThemeData = async () => {
  const themeId = route.params.themeId
  if (!themeId) {
    ElMessage.error('主题ID无效')
    router.push('/theme/list')
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
      themeForm.value = { ...theme }
    } else {
      ElMessage.error('主题不存在')
      router.push('/theme/list')
    }
  } catch (error) {
    ElMessage.error('加载主题数据失败：' + error.message)
    router.push('/theme/list')
  } finally {
    loading.close()
  }
}

// 提交表单
const submitForm = async () => {
  if (!themeFormRef.value) return
  
  await themeFormRef.value.validate(async (valid) => {
    if (valid) {
      isSubmitting.value = true
      try {
        // 模拟保存操作
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 显示成功消息
        ElMessage.success('主题更新成功！')
        
        // 跳转到主题列表
        router.push('/theme/list')
      } catch (error) {
        ElMessage.error('主题更新失败：' + error.message)
      } finally {
        isSubmitting.value = false
      }
    } else {
      console.log('表单验证失败')
      return false
    }
  })
}

// 重置表单
const resetForm = () => {
  if (!themeFormRef.value) return
  themeFormRef.value.resetFields()
}

// 取消操作
const cancel = () => {
  router.push('/theme/list')
}

// 组件挂载时加载主题数据
onMounted(() => {
  loadThemeData()
})
</script>

<style scoped>
.theme-edit-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.theme-edit-container h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #303133;
}

.theme-form {
  max-width: 800px;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.css-tabs,
.template-tabs {
  margin-top: 10px;
}

.code-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.css-preview,
.template-preview {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.css-preview pre,
.template-preview pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-form {
    max-width: 100%;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
}
</style>