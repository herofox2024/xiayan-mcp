# 微信公众号多媒体上传功能使用指南

xiayan-mcp 现已支持完整的微信公众号多媒体上传接口，包括临时素材和永久素材的上传、管理等功能。

## 新增功能

### 1. 临时素材上传

上传临时媒体文件到微信服务器，有效期为3天。

**支持类型：** image（图片）、voice（语音）、video（视频）、thumb（缩略图）

**使用方法：**
```python
# 上传临时图片
media_id = await publisher.upload_temp_media("path/to/image.jpg", "image")
```

### 2. 永久素材上传

上传永久素材到微信服务器，可永久保存。

**支持类型：** image（图片）、voice（语音）、video（视频）、thumb（缩略图）

**使用方法：**
```python
# 上传永久图片
media_id = await publisher.upload_permanent_material("path/to/image.jpg", "image")

# 上传永久视频（需要提供描述信息）
video_description = {
    "title": "视频标题",
    "introduction": "视频简介"
}
media_id = await publisher.upload_permanent_material(
    "path/to/video.mp4", "video", video_description
)
```

### 3. 图文消息图片上传

专门用于图文消息中的图片上传，返回可直接在图文内容中使用的URL。

**使用方法：**
```python
# 上传图文消息中的图片
image_url = await publisher.upload_image_for_news("path/to/image.jpg")
```

### 4. 素材管理

获取和删除永久素材列表。

**使用方法：**
```python
# 获取永久素材列表
materials = await publisher.get_media_list("image", permanent=True)

# 获取临时素材数量
counts = await publisher.get_media_list("image", permanent=False)

# 删除永久素材
success = await publisher.delete_permanent_material("media_id_here")
```

### 5. 增强的文章发布

支持在发布文章时选择封面上传类型（临时/永久）和其他高级选项。

**使用方法：**
```python
# 发布文章，使用永久封面图片
result = await publisher.publish_to_draft(
    title="文章标题",
    content="HTML内容",
    cover="封面图片路径",
    permanent_cover=True,  # 使用永久素材
    author="作者名",
    need_open_comment=0,   # 关闭评论
    only_fans_can_comment=0
)
```

## MCP工具接口

xiayan-mcp 现在提供以下MCP工具：

### 1. `upload_temp_media`
- **描述：** 上传临时媒体文件到微信服务器（有效期3天）
- **参数：**
  - `media_path`（必需）：媒体文件路径（本地或远程URL）
  - `media_type`（可选）：媒体类型（image/voice/video/thumb），默认为image

### 2. `upload_permanent_material`
- **描述：** 上传永久素材到微信服务器
- **参数：**
  - `media_path`（必需）：媒体文件路径（本地或远程URL）
  - `media_type`（可选）：媒体类型（image/voice/video/thumb），默认为image
  - `description`（可选）：视频素材的描述信息，格式为`{"title": "标题", "introduction": "简介"}`

### 3. `upload_image_for_news`
- **描述：** 上传专门用于图文消息的图片，返回可用的URL
- **参数：**
  - `image_path`（必需）：图片文件路径（本地或远程URL）

### 4. `get_media_list`
- **描述：** 获取微信服务器上的媒体素材列表
- **参数：**
  - `media_type`（可选）：媒体类型（image/voice/video/news），默认为image
  - `permanent`（可选）：是否获取永久素材，默认为true
  - `offset`（可选）：分页起始位置，默认为0
  - `count`（可选）：获取数量（1-20），默认为20

### 5. `delete_permanent_material`
- **描述：** 删除永久素材
- **参数：**
  - `media_id`（必需）：要删除的素材的media_id

### 6. `publish_article`（增强）
- **新增参数：**
  - `permanent_cover`（可选）：封面是否使用永久素材，默认为false
  - `author`（可选）：文章作者，默认为"Xiayan MCP"
  - `need_open_comment`（可选）：是否开启评论，默认为0（关闭）
  - `only_fans_can_comment`（可选）：是否仅粉丝可评论，默认为0（否）

## 使用示例

### 示例1：上传临时图片并发布文章

```
# 上传临时图片
media_id = await upload_temp_media(media_path="/path/to/image.jpg", media_type="image")

# 发布文章，使用临时封面
await publish_article(
    content="# 我的文章\n\n这是一篇测试文章。",
    theme_id="default",
    permanent_cover=False,
    author="我的名字"
)
```

### 示例2：上传永久图片并管理素材

```
# 上传永久图片
media_id = await upload_permanent_material(
    media_path="/path/to/image.jpg", 
    media_type="image"
)

# 获取图片素材列表
materials = await get_media_list(media_type="image", permanent=True)

# 删除不再需要的素材
await delete_permanent_material(media_id="要删除的media_id")
```

### 示例3：上传图文消息图片并使用

```
# 上传图文消息图片
image_url = await upload_image_for_news(image_path="/path/to/image.jpg")

# 在文章内容中使用返回的URL
article_content = f"""
# 文章标题

文章正文内容...

![图片描述]({image_url})

更多内容...
"""
```

## 注意事项

1. **权限要求：** 使用前请确保微信公众号已开通相应功能权限
2. **文件限制：** 图片文件大小不超过2MB，支持PNG、JPG格式
3. **临时素材：** 临时素材有效期3天，过期自动删除
4. **永久素材：** 永久素材数量有限制，建议定期清理
5. **网络图片：** 支持从网络URL下载后上传，但需要确保URL可访问
6. **错误处理：** 所有操作都包含完善的错误处理和提示信息

## 测试方法

运行项目中的测试脚本验证功能：

```bash
# 设置环境变量
export WECHAT_APP_ID="your_app_id"
export WECHAT_APP_SECRET="your_app_secret"

# 运行测试脚本
python test_media_upload.py
```

请确保在测试前准备好测试用的图片文件，并修改测试脚本中的文件路径。