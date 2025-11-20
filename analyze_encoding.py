"""
微信草稿内容编码修复工具
"""

import json
import html
import sys
import os

def analyze_encoding_issue():
    """分析编码问题"""
    print("=== 微信草稿编码问题分析 ===\n")
    
    # 模拟微信API返回的实际数据结构
    sample_data = {
        "item": [{
            "media_id": "9q5Pthue6WCZZGn3PsSlVrh-g9OE_h27Ob8yhPwBb2Y7C9DjBUNmIgwtHVjbz-b9",
            "content": {
                "news_item": [{
                    "title": "\\u300a\\u6d3b\\u7740\\u300b\\u4e66\\u8bc4",
                    "content": "\\n<section class=\\"article-content\\">\\n    <h1>\\u300a\\u6d3b\\u7740\\u300b\\u4e66\\u8bc4<\\/h1>"
                }]
            }
        }]
    }
    
    print("1. 原始API返回数据:")
    print(json.dumps(sample_data, ensure_ascii=False, indent=2))
    
    # 提取内容
    content = sample_data["item"][0]["content"]["news_item"][0]["content"]
    print(f"\n2. 原始content内容:")
    print(repr(content))
    
    # 解码过程
    print("\n3. 解码过程:")
    
    # 第1步：解码Unicode转义
    step1 = content.encode('utf-8').decode('unicode_escape')
    print(f"第1步 - Unicode解码: {repr(step1[:100])}")
    
    # 第2步：解码HTML实体（如果有）
    step2 = html.unescape(step1)
    print(f"第2步 - HTML解码: {repr(step2[:100])}")
    
    print(f"\n4. 最终可读内容:")
    print(step2[:200] + "...")

def create_fix_code():
    """创建修复代码"""
    fix_code = '''
def fix_wechat_content(content):
    """修复微信API返回的内容编码问题"""
    import html
    
    # 第1步：解码Unicode转义
    step1 = content.encode('utf-8').decode('unicode_escape')
    
    # 第2步：解码HTML实体
    step2 = html.unescape(step1)
    
    return step2

# 使用示例
raw_content = "\\\\n<section class=\\\\\"article-content\\\\">\\\\n    <h1>\\\\u300a\\\\u6d3b\\\\u7740\\\\u300b\\\\u4e66\\\\u8bc4<\\\\/h1>"
fixed_content = fix_wechat_content(raw_content)
print(fixed_content)
'''
    
    with open('wechat_content_fix.py', 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("\n5. 修复代码已保存到: wechat_content_fix.py")

def check_publisher_code():
    """检查并修复发布器代码中的编码处理"""
    print("\n=== 检查发布器代码 ===")
    
    publisher_file = "src/xiayan_mcp/core/publisher.py"
    if os.path.exists(publisher_file):
        with open(publisher_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找相关代码段
        if 'get_draft_list' in content:
            print("✓ 找到 get_draft_list 方法")
            
            # 检查是否有编码处理
            if 'unicode_escape' in content or 'decode' in content:
                print("✗ 可能需要添加Unicode解码处理")
            else:
                print("✗ 缺少Unicode解码处理")
                
            print("\n建议修复方案:")
            print("在 get_draft_list 方法中添加内容解码逻辑")

if __name__ == "__main__":
    analyze_encoding_issue()
    create_fix_code()
    check_publisher_code()
    
    print("\n=== 解决方案总结 ===")
    print("1. 问题原因：微信API返回的内容包含Unicode转义字符")
    print("2. 解决方法：需要双重解码（Unicode + HTML）")
    print("3. 修复位置：xiayan_mcp/core/publisher.py 的 get_draft_list 方法")
    print("4. 修复代码：已生成 wechat_content_fix.py 供参考")