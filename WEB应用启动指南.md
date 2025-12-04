# xiayan-mcp Web应用启动指南

## 概述
xiayan-mcp Web应用采用前后端分离架构，包含以下三个主要服务：

1. **MCP核心服务** - 原始的MCP服务器，处理微信公众号API调用
2. **Web后端服务** - FastAPI构建的RESTful API服务
3. **Web前端应用** - Vue 3 + Element Plus构建的可视化界面

## 功能更新记录

### 最新更新

1. **修复文章发布功能**
   - 修复了HTTP 422错误，添加了缺失的title字段验证
   - 修复了布尔值/整数类型不匹配问题
   - 删除了保存草稿按钮，简化发布流程

2. **优化文章编辑体验**
   - 实现了文章标题、作者、主题填写后自动更新到文章内容
   - 调整了编辑器尺寸为1400px×900px，优化编辑体验
   - 修复了Markdown预览功能，支持实时预览

3. **修复主题样式问题**
   - 修复了主题选择后样式不显示的问题
   - 确保不同主题显示不同的样式效果
   - 优化了前端主题数据获取，从后端API获取真实主题数据

4. **修复访问地址问题**
   - 确保前端应用通过http://localhost:8000访问
   - 修复了前端开发服务器端口冲突问题

5. **优化内容格式**
   - 修复了文章内容重复显示元信息的问题
   - 改进了Markdown转HTML的格式化算法
   - 增强了日志记录，便于调试

## 系统要求

- Python 3.8+ 
- Node.js 16+ 
- npm 8+ 或 yarn

## 快速启动（推荐）

对于已安装依赖的用户，可以按照以下步骤快速启动应用：

### 1. 构建前端应用（仅首次或前端代码更新后需要）

```bash
cd web_frontend
npm run build
```

### 2. 启动Web后端服务

```bash
cd web_backend
python main.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:8000

## 详细启动步骤

### 1. 安装系统依赖

#### 安装Python依赖

```bash
# 安装核心服务依赖
pip install -r requirements.txt

# 安装Web后端依赖
pip install -r web_backend/requirements.txt
```

#### 安装前端依赖

```bash
# 进入前端目录
cd web_frontend

# 安装依赖
npm install
```

### 2. 配置环境变量

复制环境变量模板文件并进行配置：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
# 根据实际情况配置微信公众号AppID和AppSecret
# 或者在Web界面中配置
```

### 3. 启动服务

#### 方式一：分别启动（开发环境推荐）

**启动MCP核心服务**：
```bash
python run.py
```

**启动Web后端服务**：
```bash
cd web_backend
python main.py
```

**启动前端开发服务器**：
```bash
cd web_frontend
npm run dev
```

#### 方式二：构建生产版本

**构建前端应用**：
```bash
cd web_frontend
npm run build
```

**将构建产物复制到后端静态目录**：
```bash
# 创建静态目录
mkdir -p web_backend/static

# 复制构建产物
cp -r web_frontend/dist/* web_backend/static/
```

**启动合并的Web服务**：
```bash
cd web_backend
python main.py
```

## 访问地址

- **Web应用主地址**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **前端开发服务器**：http://localhost:3000（开发模式）
- **MCP核心服务**：默认通过stdin/stdout通信（用于MCP客户端连接）

## 服务说明

### MCP核心服务
- 负责与微信公众号API交互
- 提供MCP协议服务
- 启动命令：`python run.py`
- 日志输出：控制台输出

### Web后端服务
- 提供RESTful API接口
- 处理前端请求
- 调用MCP核心服务
- 启动命令：`python web_backend/main.py`
- 访问地址：http://localhost:8000
- API文档：http://localhost:8000/docs

### 前端应用
- 可视化操作界面
- Markdown编辑器
- 主题管理
- 媒体管理
- 微信凭证配置
- 开发服务器：`npm run dev`
- 生产构建：`npm run build`

## 开发模式

在开发模式下，建议使用**分别启动**方式：

1. 启动MCP核心服务
2. 启动Web后端服务
3. 启动前端开发服务器

这样可以获得更好的开发体验，包括热重载、调试信息等。

## 生产模式

在生产环境下，建议使用**构建生产版本**方式：

1. 构建前端应用
2. 将构建产物复制到后端静态目录
3. 启动合并的Web服务

这样可以减少服务数量，便于部署和维护。

## 常见问题

### Q: 启动时提示依赖错误怎么办？
A: 确保已安装所有依赖，建议使用虚拟环境管理Python依赖。

### Q: 前端无法连接到后端怎么办？
A: 检查后端服务是否正常运行，确认API地址配置正确。

### Q: 微信API调用失败怎么办？
A: 检查微信凭证是否正确配置，网络连接是否正常。

### Q: 如何查看日志？
A: MCP核心服务和Web后端服务的日志会输出到控制台，前端日志可在浏览器开发者工具中查看。

## 停止服务

- 按 `Ctrl+C` 停止当前运行的服务
- 或者关闭终端窗口

## 后续开发

- 前端开发：在 `web_frontend/src` 目录下进行开发
- 后端开发：在 `web_backend/api` 目录下添加API路由
- 核心功能开发：在 `src/xiayan_mcp` 目录下进行开发

## 技术栈

- **前端**：Vue 3 + Element Plus + Vue Router + Axios
- **后端**：FastAPI + Uvicorn + Python 3
- **核心服务**：Python 3 + asyncio + MCP协议
- **构建工具**：Vite

## 联系方式

如有问题或建议，欢迎提交Issue或联系开发者。
