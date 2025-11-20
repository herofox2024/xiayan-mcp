"""
微信草稿内容修复工具
解决微信API返回内容的编码问题
"""

import json
import html

def fix_wechat_content(content):
    """修复微信API返回的内容编码问题
    
    Args:
        content: 微信API返回的原始内容字符串
        
    Returns:
        修复后的正常HTML内容
    """
    if not content:
        return content
    
    try:
        # 第1步：解码Unicode转义 (\u300a\u6d3b\u7740等)
        step1 = content.encode('utf-8').decode('unicode_escape')
        
        # 第2步：解码HTML实体 (&lt;, &gt;, &quot;等)
        step2 = html.unescape(step1)
        
        return step2
    except Exception as e:
        print(f"修复内容时出错: {e}")
        return content

# 测试用例
if __name__ == "__main__":
    # 模拟微信API返回的问题内容
    test_content = "\\n<section class=\\"article-content\\">\\n    <h1>\\u300a\\u6d3b\\u7740\\u300b\\u4e66\\u8bc4<\\/h1>"
    
    print("原始问题内容:")
    print(repr(test_content))
    
    fixed_content = fix_wechat_content(test_content)
    
    print("\n修复后内容:")
    print(repr(fixed_content))
    print("\n实际显示:")
    print(fixed_content)