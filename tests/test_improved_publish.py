#!/usr/bin/env python3
"""Test script for improved WeChat publishing functionality."""

import asyncio
import os
from src.xiayan_mcp.core.publisher import WeChatPublisher


async def test_cover_upload():
    """Test uploading a cover image with automatic resizing."""
    publisher = WeChatPublisher()
    
    # Test with the cover image we have
    cover_path = "E:/资料/文颜公众号MCP/picture/cover.jpg"
    
    try:
        print(f"Testing cover image upload for: {cover_path}")
        media_id = await publisher.upload_cover_image(cover_path)
        print(f"Successfully uploaded cover image. Media ID: {media_id}")
        return media_id
    except Exception as e:
        print(f"Error uploading cover image: {e}")
        return None


async def test_article_publish():
    """Test publishing an article with cover image."""
    publisher = WeChatPublisher()
    
    # Article content
    title = "《活着》书评 - 测试"
    content = """
    <h1>《活着》书评 - 测试</h1>
    
    <p>余华的《活着》是一部经典之作，讲述了福贵一生的故事。</p>
    
    <blockquote><p>"人是为了活着本身而活着，而不是为了活着之外的任何事物所活着。"</p></blockquote>
    
    <p>这本书告诉我们生命的意义在于坚持和尊严。</p>
    """
    
    cover_path = "E:/资料/文颜公众号MCP/picture/cover.jpg"
    author = "文颜"
    
    try:
        print(f"Testing article publish with cover: {cover_path}")
        result = await publisher.publish_to_draft(
            title, content, cover_path, True, author
        )
        print(f"Successfully published article. Result: {result}")
        return result
    except Exception as e:
        print(f"Error publishing article: {e}")
        return None


async def main():
    """Main test function."""
    print("Testing improved WeChat publishing functionality...")
    
    # Test 1: Cover upload
    print("\n=== Test 1: Cover Image Upload ===")
    cover_media_id = await test_cover_upload()
    
    # Test 2: Article publish with cover
    print("\n=== Test 2: Article Publish with Cover ===")
    article_result = await test_article_publish()
    
    print("\n=== Test Summary ===")
    print(f"Cover upload: {'✓' if cover_media_id else '✗'}")
    print(f"Article publish: {'✓' if article_result else '✗'}")


if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv('WECHAT_APP_ID'):
        print("Warning: WECHAT_APP_ID environment variable not set")
    if not os.getenv('WECHAT_APP_SECRET'):
        print("Warning: WECHAT_APP_SECRET environment variable not set")
    
    asyncio.run(main())