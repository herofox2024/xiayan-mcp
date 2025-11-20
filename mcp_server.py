#!/usr/bin/env python3
"""
MCP服务器启动脚本 - 专为stdio通信设计
"""

import asyncio
import sys
import os
from pathlib import Path

# 确保在正确的目录
os.chdir(Path(__file__).parent)

# 加载环境变量
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"\'')

# 添加src到路径
sys.path.insert(0, 'src')

from mcp.server.stdio import stdio_server
from xiayan_mcp.server import XiayanMCPServer

async def main():
    """主函数"""
    # 创建MCP服务器实例
    server = XiayanMCPServer()
    
    # 使用stdio服务器运行
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"MCP服务器错误: {e}", file=sys.stderr)
        sys.exit(1)