"""测试改进后的 fix_encoding 方法"""
import sys
sys.path.append('src')

from xiayan_mcp.core.formatter import MarkdownFormatter

def test_improved_fix_encoding():
    formatter = MarkdownFormatter()
    
    # 测试用例1: 正常中文内容
    normal_content = "这是正常的中文内容，包含标点符号。"
    result1 = formatter.fix_encoding(normal_content)
    print("正常内容测试:")
    print("输入:", normal_content)
    print("输出:", result1)
    print("是否相同:", normal_content == result1)
    print()
    
    # 测试用例2: 包含unicode转义的内容
    unicode_content = "这是一个\\\\u6d4b\\\\u8bd5内容"
    result2 = formatter.fix_encoding(unicode_content)
    print("Unicode转义测试:")
    print("输入:", unicode_content)
    print("输出:", result2)
    print()
    
    # 测试用例3: 包含HTML实体
    html_entity_content = "这是&lt;测试&gt;内容&quot;引号"
    result3 = formatter.fix_encoding(html_entity_content)
    print("HTML实体测试:")
    print("输入:", html_entity_content)
    print("输出:", result3)
    print()
    
    # 测试用例4: 包含十六进制编码
    hex_content = "包含\\x3c标签\\x3e的内容"
    result4 = formatter.fix_encoding(hex_content)
    print("十六进制编码测试:")
    print("输入:", hex_content)
    print("输出:", result4)
    print()
    
    # 测试用例5: 混合情况
    mixed_content = "中文\\\\u5185\\\\u5bb9\\x3c测试\\x3e内容"
    result5 = formatter.fix_encoding(mixed_content)
    print("混合情况测试:")
    print("输入:", mixed_content)
    print("输出:", result5)
    print()
    
    # 测试用例6: 空内容
    empty_content = ""
    result6 = formatter.fix_encoding(empty_content)
    print("空内容测试:")
    print("输入:", repr(empty_content))
    print("输出:", repr(result6))
    print("是否相同:", empty_content == result6)

if __name__ == "__main__":
    test_improved_fix_encoding()