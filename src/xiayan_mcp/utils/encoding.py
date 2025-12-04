"""Unified encoding handling utilities for Xiayan MCP."""

import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EncodingUtils:
    """Utility class for handling encoding issues in WeChat publishing."""

    @staticmethod
    def needs_encoding_fix(content) -> bool:
        """
        Detect if content needs encoding fixes.
        
        Args:
            content: Content to check (string or other types)
            
        Returns:
            True if encoding issues detected, False otherwise
        """
        if not content:
            return False
        
        # Only process string types
        if not isinstance(content, str):
            return False
        
        # Detect common encoding issues
        encoding_issues = [
            r'\\x[0-9a-fA-F]{2}',      # Hex encoding like \x3c
            r'\\\\u[0-9a-fA-F]{4}',  # Double escaped Unicode
            r'\\\\n|\\\\t|\\\\r',  # Double escaped control chars
            r'&amp;|&lt;|&gt;|&quot;',  # HTML entities
        ]
        
        for pattern in encoding_issues:
            try:
                if re.search(pattern, content):
                    return True
            except re.error:
                continue
        
        return False

    @staticmethod
    def fix_hex_encoding(content: str) -> str:
        """
        Fix hex encoding issues like \x3c -> <.
        
        Args:
            content: String content to fix
            
        Returns:
            Fixed string
        """
        if not content:
            return content
        
        hex_patterns = [
            (r'\\x3c', '<'),   # <
            (r'\\x3e', '>'),   # >
            (r'\\x22', '"'),   # "
            (r'\\x27', "'"),   # '
            (r'\\x5c', '\\'),  # \
            (r'\\x0a', '\n'),  # Newline
            (r'\\x0d', '\r'),  # Carriage return
            (r'\\x09', '\t'),  # Tab
        ]
        
        for pattern, replacement in hex_patterns:
            try:
                content = re.sub(pattern, replacement, content)
            except re.error:
                continue
        
        return content

    @staticmethod
    def safe_unicode_decode(content: str) -> str:
        """
        Safely decode Unicode escape sequences.
        
        Args:
            content: String content to decode
            
        Returns:
            Decoded string
        """
        if not content or '\\u' not in content:
            return content
        
        try:
            # Handle double escaped Unicode (\\u -> \u)
            content = re.sub(r'\\\\u([0-9a-fA-F]{4})', r'\\u\1', content)
            
            # Decode Unicode escape sequences
            if '\\u' in content:
                try:
                    content = content.encode('utf-8').decode('unicode_escape')
                except UnicodeDecodeError:
                    # Fallback: replace individual escape sequences
                    def replace_unicode(match):
                        try:
                            return chr(int(match.group(1), 16))
                        except:
                            return match.group(0)
                    content = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, content)
            
            return content
        except Exception as e:
            logger.warning(f"Unicode decode failed: {e}")
            return content

    @staticmethod
    def fix_encoding(content) -> str:
        """
        Comprehensive encoding fix for content.
        
        Args:
            content: Content to fix (string or other types)
            
        Returns:
            Fixed string with proper encoding, or original content if not a string
        """
        if not content:
            return content
        
        # Only process string types
        if not isinstance(content, str):
            return content
        
        try:
            logger.debug(f"Original content length: {len(content)}")
            
            # Check if fix is needed
            if not EncodingUtils.needs_encoding_fix(content):
                logger.debug("Content is fine, no encoding fix needed")
                return content
            
            # Step 1: Fix hex encoding issues
            content = EncodingUtils.fix_hex_encoding(content)
            
            # Step 2: Safely decode Unicode escape sequences
            content = EncodingUtils.safe_unicode_decode(content)
            
            # Step 3: Decode HTML entities
            content = html.unescape(content)
            
            logger.debug(f"Fixed content length: {len(content)}")
            return content
            
        except Exception as e:
            logger.error(f"Encoding fix failed: {e}")
            return content

    @staticmethod
    def debug_content(content: str, stage: str = "Unknown"):
        """
        Debug content encoding issues.
        
        Args:
            content: Content to debug
            stage: Debug stage description
        """
        logger.debug(f"=== {stage} Debug Info ===")
        logger.debug(f"Content length: {len(content)}")
        logger.debug(f"Content type: {type(content)}")
        
        # Check for Unicode escapes
        if '\\u' in content:
            logger.debug("Found Unicode escape characters")
            unicode_patterns = re.findall(r'\\\\u[0-9a-fA-F]{4}', content)
            logger.debug(f"Unicode escape sequences: {unicode_patterns[:5]}...")
        
        # Check for HTML entities
        if '&lt;' in content or '&gt;' in content:
            logger.debug("Found HTML entity encoding")
        
        logger.debug(f"=== {stage} Debug End ===")


# Create a singleton instance for easy use
enconding_utils = EncodingUtils()
