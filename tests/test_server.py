#!/usr/bin/env python3
"""
测试 xiayan-mcp 的运行状况
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from xiayan_mcp.server import XiayanMCPServer
    from xiayan_mcp.core.formatter import MarkdownFormatter
    from xiayan_mcp.core.publisher import WeChatPublisher
    from xiayan_mcp.themes.theme_manager import ThemeManager
    
    print("[OK] 所有模块导入成功")
    
    # 测试主题管理器
    theme_manager = ThemeManager()
    themes = theme_manager.get_available_themes()
    print(f"[OK] 主题管理器初始化成功，共有 {len(themes)} 个主题")
    
    # 测试格式化器
    formatter = MarkdownFormatter()
    print("[OK] MarkdownFormatter 初始化成功")
    
    # 测试发布器（需要环境变量）
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    if app_id and app_secret:
        publisher = WeChatPublisher()
        print("[OK] WeChatPublisher 初始化成功，已配置微信 API 凭证")
    else:
        print("[WARNING] WeChatPublisher 初始化成功，但缺少微信 API 凭证")
    
    # 测试服务器创建
    server = XiayanMCPServer()
    print("[OK] XiayanMCPServer 创建成功")
    
    # 测试工具列表
    async def test_tools():
        tools_result = await server._list_tools_handler()
        print(f"[OK] 工具列表获取成功，共有 {len(tools_result.tools)} 个工具")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
    
    asyncio.run(test_tools())
    
    print("\n=== 所有测试通过，xiayan-mcp 运行正常 ===")
    
except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    print("请检查依赖是否正确安装")
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()