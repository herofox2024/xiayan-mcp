# 优化xiayan-mcp前端应用计划

## 1. 清理测试脚本
- **删除根目录下的测试脚本**：
  - `test_422_capture.py`
  - `test_422_debug.py`
  - `test_frontend_request.py`
  - `test_422_error.py`
  - `test_publish.py`
- **保留**：`web_backend`和`tests`目录下的测试脚本，这些是项目测试套件的一部分

## 2. 优化文章发布功能
修改`web_frontend/src/pages/ArticlePublish.vue`文件：

### 2.1 删除保存草稿功能
- 删除第85行的保存草稿按钮：`<el-button type="info" @click="saveDraft">保存草稿</el-button>`
- 删除第221-225行的`saveDraft`函数

### 2.2 实现文章信息实时更新到内容
- 添加`watch`监听`articleForm`的变化
- 当`title`、`author`或`theme_id`变化时，更新文章内容中的对应部分
- 实现逻辑：
  - 提取现有内容的结构
  - 更新标题行
  - 在内容中添加作者信息
  - 根据主题调整内容格式（如果需要）

### 2.3 增加文章内容显示长度
- 修改`.editor-wrapper`和`.preview-wrapper`的高度，从500px增加到700px
- 调整CSS样式文件中的相关高度设置

## 3. 重启服务并测试
- 停止当前运行的服务
- 重新启动MCP核心服务、Web后端服务和前端开发服务器
- 人工测试文章发布功能：
  - 验证保存草稿按钮已删除
  - 测试文章、作者、主题变化时，文章内容相应更新
  - 确认文章内容显示长度已增加

## 技术实现细节
- 使用Vue 3的`watch` API监听表单变化
- 实现内容模板替换逻辑，保持原有内容结构
- 调整CSS样式，增加编辑器和预览区域高度

## 预期效果
- 测试脚本已清理，项目结构更清晰
- 文章发布功能更简洁，无冗余按钮
- 文章信息实时反映到内容中，提升编辑体验
- 更大的编辑区域，提升内容创作舒适度