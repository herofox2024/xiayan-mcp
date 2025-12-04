#!/usr/bin/env python3
"""
媒体相关API路由
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

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from core.xiayan_mcp import XiayanMCP

# 创建路由器
router = APIRouter()

# 创建XiayanMCP实例
xiayan_mcp = XiayanMCP()

# 媒体上传请求模型
class MediaUploadRequest(BaseModel):
    media_path: str
    media_type: Optional[str] = "image"

# 媒体响应模型
class MediaResponse(BaseModel):
    media_id: str
    message: str

class MediaListResponse(BaseModel):
    media_list: List[dict]
    total_count: int

@router.post("/upload/temp", response_model=MediaResponse)
async def upload_temp_media(media_path: str, media_type: Optional[str] = "image"):
    """上传临时媒体文件（有效期3天）"""
    try:
        media_id = await xiayan_mcp.upload_temp_media(
            media_path=media_path,
            media_type=media_type
        )
        return MediaResponse(
            media_id=media_id,
            message="临时媒体文件上传成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传临时媒体失败: {str(e)}"
        )

@router.post("/upload/permanent", response_model=MediaResponse)
async def upload_permanent_material(media_path: str, media_type: Optional[str] = "image"):
    """上传永久媒体素材"""
    try:
        media_id = await xiayan_mcp.upload_permanent_material(
            media_path=media_path,
            media_type=media_type
        )
        return MediaResponse(
            media_id=media_id,
            message="永久媒体素材上传成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传永久媒体素材失败: {str(e)}"
        )

@router.post("/upload/image_for_news")
async def upload_image_for_news(media_path: str):
    """上传新闻图片，返回可直接使用的URL"""
    try:
        image_url = await xiayan_mcp.upload_image_for_news(
            image_path=media_path
        )
        return {"image_url": image_url, "message": "新闻图片上传成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传新闻图片失败: {str(e)}"
        )

@router.get("/list", response_model=MediaListResponse)
async def get_media_list(
    media_type: Optional[str] = "image",
    permanent: Optional[bool] = True,
    offset: Optional[int] = 0,
    count: Optional[int] = 20
):
    """获取媒体素材列表"""
    try:
        result = await xiayan_mcp.get_media_list(
            media_type=media_type,
            permanent=permanent,
            offset=offset,
            count=count
        )
        return MediaListResponse(
            media_list=result.get("items", []),
            total_count=result.get("total_count", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取媒体列表失败: {str(e)}"
        )

@router.post("/upload/cover", response_model=MediaResponse)
async def upload_cover_image(media_path: str):
    """上传封面图片"""
    try:
        media_id = await xiayan_mcp.upload_cover_image(
            image_path=media_path
        )
        return MediaResponse(
            media_id=media_id,
            message="封面图片上传成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传封面图片失败: {str(e)}"
        )

@router.delete("/{media_id}")
async def delete_permanent_material(media_id: str):
    """删除永久媒体素材"""
    try:
        result = await xiayan_mcp.delete_permanent_material(
            media_id=media_id
        )
        return {"message": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除永久媒体素材失败: {str(e)}"
        )

@router.get("/test")
async def test_media_api():
    """测试媒体API"""
    return {"message": "媒体API测试成功"}
