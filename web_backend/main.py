#!/usr/bin/env python3
"""
xiayan-mcp Web后端主应用
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录和src目录到Python路径，以便导入xiayan-mcp模块
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

# 先添加src目录到Python路径，然后添加项目根目录
sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# 创建FastAPI应用
app = FastAPI(
    title="xiayan-mcp Web API",
    description="xiayan-mcp的Web可视化界面API",
    version="1.0.0"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
from api.article import router as article_router
from api.theme import router as theme_router
from api.media import router as media_router
from api.credential import router as credential_router

app.include_router(article_router, prefix="/api/articles", tags=["文章管理"])
app.include_router(theme_router, prefix="/api/themes", tags=["主题管理"])
app.include_router(media_router, prefix="/api/media", tags=["媒体管理"])
app.include_router(credential_router, prefix="/api/credentials", tags=["凭证管理"])

# API根路径
@app.get("/api")
async def api_root():
    return {
        "message": "xiayan-mcp Web API 启动成功",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }

# 静态文件服务
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    # 前端应用路由，处理所有非API和非文档路由
    @app.get("/{path:path}", include_in_schema=False)
    async def serve_frontend(path: str):
        # 如果是API路径或文档路径，让FastAPI处理
        if path in ["docs", "redoc", "openapi.json", "favicon.ico"] or path.startswith("api"):
            return None
        # 其他路径返回前端应用
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "xiayan-mcp Web API"}

# 所有以/api/开头的未匹配路径返回API信息
@app.get("/api/{path:path}", include_in_schema=False)
async def api_path_not_found(path: str):
    return {
        "message": f"API路径未找到: /api/{path}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 添加422错误处理器，捕获并记录详细信息
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理422验证错误，记录详细信息"""
    print(f"=== 422验证错误详情 ===")
    print(f"请求URL: {request.url}")
    print(f"请求方法: {request.method}")
    print(f"请求头: {dict(request.headers)}")
    # 尝试获取请求体
    try:
        body = await request.body()
        print(f"请求体: {body.decode() if body else '空'}")
    except Exception as e:
        print(f"无法获取请求体: {e}")
    print(f"验证错误: {exc}")
    print(f"验证错误详情: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# 首页路由
@app.get("/")
async def read_root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "xiayan-mcp Web API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
