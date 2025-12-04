#!/usr/bin/env python3
"""
微信凭证管理API路由
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
from typing import Optional
from core.xiayan_mcp import XiayanMCP

# 创建路由器
router = APIRouter()

# 创建XiayanMCP实例
xiayan_mcp = XiayanMCP()

# 凭证请求模型
class CredentialRequest(BaseModel):
    app_id: str
    app_secret: str
    save_to_env: Optional[bool] = True

# 凭证响应模型
class CredentialResponse(BaseModel):
    app_id: str
    app_secret: Optional[str] = None
    configured: bool
    message: str

@router.get("/", response_model=CredentialResponse)
async def get_credentials():
    """获取当前微信凭证信息"""
    try:
        result = await xiayan_mcp.get_credentials()
        return CredentialResponse(
            app_id=result.get("app_id", ""),
            app_secret=result.get("app_secret", ""),
            configured=result.get("configured", False),
            message=result.get("message", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取凭证信息失败: {str(e)}"
        )

@router.post("/", response_model=CredentialResponse)
async def update_credentials(credential: CredentialRequest):
    """更新微信凭证信息"""
    try:
        result = await xiayan_mcp.update_credentials(
            app_id=credential.app_id,
            app_secret=credential.app_secret,
            save_to_env=credential.save_to_env
        )
        return CredentialResponse(
            app_id=result.get("app_id", ""),
            app_secret=result.get("app_secret", ""),
            configured=result.get("configured", False),
            message=result.get("message", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新凭证信息失败: {str(e)}"
        )

@router.get("/test")
async def test_credential_api():
    """测试凭证API"""
    return {"message": "凭证API测试成功"}
