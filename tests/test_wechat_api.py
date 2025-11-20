"""Test script to debug WeChat API publishing issues."""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from xiayan_mcp.core.publisher import WeChatPublisher

async def test_wechat_api():
    """Test WeChat API publishing."""
    print("Testing WeChat API...")
    
    # Load environment variables
    with open('.env', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    # Create publisher
    publisher = WeChatPublisher()
    
    # Test access token
    try:
        print("Getting access token...")
        token = await publisher._get_access_token()
        print(f"SUCCESS: Access token obtained: {token[:20]}...")
    except Exception as e:
        print(f"ERROR: Failed to get access token: {e}")
        return
    
    # Test image upload
    try:
        print("Uploading test image...")
        image_url = "https://picsum.photos/seed/test/200/200.jpg"
        cover_media_id = await publisher._upload_media(image_url)
        print(f"SUCCESS: Image uploaded with media_id: {cover_media_id}")
    except Exception as e:
        print(f"ERROR: Failed to upload image: {e}")
        cover_media_id = ""

    # Test getting draft list to check permissions
    try:
        print("Getting draft list...")
        drafts = await publisher.get_draft_list()
        print(f"SUCCESS: Got draft list: {drafts}")
    except Exception as e:
        print(f"ERROR: Failed to get draft list: {e}")

    # Test draft creation using existing thumb_media_id
    try:
        print("Getting existing thumb_media_id...")
        drafts = await publisher.get_draft_list()
        if 'item' in drafts and drafts['item']:
            existing_thumb_media_id = drafts['item'][0]['content']['news_item'][0]['thumb_media_id']
            print(f"Found existing thumb_media_id: {existing_thumb_media_id}")
            
            print("Creating draft with existing thumb_media_id...")
            title = "测试文章"
            content = "<p>这是一个测试文章的内容。</p>"
            media_id = await publisher._add_draft(title, content, existing_thumb_media_id)
            print(f"SUCCESS: Draft created successfully: {media_id}")
        else:
            print("No existing drafts found")
    except Exception as e:
        print(f"ERROR: Failed to create draft with existing thumb_media_id: {e}")
        return
    
    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_wechat_api())