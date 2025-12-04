#!/usr/bin/env python3
"""
主题相关API路由
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
from typing import List, Optional
from core.xiayan_mcp import XiayanMCP

# 创建路由器
router = APIRouter()

# 创建XiayanMCP实例
xiayan_mcp = XiayanMCP()

# 主题响应模型
class ThemeResponse(BaseModel):
    id: str
    name: str
    description: str

class ThemePreviewResponse(BaseModel):
    html_content: str

class ThemeCreateRequest(BaseModel):
    id: str
    name: str
    description: str
    template: Optional[str] = None
    css_styles: Optional[str] = None

class ThemeUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    css_styles: Optional[str] = None

@router.get("/", response_model=List[ThemeResponse])
async def get_themes(detailed: Optional[bool] = False):
    """获取所有可用主题"""
    try:
        # 直接创建ThemeManager实例，绕过xiayan_mcp实例
        from xiayan_mcp.themes.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        if detailed:
            themes = theme_manager.get_available_themes()
        else:
            # 简化主题信息
            themes = [
                {"id": theme.id, "name": theme.name, "description": theme.description}
                for theme in theme_manager._themes.values()
            ]
        
        return [
            ThemeResponse(
                id=theme["id"],
                name=theme["name"],
                description=theme["description"]
            ) for theme in themes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取主题列表失败: {str(e)}"
        )

@router.get("/{theme_id}/preview", response_model=ThemePreviewResponse)
async def preview_theme(theme_id: str, sample_content: Optional[str] = None):
    """预览主题效果"""
    try:
        preview = await xiayan_mcp.preview_theme(theme_id, sample_content)
        return ThemePreviewResponse(html_content=preview)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预览主题失败: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_theme(theme: ThemeCreateRequest):
    """添加自定义主题"""
    try:
        result = await xiayan_mcp.add_custom_theme(
            id=theme.id,
            name=theme.name,
            description=theme.description,
            template=theme.template,
            css_styles=theme.css_styles
        )
        return {"message": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加主题失败: {str(e)}"
        )

@router.put("/{theme_id}")
async def update_theme(theme_id: str, theme: ThemeUpdateRequest):
    """更新现有主题"""
    try:
        result = await xiayan_mcp.update_theme(
            theme_id=theme_id,
            name=theme.name,
            description=theme.description,
            template=theme.template,
            css_styles=theme.css_styles
        )
        return {"message": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新主题失败: {str(e)}"
        )

@router.get("/test")
async def test_theme_api():
    """测试主题API"""
    return {"message": "主题API测试成功"}
