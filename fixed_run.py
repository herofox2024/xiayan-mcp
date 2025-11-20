#!/usr/bin/env python3
"""
修复版启动脚本 - 确保环境变量正确加载
"""

import asyncio
import sys
import os
from pathlib import Path

# 首先加载环境变量
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print("加载环境变量...")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"\'')
                print(f"设置环境变量: {key}")

# 检查必要的环境变量
required_vars = ['WECHAT_APP_ID', 'WECHAT_APP_SECRET']
for var in required_vars:
    if not os.getenv(var):
        print(f"错误: 环境变量 {var} 未设置")
        sys.exit(1)

print("环境变量加载完成")

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xiayan_mcp.server import main

if __name__ == "__main__":
    try:
        print("启动xiayan-mcp服务器...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("服务器被用户中断")
    except Exception as e:
        print(f"服务器错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)