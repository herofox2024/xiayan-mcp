# xiayan-mcp 启动指南

## 1. 环境准备

### 安装Python 3.9+
```bash
# 检查Python版本
python --version
# 或
python3 --version
```

### 安装依赖
```bash
# 进入项目目录
cd "e:\资料\文颜公众号MCP\xiayan-mcp"

# 安装项目依赖
pip install -r requirements.txt

# 或开发模式安装（推荐）
pip install -e .
```

### 依赖说明
xiayan-mcp使用以下核心依赖：
- **mcp>=0.9.0** - MCP协议支持
- **markdown>=3.5.0** - Markdown解析
- **pygments>=2.16.0** - 代码高亮
- **requests>=2.31.0** - HTTP请求
- **pydantic>=2.0.0** - 数据验证
- **jinja2>=3.1.0** - 模板引擎
- **python-frontmatter>=1.0.0** - 文章元数据
- **beautifulsoup4>=4.12.0** - HTML解析

## 2. 配置微信公众号API

### 获取API凭证
1. 登录[微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 获取`AppID`和`AppSecret`

### 配置环境变量

#### 方式一：交互式配置（推荐）

启动服务器时，系统会自动检查微信公众号API凭证是否设置：
- 如果未设置，会**交互式提示**您输入凭证
- 使用安全的输入方式，**App Secret会被隐藏**，保护隐私
- 支持将凭证保存到`.env`文件，下次自动加载

```bash
python run.py
```

#### 方式二：手动编辑.env文件

创建 `.env` 文件并配置环境变量：

```bash
# Windows
notepad .env

# Linux/Mac
nano .env
```

在`.env`文件中填入：
```
# 微信公众号 API 配置
WECHAT_APP_ID=your_id_here
WECHAT_APP_SECRET=your_secret_here

# 可选配置
DEBUG=False
HOST_IMAGE_PATH=/path/to/local/images
```

### 配置IP白名单
在微信公众平台的基本配置页面，将你的服务器IP地址添加到IP白名单中。

**注意**：xiayan-mcp会自动从`.env`文件加载环境变量，无需手动设置系统环境变量。

## 3. 启动方式

### 方式一：直接运行启动脚本（推荐）
```bash
# 使用启动脚本（自动配置Python路径）
python run.py

# 强制重新配置微信API凭证
python run.py --reconfigure
# 或使用短选项
python run.py -r

# 启用调试日志
python run.py --debug
# 或使用短选项
python run.py -d
```

#### 命令行选项说明
- `--reconfigure` 或 `-r`：强制重新配置微信API凭证
- `--debug` 或 `-d`：启用调试日志，用于排查问题

**启动成功输出示例：**
```
=== 夏颜公众号助手 (xiayan-mcp) ===
正在启动MCP服务器...
正在初始化xiayan-mcp服务器...
服务器初始化完成，正在启动MCP服务...
MCP服务器已就绪，正在等待请求...
提示：使用Ctrl+C可以停止服务器
```

### 方式二：使用包管理器运行
```bash
# 确保已安装项目
pip install -e .

# 直接运行包命令
xiayan-mcp
```

### 方式三：Python模块运行
```bash
# 在项目根目录
cd "e:\资料\文颜公众号MCP\xiayan-mcp"
python -m xiayan_mcp.server
```

### 方式四：直接运行源码
```bash
# 手动设置Python路径并运行
cd "e:\资料\文颜公众号MCP\xiayan-mcp" #这里输入你的项目所在路径
export PYTHONPATH=$PYTHONPATH:./src  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;.\src     # Windows
python src/xiayan_mcp/server.py
```

### 方式五：使用项目提供的其他启动脚本
```bash
# 使用固定版本的启动脚本（修复编码问题）
python fixed_run.py

# 使用MCP服务器脚本
python mcp_server.py
```

## 4. MCP客户端集成

### Codebuddy配置
在Codebuddy的MCP配置中添加xiayan-mcp服务器：

#### 配置方式一：通过Codebuddy设置界面
1. 打开Codebuddy设置
2. 找到"MCP Servers"或"MCP配置"选项
3. 添加新的MCP服务器：
   - **名称**: 夏颜公众号助手
   - **命令**: python
   - **参数**: `["e:\\资料\\文颜公众号MCP\\xiayan-mcp\\run.py"]`
   - **环境变量**:
     ```
     WECHAT_APP_ID=your_app_id
     WECHAT_APP_SECRET=your_app_secret
     ```

#### 配置方式二：编辑配置文件
如果Codebuddy使用配置文件，通常在用户目录下的`.codebuddy`或配置目录中，找到MCP配置文件并添加：

```json
{
  "mcpServers": {
    "xiayan-mcp": {
      "name": "夏颜公众号助手",
      "command": "python",
      "args": ["e:\\资料\\文颜公众号MCP\\xiayan-mcp\\run.py"],
      "env": {
        "WECHAT_APP_ID": "your_app_id",
        "WECHAT_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

#### 配置方式三：使用Codebuddy命令行
如果Codebuddy支持命令行配置MCP服务器：

```bash
codebuddy mcp add xiayan-mcp \
  --name "夏颜公众号助手" \
  --command python \
  --args "e:\\资料\\文颜公众号MCP\\xiayan-mcp\\run.py" \
  --env WECHAT_APP_ID=your_app_id \
  --env WECHAT_APP_SECRET=your_app_secret
```

### 其他MCP客户端配置
对于其他支持MCP协议的客户端，请参考相应文档配置服务器命令：
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

## 5. MCP客户端集成使用

### 在Codebuddy中使用xiayan-mcp

配置完成后，重启Codebuddy，你就可以在对话中使用xiayan-mcp的功能：

#### 1. 列出可用主题
```
请列出xiayan-mcp支持的所有主题
```

#### 2. 发布文章
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

#### 3. 批量操作
```
请先列出所有主题，然后帮我用orangeheart主题发布以下内容...
```

### 验证MCP连接

在Codebuddy中输入测试指令确认服务正常：

1. **检查服务状态**：
```
检查xiayan-mcp服务是否正常运行
```

2. **测试主题功能**：
```
使用list_themes工具列出所有可用主题
```

### 检查服务状态
```bash
# 启动后应该看到类似输出（如果启用调试模式）：
# Server started successfully
# Waiting for MCP connections...
```

### 使用MCP Inspector测试
```bash
# 安装MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 启动Inspector
mcp-inspector

# 在Inspector中配置服务器
# 然后测试 "list_themes" 工具
```

### 测试工具调用
启动成功后，可以通过MCP客户端测试以下工具：

1. **列出可用主题**：
```json
{
  "tool": "list_themes",
  "arguments": {}
}
```

2. **发布文章**：
```json
{
  "tool": "publish_article",
  "arguments": {
    "content": "---\ntitle: 测试文章\ncover: https://example.com/cover.jpg\n---\n\n# 这是测试文章\n\n文章内容...",
    "theme_id": "default"
  }
}
```

## 6. 验证启动

### 问题1：导入错误
```bash
# 错误：ModuleNotFoundError: No module named 'xiayan_mcp'
# 解决：
export PYTHONPATH=$PYTHONPATH:./src  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;.\src     # Windows
# 或使用启动脚本
python run.py  # 自动配置路径
```

### 问题2：微信API调用失败
```bash
# 检查环境变量
echo $WECHAT_APP_ID
echo $WECHAT_APP_SECRET

# 检查.env文件
cat .env

# 确认IP白名单配置
# 确认API凭证正确性
```

### 问题3：依赖冲突
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt

# 如果仍有问题，尝试清理缓存
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

### 问题4：编码问题
```bash
# 如果遇到编码错误，使用修复版本
python fixed_run.py

# 或运行诊断脚本
python diagnose.py
python simple_diagnose.py
```

### 问题5：MCP连接失败
```bash
# 检查MCP客户端配置是否正确
# 确认命令路径和参数
# 检查环境变量设置

# 在Windows下测试路径
python "e:\资料\文颜公众号MCP\xiayan-mcp\run.py"

# 检查Python版本兼容性
python --version  # 需要3.9+

# 检查端口占用
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac
```

### 问题6：测试文件缺失
```bash
# 如果测试文件不在tests目录，可以手动移动
# 所有测试文件应位于tests/目录下
ls tests/
```

## 7. 常见问题排查

如果需要开发和调试：

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 启用调试模式
export DEBUG=True
python run.py

# 运行测试
pytest

# 代码格式化
black src/
ruff check src/
```

## 8. 开发模式启动

### Docker部署
```bash
# 构建Docker镜像（需要创建Dockerfile）
docker build -t xiayan-mcp .

# 运行容器
docker run --rm -i \
  -e WECHAT_APP_ID=your_app_id \
  -e WECHAT_APP_SECRET=your_app_secret \
  xiayan-mcp
```

### 系统服务
可以配置为systemd服务（Linux）或Windows服务，实现开机自启动。

## 9. 生产环境部署

- 使用虚拟环境隔离依赖
- 配置适当的日志级别
- 考虑异步处理的并发限制
- 监控内存和CPU使用情况

## 10. 性能优化

- 使用虚拟环境隔离依赖
- 配置适当的日志级别
- 考虑异步处理的并发限制
- 监控内存和CPU使用情况

## 11. 安全注意事项

- 不要在代码中硬编码API密钥
- 使用环境变量或安全的配置管理
- 定期轮换API密钥
- 限制服务器的网络访问权限
- 监控API调用频率和异常

---

启动成功后，xiayan-mcp将等待MCP客户端的连接，你可以通过支持MCP协议的AI工具来使用它发布微信公众号文章。

如有问题，请查看[故障排除](#7-常见问题排查)部分或提交Issue。