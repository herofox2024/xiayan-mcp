#!/usr/bin/env python3
"""Debug markdown to HTML conversion."""

import sys
import os
sys.path.append('E:/资料/文颜公众号MCP/xiayan-mcp/src')

from xiayan_mcp.core.formatter import MarkdownFormatter

def test_conversion():
    """Test markdown to HTML conversion."""
    formatter = MarkdownFormatter()
    
    # Read the book_review.md file
    with open('E:/资料/文颜公众号MCP/xiayan-mcp/book_review.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ORIGINAL MARKDOWN ===")
    print(content[:500] + "..." if len(content) > 500 else content)
    
    print("\n=== FORMATTED RESULT ===")
    
    # Test with default theme
    result = formatter.format(content, "default")
    
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Cover: {result.get('cover', 'N/A')}")
    print(f"Content length: {len(result.get('content', ''))}")
    
    # Save the HTML result to a file for inspection
    with open('E:/资料/文颜公众号MCP/xiayan-mcp/debug_output.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Debug Output</title>
</head>
<body>
    <h1>Title: {result.get('title', 'N/A')}</h1>
    <h2>Cover: {result.get('cover', 'N/A')}</h2>
    <hr>
    <div>
        {result.get('content', 'N/A')}
    </div>
</body>
</html>
        """)
    
    print(f"\nDebug output saved to: debug_output.html")
    
    return result

if __name__ == "__main__":
    test_conversion()