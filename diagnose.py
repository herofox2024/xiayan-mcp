#!/usr/bin/env python3
"""
诊断脚本 - 检查xiayan-mcp配置问题
"""

import os
import sys
import importlib

def check_environment():
    """检查环境配置"""
    print("=== 环境配置检查 ===")
    
    # 检查当前目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查.env文件
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print("✅ .env文件存在")
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"环境变量内容: {content[:200]}...")
    else:
        print("❌ .env文件不存在")
    
    # 检查必要的环境变量
    required_vars = ['WECHAT_APP_ID', 'WECHAT_APP_SECRET']
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ 环境变量 {var} 已设置")
        else:
            print(f"❌ 环境变量 {var} 未设置")

def check_dependencies():
    """检查依赖包"""
    print("\n=== 依赖包检查 ===")
    
    required_packages = [
        'mcp',
        'aiohttp', 
        'frontmatter',
        'markdown',
        'beautifulsoup4',
        'jinja2',
        'pillow'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")

def check_imports():
    """检查模块导入"""
    print("\n=== 模块导入检查 ===")
    
    # 添加src到路径
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    try:
        from xiayan_mcp.server import main
        print("✅ 主模块导入成功")
        
        from xiayan_mcp.core.publisher import WeChatPublisher
        print("✅ 发布器模块导入成功")
        
        from xiayan_mcp.core.formatter import MarkdownFormatter
        print("✅ 格式化器模块导入成功")
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")

def main():
    """主函数"""
    print("xiayan-mcp 诊断工具")
    print("=" * 50)
    
    check_environment()
    check_dependencies()
    check_imports()
    
    print("\n=== 诊断完成 ===")

if __name__ == "__main__":
    main()