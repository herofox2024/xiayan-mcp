#!/usr/bin/env python3
"""
测试ThemeManager在Web后端环境中的状态
"""

import sys
import os

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

# 测试ThemeManager的状态
print("=== 测试ThemeManager状态 ===")
print(f"ThemeManager实例: {theme_manager}")
print(f"主题数量: {len(theme_manager._themes)}")
print(f"主题字典: {theme_manager._themes}")

# 打印每个主题的详细信息
print("\n=== 主题详细信息 ===")
for theme_id, theme in theme_manager._themes.items():
    print(f"\n主题ID: {theme_id}")
    print(f"主题名称: {theme.name}")
    print(f"主题描述: {theme.description}")
    print(f"主题模板: {theme.template[:50]}...")
    print(f"主题CSS: {theme.css_styles[:50]}...")

# 测试get_available_themes方法
print("\n=== 测试get_available_themes方法 ===")
available_themes = theme_manager.get_available_themes()
print(f"可用主题数量: {len(available_themes)}")
print(f"可用主题: {available_themes}")

# 测试简化主题信息
print("\n=== 测试简化主题信息 ===")
simple_themes = [
    {"id": theme.id, "name": theme.name, "description": theme.description}
    for theme in theme_manager._themes.values()
]
print(f"简化主题数量: {len(simple_themes)}")
print(f"简化主题: {simple_themes}")