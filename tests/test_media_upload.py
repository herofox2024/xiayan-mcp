#!/usr/bin/env python3
"""
Test script for xiayan-mcp media upload functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from xiayan_mcp.core.publisher import WeChatPublisher


async def test_temp_media_upload():
    """Test temporary media upload."""
    print("Testing temporary media upload...")
    
    publisher = WeChatPublisher()
    
    # Test with a sample image (you'll need to provide a valid image path)
    # This is just a placeholder - replace with an actual image path for testing
    test_image_path = "test_image.jpg"  # Replace with actual image
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found at {test_image_path}, skipping test")
        return
    
    try:
        media_id = await publisher.upload_temp_media(test_image_path, "image")
        print(f"✅ Temporary media uploaded successfully. Media ID: {media_id}")
    except Exception as e:
        print(f"❌ Failed to upload temporary media: {e}")


async def test_permanent_material_upload():
    """Test permanent material upload."""
    print("\nTesting permanent material upload...")
    
    publisher = WeChatPublisher()
    
    # Test with a sample image
    test_image_path = "test_image.jpg"  # Replace with actual image
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found at {test_image_path}, skipping test")
        return
    
    try:
        media_id = await publisher.upload_permanent_material(test_image_path, "image")
        print(f"✅ Permanent material uploaded successfully. Media ID: {media_id}")
    except Exception as e:
        print(f"❌ Failed to upload permanent material: {e}")


async def test_image_for_news():
    """Test image upload for news articles."""
    print("\nTesting image upload for news...")
    
    publisher = WeChatPublisher()
    
    # Test with a sample image
    test_image_path = "test_image.jpg"  # Replace with actual image
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found at {test_image_path}, skipping test")
        return
    
    try:
        image_url = await publisher.upload_image_for_news(test_image_path)
        print(f"✅ Image uploaded for news successfully. URL: {image_url}")
    except Exception as e:
        print(f"❌ Failed to upload image for news: {e}")


async def test_media_list():
    """Test getting media list."""
    print("\nTesting media list retrieval...")
    
    publisher = WeChatPublisher()
    
    try:
        # Test permanent materials
        result = await publisher.get_media_list("image", permanent=True)
        print(f"✅ Permanent image materials retrieved successfully:")
        print(f"   Total count: {result.get('total_count', 'N/A')}")
        print(f"   Items returned: {len(result.get('item', []))}")
        
        # Test temporary materials
        result = await publisher.get_media_list("image", permanent=False)
        print(f"✅ Temporary image materials count retrieved successfully:")
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ Failed to get media list: {e}")


async def test_publish_with_permanent_cover():
    """Test publishing article with permanent cover."""
    print("\nTesting article publishing with permanent cover...")
    
    publisher = WeChatPublisher()
    
    # Sample article data
    title = "Test Article with Permanent Cover"
    content = """
    <h2>Test Article</h2>
    <p>This is a test article to verify the permanent cover upload functionality.</p>
    <p>Published using xiayan-mcp with enhanced media upload capabilities.</p>
    """
    
    # Test with a sample cover image
    test_cover_path = "test_cover.jpg"  # Replace with actual image
    
    if not os.path.exists(test_cover_path):
        print(f"⚠️  Test cover not found at {test_cover_path}, skipping test")
        return
    
    try:
        result = await publisher.publish_to_draft(
            title, content, test_cover_path, permanent_cover=True,
            author="Test Author", need_open_comment=0, only_fans_can_comment=0
        )
        print(f"✅ Article published successfully with permanent cover:")
        print(f"   Media ID: {result.get('media_id')}")
        print(f"   Title: {result.get('title')}")
        print(f"   Status: {result.get('status')}")
    except Exception as e:
        print(f"❌ Failed to publish article: {e}")


async def test_remote_media_upload():
    """Test uploading media from remote URL."""
    print("\nTesting remote media upload...")
    
    publisher = WeChatPublisher()
    
    # Test with a sample remote image URL
    # Using a placeholder URL - replace with a valid image URL for testing
    test_remote_url = "https://example.com/test_image.jpg"  # Replace with actual URL
    
    try:
        media_id = await publisher.upload_temp_media(test_remote_url, "image")
        print(f"✅ Remote media uploaded successfully. Media ID: {media_id}")
    except Exception as e:
        print(f"❌ Failed to upload remote media: {e}")


async def main():
    """Run all tests."""
    print("🚀 Starting xiayan-mcp media upload tests\n")
    
    # Check if environment variables are set
    if not os.getenv('WECHAT_APP_ID') or not os.getenv('WECHAT_APP_SECRET'):
        print("❌ WECHAT_APP_ID and WECHAT_APP_SECRET environment variables are required for testing.")
        print("Please set these environment variables and try again.")
        return
    
    # Run tests
    await test_temp_media_upload()
    await test_permanent_material_upload()
    await test_image_for_news()
    await test_media_list()
    await test_publish_with_permanent_cover()
    await test_remote_media_upload()
    
    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())