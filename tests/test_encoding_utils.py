#!/usr/bin/env python3
"""
Test script for EncodingUtils class
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xiayan_mcp.utils.encoding import EncodingUtils


def test_needs_encoding_fix():
    """Test if content needs encoding fix detection"""
    encoding_utils = EncodingUtils()
    
    # Test cases
    test_cases = [
        # (content, expected_result)
        ("Normal content", False),
        (r"Content with hex encoding \\x3cdiv\\x3e", True),
        (r"Content with unicode escape \\u4e2d\\u6587", True),
        ("Content with HTML entities &lt;div&gt;", True),
    ]
    
    for content, expected in test_cases:
        result = encoding_utils.needs_encoding_fix(content)
        assert result == expected, f"Test failed for content: '{content}', expected: {expected}, got: {result}"
    
    print("✅ test_needs_encoding_fix passed")


def test_fix_encoding():
    """Test comprehensive encoding fix"""
    encoding_utils = EncodingUtils()
    
    # Test cases
    test_cases = [
        # (input_content, expected_output)
        (r"\x3cdiv\x3e\\u4e2d\\u6587\x3c/div\x3e", "<div>中文</div>"),
        ("&lt;b&gt;bold&lt;/b&gt;", "<b>bold</b>"),
        ("Normal content", "Normal content"),
        ("Hello &amp; world", "Hello & world"),
    ]
    
    for input_content, expected in test_cases:
        result = encoding_utils.fix_encoding(input_content)
        assert result == expected, f"Test failed for input: '{input_content}', expected: {expected}, got: {result}"
    
    print("✅ test_fix_encoding passed")


def test_edge_cases():
    """Test edge cases for encoding utils"""
    encoding_utils = EncodingUtils()
    
    # Test empty content
    assert encoding_utils.fix_encoding("") == ""
    assert encoding_utils.needs_encoding_fix("") is False
    
    # Test None content
    assert encoding_utils.fix_encoding(None) is None
    assert encoding_utils.needs_encoding_fix(None) is False
    
    # Test non-string content
    assert encoding_utils.fix_encoding(123) == 123
    assert encoding_utils.needs_encoding_fix(123) is False
    
    print("✅ test_edge_cases passed")


def run_all_tests():
    """Run all encoding utils tests"""
    print("Running EncodingUtils tests...")
    
    test_needs_encoding_fix()
    test_fix_encoding()
    test_edge_cases()
    
    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_all_tests()
