#!/usr/bin/env python3
"""
简单测试脚本，确保所有错误都能被捕获和显示
"""

import sys
import os

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# 简单测试
print("=== 简单测试 ===")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"web_backend_dir: {web_backend_dir}")
print(f"project_root: {project_root}")
print(f"src_path: {src_path}")
print(f"sys.path: {sys.path}")

# 测试导入
print("\n=== 测试导入 ===")
try:
    from xiayan_mcp.themes.theme_manager import ThemeManager
    print("✓ 成功导入ThemeManager")
except Exception as e:
    print(f"✗ 导入ThemeManager失败: {e}")
    sys.exit(1)

# 测试ThemeManager初始化
print("\n=== 测试ThemeManager初始化 ===")
try:
    theme_manager = ThemeManager()
    print("✓ 成功创建ThemeManager实例")
except Exception as e:
    print(f"✗ 创建ThemeManager实例失败: {e}")
    sys.exit(1)

# 测试主题数量
print("\n=== 测试主题数量 ===")
try:
    theme_count = len(theme_manager._themes)
    print(f"✓ 主题数量: {theme_count}")
except Exception as e:
    print(f"✗ 获取主题数量失败: {e}")
    sys.exit(1)

# 测试主题字典
print("\n=== 测试主题字典 ===")
try:
    themes = list(theme_manager._themes.keys())
    print(f"✓ 主题ID列表: {themes}")
except Exception as e:
    print(f"✗ 获取主题字典失败: {e}")
    sys.exit(1)

# 测试获取第一个主题
print("\n=== 测试获取第一个主题 ===")
try:
    first_theme_id = next(iter(theme_manager._themes.keys()))
    first_theme = theme_manager._themes[first_theme_id]
    print(f"✓ 第一个主题ID: {first_theme_id}")
    print(f"✓ 第一个主题名称: {first_theme.name}")
    print(f"✓ 第一个主题描述: {first_theme.description}")
except Exception as e:
    print(f"✗ 获取第一个主题失败: {e}")
    sys.exit(1)

# 测试简化主题信息
print("\n=== 测试简化主题信息 ===")
try:
    simple_themes = []
    for theme_id, theme in theme_manager._themes.items():
        simple_theme = {
            "id": theme.id,
            "name": theme.name,
            "description": theme.description
        }
        simple_themes.append(simple_theme)
    print(f"✓ 简化主题信息成功，数量: {len(simple_themes)}")
    print(f"✓ 第一个简化主题: {simple_themes[0]}")
except Exception as e:
    print(f"✗ 简化主题信息失败: {e}")
    sys.exit(1)

print("\n=== 所有测试通过 ===")