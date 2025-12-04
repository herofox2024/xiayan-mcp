#!/usr/bin/env python3
"""
测试list_themes方法
"""

import sys
import os
import asyncio

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# 导入所需模块
from xiayan_mcp.themes.theme_manager import ThemeManager

async def test_list_themes():
    """测试list_themes方法"""
    print("=== 测试list_themes方法 ===")
    
    # 创建ThemeManager实例
    theme_manager = ThemeManager()
    
    # 测试theme_manager的初始化
    print(f"theme_manager实例: {theme_manager}")
    print(f"theme_manager._themes: {theme_manager._themes}")
    print(f"theme_manager._themes类型: {type(theme_manager._themes)}")
    print(f"主题数量: {len(theme_manager._themes)}")
    
    # 测试get_available_themes方法
    print("\n=== 测试get_available_themes方法 ===")
    try:
        available_themes = theme_manager.get_available_themes()
        print(f"available_themes: {available_themes}")
        print(f"available_themes数量: {len(available_themes)}")
    except Exception as e:
        print(f"get_available_themes方法失败: {e}")
    
    # 测试简化主题信息
    print("\n=== 测试简化主题信息 ===")
    try:
        simple_themes = [
            {"id": theme.id, "name": theme.name, "description": theme.description}
            for theme in theme_manager._themes.values()
        ]
        print(f"simple_themes: {simple_themes}")
        print(f"simple_themes数量: {len(simple_themes)}")
    except Exception as e:
        print(f"简化主题信息失败: {e}")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_list_themes())