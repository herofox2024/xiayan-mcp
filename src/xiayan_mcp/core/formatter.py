"""Enhanced Markdown formatter with WeChat publishing support."""

import re
import html
import json
import logging
from typing import Dict, Optional
import frontmatter
import markdown
from bs4 import BeautifulSoup
from jinja2 import Environment, BaseLoader

from ..themes.theme_manager import ThemeManager
from ..utils.encoding import enconding_utils


# 设置日志
logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Enhanced Markdown formatter with themes for WeChat publishing."""
    
    def __init__(self):
        """Initialize the formatter."""
        self.theme_manager = ThemeManager()
        
        # 配置Markdown扩展
        self.md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.footnotes',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.abbr',
            'markdown.extensions.md_in_html',
        ], extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            }
        })
        
        # 微信兼容的CSS样式
        self.base_styles = {
            'font-family': '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif',
            'line-height': '1.8',
            'color': '#333',
            'text-align': 'justify',
            'max-width': '100%',
            'margin': '0',
            'padding': '20px'
        }
        
        self.element_styles = {
            'h1': {
                'font-size': '24px',
                'font-weight': 'bold',
                'text-align': 'center',
                'margin': '24px 0 16px',
                'padding-bottom': '10px',
                'border-bottom': '1px solid #eee',
                'line-height': '1.4'
            },
            'h2': {
                'font-size': '20px',
                'font-weight': 'bold',
                'margin': '20px 0 14px',
                'line-height': '1.4'
            },
            'h3': {
                'font-size': '18px',
                'font-weight': 'bold',
                'margin': '18px 0 12px',
                'line-height': '1.4'
            },
            'p': {
                'margin-bottom': '1.2em',
                'line-height': '1.8',
                'text-indent': '2em'
            },
            'ul': {
                'margin': '1em 0',
                'padding-left': '2.5em'
            },
            'ol': {
                'margin': '1em 0',
                'padding-left': '2.5em'
            },
            'li': {
                'margin-bottom': '0.6em',
                'line-height': '1.8'
            },
            'blockquote': {
                'margin': '1.5em 0',
                'padding': '15px 20px',
                'border-left': '4px solid #ddd',
                'background-color': '#f9f9f9',
                'color': '#666',
                'font-style': 'italic'
            },
            'code': {
                'background-color': '#f4f4f4',
                'padding': '3px 6px',
                'border-radius': '3px',
                'font-family': 'Monaco, "Consolas", monospace'
            },
            'pre': {
                'background-color': '#f4f4f4',
                'padding': '1em',
                'border-radius': '5px',
                'overflow-x': 'auto',
                'margin': '1em 0'
            },
            'strong': {
                'font-weight': 'bold'
            },
            'em': {
                'font-style': 'italic'
            },
            'img': {
                'max-width': '100%',
                'height': 'auto',
                'display': 'block',
                'margin': '1.5em auto',
                'border-radius': '4px'
            }
        }

    def fix_encoding(self, content):
        """修复编码问题（使用统一编码处理工具）"""
        return enconding_utils.fix_encoding(content)

    def _needs_encoding_fix(self, content):
        """检测是否需要编码修复（使用统一编码处理工具）"""
        return enconding_utils.needs_encoding_fix(content)

    def _fix_hex_encoding(self, content):
        """修复十六进制编码问题（使用统一编码处理工具）"""
        return enconding_utils.fix_hex_encoding(content)

    def _safe_unicode_decode(self, content):
        """安全的Unicode转义解码（使用统一编码处理工具）"""
        return enconding_utils.safe_unicode_decode(content)

    def _fix_common_encoding_issues(self, content):
        """修复常见编码问题（使用统一编码处理工具）"""
        return self._fix_hex_encoding(content)

    def format(self, content: str, theme_id: str = "default") -> Dict[str, str]:
        """
        Format markdown content with specified theme.
        
        Args:
            content: Raw markdown content with optional frontmatter
            theme_id: Theme identifier to apply
            
        Returns:
            Dictionary containing title, cover, and formatted HTML content
        """
        try:
            # 修复输入内容的编码
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            # Parse frontmatter
            post = frontmatter.loads(content)
            metadata = post.metadata
            markdown_content = post.content
            
            # Extract title and cover from frontmatter
            title = metadata.get('title', '')
            cover = metadata.get('cover', '')
            
            logger.info(f"处理文章: {title}")
            
            # Convert markdown to HTML
            html_content = self.md.convert(markdown_content)
            
            # If no cover in frontmatter, try to extract from content
            if not cover:
                first_image = self._extract_images(html_content)
                if first_image:
                    cover = first_image[0] if isinstance(first_image, list) else first_image
            
            # Apply theme styling
            theme = self.theme_manager.get_theme(theme_id)
            styled_html = self._apply_theme(html_content, theme)
            
            # 确保编码正确
            if isinstance(styled_html, bytes):
                styled_html = styled_html.decode('utf-8')
            
            result = {
                "title": title,
                "cover": cover,
                "content": styled_html
            }
            
            logger.info(f"格式化完成，标题: {title}")
            return result
            
        except Exception as e:
            logger.error(f"格式化时出错: {e}")
            # 返回基本格式
            return {
                "title": "格式化错误",
                "cover": "",
                "content": f"<p>格式化错误: {str(e)}</p>"
            }

    def format_markdown_for_wechat(self, content: str) -> str:
        """
        将Markdown内容格式化为适合微信公众号的HTML格式。
        
        Args:
            content: 原始Markdown内容，可包含frontmatter
            
        Returns:
            格式化后的HTML内容字符串
        """
        try:
            # 修复输入内容的编码
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            # Parse frontmatter
            post = frontmatter.loads(content)
            metadata = post.metadata
            markdown_content = post.content
            
            # 提取标题（用于日志）
            title = metadata.get('title', '未命名文章')
            logger.info(f"处理文章: {title}")
            
            # Convert markdown to HTML
            html_content = self.md.convert(markdown_content)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Clean up HTML for WeChat compatibility
            self._clean_html_for_wechat(soup)
            
            # Apply additional WeChat-compatible styles
            self._apply_enhanced_styles(soup)
            
            # 修复编码问题
            result_html = str(soup)
            result_html = self.fix_encoding(result_html)
            
            # 确保最终结果正确编码
            if isinstance(result_html, bytes):
                result_html = result_html.decode('utf-8')
            
            logger.info(f"文章格式化完成: {title}, 长度: {len(result_html)}")
            
            return result_html
            
        except Exception as e:
            logger.error(f"格式化文章时出错: {e}")
            logger.exception("详细错误信息: ")
            # 返回包含错误信息的HTML
            return f'<p>格式化错误: {str(e)}</p>'

    def _apply_theme(self, html_content: str, theme: 'Theme') -> str:
        """
        Apply theme styling to HTML content.
        
        Args:
            html_content: Raw HTML content
            theme: Theme to apply
            
        Returns:
            Styled HTML content
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Clean up HTML for WeChat compatibility
            self._clean_html_for_wechat(soup)
            
            # Apply additional微信兼容的样式
            self._apply_enhanced_styles(soup)
            
            # 直接使用_wrap_in_template方法，确保主题CSS样式能够正确应用
            # 这个方法会创建包含CSS样式的完整HTML结构
            return self._wrap_in_template(str(soup), theme)
                
        except Exception as e:
            logger.error(f"Applying theme error: {e}")
            return str(soup)

    def _combine_styles(self, theme_css: str) -> str:
        """组合主题样式和微信兼容样式"""
        # 返回完整的CSS样式表，确保主题样式能够正确应用
        return theme_css or ""

    def _wrap_in_template(self, content: str, theme: 'Theme') -> str:
        """包装内容到基本微信模板"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文章</title>
    <style>
        {self._combine_styles(theme.css_styles or "")}
    </style>
</head>
<body>
    <div class="article-content">
        {content}
    </div>
</body>
</html>
        """

    def _apply_enhanced_styles(self, soup):
        """应用增强的微信兼容样式"""
        for tag in soup.find_all():
            tag_name = tag.name.lower()
            
            if tag_name in self.element_styles:
                # 合并样式
                existing_style = tag.get('style', '')
                element_style = self.element_styles[tag_name]
                
                # 解析现有样式
                css_dict = {}
                if existing_style:
                    for prop in existing_style.split(';'):
                        if ':' in prop:
                            key, value = prop.split(':', 1)
                            css_dict[key.strip()] = value.strip()
                
                # 添加微信样式
                for prop, value in self.element_styles[tag_name].items():
                    css_dict[prop] = value
                
                # 转换回字符串
                new_style = '; '.join([f"{k}: {v}" for k, v in css_dict.items()])
                tag['style'] = new_style

    def _clean_html_for_wechat(self, soup):
        """
        Clean HTML content for WeChat compatibility.
        
        Args:
            soup: BeautifulSoup object to clean
        """
        # 移除不支持的标签
        unsupported_tags = ['script', 'style', 'meta', 'link', 'iframe', 'form', 'input', 'button']
        for tag in soup.find_all(unsupported_tags):
            tag.decompose()
        
        # 清理属性
        for tag in soup.find_all():
            # 移除可能有问题的属性
            problematic_attrs = ['id', 'class', 'data-*', 'onclick', 'onload']
            for attr in list(tag.attrs.keys()):
                if any(attr.startswith(pattern.replace('*', '')) for pattern in problematic_attrs):
                    del tag[attr]
            
            # 针对图片标签的特殊处理
            if tag.name == 'img':
                # 只保留必要的属性
                allowed_attrs = ['src', 'alt', 'width', 'height']
                for attr in list(tag.attrs.keys()):
                    if attr not in allowed_attrs:
                        del tag[attr]
                
                # 确保有基本样式
                if 'style' not in tag.attrs:
                    tag['style'] = self.element_styles['img']
            
            # 清理a标签
            elif tag.name == 'a':
                # 保留href和title属性
                allowed_attrs = ['href', 'title', 'target']
                for attr in list(tag.attrs.keys()):
                    if attr not in allowed_attrs:
                        del tag[attr]
                
                # 添加新窗口打开
                if 'target' not in tag.attrs:
                    tag['target'] = '_blank'
            
            # 清理代码块
            elif tag.name == 'pre':
                if 'style' not in tag.attrs:
                    tag['style'] = self.element_styles['pre']
            
            elif tag.name == 'code':
                if 'style' not in tag.attrs:
                    tag['style'] = self.element_styles['code']
        
        # 转换不支持的元素
        for hr in soup.find_all('hr'):
            hr.replace_with(soup.new_tag('div', attrs={'style': 'border-bottom: 1px solid #eee; margin: 1em 0;'}))

    def _extract_images(self, html_content: str) -> list:
        """Extract all image URLs from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    images.append(src)
            
            return images
        except Exception as e:
            logger.error(f"提取图片时出错: {e}")
            return []

    def _auto_generate_cover(self, html_content: str) -> Optional[str]:
        """Automatically select first image as cover if none provided."""
        images = self._extract_images(html_content)
        return images[0] if images else None

    def debug_content(self, content: str, stage: str = "未知"):
        """调试内容"""
        logger.debug(f"=== {stage} 调试信息 ===")
        logger.debug(f"内容长度: {len(content)}")
        logger.debug(f"内容类型: {type(content)}")
        
        # 检查编码问题
        if '\\u' in content:
            logger.debug("发现Unicode转义字符")
            import re
            unicode_patterns = re.findall(r'\\\\u[0-9a-fA-F]{4}', content)
            logger.debug(f"Unicode转义序列: {unicode_patterns[:5]}...")
        
        # 检查HTML实体编码
        if '&lt;' in content or '&gt;' in content:
            logger.debug("发现HTML实体编码")
        
        # 检查编码格式
        try:
            if isinstance(content, bytes):
                decoded_content = content.decode('utf-8')
                logger.debug(f"字节内容: {decoded_content[:50]}...")
            else:
                logger.debug(f"字符串内容: {content[:50]}...")
        except Exception as e:
            logger.error(f"编码检查失败: {e}")
        
        logger.debug(f"=== {stage} 调试结束 ===")