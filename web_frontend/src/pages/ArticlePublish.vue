<template>
  <div class="article-publish-container">
    <el-form :model="articleForm" :rules="rules" ref="articleFormRef" label-width="80px">
      <!-- 文章标题 -->
      <el-form-item label="文章标题" prop="title">
        <el-input
          v-model="articleForm.title"
          placeholder="请输入文章标题"
          maxlength="100"
          show-word-limit
        ></el-input>
      </el-form-item>

      <!-- 作者 -->
      <el-form-item label="作者" prop="author">
        <el-input
          v-model="articleForm.author"
          placeholder="请输入作者名称"
          maxlength="50"
          show-word-limit
        ></el-input>
      </el-form-item>

      <!-- 主题选择 -->
      <el-form-item label="主题" prop="theme_id">
        <el-select
          v-model="articleForm.theme_id"
          placeholder="请选择文章主题"
          style="width: 100%"
        >
          <el-option
            v-for="theme in themes"
            :key="theme.id"
            :label="theme.name"
            :value="theme.id"
          >
            <span>{{ theme.name }}</span>
            <span v-if="theme.description" class="theme-description">({{ theme.description }})</span>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 评论设置 -->
      <el-form-item label="评论设置">
        <el-checkbox v-model="articleForm.need_open_comment">允许评论</el-checkbox>
        <el-checkbox v-model="articleForm.only_fans_can_comment" class="ml-4">仅粉丝可评论</el-checkbox>
      </el-form-item>

      <!-- 封面图设置 -->
      <el-form-item label="封面图">
        <el-radio-group v-model="articleForm.permanent_cover" size="small">
          <el-radio-button :label="false">临时封面</el-radio-button>
          <el-radio-button :label="true">永久封面</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- Markdown编辑器 -->
      <el-form-item label="文章内容">
        <div class="markdown-editor-container">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="编辑" name="edit">
              <div class="editor-wrapper">
                <textarea
                  v-model="articleForm.content"
                  placeholder="请输入Markdown格式的文章内容"
                  class="markdown-textarea"
                ></textarea>
              </div>
            </el-tab-pane>
            <el-tab-pane label="预览" name="preview">
              <div class="preview-wrapper">
                <div class="preview-content" v-html="previewContent"></div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="isSubmitting">
          发布文章
        </el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 表单引用
const articleFormRef = ref()

// 发布状态
const isSubmitting = ref(false)

// 当前激活的标签页
const activeTab = ref('edit')

// 从后端API获取主题数据
const themes = ref([])

// 获取主题列表
const fetchThemes = async () => {
  try {
    const response = await fetch('/api/themes/')
    if (response.ok) {
      const data = await response.json()
      themes.value = data
      console.log('获取主题列表成功:', data)
    } else {
      console.error('获取主题列表失败:', response.status)
    }
  } catch (error) {
    console.error('获取主题列表出错:', error)
  }
}

// 文章表单数据
const articleForm = ref({
  title: '',
  author: 'Xiayan MCP',
  content: '# 文章标题\n\n这是一篇测试文章，使用Markdown格式编写。\n\n## 二级标题\n\n- 列表项1\n- 列表项2\n- 列表项3\n\n**粗体文本** *斜体文本*\n\n> 引用内容\n\n```python\n# Python代码示例\nprint("Hello, World!")\n```',
  theme_id: 'default',
  need_open_comment: false,
  only_fans_can_comment: false,
  permanent_cover: false
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者名称', trigger: 'blur' },
    { min: 1, max: 50, message: '作者名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  theme_id: [
    { required: true, message: '请选择文章主题', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' }
  ]
}

// 监听表单变化，实时更新文章内容
watch(
  () => {
    return {
      title: articleForm.value.title,
      author: articleForm.value.author,
      theme_id: articleForm.value.theme_id
    };
  },
  (newVal, oldVal) => {
    console.log('表单变化触发更新:', newVal, oldVal);
    
    // 检查是否有实际变化
    if (JSON.stringify(newVal) === JSON.stringify(oldVal)) {
      console.log('值未变化，跳过更新');
      return;
    }
    
    try {
      // 更新文章标题和元信息
      let updatedContent = articleForm.value.content;
      console.log('当前文章内容:', updatedContent.substring(0, 100) + '...');
      
      // 1. 处理标题
      const titleRegex = /^#\s+.+$/m;
      const titleMatch = updatedContent.match(titleRegex);
      
      if (titleMatch) {
        // 更新已有标题
        updatedContent = updatedContent.replace(titleRegex, `# ${newVal.title}`);
        console.log('已更新标题');
      } else {
        // 添加新标题
        updatedContent = `# ${newVal.title}\n\n${updatedContent}`;
        console.log('已添加标题');
      }
      
      // 2. 处理作者和主题信息
      // 移除所有已有的重复元信息行（没有---分隔符的情况）
      updatedContent = updatedContent.replace(/^author:\s+.+$/gm, '');
      updatedContent = updatedContent.replace(/^theme:\s+.+$/gm, '');
      // 移除多余的空行
      updatedContent = updatedContent.replace(/\n{3,}/g, '\n\n');
      
      // 处理---分隔的元信息块
      const metaRegex = /---\n(.*?)\n---\n/s;
      const metaMatch = updatedContent.match(metaRegex);
      
      const metaContent = `---\nauthor: ${newVal.author}\ntheme: ${newVal.theme_id}\n---\n`;
      
      if (metaMatch) {
        // 更新已有元信息
        updatedContent = updatedContent.replace(metaRegex, metaContent);
        console.log('已更新元信息');
      } else {
        // 在标题后添加元信息
        const titleLineRegex = /^#\s+.+\n/m;
        updatedContent = updatedContent.replace(titleLineRegex, `$&${metaContent}`);
        console.log('已添加元信息');
      }
      
      // 3. 更新文章内容
      articleForm.value.content = updatedContent;
      console.log('文章内容更新完成');
      console.log('更新后内容:', updatedContent.substring(0, 100) + '...');
      
    } catch (error) {
      console.error('更新文章内容时出错:', error);
    }
  },
  { deep: true }
)

// 预览内容（修复版）
const previewContent = ref('')
const isPreviewLoading = ref(false)

// 简单的Markdown转HTML（降级方案）
const simpleMarkdownPreview = () => {
  let content = articleForm.value.content
  
  // 修复换行符处理（兼容Windows和Unix换行符）
  content = content.replace(/\r\n/g, '\n')
  
  // 代码块转换（优先处理，避免影响其他转换）
  content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
  
  // 标题转换
  content = content.replace(/^(#{1,6})\s+(.*)$/gm, (match, level, text) => {
    const hLevel = Math.min(6, level.length)
    return `<h${hLevel}>${text}</h${hLevel}>`
  })
  
  // 粗体转换
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // 斜体转换
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  
  // 无序列表转换
  content = content.replace(/^-\s+(.*)$/gm, '<li>$1</li>')
  content = content.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>')
  
  // 有序列表转换
  content = content.replace(/^(\d+)\.\s+(.*)$/gm, '<li>$2</li>')
  content = content.replace(/(<li>.*?<\/li>)+/gs, '<ol>$&</ol>')
  
  // 引用转换
  content = content.replace(/^>\s+(.*)$/gm, '<blockquote>$1</blockquote>')
  
  // 行内代码转换
  content = content.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  // 段落转换（处理剩余的行）
  content = content.replace(/^(?!<h|<ul|<ol|<li|<blockquote|<pre|<code).*$/gm, '<p>$&</p>')
  
  // 空行处理
  content = content.replace(/\n{2,}/g, '</p><p>')
  
  // 移除多余的空段落
  content = content.replace(/<p><\/p>/g, '')
  
  return content
}

// 主题化预览内容
const updatePreviewContent = async () => {
  if (activeTab.value !== 'preview') {
    return
  }
  
  isPreviewLoading.value = true
  try {
    // 使用简单的Markdown转换作为默认预览
    let htmlContent = simpleMarkdownPreview()
    
    // 尝试从后端获取主题化预览
    try {
      const response = await fetch(`/api/themes/${articleForm.value.theme_id}/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sample_content: articleForm.value.content
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        htmlContent = result.html_content
        console.log('主题预览更新成功')
      }
    } catch (error) {
      console.error('获取主题预览失败，使用本地预览:', error)
    }
    
    previewContent.value = htmlContent
  } catch (error) {
    console.error('更新预览内容出错:', error)
    previewContent.value = '<p>预览生成失败</p>'
  } finally {
    isPreviewLoading.value = false
  }
}

// 监听内容和主题变化，更新预览
watch(
  [() => articleForm.value.content, () => articleForm.value.theme_id, () => activeTab.value],
  () => {
    updatePreviewContent()
  }
)

// 提交表单
const submitForm = async () => {
  if (!articleFormRef.value) return
  
  await articleFormRef.value.validate(async (valid) => {
    if (valid) {
      isSubmitting.value = true
      try {
        // 调用真实的后端API
        const response = await fetch('/api/articles/publish', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(articleForm.value)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const result = await response.json()
        
        // 显示成功消息
        ElMessage.success(result.message || '文章发布成功！')
        
        // 重置表单
        resetForm()
      } catch (error) {
        console.error('发布文章失败：', error)
        ElMessage.error('文章发布失败：' + error.message)
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
  if (!articleFormRef.value) return
  articleFormRef.value.resetFields()
}

// 组件挂载时执行
onMounted(async () => {
  console.log('ArticlePublish组件已挂载')
  // 获取主题列表
  await fetchThemes()
  // 初始化预览内容
  updatePreviewContent()
})
</script>

<style scoped>
.article-publish-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.theme-description {
  font-size: 12px;
  color: #909399;
}

.markdown-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-wrapper {
  height: 900px;
  overflow: hidden;
}

.markdown-textarea {
  width: 100%;
  height: 100%;
  padding: 15px;
  border: none;
  outline: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  background-color: #fafafa;
}

.preview-wrapper {
  height: 900px;
  overflow-y: auto;
  padding: 15px;
  background-color: #fff;
}

.preview-content {
  font-size: 14px;
  line-height: 1.8;
}

.preview-content h1,
.preview-content h2,
.preview-content h3,
.preview-content h4,
.preview-content h5,
.preview-content h6 {
  margin: 20px 0 10px 0;
  font-weight: bold;
}

.preview-content h1 {
  font-size: 24px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 10px;
}

.preview-content h2 {
  font-size: 20px;
}

.preview-content h3 {
  font-size: 18px;
}

.preview-content ul {
  padding-left: 20px;
}

.preview-content li {
  margin: 5px 0;
}

.preview-content blockquote {
  margin: 10px 0;
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
  border-radius: 4px;
}

.preview-content pre {
  margin: 10px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow-x: auto;
}

.preview-content code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.preview-content p {
  margin: 10px 0;
}

.ml-4 {
  margin-left: 16px;
}
</style>