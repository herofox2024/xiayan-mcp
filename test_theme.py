#!/usr/bin/env python3
"""
测试主题管理器
"""

from src.xiayan_mcp.themes.theme_manager import ThemeManager

# 创建主题管理器实例
theme_manager = ThemeManager()

# 测试加载主题
print("加载的主题数量:", len(theme_manager._themes))
print("可用主题:")
for theme_id, theme in theme_manager._themes.items():
    print(f"- {theme_id}: {theme.name} - {theme.description}")

# 测试获取主题列表
themes = theme_manager.get_available_themes()
print("\n获取的主题列表:", themes)

# 测试简化主题信息
simple_themes = [
    {"id": theme.id, "name": theme.name, "description": theme.description}
    for theme in theme_manager._themes.values()
]
print("\n简化主题信息:", simple_themes)