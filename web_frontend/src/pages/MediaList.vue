<template>
  <div class="media-list-container">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <h2>媒体列表</h2>
      <el-button type="primary" @click="handleUploadMedia">
        <el-icon><Upload /></el-icon>
        上传媒体
      </el-button>
    </div>

    <!-- 搜索和筛选区 -->
    <div class="search-filter">
      <el-select
        v-model="mediaTypeFilter"
        placeholder="筛选媒体类型"
        clearable
        class="filter-select"
      >
        <el-option label="所有类型" value=""></el-option>
        <el-option label="图片" value="image"></el-option>
        <el-option label="视频" value="video"></el-option>
        <el-option label="音频" value="voice"></el-option>
        <el-option label="缩略图" value="thumb"></el-option>
      </el-select>

      <el-input
        v-model="searchKeyword"
        placeholder="搜索媒体名称或ID"
        clearable
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon class="el-input__icon"><Search /></el-icon>
        </template>
      </el-input>

      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <!-- 媒体列表 -->
    <div class="media-grid">
      <el-card
        v-for="media in filteredMedia"
        :key="media.media_id"
        class="media-card"
      >
        <template #header>
          <div class="media-card-header">
            <span class="media-name">{{ media.name }}</span>
            <el-tag :type="getMediaTypeTagType(media.type)">{{ media.type }}</el-tag>
          </div>
        </template>

        <!-- 媒体预览 -->
        <div class="media-preview">
          <div v-if="media.type === 'image'" class="image-preview">
            <el-image
              :src="media.url"
              :preview-src-list="[media.url]"
              fit="cover"
              @click="handlePreviewMedia(media)"
            ></el-image>
          </div>
          <div v-else-if="media.type === 'video'" class="video-preview">
            <el-icon class="video-icon"><VideoPlay /></el-icon>
            <span class="media-type-text">视频文件</span>
            <el-button type="text" @click="handlePreviewMedia(media)">播放</el-button>
          </div>
          <div v-else-if="media.type === 'voice'" class="voice-preview">
            <el-icon class="voice-icon"><Microphone /></el-icon>
            <span class="media-type-text">音频文件</span>
            <el-button type="text" @click="handlePreviewMedia(media)">播放</el-button>
          </div>
          <div v-else class="other-preview">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="media-type-text">{{ media.type }}文件</span>
          </div>
        </div>

        <!-- 媒体信息 -->
        <div class="media-info">
          <div class="info-item">
            <span class="info-label">大小：</span>
            <span class="info-value">{{ formatFileSize(media.size) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间：</span>
            <span class="info-value">{{ formatDate(media.created_at) }}</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="media-actions">
          <el-button
            type="info"
            size="small"
            @click="handleCopyLink(media.url)"
            class="action-btn"
          >
            <el-icon><DocumentCopy /></el-icon>
            复制链接
          </el-button>
          <el-button
            type="primary"
            size="small"
            @click="handlePreviewMedia(media)"
            class="action-btn"
          >
            <el-icon><View /></el-icon>
            预览
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="handleDeleteMedia(media)"
            class="action-btn"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredMedia.length === 0" class="empty-state">
      <el-empty description="暂无媒体文件"></el-empty>
    </div>

    <!-- 分页 -->
    <div v-if="filteredMedia.length > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredMedia.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      ></el-pagination>
    </div>

    <!-- 媒体预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewMedia.name || '媒体预览'"
      width="80%"
      :before-close="handleClosePreview"
    >
      <div class="preview-dialog-content">
        <div v-if="previewMedia.type === 'image'" class="dialog-image-preview">
          <el-image :src="previewMedia.url" fit="contain"></el-image>
        </div>
        <div v-else-if="previewMedia.type === 'video'" class="dialog-video-preview">
          <video :src="previewMedia.url" controls width="100%"></video>
        </div>
        <div v-else-if="previewMedia.type === 'voice'" class="dialog-voice-preview">
          <audio :src="previewMedia.url" controls width="100%"></audio>
        </div>
        <div v-else class="dialog-other-preview">
          <el-empty description="不支持的媒体类型预览"></el-empty>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, VideoPlay, Microphone, Document, DocumentCopy, View, Delete } from '@element-plus/icons-vue'

const router = useRouter()

// 搜索和筛选
const searchKeyword = ref('')
const mediaTypeFilter = ref('')

// 分页参数
const currentPage = ref(1)
const pageSize = ref(12)

// 预览对话框
const previewDialogVisible = ref(false)
const previewMedia = ref({})

// 模拟媒体数据
const mediaList = ref([
  {
    media_id: 'media_001',
    name: '示例图片1.jpg',
    type: 'image',
    size: 1024 * 1024, // 1MB
    url: 'https://picsum.photos/id/1/800/600',
    created_at: new Date().toISOString()
  },
  {
    media_id: 'media_002',
    name: '示例图片2.jpg',
    type: 'image',
    size: 2048 * 1024, // 2MB
    url: 'https://picsum.photos/id/2/800/600',
    created_at: new Date(Date.now() - 86400000).toISOString() // 1天前
  },
  {
    media_id: 'media_003',
    name: '示例视频.mp4',
    type: 'video',
    size: 10 * 1024 * 1024, // 10MB
    url: 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
    created_at: new Date(Date.now() - 172800000).toISOString() // 2天前
  },
  {
    media_id: 'media_004',
    name: '示例音频.mp3',
    type: 'voice',
    size: 512 * 1024, // 512KB
    url: 'https://sample-videos.com/audio/mp3/crowd-cheering.mp3',
    created_at: new Date(Date.now() - 259200000).toISOString() // 3天前
  }
])

// 筛选后的媒体列表
const filteredMedia = computed(() => {
  let result = [...mediaList.value]
  
  // 按类型筛选
  if (mediaTypeFilter.value) {
    result = result.filter(media => media.type === mediaTypeFilter.value)
  }
  
  // 按关键词筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(media => 
      media.name.toLowerCase().includes(keyword) ||
      media.media_id.toLowerCase().includes(keyword)
    )
  }
  
  return result
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

// 获取媒体类型标签颜色
const getMediaTypeTagType = (type) => {
  const typeMap = {
    'image': 'success',
    'video': 'warning',
    'voice': 'info',
    'thumb': 'primary'
  }
  return typeMap[type] || 'default'
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  mediaTypeFilter.value = ''
  currentPage.value = 1
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

// 当前页变化
const handleCurrentChange = (current) => {
  currentPage.value = current
}

// 上传媒体
const handleUploadMedia = () => {
  router.push('/media/upload')
}

// 复制链接
const handleCopyLink = (url) => {
  navigator.clipboard.writeText(url)
    .then(() => {
      ElMessage.success('链接复制成功！')
    })
    .catch(() => {
      ElMessage.error('链接复制失败，请手动复制')
    })
}

// 预览媒体
const handlePreviewMedia = (media) => {
  previewMedia.value = media
  previewDialogVisible.value = true
}

// 关闭预览
const handleClosePreview = () => {
  previewDialogVisible.value = false
}

// 删除媒体
const handleDeleteMedia = (media) => {
  ElMessageBox.confirm(
    `确定要删除媒体文件 "${media.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 模拟删除操作
    const index = mediaList.value.findIndex(item => item.media_id === media.media_id)
    if (index !== -1) {
      mediaList.value.splice(index, 1)
      ElMessage.success('媒体文件删除成功')
    }
  }).catch(() => {
    // 取消删除
    ElMessage.info('已取消删除')
  })
}
</script>

<style scoped>
.media-list-container {
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
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.search-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  width: 150px;
}

.search-input {
  width: 300px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.media-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.media-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.media-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.media-name {
  font-weight: bold;
  color: #303133;
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.media-preview {
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  border-radius: 4px;
  margin: 10px 0;
  cursor: pointer;
}

.image-preview {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 4px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-preview:hover img {
  transform: scale(1.05);
}

.video-preview, .voice-preview, .other-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.video-icon, .voice-icon, .file-icon {
  font-size: 48px;
  color: #909399;
}

.media-type-text {
  color: #606266;
  font-size: 14px;
}

.media-info {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

.info-item {
  display: flex;
  margin: 5px 0;
}

.info-label {
  font-weight: bold;
  margin-right: 5px;
}

.media-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
}

.action-btn {
  flex: 1;
  margin: 0 5px;
}

.empty-state {
  text-align: center;
  padding: 50px 0;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 预览对话框 */
.preview-dialog-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.dialog-image-preview, .dialog-video-preview, .dialog-voice-preview {
  width: 100%;
  max-height: 60vh;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-image-preview img {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.dialog-other-preview {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-select, .search-input {
    width: 100%;
  }
  
  .media-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }
  
  .media-card {
    margin-bottom: 10px;
  }
}
</style>