#!/usr/bin/env python3
"""
启动脚本 for xiayan-mcp
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xiayan_mcp.server import main


if __name__ == "__main__":
    print("=== 夏颜公众号助手 (xiayan-mcp) ===", file=sys.stderr)
    print("正在启动MCP服务器...", file=sys.stderr)
    asyncio.run(main())