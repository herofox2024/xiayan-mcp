#!/usr/bin/env python3
"""
测试主题API路由
"""

import sys
import os
import asyncio
from fastapi import APIRouter

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, src_path)
sys.path.insert(1, project_root)

# 测试core.xiayan_mcp的导入
print("=== 测试core.xiayan_mcp的导入 ===")
try:
    from core.xiayan_mcp import XiayanMCP
    print("✓ 成功导入XiayanMCP")
except Exception as e:
    print(f"✗ 导入XiayanMCP失败: {e}")
    sys.exit(1)

# 测试XiayanMCP实例的创建
print("\n=== 测试XiayanMCP实例的创建 ===")
try:
    xiayan_mcp = XiayanMCP()
    print(f"✓ 成功创建XiayanMCP实例: {xiayan_mcp}")
except Exception as e:
    print(f"✗ 创建XiayanMCP实例失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试list_themes方法
async def test_list_themes():
    """测试list_themes方法"""
    print("\n=== 测试list_themes方法 ===")
    try:
        themes = await xiayan_mcp.list_themes(detailed=False)
        print(f"✓ list_themes返回: {themes}")
        print(f"✓ 主题数量: {len(themes)}")
        return themes
    except Exception as e:
        print(f"✗ list_themes方法失败: {e}")
        import traceback
        traceback.print_exc()
        return []

# 运行测试
if __name__ == "__main__":
    themes = asyncio.run(test_list_themes())
    print(f"\n=== 最终结果 ===")
    print(f"测试返回的主题数量: {len(themes)}")
    print(f"测试返回的主题: {themes}")