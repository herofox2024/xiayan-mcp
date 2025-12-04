#!/usr/bin/env python3
"""
测试主题API
"""

import sys
import os
import asyncio
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List, Optional

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# 导入ThemeManager
from xiayan_mcp.themes.theme_manager import ThemeManager

# 创建ThemeManager实例
theme_manager = ThemeManager()

# 定义响应模型
class ThemeResponse(BaseModel):
    id: str
    name: str
    description: str

async def test_api_logic():
    """测试API逻辑"""
    print("=== 测试API逻辑 ===")
    
    # 模拟API参数
    detailed = False
    
    # 模拟API逻辑
    print(f"detailed参数: {detailed}")
    
    # 获取主题列表
    if detailed:
        themes = theme_manager.get_available_themes()
    else:
        # 简化主题信息
        themes = [
            {"id": theme.id, "name": theme.name, "description": theme.description}
            for theme in theme_manager._themes.values()
        ]
    
    print(f"获取的主题数量: {len(themes)}")
    print(f"主题列表: {themes}")
    
    # 模拟转换为响应模型
    response = [
        ThemeResponse(
            id=theme["id"],
            name=theme["name"],
            description=theme["description"]
        ) for theme in themes
    ]
    
    print(f"转换后的响应数量: {len(response)}")
    print(f"转换后的响应: {response}")
    
    return response

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_api_logic())