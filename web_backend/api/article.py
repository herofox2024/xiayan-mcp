#!/usr/bin/env python3
"""
文章相关API路由
"""

import sys
import os

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

# 先添加src目录到Python路径，然后添加项目根目录
sys.path.insert(0, src_path)
sys.path.insert(1, project_root)

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional, Union
from core.xiayan_mcp import XiayanMCP

# 创建路由器
router = APIRouter()

# 创建XiayanMCP实例
xiayan_mcp = XiayanMCP()

# 文章请求模型
class ArticleRequest(BaseModel):
    content: str
    title: Optional[str] = "未命名文章"
    theme_id: Optional[str] = "default"
    permanent_cover: Optional[bool] = False
    author: Optional[str] = "Xiayan MCP"
    need_open_comment: Optional[Union[int, bool]] = 0
    only_fans_can_comment: Optional[Union[int, bool]] = 0

# 文章响应模型
class ArticleResponse(BaseModel):
    message: str
    media_id: Optional[str] = None
    cover_media_id: Optional[str] = None

@router.post("/publish", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def publish_article(article: ArticleRequest):
    """发布文章到微信公众号草稿箱"""
    print("=== 收到文章发布请求 ===")
    print(f"请求内容: {article}")
    try:
        print("调用xiayan_mcp.publish_article方法...")
        # 转换布尔值为整数（微信API期望整数）
        need_open_comment = int(article.need_open_comment) if isinstance(article.need_open_comment, bool) else article.need_open_comment
        only_fans_can_comment = int(article.only_fans_can_comment) if isinstance(article.only_fans_can_comment, bool) else article.only_fans_can_comment
        
        result = await xiayan_mcp.publish_article(
            title=article.title,
            content=article.content,
            theme_id=article.theme_id,
            permanent_cover=article.permanent_cover,
            author=article.author,
            need_open_comment=need_open_comment,
            only_fans_can_comment=only_fans_can_comment
        )
        print(f"publish_article方法返回结果: {result}")
        response = ArticleResponse(
            message=result["message"],
            media_id=result.get("media_id"),
            cover_media_id=result.get("cover_media_id")
        )
        print(f"返回响应: {response}")
        return response
    except Exception as e:
        print(f"发布文章失败: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发布文章失败: {str(e)}"
        )



@router.get("/test")
async def test_article_api():
    """测试文章API"""
    return {"message": "文章API测试成功"}
