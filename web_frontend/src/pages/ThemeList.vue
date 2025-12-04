<template>
  <div class="theme-list-container">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <h2>主题列表</h2>
      <el-button type="primary" @click="handleAddTheme">
        <el-icon><Plus /></el-icon>
        添加主题
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索主题名称或描述"
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

    <!-- 主题列表 -->
    <div class="theme-table-container">
      <el-table
        :data="filteredThemes"
        stripe
        border
        style="width: 100%"
        @row-dblclick="handleRowDoubleClick"
      >
        <el-table-column prop="id" label="主题ID" width="180" align="center"></el-table-column>
        <el-table-column prop="name" label="主题名称" min-width="150"></el-table-column>
        <el-table-column prop="description" label="主题描述" min-width="250"></el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button
              type="info"
              size="small"
              @click="handlePreviewTheme(scope.row.id)"
              class="mr-2"
            >
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleEditTheme(scope.row.id)"
              class="mr-2"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteTheme(scope.row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredThemes.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      ></el-pagination>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, View, Edit, Delete } from '@element-plus/icons-vue'

const router = useRouter()

// 搜索关键词
const searchKeyword = ref('')

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)

// 模拟主题数据
const themes = ref([
  {
    id: 'default',
    name: '默认主题',
    description: '简洁大方的默认样式',
    created_at: new Date().toISOString()
  },
  {
    id: 'orangeheart',
    name: '橙心主题',
    description: '温暖的橙色主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'rainbow',
    name: '彩虹主题',
    description: '多彩的彩虹主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'lapis',
    name: '青金石主题',
    description: '高贵的蓝色主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'pie',
    name: '馅饼主题',
    description: '可爱的馅饼主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'maize',
    name: '玉米主题',
    description: '明亮的黄色主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'purple',
    name: '紫色主题',
    description: '神秘的紫色主题',
    created_at: new Date().toISOString()
  },
  {
    id: 'phycat',
    name: '猫咪主题',
    description: '萌系猫咪主题',
    created_at: new Date().toISOString()
  }
])

// 筛选后的主题列表
const filteredThemes = computed(() => {
  if (!searchKeyword.value) {
    return themes.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return themes.value.filter(theme => 
    theme.name.toLowerCase().includes(keyword) || 
    (theme.description && theme.description.toLowerCase().includes(keyword)) ||
    theme.id.toLowerCase().includes(keyword)
  )
})

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
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

// 添加主题
const handleAddTheme = () => {
  router.push('/theme/add')
}

// 预览主题
const handlePreviewTheme = (themeId) => {
  router.push(`/theme/preview/${themeId}`)
}

// 编辑主题
const handleEditTheme = (themeId) => {
  router.push(`/theme/edit/${themeId}`)
}

// 删除主题
const handleDeleteTheme = (theme) => {
  ElMessageBox.confirm(
    `确定要删除主题 "${theme.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 模拟删除操作
    const index = themes.value.findIndex(item => item.id === theme.id)
    if (index !== -1) {
      themes.value.splice(index, 1)
      ElMessage.success('主题删除成功')
    }
  }).catch(() => {
    // 取消删除
    ElMessage.info('已取消删除')
  })
}

// 双击行编辑
const handleRowDoubleClick = (row) => {
  handleEditTheme(row.id)
}
</script>

<style scoped>
.theme-list-container {
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

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 300px;
}

.theme-table-container {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.mr-2 {
  margin-right: 8px;
}
</style>