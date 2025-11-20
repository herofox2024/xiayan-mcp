#!/usr/bin/env python3
"""Debug the exact issue with content display in WeChat draft."""

import sys
import os
sys.path.append('E:/资料/文颜公众号MCP/xiayan-mcp/src')

from xiayan_mcp.core.formatter import MarkdownFormatter

def test_detailed_conversion():
    """Test detailed markdown conversion step by step."""
    formatter = MarkdownFormatter()
    
    # Simple test content first
    test_content = """---
title: 测试标题
author: 测试作者
---

# 测试标题

这是第一段内容。

## 第二部分

这是第二段内容。

![测试图片](https://example.com/image.jpg)
"""
    
    print("=== 简单测试内容 ===")
    print(test_content)
    
    print("\n=== 转换步骤分析 ===")
    
    # Step 1: Parse frontmatter
    import frontmatter
    post = frontmatter.loads(test_content)
    print(f"Frontmatter: {post.metadata}")
    print(f"Content: {post.content[:100]}...")
    
    # Step 2: Convert to HTML
    html_content = formatter.md.convert(post.content)
    print(f"\nHTML Content:\n{html_content}")
    
    # Step 3: Format with theme
    result = formatter.format(test_content, "default")
    print(f"\nFormatted Result:\nTitle: {result['title']}")
    print(f"Cover: {result['cover']}")
    print(f"Content: {result['content']}")
    
    # Step 4: Save to file for inspection
    with open('E:/资料/文颜公众号MCP/xiayan-mcp/debug_simple.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Simple Debug</title>
</head>
<body>
    <h1>Title: {result['title']}</h1>
    <h2>Cover: {result['cover']}</h2>
    <hr>
    <div>
        {result['content']}
    </div>
</body>
</html>
        """)
    
    print("\n简单测试完成，请查看 debug_simple.html")

def test_book_review():
    """Test with the actual book_review.md content."""
    formatter = MarkdownFormatter()
    
    # Read the actual content
    with open('E:/资料/文颜公众号MCP/xiayan-mcp/book_review.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== 书评内容 ===")
    
    # Check frontmatter parsing
    import frontmatter
    post = frontmatter.loads(content)
    print(f"Frontmatter metadata: {post.metadata}")
    print(f"Content length: {len(post.content)}")
    
    # Check first few lines of content
    lines = post.content.split('\n')[:10]
    print(f"First 10 lines of content: {lines}")
    
    # Format with theme
    result = formatter.format(content, "default")
    print(f"\nFormatting result:")
    print(f"Title: {result['title']}")
    print(f"Cover: {result['cover']}")
    
    # Check if there are any encoding issues
    print(f"Content preview (first 500 chars): {result['content'][:500]}")
    
    # Save to file
    with open('E:/资料/文颜公众号MCP/xiayan-mcp/debug_book_review.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Book Review Debug</title>
</head>
<body>
    <h1>Title: {result['title']}</h1>
    <h2>Cover: {result['cover']}</h2>
    <hr>
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        {result['content']}
    </div>
</body>
</html>
        """)

if __name__ == "__main__":
    test_detailed_conversion()
    print("\n" + "="*50)
    test_book_review()