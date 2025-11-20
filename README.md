# 夏颜 MCP Server

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/xiayan-mcp.svg)](https://badge.fury.io/py/xiayan-mcp)

「夏颜」是一款基于Python的Markdown排版美化工具，让你将Markdown一键发布至微信公众号草稿箱，并使用优雅的主题系统进行排版。本项目基于MCP（Model Context Protocol）协议，可与支持MCP的AI助手无缝集成。

## 功能特性

- 🔧 **Python实现** - 使用纯Python编写，易于扩展和定制
- 🎨 **多主题支持** - 内置8种精美主题，适配不同内容风格
- 📝 **Markdown渲染** - 完整支持Markdown语法，包括代码高亮、表格、TOC等
- 🖼️ **图片自动上传** - 支持本地和网络图片自动上传
- 📱 **微信公众号集成** - 直接发布到公众号草稿箱
- 🔌 **MCP协议** - 基于模型上下文协议，可与AI助手无缝集成
- 📁 **多媒体管理** - 支持临时/永久素材上传、管理和删除
- 🛠️ **丰富工具集** - 提供7个专业MCP工具，覆盖发布、管理全流程

## 主题预览

内置主题包括：

- **默认主题** - 简洁大方的默认样式
- **Orange Heart** - 温暖橙心主题
- **Rainbow** - 彩虹渐变主题  
- **Lapis** - 青金石主题
- **Pie** - 优雅派主题
- **Maize** - 玉米黄主题
- **Purple** - 紫色主题
- **物理猫薄荷** - 清新自然主题

## 安装使用

### 环境要求

- Python 3.9+
- 微信公众号开发者权限
- MCP客户端（如Codebuddy、Claude Desktop等）

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/herofox/xiayan-mcp.git
cd xiayan-mcp

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入微信公众号API凭证

# 启动服务
python run.py
```

### 开发环境设置

### MCP配置

在你的MCP客户端配置文件中添加：

```json
{
  "mcpServers": {
    "xiayan-mcp": {
      "name": "夏颜公众号助手",
      "command": "python",
      "args": ["path/to/xiayan-mcp/run.py"],
      "env": {
        "WECHAT_APP_ID": "your_wechat_app_id",
        "WECHAT_APP_SECRET": "your_wechat_app_secret"
      }
    }
  }
}
```

#### Codebuddy快速配置

如果你使用Codebuddy，可以直接使用以下配置：

```json
{
  "mcpServers": {
    "xiayan-mcp": {
      "name": "夏颜公众号助手",
      "command": "python",
      "args": ["e:\\资料\\文颜公众号MCP\\xiayan-mcp\\run.py"],
      "env": {
        "WECHAT_APP_ID": "your_wechat_app_id",
        "WECHAT_APP_SECRET": "your_wechat_app_secret"
      }
    }
  }
}
```

### 环境变量

需要在环境中设置微信公众号的API凭证：

- `WECHAT_APP_ID` - 微信公众号App ID
- `WECHAT_APP_SECRET` - 微信公众号App Secret

### 文章格式

在Markdown文章开头添加frontmatter：

```markdown
---
title: 你的文章标题
cover: /path/to/cover/image.jpg
---

# 正文内容

这里是你的文章正文内容...
```

## MCP工具接口

xiayan-mcp 提供以下7个专业工具：

### 1. `publish_article` - 发布文章
将Markdown文章发布到微信公众号草稿箱，支持主题选择和高级选项。

**参数：**
- `content`（必需）：Markdown内容，支持frontmatter
- `theme_id`（可选）：主题ID，默认为default
- `permanent_cover`（可选）：封面是否使用永久素材，默认false
- `author`（可选）：作者名，默认为"Xiayan MCP"
- `need_open_comment`（可选）：是否开启评论，默认0
- `only_fans_can_comment`（可选）：是否仅粉丝可评论，默认0

### 2. `list_themes` - 列出主题
获取所有可用的主题信息。

### 3. `upload_temp_media` - 上传临时素材
上传临时媒体文件，有效期3天。

**参数：**
- `media_path`（必需）：媒体文件路径
- `media_type`（可选）：类型（image/voice/video/thumb），默认image

### 4. `upload_permanent_material` - 上传永久素材
上传永久素材到微信服务器。

**参数：**
- `media_path`（必需）：媒体文件路径
- `media_type`（可选）：类型（image/voice/video/thumb），默认image
- `description`（可选）：视频描述（视频素材必需）

### 5. `upload_image_for_news` - 上传图文图片
专门用于图文消息的图片上传，返回可用URL。

**参数：**
- `image_path`（必需）：图片文件路径

### 6. `get_media_list` - 获取素材列表
获取微信服务器上的媒体素材列表。

**参数：**
- `media_type`（可选）：媒体类型，默认image
- `permanent`（可选）：是否永久素材，默认true
- `offset`（可选）：分页起始位置，默认0
- `count`（可选）：获取数量（1-20），默认20

### 7. `delete_permanent_material` - 删除永久素材
删除指定的永久素材。

**参数：**
- `media_id`（必需）：要删除的素材media_id

## 使用示例

### 基础文章发布
```
请使用xiayan-mcp帮我发布一篇文章到微信公众号草稿箱：

---
title: 测试文章
cover: https://example.com/cover.jpg
---

# 这是测试文章

这是一篇使用xiayan-mcp发布的测试文章，使用了default主题。

## 功能介绍

- Markdown排版
- 多主题支持
- 自动图片上传
- 微信公众号发布

主题ID请使用：default
```

### 多媒体操作
```
请帮我：
1. 上传一张临时图片：/path/to/image.jpg
2. 获取图片素材列表
3. 使用orangeheart主题发布一篇文章
```

### 高级发布选项
```
发布文章到微信公众号，要求：
- 使用purple主题
- 封面图片作为永久素材
- 开启评论功能
- 作者名为"我的名字"

内容：
---
title: 高级测试文章
cover: /path/to/cover.jpg
---

# 高级测试文章

这是测试高级功能的文章...
```

## 项目结构

```
xiayan-mcp/
├── src/                          # 源代码目录
│   └── xiayan_mcp/               # Python包
│       ├── __init__.py           # 包初始化
│       ├── server.py             # MCP服务器主入口
│       ├── core/                 # 核心功能模块
│       │   ├── __init__.py
│       │   ├── formatter.py      # Markdown格式化器
│       │   └── publisher.py      # 微信公众号发布器
│       └── themes/               # 主题系统
│           ├── __init__.py
│           └── theme_manager.py  # 主题管理器
├── tests/                        # 测试文件目录
├── data/                         # 数据目录
├── .env.example                  # 环境变量模板
├── .env                          # 实际环境变量配置
├── pyproject.toml               # Python项目配置
├── requirements.txt             # 依赖包列表
├── run.py                       # 主启动脚本
├── mcp_server.py                # MCP服务器脚本
├── fixed_run.py                 # 修复版启动脚本
└── README.md                    # 项目说明文档
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/herofox2024/xiayan-mcp.git
cd xiayan-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
ruff check src/
```

### 添加新主题

1. 在`themes/theme_manager.py`中添加新主题
2. 定义对应的CSS样式
3. 更新主题列表

```python
# 示例：添加新主题
"my_theme": Theme(
    id="my_theme",
    name="我的主题",
    description="自定义主题描述",
    template=self._get_default_template(),
    css_styles=self._get_my_theme_css()
)
```

## 微信公众号配置

1. 登录微信公众平台
2. 获取App ID和App Secret
3. 配置服务器IP白名单
4. 设置开发者权限

详细配置参考：[微信公众平台开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)

## 故障排除

### 常见问题

1. **Access Token获取失败**
   - 检查App ID和App Secret是否正确
   - 确认服务器IP在白名单中
   - 验证`.env`文件配置

2. **图片上传失败**
   - 检查图片路径是否正确
   - 确认图片格式支持（jpg、png等）
   - 检查图片大小限制（微信API限制）

3. **主题不生效**
   - 检查theme_id是否正确
   - 确认CSS语法无误
   - 验证主题文件是否存在

4. **MCP连接失败**
   - 检查Python路径和命令参数
   - 确认环境变量设置正确
   - 验证MCP客户端配置
   - 检查端口占用情况

5. **导入模块错误**
   - 设置PYTHONPATH：`export PYTHONPATH=$PYTHONPATH:./src`
   - 或使用启动脚本：`python run.py`
   - 检查虚拟环境是否正确激活

6. **编码问题**
   - 使用修复版本：`python fixed_run.py`
   - 运行诊断脚本：`python diagnose.py`

### 调试模式

启用详细日志：

```bash
# 设置调试模式
export DEBUG=True

# 启动服务
python run.py

# 或使用更详细的日志
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" run.py
```

### 测试工具

项目提供多个诊断脚本：
- `diagnose.py` - 全面诊断工具
- `simple_diagnose.py` - 简化诊断
- `analyze_encoding.py` - 编码分析
- `debug_conversion.py` - 调试转换

## 贡献

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码格式化
black src/

# 代码检查
ruff check src/

# 类型检查
mypy src/

# 运行测试
pytest tests/
```

### 启动方式

xiayan-mcp支持多种启动方式：

1. **基础启动**：`python run.py`
2. **包管理启动**：`xiayan-mcp`（需先安装 `pip install -e .`）
3. **模块启动**：`python -m xiayan_mcp.server`
4. **修复启动**：`python fixed_run.py`（解决编码问题）
5. **MCP服务器启动**：`python mcp_server.py`

### 测试文件

所有测试文件已整理到 `tests/` 目录中，包含：
- Python测试脚本（`test_*.py`）
- Markdown测试文档（`test_*.md`）
- 测试数据文件

## 许可证

本项目采用 Apache License 2.0 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 更新日志

### v0.1.0
- ✨ 新增完整的微信公众号多媒体上传功能
- 🎨 支持8种精美主题（default, orangeheart, rainbow, lapis, pie, maize, purple, phycat）
- 🔧 提供7个专业MCP工具
- 📱 完善的文档和示例
- 🛠️ 支持临时/永久素材管理
- 🔍 提供多种诊断和调试工具
- 🧪 完整的测试套件（tests/目录）

## 致谢

感谢以下开源项目的启发和支持：

- [文颜 wenyan-mcp](https://github.com/caol64/wenyan-mcp) - 原始TypeScript实现
- [MCP SDK](https://github.com/modelcontextprotocol/servers) - 模型上下文协议
- [Python-Markdown](https://python-markdown.github.io/) - Markdown解析库

## 联系方式

- 项目主页: https://github.com/herofox2024/xiayan-mcp
- 问题反馈: https://github.com/herofox2024/xiayan-mcp/issues
- 邮箱: 42845734@qq.com

---

⭐ 如果这个项目对你有帮助，请给我们一个Star！