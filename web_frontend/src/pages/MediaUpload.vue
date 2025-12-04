<template>
  <div class="media-upload-container">
    <!-- 页面标题 -->
    <h2>上传媒体</h2>

    <!-- 上传配置 -->
    <el-card class="upload-config-card">
      <div class="upload-config">
        <div class="config-item">
          <span class="config-label">媒体类型：</span>
          <el-radio-group v-model="mediaType" size="small">
            <el-radio-button label="image">图片</el-radio-button>
            <el-radio-button label="video">视频</el-radio-button>
            <el-radio-button label="voice">音频</el-radio-button>
            <el-radio-button label="thumb">缩略图</el-radio-button>
          </el-radio-group>
        </div>
        <div class="config-item">
          <span class="config-label">存储类型：</span>
          <el-radio-group v-model="mediaStorage" size="small">
            <el-radio-button label="temp">临时媒体 (3天有效期)</el-radio-button>
            <el-radio-button label="permanent">永久媒体</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- 上传区域 -->
    <el-card class="upload-card">
      <el-upload
        v-model:file-list="fileList"
        :action="uploadAction"
        :headers="uploadHeaders"
        :data="uploadData"
        :multiple="true"
        :limit="10"
        :on-exceed="handleExceed"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-progress="handleProgress"
        :before-upload="beforeUpload"
        drag
        accept="image/*,video/*,audio/*"
        class="upload-dragger"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持上传图片、视频、音频和缩略图文件，单次最多上传10个文件
          </div>
        </template>
      </el-upload>
    </el-card>

    <!-- 上传队列 -->
    <div v-if="fileList.length > 0" class="upload-queue">
      <h3>上传队列 ({{ fileList.length }})</h3>
      <el-table :data="fileList" border stripe size="small">
        <el-table-column prop="name" label="文件名" min-width="200"></el-table-column>
        <el-table-column prop="size" label="文件大小" width="120">
          <template #default="scope">{{ formatFileSize(scope.row.size) }}</template>
        </el-table-column>
        <el-table-column prop="percentage" label="进度" width="150">
          <template #default="scope">
            <el-progress
              v-if="scope.row.status !== 'success'"
              :percentage="scope.row.percentage || 0"
              :status="getProgressStatus(scope.row.status)"
              stroke-width="8"
            ></el-progress>
            <el-tag v-else type="success">上传成功</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button
              v-if="scope.row.status !== 'success'"
              type="danger"
              size="small"
              @click="handleRemove(scope.row)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              @click="handleCopyUrl(scope.row.response.url)"
            >
              <el-icon><DocumentCopy /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 上传结果 -->
    <div v-if="uploadResults.length > 0" class="upload-results">
      <h3>上传结果 ({{ uploadResults.length }})</h3>
      <el-table :data="uploadResults" border stripe size="small">
        <el-table-column prop="name" label="文件名" min-width="200"></el-table-column>
        <el-table-column prop="type" label="类型" width="100"></el-table-column>
        <el-table-column prop="url" label="访问地址" min-width="300">
          <template #default="scope">
            <el-input
              v-model="scope.row.url"
              readonly
              size="small"
              class="url-input"
            >
              <template #append>
                <el-button
                  type="primary"
                  size="small"
                  @click="handleCopyUrl(scope.row.url)"
                >
                  复制
                </el-button>
              </template>
            </el-input>
          </template>
        </el-table-column>
        <el-table-column prop="media_id" label="媒体ID" min-width="200"></el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="storage" label="存储类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.storage === 'permanent' ? 'success' : 'info'">
              {{ scope.row.storage === 'permanent' ? '永久' : '临时' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Delete, DocumentCopy } from '@element-plus/icons-vue'

// 上传配置
const mediaType = ref('image')
const mediaStorage = ref('temp')

// 上传列表和结果
const fileList = ref([])
const uploadResults = ref([])

// 上传URL和配置
const uploadAction = ref('/api/upload/media')

// 上传请求头
const uploadHeaders = computed(() => {
  return {
    'Authorization': 'Bearer ' + localStorage.getItem('token') || ''
  }
})

// 上传额外数据
const uploadData = computed(() => {
  return {
    media_type: mediaType.value,
    storage_type: mediaStorage.value
  }
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取进度状态
const getProgressStatus = (status) => {
  switch (status) {
    case 'uploading':
      return 'progress'
    case 'success':
      return 'success'
    case 'error':
      return 'exception'
    default:
      return 'progress'
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'ready':
      return 'info'
    case 'uploading':
      return 'warning'
    case 'success':
      return 'success'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'ready':
      return '等待上传'
    case 'uploading':
      return '上传中'
    case 'success':
      return '成功'
    case 'error':
      return '失败'
    default:
      return '未知'
  }
}

// 文件超出限制处理
const handleExceed = (files, fileList) => {
  ElMessage.warning(`当前限制单次上传10个文件，本次选择了${files.length}个文件，将自动忽略超出的文件。`)
}

// 上传前处理
const beforeUpload = (file) => {
  // 检查文件大小
  const maxSize = getMaxFileSize()
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过${formatFileSize(maxSize)}`)
    return false
  }
  return true
}

// 获取最大文件大小（根据媒体类型）
const getMaxFileSize = () => {
  const sizeMap = {
    'image': 2 * 1024 * 1024, // 2MB
    'video': 100 * 1024 * 1024, // 100MB
    'voice': 2 * 1024 * 1024, // 2MB
    'thumb': 64 * 1024 // 64KB
  }
  return sizeMap[mediaType.value] || 2 * 1024 * 1024
}

// 上传进度处理
const handleProgress = (event, file, fileList) => {
  // 进度已经在file.percentage中自动更新
}

// 上传成功处理
const handleSuccess = (response, file, fileList) => {
  if (response.code === 200) {
    // 将成功的上传结果添加到结果列表
    const uploadResult = {
      name: file.name,
      type: mediaType.value,
      url: response.data.url,
      media_id: response.data.media_id,
      storage: mediaStorage.value,
      created_at: new Date().toISOString()
    }
    uploadResults.value.unshift(uploadResult)
    ElMessage.success(`文件 "${file.name}" 上传成功`)
  } else {
    ElMessage.error(`文件 "${file.name}" 上传失败：${response.message}`)
  }
}

// 上传失败处理
const handleError = (error, file, fileList) => {
  ElMessage.error(`文件 "${file.name}" 上传失败：${error.message || '网络错误'}`)
}

// 删除文件
const handleRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 复制URL
const handleCopyUrl = (url) => {
  navigator.clipboard.writeText(url)
    .then(() => {
      ElMessage.success('链接复制成功！')
    })
    .catch(() => {
      ElMessage.error('链接复制失败，请手动复制')
    })
}
</script>

<style scoped>
.media-upload-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.media-upload-container h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #303133;
}

.upload-config-card, .upload-card {
  margin-bottom: 20px;
}

.upload-config {
  display: flex;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.config-label {
  font-weight: bold;
  color: #303133;
}

.upload-card {
  min-height: 200px;
}

.upload-dragger {
  width: 100%;
}

.upload-queue, .upload-results {
  margin-top: 20px;
}

.upload-queue h3, .upload-results h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.url-input {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-config {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .config-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>