#!/usr/bin/env python3
"""
测试FastAPI的基本功能
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# 创建FastAPI应用
app = FastAPI()

# 定义响应模型
class ThemeResponse(BaseModel):
    id: str
    name: str
    description: str

# 简单的测试路由
@app.get("/api/test", response_model=List[ThemeResponse])
async def test_api():
    """测试API"""
    # 返回固定的主题列表
    themes = [
        {"id": "default", "name": "默认主题", "description": "简洁大方的默认主题"},
        {"id": "orangeheart", "name": "Orange Heart", "description": "温暖橙心主题"},
        {"id": "rainbow", "name": "Rainbow", "description": "彩虹主题"}
    ]
    
    return [
        ThemeResponse(
            id=theme["id"],
            name=theme["name"],
            description=theme["description"]
        ) for theme in themes
    ]

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)