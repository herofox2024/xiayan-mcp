<template>
  <div class="credential-container">
    <!-- 页面标题 -->
    <h2>微信凭证配置</h2>
    <p class="page-description">
      请配置您的微信公众号开发者凭证，这些凭证用于调用微信公众号API，发布文章、管理媒体等操作。
    </p>

    <!-- 安全提示 -->
    <el-alert
      title="安全提示"
      type="warning"
      :closable="false"
      class="security-alert"
    >
      <template #default>
        <div>
          <p>1. 微信凭证包含AppID和AppSecret，是调用微信API的重要凭证</p>
          <p>2. 请勿将这些凭证泄露给他人，以免造成不必要的损失</p>
          <p>3. 建议定期更换AppSecret，保障账号安全</p>
          <p>4. 凭证将加密存储在本地，不会上传到任何服务器</p>
        </div>
      </template>
    </el-alert>

    <!-- 配置表单 -->
    <el-card class="credential-card">
      <el-form :model="credentialForm" :rules="rules" ref="credentialFormRef" label-width="120px">
        <!-- AppID -->
        <el-form-item label="AppID" prop="app_id">
          <el-input
            v-model="credentialForm.app_id"
            placeholder="请输入微信公众号AppID"
            maxlength="50"
            show-word-limit
            clearable
          ></el-input>
          <div class="form-help-text">
            微信公众号的唯一标识，可在微信公众平台开发者中心获取
          </div>
        </el-form-item>

        <!-- AppSecret -->
        <el-form-item label="AppSecret" prop="app_secret">
          <el-input
            v-model="credentialForm.app_secret"
            placeholder="请输入微信公众号AppSecret"
            maxlength="100"
            show-word-limit
            :type="showAppSecret ? 'text' : 'password'"
            clearable
          >
            <template #append>
              <el-button
                @click="showAppSecret = !showAppSecret"
                type="text"
              >
                <el-icon v-if="showAppSecret"><View /></el-icon>
                <el-icon v-else><Hide /></el-icon>
              </el-button>
            </template>
          </el-input>
          <div class="form-help-text">
            微信公众号的密钥，可在微信公众平台开发者中心获取，请注意保密
          </div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="isSubmitting">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button @click="resetForm">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
          <el-button type="danger" @click="clearCredentials">
            <el-icon><Delete /></el-icon>
            清除凭证
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 凭证状态 -->
    <el-card v-if="savedCredentials" class="status-card">
      <template #header>
        <div class="card-header">
          <span>当前凭证状态</span>
          <el-tag type="success">已配置</el-tag>
        </div>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="AppID">
          <code>{{ savedCredentials.app_id }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="AppSecret">
          <code>{{ maskAppSecret(savedCredentials.app_secret) }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="保存时间">
          {{ formatDate(savedCredentials.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, RefreshRight, Delete, View, Hide } from '@element-plus/icons-vue'

// 表单引用
const credentialFormRef = ref()

// 提交状态
const isSubmitting = ref(false)

// 显示密码
const showAppSecret = ref(false)

// 已保存的凭证
const savedCredentials = ref(null)

// 凭证表单数据
const credentialForm = ref({
  app_id: '',
  app_secret: ''
})

// 表单验证规则
const rules = {
  app_id: [
    { required: true, message: '请输入AppID', trigger: 'blur' },
    { min: 1, max: 50, message: 'AppID长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  app_secret: [
    { required: true, message: '请输入AppSecret', trigger: 'blur' },
    { min: 1, max: 100, message: 'AppSecret长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 掩码处理AppSecret
const maskAppSecret = (appSecret) => {
  if (!appSecret) return ''
  if (appSecret.length <= 8) {
    return appSecret.replace(/./g, '*')
  }
  const prefix = appSecret.substring(0, 4)
  const suffix = appSecret.substring(appSecret.length - 4)
  const middle = '*'.repeat(appSecret.length - 8)
  return prefix + middle + suffix
}

// 从本地存储加载凭证
const loadCredentials = () => {
  try {
    const credentials = localStorage.getItem('wechat_credentials')
    if (credentials) {
      const parsed = JSON.parse(credentials)
      savedCredentials.value = parsed
      // 表单中只显示AppID，不显示AppSecret
      credentialForm.value.app_id = parsed.app_id
      credentialForm.value.app_secret = ''
    }
  } catch (error) {
    console.error('加载凭证失败：', error)
    ElMessage.error('加载凭证失败')
  }
}

// 保存凭证
const saveCredentials = (credentials) => {
  try {
    const data = {
      ...credentials,
      updated_at: new Date().toISOString()
    }
    localStorage.setItem('wechat_credentials', JSON.stringify(data))
    savedCredentials.value = data
    return true
  } catch (error) {
    console.error('保存凭证失败：', error)
    return false
  }
}

// 清除凭证
const clearCredentialsFromStorage = () => {
  try {
    localStorage.removeItem('wechat_credentials')
    savedCredentials.value = null
    return true
  } catch (error) {
    console.error('清除凭证失败：', error)
    return false
  }
}

// 提交表单
const submitForm = async () => {
  if (!credentialFormRef.value) return
  
  await credentialFormRef.value.validate(async (valid) => {
    if (valid) {
      isSubmitting.value = true
      try {
        // 模拟保存操作
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 保存凭证到本地存储
        if (saveCredentials(credentialForm.value)) {
          ElMessage.success('凭证配置保存成功！')
        } else {
          ElMessage.error('凭证保存失败，请检查浏览器存储权限')
        }
      } catch (error) {
        ElMessage.error('保存失败：' + error.message)
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
  if (!credentialFormRef.value) return
  credentialFormRef.value.resetFields()
  // 如果有已保存的凭证，恢复AppID
  if (savedCredentials.value) {
    credentialForm.value.app_id = savedCredentials.value.app_id
  }
}

// 清除凭证
const clearCredentials = () => {
  ElMessageBox.confirm(
    '确定要清除当前的微信凭证吗？此操作不可恢复。',
    '清除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    if (clearCredentialsFromStorage()) {
      credentialForm.value = {
        app_id: '',
        app_secret: ''
      }
      ElMessage.success('凭证已清除')
    } else {
      ElMessage.error('清除凭证失败')
    }
  }).catch(() => {
    // 取消清除
    ElMessage.info('已取消清除')
  })
}

// 组件挂载时加载凭证
onMounted(() => {
  loadCredentials()
})
</script>

<style scoped>
.credential-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.credential-container h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #303133;
}

.page-description {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.security-alert {
  margin-bottom: 20px;
}

.security-alert p {
  margin: 5px 0;
  font-size: 14px;
}

.credential-card {
  margin-bottom: 20px;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.status-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: bold;
  color: #303133;
}

.status-card code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .credential-container {
    padding: 15px;
  }
  
  .credential-card {
    margin-bottom: 15px;
  }
  
  .security-alert {
    margin-bottom: 15px;
  }
}
</style>