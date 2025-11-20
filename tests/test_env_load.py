#!/usr/bin/env python3
"""Test script to verify environment variable loading."""

import sys, os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print(f"Loading .env from: {env_path}")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"\'')

print('WECHAT_APP_ID length:', len(os.getenv('WECHAT_APP_ID', '')))
print('WECHAT_APP_SECRET length:', len(os.getenv('WECHAT_APP_SECRET', '')))

if os.getenv('WECHAT_APP_ID'):
    print('Environment variables loaded successfully!')
else:
    print('Failed to load environment variables.')