#!/usr/bin/env python3
"""
测试Web后端的xiayan_mcp集成
"""

import asyncio
from core.xiayan_mcp import XiayanMCP

async def test_list_themes():
    """测试获取主题列表"""
    xiayan_mcp = XiayanMCP()
    
    # 测试获取主题列表
    print("测试获取主题列表...")
    themes = await xiayan_mcp.list_themes(detailed=False)
    print(f"获取的主题数量: {len(themes)}")
    print(f"主题列表: {themes}")
    
    # 测试获取详细主题列表
    print("\n测试获取详细主题列表...")
    detailed_themes = await xiayan_mcp.list_themes(detailed=True)
    print(f"获取的详细主题数量: {len(detailed_themes)}")
    print(f"详细主题列表: {detailed_themes}")
    
    # 测试获取凭证
    print("\n测试获取凭证...")
    credentials = await xiayan_mcp.get_credentials()
    print(f"凭证信息: {credentials}")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_list_themes())