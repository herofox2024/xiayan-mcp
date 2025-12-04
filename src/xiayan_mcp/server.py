"""MCP Server implementation for Xiayan."""

import asyncio
import json
import logging
import html
import re
import sys
import os
import argparse
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

# Interactive input for WeChat API credentials if not already set
def _prompt_for_wechat_credentials(force: bool = False):
    """Prompt user for WeChat API credentials interactively if not set.
    
    Args:
        force: Whether to force reconfiguration even if credentials are already set
    """
    import getpass
    
    # Check if credentials are already set
    app_id = os.getenv('WECHAT_APP_ID', '')
    app_secret = os.getenv('WECHAT_APP_SECRET', '')
    
    if app_id and app_secret and not force:
        return
    
    # If force is True, clear existing credentials
    if force:
        print("\n=== 重新配置微信公众号API凭证 ===")
        print("当前凭证将被替换。\n")
        app_id = ''
        app_secret = ''
    else:
        print("\n=== 微信公众号API凭证配置 ===")
        print("请输入您的微信公众号开发者凭证，用于发布文章到公众号草稿箱。")
        print("您可以在微信公众平台 -> 设置与开发 -> 基本配置中获取这些信息。\n")
    
    # Prompt for App ID with validation
    while True:
        app_id_input = input("请输入微信公众号App ID: ").strip()
        # Simple validation: App ID should be a string of numbers and letters
        if app_id_input and re.match(r'^[a-zA-Z0-9]+$', app_id_input):
            app_id = app_id_input
            break
        print("App ID格式不正确，请输入字母和数字的组合。")
    
    # Prompt for App Secret with validation (hide input)
    while True:
        app_secret_input = getpass.getpass("请输入微信公众号App Secret (输入时不显示): ").strip()
        # Simple validation: App Secret should be a longer string
        if app_secret_input and len(app_secret_input) > 10:
            app_secret = app_secret_input
            break
        print("App Secret格式不正确，请输入有效的Secret（长度应大于10个字符）。")
    
    # Set environment variables
    os.environ['WECHAT_APP_ID'] = app_id
    os.environ['WECHAT_APP_SECRET'] = app_secret
    
    # Option to save to .env file with better prompt
    print("\n建议将凭证保存到.env文件，以便下次自动加载。")
    save_to_env = input("是否将凭证保存到.env文件？(y/n): ").strip().lower()
    if save_to_env == 'y':
        try:
            # Read existing .env content
            env_content = []
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_content = f.readlines()
            
            # Update or add credentials
            app_id_found = False
            app_secret_found = False
            
            for i, line in enumerate(env_content):
                if line.strip().startswith('WECHAT_APP_ID='):
                    env_content[i] = f"WECHAT_APP_ID={app_id}\n"
                    app_id_found = True
                elif line.strip().startswith('WECHAT_APP_SECRET='):
                    env_content[i] = f"WECHAT_APP_SECRET={app_secret}\n"
                    app_secret_found = True
            
            if not app_id_found:
                env_content.append(f"WECHAT_APP_ID={app_id}\n")
            if not app_secret_found:
                env_content.append(f"WECHAT_APP_SECRET={app_secret}\n")
            
            # Write back to .env file
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_content)
            
            print("✅ 凭证已成功保存到.env文件。")
        except Exception as e:
            print(f"❌ 保存凭证到.env文件失败: {e}")
    else:
        print("⚠️  凭证未保存到.env文件，下次启动时需要重新输入。")
    
    print("✅ 微信公众号API凭证配置完成。\n")

# Parse command line arguments
def parse_args():
    """Parse command line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Xiayan MCP Server for WeChat Official Account publishing")
    parser.add_argument('--reconfigure', '-r', action='store_true', 
                        help='Force reconfiguration of WeChat API credentials')
    parser.add_argument('--debug', '-d', action='store_true', 
                        help='Enable debug logging')
    return parser.parse_args()

# Parse arguments and call interactive prompt
args = parse_args()

# Set logging level based on debug flag
if args.debug:
    logging.basicConfig(level=logging.DEBUG)

# Call the interactive prompt with force flag
_prompt_for_wechat_credentials(force=args.reconfigure)

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
from .utils.encoding import enconding_utils


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
                            "properties": {
                                "detailed": {
                                    "type": "boolean",
                                    "description": "Whether to return detailed theme information.",
                                    "default": False,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="preview_theme",
                        description="Get HTML preview of a theme with sample content.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "theme_id": {
                                    "type": "string",
                                    "description": "ID of the theme to preview.",
                                },
                                "sample_content": {
                                    "type": "string",
                                    "description": "Optional sample content to use for preview.",
                                },
                            },
                            "required": ["theme_id"],
                        },
                    ),
                    Tool(
                        name="add_custom_theme",
                        description="Add a custom theme to the theme manager.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Unique ID for the custom theme.",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Name of the custom theme.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the custom theme.",
                                },
                                "template": {
                                    "type": "string",
                                    "description": "HTML template for the custom theme.",
                                },
                                "css_styles": {
                                    "type": "string",
                                    "description": "CSS styles for the custom theme.",
                                },
                            },
                            "required": ["id", "name", "description"],
                        },
                    ),
                    Tool(
                        name="update_theme",
                        description="Update an existing theme with new properties.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "theme_id": {
                                    "type": "string",
                                    "description": "ID of the theme to update.",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "New name for the theme.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description for the theme.",
                                },
                                "template": {
                                    "type": "string",
                                    "description": "New HTML template for the theme.",
                                },
                                "css_styles": {
                                    "type": "string",
                                    "description": "New CSS styles for the theme.",
                                },
                            },
                            "required": ["theme_id"],
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
                return await self._handle_list_themes(arguments)
            elif name == "preview_theme":
                return await self._handle_preview_theme(arguments)
            elif name == "add_custom_theme":
                return await self._handle_add_custom_theme(arguments)
            elif name == "update_theme":
                return await self._handle_update_theme(arguments)
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
        
        try:
            # 1. 解析参数
            content, theme_id, permanent_cover, author, need_open_comment, only_fans_can_comment = self._parse_publish_arguments(arguments)
            
            # 2. 验证内容
            if not content:
                logger.error("内容不能为空")
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: content is required")]
                )
            
            # 3. 修复内容编码
            content = self._fix_content_encoding(content)
            
            # 4. 格式化内容
            title, html_content, cover = await self._format_content(content, theme_id)
            
            # 5. 最终编码检查
            html_content = self._final_encoding_check(html_content, title, cover)
            
            # 6. 发布到微信草稿箱
            result = await self._publish_to_wechat_draft(
                title, html_content, cover, permanent_cover, 
                author, need_open_comment, only_fans_can_comment
            )
            
            # 7. 构建响应
            return self._build_publish_response(result, permanent_cover)
            
        except Exception as e:
            return self._handle_publish_error(e)
    
    def _parse_publish_arguments(self, arguments: Dict[str, Any]) -> tuple:
        """Parse and validate publish article arguments."""
        content = arguments.get("content", "")
        theme_id = arguments.get("theme_id", "default")
        permanent_cover = arguments.get("permanent_cover", False)
        author = arguments.get("author", "Xiayan MCP")
        need_open_comment = arguments.get("need_open_comment", 0)
        only_fans_can_comment = arguments.get("only_fans_can_comment", 0)
        
        return content, theme_id, permanent_cover, author, need_open_comment, only_fans_can_comment
    
    def _fix_content_encoding(self, content: str) -> str:
        """Fix content encoding issues."""
        logger.info(f"内容长度: {len(content)} 字符")
        logger.debug(f"内容开头: {content[:200]}...")
        
        # 确保内容正确编码为UTF-8
        if isinstance(content, bytes):
            content = content.decode('utf-8')
            logger.info("将字节内容解码为UTF-8")
        
        # 谨慎地修复内容中的编码问题
        try:
            original_content = content
            content = enconding_utils.fix_encoding(content)
            if content != original_content:
                logger.info("已修复内容编码问题")
            else:
                logger.debug("内容编码正常，无需修复")
        except Exception as e:
            logger.warning(f"修复内容编码时出错: {e}，继续使用原始内容")
        
        return content
    
    async def _format_content(self, content: str, theme_id: str) -> tuple:
        """Format content using the specified theme."""
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
                html_content = enconding_utils.fix_encoding(html_content)
            
            logger.debug(f"格式化后的内容开头: {html_content[:300]}...")
            
            return title, html_content, cover
            
        except Exception as e:
            logger.error(f"格式化内容时出错: {e}")
            logger.exception("详细错误信息: ")
            raise ValueError(f"格式化内容失败: {str(e)}")
    
    def _final_encoding_check(self, html_content: str, title: str, cover: str) -> str:
        """Perform final encoding check on HTML content."""
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
        if enconding_utils.needs_encoding_fix(html_content):
            logger.warning("发现编码问题，尝试谨慎修复")
            try:
                original_html = html_content
                html_content = enconding_utils.fix_encoding(html_content)
                if html_content != original_html:
                    logger.info("成功修复编码问题")
            except Exception as e:
                logger.warning(f"修复编码问题时出错: {e}")
        else:
            logger.debug("HTML内容编码正常，无需额外修复")
        
        return html_content
    
    async def _publish_to_wechat_draft(self, title: str, html_content: str, cover: str, 
                                     permanent_cover: bool, author: str, 
                                     need_open_comment: int, only_fans_can_comment: int) -> dict:
        """Publish content to WeChat draft box."""
        logger.info(f"开始发布到微信公众号草稿箱，标题: {title}")
        result = await self.publisher.publish_to_draft(
            title, html_content, cover, permanent_cover, 
            author, need_open_comment, only_fans_can_comment
        )
        logger.info(f"成功发布到草稿箱，结果: {result}")
        return result
    
    def _build_publish_response(self, result: dict, permanent_cover: bool) -> CallToolResult:
        """Build response for successful publish."""
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
    
    def _handle_publish_error(self, error: Exception) -> CallToolResult:
        """Handle errors during publish process."""
        logger.error(f"发布文章时出错: {error}")
        logger.exception("详细错误信息: ")
        
        error_message = f"发布文章时出错: {str(error)}"
        
        # 提供更具体的错误信息
        if "encoding" in str(error).lower():
            error_message += "\n这可能是编码问题，请检查文章内容是否包含特殊字符。"
        elif "timeout" in str(error).lower():
            error_message += "\n请求超时，请检查网络连接或稍后重试。"
        elif "permission" in str(error).lower():
            error_message += "\n权限不足，请检查API配置或访问权限。"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=error_message
                )
            ]
        )

    async def _handle_list_themes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle list_themes tool call."""
        detailed = arguments.get("detailed", False)
        
        if detailed:
            themes = self.theme_manager.get_available_themes()
        else:
            # For backward compatibility, return simple theme list
            themes = [{"id": theme.id, "name": theme.name, "description": theme.description} 
                     for theme in self.theme_manager._themes.values()]
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(themes, ensure_ascii=False))]
        )
    
    async def _handle_preview_theme(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle preview_theme tool call."""
        theme_id = arguments.get("theme_id")
        sample_content = arguments.get("sample_content", "")
        
        if not theme_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: theme_id is required")]
            )
        
        try:
            preview_html = self.theme_manager.get_theme_preview(theme_id, sample_content)
            return CallToolResult(
                content=[TextContent(type="text", text=preview_html)]
            )
        except Exception as e:
            logger.error(f"Failed to preview theme: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    async def _handle_add_custom_theme(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle add_custom_theme tool call."""
        from .themes.theme import Theme
        
        theme_id = arguments.get("id")
        name = arguments.get("name")
        description = arguments.get("description")
        template = arguments.get("template", "")
        css_styles = arguments.get("css_styles", "")
        
        if not all([theme_id, name, description]):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: id, name, and description are required")]
            )
        
        try:
            custom_theme = Theme(
                id=theme_id,
                name=name,
                description=description,
                template=template,
                css_styles=css_styles
            )
            
            self.theme_manager.add_custom_theme(custom_theme)
            return CallToolResult(
                content=[TextContent(type="text", text=f"Theme '{theme_id}' added successfully")]
            )
        except Exception as e:
            logger.error(f"Failed to add custom theme: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    async def _handle_update_theme(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle update_theme tool call."""
        theme_id = arguments.get("theme_id")
        
        if not theme_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: theme_id is required")]
            )
        
        # Remove theme_id from arguments since it's not a theme property
        update_args = {k: v for k, v in arguments.items() if k != "theme_id"}
        
        try:
            updated_theme = self.theme_manager.update_theme(theme_id, **update_args)
            return CallToolResult(
                content=[TextContent(type="text", text=f"Theme '{theme_id}' updated successfully")]
            )
        except Exception as e:
            logger.error(f"Failed to update theme: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )

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
            print("MCP服务器已就绪，正在等待请求...", file=sys.stderr)
            print("提示：使用Ctrl+C可以停止服务器", file=sys.stderr)
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the Xiayan MCP server."""
    print("正在初始化xiayan-mcp服务器...", file=sys.stderr)
    server = XiayanMCPServer()
    try:
        print("服务器初始化完成，正在启动MCP服务...", file=sys.stderr)
        await server.run()
    except KeyboardInterrupt:
        print("服务器已被用户停止", file=sys.stderr)
    except Exception as e:
        print(f"服务器错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())