"""MCP Server implementation for Xiayan."""

import asyncio
import json
import logging
import html
import re
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"\'')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from .core.formatter import MarkdownFormatter
from .core.publisher import WeChatPublisher
from .themes.theme_manager import ThemeManager


def _fix_content_encoding(content):
    """修复内容编码问题 - 更谨慎的策略"""
    if not content or not isinstance(content, str):
        return content
    
    try:
        # 先检测是否真的需要修复
        needs_fix = _needs_encoding_fix(content)
        if not needs_fix:
            return content
        
        logger.debug(f"检测到编码问题，开始修复，内容长度: {len(content)}")
        
        # 只修复真正的编码问题，避免过度处理
        # 修复十六进制编码错误（如 \x3c -> <）
        content = re.sub(r'\\x3c', '<', content)
        content = re.sub(r'\\x3e', '>', content)
        content = re.sub(r'\\x22', '"', content)
        content = re.sub(r'\\x27', "'", content)
        content = re.sub(r'\\x5c', '\\\\', content)
        
        # 处理双反斜杠Unicode转义（如 \\u4e2d -> \u4e2d）
        content = re.sub(r'\\\\u([0-9a-fA-F]{4})', r'\\u\1', content)
        
        # 谨慎地处理Unicode转义序列
        # 只对确认是转义序列的部分进行解码
        if '\\u' in content:
            try:
                content = content.encode('utf-8').decode('unicode_escape')
            except Exception as decode_error:
                logger.warning(f"Unicode解码失败: {decode_error}")
                # 如果失败，尝试只修复明显的Unicode转义
                content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), content)
        
        # 最后解码HTML实体
        content = html.unescape(content)
        
        logger.debug(f"编码修复完成，内容长度: {len(content)}")
        return content
        
    except Exception as e:
        logger.warning(f"修复编码时出错: {e}")
        return content

def _needs_encoding_fix(content):
    """检测是否需要编码修复"""
    if not content:
        return False
    
    # 检测常见的编码问题
    encoding_issues = [
        r'\\x[0-9a-fA-F]{2}',      # 十六进制编码如 \x3c
        r'\\\\u[0-9a-fA-F]{4}',  # 双反斜杠Unicode转义
        r'\\u[0-9a-fA-F]{4}',      # Unicode转义
        r'&amp;|&lt;|&gt;|&quot;',  # HTML实体
    ]
    
    for pattern in encoding_issues:
        try:
            if re.search(pattern, content):
                return True
        except re.error:
            continue
    
    return False


class XiayanMCPServer:
    """Xiayan MCP Server for WeChat Official Account publishing."""

    def __init__(self):
        """Initialize the Xiayan MCP server."""
        self.server = Server("xiayan-mcp")
        self.theme_manager = ThemeManager()
        self.formatter = MarkdownFormatter()
        self.publisher = WeChatPublisher()
        
        # Register handlers using decorators
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="publish_article",
                        description="Format a Markdown article using a selected theme and publish it to '微信公众号'.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The original Markdown content to publish, preserving its frontmatter (if present).",
                                },
                                "theme_id": {
                                    "type": "string",
                                    "description": "ID of the theme to use (e.g., default, orangeheart, rainbow, lapis, pie, maize, purple, phycat).",
                                },
                                "permanent_cover": {
                                    "type": "boolean",
                                    "description": "Whether to upload cover image as permanent material (true) or temporary (false).",
                                    "default": False,
                                },
                                "author": {
                                    "type": "string",
                                    "description": "Article author name.",
                                    "default": "Xiayan MCP",
                                },
                                "need_open_comment": {
                                    "type": "integer",
                                    "description": "Enable open comments (0 for no, 1 for yes).",
                                    "enum": [0, 1],
                                    "default": 0,
                                },
                                "only_fans_can_comment": {
                                    "type": "integer",
                                    "description": "Only fans can comment (0 for no, 1 for yes).",
                                    "enum": [0, 1],
                                    "default": 0,
                                },
                            },
                            "required": ["content"],
                        },
                    ),
                    Tool(
                        name="list_themes",
                        description="List the themes compatible with the 'publish_article' tool to publish an article to '微信公众号'.",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    Tool(
                        name="upload_temp_media",
                        description="Upload temporary media file to WeChat server (valid for 3 days). Supports image, voice, video, and thumb.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "media_path": {
                                    "type": "string",
                                    "description": "Path to media file (local or remote URL).",
                                },
                                "media_type": {
                                    "type": "string",
                                    "description": "Type of media (image, voice, video, thumb).",
                                    "enum": ["image", "voice", "video", "thumb"],
                                    "default": "image",
                                },
                            },
                            "required": ["media_path"],
                        },
                    ),
                    Tool(
                        name="upload_permanent_material",
                        description="Upload permanent material to WeChat server. Supports image, voice, video, and thumb.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "media_path": {
                                    "type": "string",
                                    "description": "Path to media file (local or remote URL).",
                                },
                                "media_type": {
                                    "type": "string",
                                    "description": "Type of media (image, voice, video, thumb).",
                                    "enum": ["image", "voice", "video", "thumb"],
                                    "default": "image",
                                },
                                "description": {
                                    "type": "object",
                                    "description": "Description for video material (required for video). Format: {\"title\": \"Video Title\", \"introduction\": \"Video Intro\"}.",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "introduction": {"type": "string"},
                                    },
                                },
                            },
                            "required": ["media_path"],
                        },
                    ),
                    Tool(
                        name="upload_image_for_news",
                        description="Upload image specifically for use in news articles. Returns a URL that can be used directly in news content.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image_path": {
                                    "type": "string",
                                    "description": "Path to image file (local or remote URL).",
                                },
                            },
                            "required": ["image_path"],
                        },
                    ),
                    Tool(
                        name="get_media_list",
                        description="Get list of media materials from WeChat server.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "media_type": {
                                    "type": "string",
                                    "description": "Type of media (image, voice, video, news).",
                                    "enum": ["image", "voice", "video", "news"],
                                    "default": "image",
                                },
                                "permanent": {
                                    "type": "boolean",
                                    "description": "Whether to get permanent materials (true) or temporary (false).",
                                    "default": True,
                                },
                                "offset": {
                                    "type": "integer",
                                    "description": "Starting offset for pagination.",
                                    "default": 0,
                                },
                                "count": {
                                    "type": "integer",
                                    "description": "Number of items to retrieve (1-20).",
                                    "default": 20,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="upload_cover_image",
                        description="Upload cover image specifically for WeChat articles. Automatically resizes to meet WeChat requirements (64KB max for thumbnails).",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "image_path": {
                                    "type": "string",
                                    "description": "Path to image file (local or remote URL).",
                                },
                            },
                            "required": ["image_path"],
                        },
                    ),
                    Tool(
                        name="delete_permanent_material",
                        description="Delete permanent material from WeChat server.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "media_id": {
                                    "type": "string",
                                    "description": "Media ID of the material to delete.",
                                },
                            },
                            "required": ["media_id"],
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            if name == "publish_article":
                return await self._handle_publish_article(arguments)
            elif name == "list_themes":
                return await self._handle_list_themes()
            elif name == "upload_temp_media":
                return await self._handle_upload_temp_media(arguments)
            elif name == "upload_permanent_material":
                return await self._handle_upload_permanent_material(arguments)
            elif name == "upload_image_for_news":
                return await self._handle_upload_image_for_news(arguments)
            elif name == "upload_cover_image":
                return await self._handle_upload_cover_image(arguments)
            elif name == "get_media_list":
                return await self._handle_get_media_list(arguments)
            elif name == "delete_permanent_material":
                return await self._handle_delete_permanent_material(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_publish_article(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle publish_article tool call."""
        logger.info("开始处理文章发布请求")
        logger.debug(f"传入的参数: {arguments}")
        
        content = arguments.get("content", "")
        theme_id = arguments.get("theme_id", "default")
        permanent_cover = arguments.get("permanent_cover", False)
        author = arguments.get("author", "Xiayan MCP")
        need_open_comment = arguments.get("need_open_comment", 0)
        only_fans_can_comment = arguments.get("only_fans_can_comment", 0)
        
        if not content:
            logger.error("内容不能为空")
            return CallToolResult(
                content=[TextContent(type="text", text="Error: content is required")]
            )
        
        logger.info(f"内容长度: {len(content)} 字符")
        logger.debug(f"内容开头: {content[:200]}...")
        
        try:
            # 确保内容正确编码为UTF-8
            if isinstance(content, bytes):
                content = content.decode('utf-8')
                logger.info("将字节内容解码为UTF-8")
            
            # 谨慎地修复内容中的编码问题
            try:
                original_content = content
                content = _fix_content_encoding(content)
                if content != original_content:
                    logger.info("已修复内容编码问题")
                else:
                    logger.debug("内容编码正常，无需修复")
            except Exception as e:
                logger.warning(f"修复内容编码时出错: {e}，继续使用原始内容")
            
            # 使用增强的格式化器处理Markdown内容
            logger.info(f"开始使用主题 '{theme_id}' 格式化内容")
            title = "未命名文章"
            html_content = ""
            cover = ""
            
            try:
                # 使用正确的format方法，返回字典
                formatted_result = self.formatter.format(content, theme_id)
                
                # 检查返回结果类型
                if isinstance(formatted_result, dict):
                    title = formatted_result.get("title", "未命名文章")
                    html_content = formatted_result.get("content", "")
                    cover = formatted_result.get("cover", "")
                else:
                    # 如果返回的不是字典，尝试使用format_markdown_for_wechat方法
                    logger.warning("format方法返回非字典类型，尝试使用format_markdown_for_wechat")
                    html_content = self.formatter.format_markdown_for_wechat(content)
                    title = "未命名文章"
                    
                    # 尝试从HTML内容中提取标题和封面
                    import re
                    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                    
                    img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', html_content, re.IGNORECASE)
                    if img_match:
                        cover = img_match.group(1)
                
                logger.info(f"内容格式化完成，标题: {title}, 长度: {len(html_content)} 字符")
                
                # 验证格式化后的内容
                if not html_content.strip():
                    logger.error("格式化后的内容为空")
                    raise ValueError("格式化后的内容为空")
                
                # 检查是否仍然包含 Unicode 转义序列
                if '\\u' in html_content:
                    logger.warning("格式化后的内容仍包含 Unicode 转义序列，尝试再次修复")
                    html_content = _fix_content_encoding(html_content)
                
                logger.debug(f"格式化后的内容开头: {html_content[:300]}...")
                
            except Exception as e:
                logger.error(f"格式化内容时出错: {e}")
                logger.exception("详细错误信息: ")
                raise ValueError(f"格式化内容失败: {str(e)}")
            
            # 再次确保HTML内容正确编码
            if isinstance(html_content, bytes):
                html_content = html_content.decode('utf-8')
                logger.info("将HTML内容从字节解码为UTF-8")
            
            # 确保title和cover也是字符串
            if isinstance(title, dict):
                title = str(title)
            if isinstance(cover, dict):
                cover = str(cover)
            
            # 最终编码检查 - 更谨慎的策略
            # 只有在确认有编码问题时才进行修复
            if _needs_encoding_fix(html_content):
                logger.warning("发现编码问题，尝试谨慎修复")
                try:
                    original_html = html_content
                    html_content = _fix_content_encoding(html_content)
                    if html_content != original_html:
                        logger.info("成功修复编码问题")
                except Exception as e:
                    logger.warning(f"修复编码问题时出错: {e}")
            else:
                logger.debug("HTML内容编码正常，无需额外修复")
            
            # 发布到微信公众号草稿箱
            logger.info(f"开始发布到微信公众号草稿箱，标题: {title}")
            result = await self.publisher.publish_to_draft(
                title, html_content, cover, permanent_cover, 
                author, need_open_comment, only_fans_can_comment
            )
            
            logger.info(f"成功发布到草稿箱，结果: {result}")
            
            cover_type = "permanent" if permanent_cover else "temporary"
            cover_media_id = result.get('cover_media_id', '')
            media_id = result.get('media_id', 'unknown')
            
            response_text = f"文章已成功发布到微信公众号草稿箱。媒体ID: {media_id}。"
            
            if cover_media_id:
                response_text += f"封面图片已作为{cover_type}素材上传，媒体ID: {cover_media_id}。"
            
            logger.info(f"准备返回响应: {response_text}")
            
            return CallToolResult(
                content=[
                    TextContent(type="text", text=response_text)
                ]
            )
            
        except Exception as e:
            logger.error(f"发布文章时出错: {e}")
            logger.exception("详细错误信息: ")
            
            error_message = f"发布文章时出错: {str(e)}"
            
            # 提供更具体的错误信息
            if "encoding" in str(e).lower():
                error_message += "\n这可能是编码问题，请检查文章内容是否包含特殊字符。"
            elif "timeout" in str(e).lower():
                error_message += "\n请求超时，请检查网络连接或稍后重试。"
            elif "permission" in str(e).lower():
                error_message += "\n权限不足，请检查API配置或访问权限。"
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=error_message
                    )
                ]
            )

    async def _handle_list_themes(self) -> CallToolResult:
        """Handle list_themes tool call."""
        themes = self.theme_manager.get_available_themes()
        
        theme_contents = []
        for theme in themes:
            theme_info = {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description
            }
            theme_contents.append(
                TextContent(type="text", text=json.dumps(theme_info, ensure_ascii=False))
            )
        
        return CallToolResult(content=theme_contents)

    async def _handle_upload_temp_media(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle upload_temp_media tool call."""
        media_path = arguments.get("media_path", "")
        media_type = arguments.get("media_type", "image")
        
        if not media_path:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: media_path is required")]
            )
        
        try:
            media_id = await self.publisher.upload_temp_media(media_path, media_type)
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Temporary media uploaded successfully. Media ID: {media_id} (valid for 3 days)."
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error uploading temporary media: {str(e)}")
                ]
            )

    async def _handle_upload_permanent_material(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle upload_permanent_material tool call."""
        media_path = arguments.get("media_path", "")
        media_type = arguments.get("media_type", "image")
        description = arguments.get("description", None)
        
        if not media_path:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: media_path is required")]
            )
        
        try:
            media_id = await self.publisher.upload_permanent_material(media_path, media_type, description)
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Permanent material uploaded successfully. Media ID: {media_id}"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error uploading permanent material: {str(e)}")
                ]
            )

    async def _handle_upload_image_for_news(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle upload_image_for_news tool call."""
        image_path = arguments.get("image_path", "")
        
        if not image_path:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: image_path is required")]
            )
        
        try:
            image_url = await self.publisher.upload_image_for_news(image_path)
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Image uploaded for news successfully. Image URL: {image_url}"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error uploading image for news: {str(e)}")
                ]
            )
    
    async def _handle_upload_cover_image(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle upload_cover_image tool call."""
        image_path = arguments.get("image_path", "")
        
        if not image_path:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: image_path is required")]
            )
        
        try:
            media_id = await self.publisher.upload_cover_image(image_path)
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Cover image uploaded successfully. Media ID: {media_id}. This can be used as thumb_media_id for article covers."
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error uploading cover image: {str(e)}")
                ]
            )

    async def _handle_get_media_list(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_media_list tool call."""
        media_type = arguments.get("media_type", "image")
        permanent = arguments.get("permanent", True)
        offset = arguments.get("offset", 0)
        count = arguments.get("count", 20)
        
        try:
            result = await self.publisher.get_media_list(media_type, permanent, offset, count)
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Media list retrieved successfully:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error getting media list: {str(e)}")
                ]
            )

    async def _handle_delete_permanent_material(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle delete_permanent_material tool call."""
        media_id = arguments.get("media_id", "")
        
        if not media_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: media_id is required")]
            )
        
        try:
            success = await self.publisher.delete_permanent_material(media_id)
            if success:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Permanent material {media_id} deleted successfully."
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Failed to delete permanent material {media_id}."
                        )
                    ]
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error deleting permanent material: {str(e)}")
                ]
            )

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the Xiayan MCP server."""
    server = XiayanMCPServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())