"""WeChat Official Account publisher."""

import os
import asyncio
import logging
from typing import Dict, Optional, List, Union, Tuple
import aiohttp
import json
import mimetypes
import tempfile

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


logger = logging.getLogger(__name__)


# 微信API错误码映射表
WECHAT_ERROR_CODES = {
    40001: "无效的凭证（access_token）",
    40002: "不合法的凭证类型",
    40003: "不合法的OpenID",
    40004: "不合法的媒体文件类型",
    40005: "不合法的文件类型",
    40006: "不合法的文件大小",
    40007: "不合法的媒体文件id",
    40008: "不合法的消息类型",
    40009: "不合法的图片文件大小",
    40010: "不合法的语音文件大小",
    40011: "不合法的视频文件大小",
    40012: "不合法的缩略图文件大小",
    40013: "不合法的AppID",
    40014: "不合法的access_token",
    40015: "不合法的菜单类型",
    40016: "不合法的按钮个数",
    40017: "不合法的按钮个数",
    40018: "不合法的按钮名字长度",
    40019: "不合法的按钮KEY长度",
    40020: "不合法的按钮URL长度",
    40021: "不合法的菜单版本号",
    40022: "不合法的子菜单级数",
    40023: "不合法的子菜单按钮个数",
    40024: "不合法的子菜单按钮类型",
    40025: "不合法的子菜单按钮名字长度",
    40026: "不合法的子菜单按钮KEY长度",
    40027: "不合法的子菜单按钮URL长度",
    40028: "不合法的自定义菜单使用用户",
    40029: "不合法的oauth_code",
    40030: "不合法的refresh_token",
    40031: "不合法的openid列表",
    40032: "不合法的openid列表长度",
    40033: "不合法的请求字符",
    40035: "不合法的参数",
    40038: "不合法的请求格式",
    40039: "不合法的URL长度",
    40050: "不合法的分组id",
    40051: "分组名字不合法",
    40060: "删除单篇图文时，指定的article_idx不合法",
    40117: "分组名字不合法",
    40118: "media_id大小不合法",
    40119: "button类型错误",
    40120: "button名字错误",
    40121: "button KEY错误",
    40122: "button URL错误",
    40132: "不合法的媒体文件类型",
    40137: "不合法的APPID",
    40155: "不合法的素材类型",
    41001: "缺少access_token参数",
    41002: "缺少appid参数",
    41003: "缺少refresh_token参数",
    41004: "缺少secret参数",
    41005: "缺少多媒体文件数据",
    41006: "缺少media_id参数",
    41007: "缺少子菜单数据",
    41008: "缺少oauth code",
    41009: "缺少openid",
    42001: "access_token超时",
    42002: "refresh_token超时",
    42003: "oauth_code超时",
    42007: "用户修改微信密码，accesstoken和refreshtoken失效",
    43002: "需要GET请求",
    43003: "需要POST请求",
    43004: "需要HTTPS请求",
    43005: "需要接收者关注",
    43006: "需要好友关系",
    44001: "多媒体文件为空",
    44002: "POST的数据包为空",
    44003: "图文消息内容为空",
    44004: "文本消息内容为空",
    45001: "多媒体文件大小超过限制",
    45002: "消息内容超过限制",
    45003: "标题字段超过限制",
    45004: "描述字段超过限制",
    45005: "链接字段超过限制",
    45006: "图片链接字段超过限制",
    45007: "语音播放时间超过限制",
    45008: "图文消息超过限制",
    45009: "接口调用超过限制",
    45010: "创建菜单个数超过限制",
    45011: "API调用太频繁，请稍候再试",
    45015: "回复时间超过限制",
    45016: "系统繁忙",
    45017: "媒体文件格式不正确",
    45018: "上传的文件不是合法的媒体文件",
    45019: "上传的缩略图不是合法的图片文件",
    45022: "图片大小超过限制",
    45026: "文字消息超过限制",
    45038: "图文消息title字段超过限制",
    47001: "解析JSON/XML内容错误",
    48001: "api功能未授权",
    50001: "用户未授权该api",
    50002: "用户受限，可能是违规后接口被封禁",
    61451: "参数错误(invalid parameter)",
    61452: "无效客服账号(invalid kf_account)",
    61453: "客服帐号已存在(kf_account exsited)",
    61454: "客服帐号名长度超过限制(仅允许10个英文字符，不包括@及@后的公众号的微信号)",
    61455: "客服帐号名包含非法字符(仅允许英文+数字)",
    61456: "客服帐号个数超过限制(10个客服账号)",
    61457: "无效头像文件类型",
    61450: "系统错误(sys error)",
    61500: "日期格式错误",
    61501: "日期范围错误",
    9001001: "POST数据参数不合法",
    9001002: "远端服务不可用",
    9001003: "Ticket不合法",
    9001004: "获取摇周边ticket失败",
    9001005: "获取设备ID失败",
    9001006: "获取openid失败",
    9001007: "上传文件缺失",
    9001008: "上传素材的文件类型不合法",
    9001009: "上传素材的文件尺寸不合法",
    9001010: "上传失败",
    9001020: "帐号不合法",
    9001021: "已有设备激活率低于50%，不能新增设备",
    9001022: "设备申请数不合法，必须为大于0的数字",
    9001023: "已存在审核中的设备ID申请",
    9001024: "一次查询设备ID数量不能超过50",
    9001025: "设备ID不合法",
    9001026: "页面ID不合法",
    9001027: "页面参数不合法",
    9001028: "一次删除页面ID数量不能超过10",
    9001029: "页面已应用在设备中，请先解除应用关系",
    9001030: "一次查询页面ID数量不能超过50",
    9001031: "时间区间不合法",
    9001032: "保存设备与页面的绑定关系参数错误",
    9001033: "门店ID不合法",
    9001034: "设备备注信息过长",
    9001035: "设备申请参数不合法",
    9001036: "查询起始值begin不合法"
}


class WeChatPublisher:
    """Publisher for WeChat Official Account."""

    def __init__(self):
        """Initialize the publisher with WeChat API credentials."""
        self.app_id = os.getenv('WECHAT_APP_ID', '')
        self.app_secret = os.getenv('WECHAT_APP_SECRET', '')
        self.base_url = 'https://api.weixin.qq.com/cgi-bin'
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[int] = None

    def _handle_wechat_api_error(self, data: Dict, context: str = "操作") -> None:
        """Handle WeChat API error responses.
        
        Args:
            data: API response data
            context: Operation context for error message
        
        Raises:
            Exception: With friendly error message
        """
        if 'access_token' in data or 'media_id' in data:
            return  # No error, upload successful
            
        errcode = data.get('errcode')
        errmsg = data.get('errmsg', 'Unknown error')
        
        # Get friendly error message from mapping table
        friendly_msg = WECHAT_ERROR_CODES.get(errcode, errmsg)
        
        raise Exception(f"{context}失败: {friendly_msg} (错误码: {errcode})")

    async def _get_access_token(self) -> str:
        """Get WeChat API access token using the new stable access token API."""
        import time
        
        # Check if token is still valid
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token

        if not self.app_id or not self.app_secret:
            raise ValueError("WECHAT_APP_ID and WECHAT_APP_SECRET environment variables are required")

        # Use the new stable access token API
        url = f"{self.base_url}/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    # First check response status
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP error {response.status}: {error_text}")
                    
                    # Get response text and try to parse as JSON regardless of content type
                    response_text = await response.text()
                    
                    # Debug: Log response for troubleshooting
                    logger.debug(f"Token response: {response_text[:200]}")
                    
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        content_type = response.headers.get('content-type', '')
                        raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                    
                    # Handle API errors
                    self._handle_wechat_api_error(data, "获取访问令牌")
                    
                    self.access_token = data['access_token']
                    expires_in = data.get('expires_in', 7200)
                    self.token_expires_at = time.time() + expires_in - 300  # Refresh 5 minutes before expiry
                    return self.access_token
                    
        except Exception as e:
            # If the old API fails, try the new stable access token API
            logger.info("Falling back to stable access token API...")
            return await self._get_stable_access_token()

    async def _get_stable_access_token(self) -> str:
        """Get stable access token using the new API."""
        import time
        
        # New stable access token API
        url = f"{self.base_url}/stable_token"
        data = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
            "force_refresh": False
        }

        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                # First check response status
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                # Get response text and try to parse as JSON regardless of content type
                response_text = await response.text()
                
                # Debug: Log response for troubleshooting
                logger.debug(f"Stable token response: {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "获取稳定访问令牌")
                
                if 'access_token' not in result or 'expires_in' not in result:
                    raise Exception(f"Invalid response from stable token API: 缺少必要字段")
                
                self.access_token = result['access_token']
                expires_in = result['expires_in']
                self.token_expires_at = time.time() + expires_in - 300  # Refresh 5 minutes before expiry
                return self.access_token

    async def _resize_image_for_thumb(self, image_path: str, max_size_kb: int = 64) -> str:
        """
        Resize image to meet WeChat thumb requirements (max 64KB).
        
        Args:
            image_path: Path to original image
            max_size_kb: Maximum size in KB (default: 64)
            
        Returns:
            Path to resized temporary image file
        """
        try:
            from PIL import Image
            import tempfile
            
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate target size (keeping aspect ratio)
            width, height = img.size
            max_dimension = 400  # Recommended size for thumb
            
            if width > max_dimension or height > max_dimension:
                # Calculate new size maintaining aspect ratio
                ratio = min(max_dimension / width, max_dimension / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to temporary file with compression
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Try different quality levels to meet size requirement
            quality = 85
            while quality > 10:
                img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                
                # Check file size
                file_size_kb = os.path.getsize(temp_path) / 1024
                if file_size_kb <= max_size_kb:
                    return temp_path
                
                quality -= 10
            
            # If still too large, try smaller dimensions
            max_dimension = 300
            if width > max_dimension or height > max_dimension:
                ratio = min(max_dimension / width, max_dimension / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                quality = 85
                while quality > 10:
                    img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                    file_size_kb = os.path.getsize(temp_path) / 1024
                    if file_size_kb <= max_size_kb:
                        return temp_path
                    quality -= 10
            
            # Return the resized image even if slightly over limit
            return temp_path
            
        except ImportError:
            # If PIL is not available, return original path
            logger.warning("PIL not available, cannot resize image. Install Pillow for image resizing.")
            return image_path
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image_path

    async def _upload_media(self, media_path: str, media_type: str = 'image', permanent: bool = False, 
                           description: Optional[Dict] = None) -> str:
        """
        Upload media file to WeChat server.
        
        Args:
            media_path: Path to media file (local or remote)
            media_type: Type of media ('image', 'voice', 'video', 'thumb')
            permanent: Whether to upload as permanent material (default: False for temporary)
            description: Additional description for video material (required for permanent video)
            
        Returns:
            Media ID from WeChat server
        """
        access_token = await self._get_access_token()
        
        # Choose API endpoint based on permanent or temporary
        if permanent:
            url = f"{self.base_url}/material/add_material?access_token={access_token}&type={media_type}"
        else:
            url = f"{self.base_url}/media/upload?access_token={access_token}&type={media_type}"
        
        # Handle different media sources
        original_media_path = media_path
        
        # Special handling for thumb type to ensure size requirements
        if media_type == 'thumb':
            # For thumb images, we need to resize to meet WeChat requirements (64KB max)
            if media_path.startswith(('http://', 'https://')):
                # Download remote image first
                media_data, filename = await self._download_media(media_path)
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    temp_file.write(media_data)
                    temp_path = temp_file.name
                media_path = temp_path
            else:
                filename = os.path.basename(media_path)
                temp_path = None
            
            # Resize image to meet thumb requirements
            resized_path = await self._resize_image_for_thumb(media_path)
            media_path = resized_path
            
            # Read the resized file
            with open(media_path, 'rb') as f:
                media_data = f.read()
            
            # Clean up temporary files
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            if resized_path != original_media_path and os.path.exists(resized_path):
                # We'll clean up after upload
                pass
        else:
            # Handle other media types
            if media_path.startswith(('http://', 'https://')):
                # Download remote image first
                media_data, filename = await self._download_media(media_path)
            else:
                # Read local file
                if not os.path.exists(media_path):
                    raise FileNotFoundError(f"Media file not found: {media_path}")
                
                filename = os.path.basename(media_path)
                with open(media_path, 'rb') as f:
                    media_data = f.read()

        # Determine content type
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Upload to WeChat
        try:
            data = aiohttp.FormData()
            
            if permanent and media_type == 'video' and description:
                # For permanent video, add description
                data.add_field('description', json.dumps(description), 
                             content_type='application/json')
            
            data.add_field('media', media_data, filename=filename, content_type=content_type)
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                
                if permanent and media_type == 'video' and description:
                    # For permanent video, add description
                    data.add_field('description', json.dumps(description), 
                                 content_type='application/json')
                
                data.add_field('media', media_data, filename=filename, content_type=content_type)
                
                async with session.post(url, data=data) as response:
                    # First check response status
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP error {response.status}: {error_text}")
                    
                    # Get response text and try to parse as JSON regardless of content type
                    response_text = await response.text()
                    
                    # Debug: Log first 200 chars of response for troubleshooting
                    logger.debug(f"Upload response (first 200 chars): {response_text[:200]}")
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        content_type = response.headers.get('content-type', '')
                        raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                    
                    # Handle API errors
                    self._handle_wechat_api_error(result, "上传媒体文件")
                    
                    if 'media_id' not in result:
                        raise Exception(f"Failed to upload media: 缺少media_id字段")
                    
                    return result['media_id']
            
        except Exception as e:
            # Clean up temporary files on error
            if media_type == 'thumb' and 'original_media_path' in locals() and media_path != original_media_path and os.path.exists(media_path):
                os.unlink(media_path)
            raise e
        
        finally:
            # Clean up temporary files
            if media_type == 'thumb' and 'original_media_path' in locals() and media_path != original_media_path and os.path.exists(media_path):
                os.unlink(media_path)

    async def _download_media(self, url: str) -> Tuple[bytes, str]:
        """Download media from remote URL and return data with filename."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download media: HTTP {response.status}")
                
                # Try to get filename from URL or Content-Disposition header
                filename = "media"
                if 'Content-Disposition' in response.headers:
                    disposition = response.headers['Content-Disposition']
                    if 'filename=' in disposition:
                        filename = disposition.split('filename=')[-1].strip('"')
                else:
                    # Extract filename from URL
                    from urllib.parse import unquote, urlparse
                    parsed_url = urlparse(url)
                    path_filename = unquote(os.path.basename(parsed_url.path))
                    if path_filename:
                        filename = path_filename
                
                # Ensure filename has extension
                if not mimetypes.guess_type(filename)[0]:
                    content_type = response.headers.get('content-type', '')
                    extension = mimetypes.guess_extension(content_type)
                    if extension:
                        filename += extension
                
                return await response.read(), filename

    async def _add_draft(self, title: str, content: str, cover_media_id: str = '') -> str:
        """
        Add article to WeChat draft using the new API.
        
        Args:
            title: Article title
            content: HTML content
            cover_media_id: Media ID for cover image
            
        Returns:
            Media ID of the created draft
        """
        access_token = await self._get_access_token()
        url = f"{self.base_url}/draft/add?access_token={access_token}"
        
        # Build article object according to WeChat API requirements
        article = {
            "title": title,
            "content": content,
            "digest": "",  # Auto-generated by WeChat
            "author": "Xiayan MCP",
            "content_source_url": "",
            "show_cover_pic": 0,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
        
        # Only add cover media if provided and valid
        if cover_media_id:
            article["show_cover_pic"] = 1
            article["thumb_media_id"] = cover_media_id

        articles = [article]
        data = {"articles": articles}
        
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                # First check response status
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                # Get response text and try to parse as JSON regardless of content type
                response_text = await response.text()
                
                # Debug: Log first 200 chars of response for troubleshooting
                logger.debug(f"Response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "添加草稿")
                
                if 'media_id' not in result:
                    raise Exception(f"Failed to add draft: 缺少media_id字段")
                
                return result['media_id']

    async def upload_cover_image(self, image_path: str) -> str:
        """
        Upload cover image specifically for WeChat articles.
        This method ensures the image meets WeChat's requirements for article covers.
        
        Args:
            image_path: Path to image file (local or remote URL)
            
        Returns:
            Media ID of uploaded thumbnail
        """
        try:
            # Always upload as permanent thumb material for article covers
            # This ensures the cover image is permanently available
            media_id = await self.upload_permanent_material(image_path, 'thumb')
            return media_id
        except Exception as e:
            raise Exception(f"Failed to upload cover image: {str(e)}")

    async def _add_draft_with_options(self, title: str, content: str, cover_media_id: str = '',
                                    author: str = "Xiayan MCP", need_open_comment: int = 0, 
                                    only_fans_can_comment: int = 0) -> str:
        """
        Add article to WeChat draft using the new API with extended options.
        
        Args:
            title: Article title
            content: HTML content
            cover_media_id: Media ID for cover image
            author: Article author
            need_open_comment: Enable open comments (0/1)
            only_fans_can_comment: Only fans can comment (0/1)
            
        Returns:
            Media ID of the created draft
        """
        access_token = await self._get_access_token()
        url = f"{self.base_url}/draft/add?access_token={access_token}"
        
        # Build article object according to WeChat API requirements
        article = {
            "title": title,
            "content": content,
            "digest": "",  # Auto-generated by WeChat
            "author": author,
            "content_source_url": "",
            "show_cover_pic": 0,
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment
        }
        
        # Only add cover media if provided and valid
        if cover_media_id:
            article["show_cover_pic"] = 1
            article["thumb_media_id"] = cover_media_id

        articles = [article]
        data = {"articles": articles}
        
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                # First check response status
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                # Get response text and try to parse as JSON regardless of content type
                response_text = await response.text()
                
                # Debug: Log first 200 chars of response for troubleshooting
                logger.debug(f"Response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "添加草稿")
                
                if 'media_id' not in result:
                    raise Exception(f"Failed to add draft: 缺少media_id字段")
                
                return result['media_id']

    async def publish_to_draft(self, title: str, content: str, cover: str = '', 
                              permanent_cover: bool = False, author: str = "Xiayan MCP",
                              need_open_comment: int = 0, only_fans_can_comment: int = 0) -> Dict[str, str]:
        """
        Publish article to WeChat draft box.
        
        Args:
            title: Article title
            content: Formatted HTML content
            cover: Cover image URL or path
            permanent_cover: Whether to upload cover as permanent material
            author: Article author
            need_open_comment: Enable open comments (0/1)
            only_fans_can_comment: Only fans can comment (0/1)
            
        Returns:
            Dictionary with media_id and other response data
        """
        try:
            logger.info(f"开始发布文章到草稿箱")
            logger.info(f"文章标题: {title}")
            logger.info(f"是否有封面: {'是' if cover else '否'}")
            logger.info(f"作者: {author}")
            logger.info(f"内容长度: {len(content)} 字符")
            
            # Upload cover image if provided
            logger.info(f"开始处理封面图片...")
            cover_media_id = await self._get_or_create_cover(cover, content)
            logger.info(f"封面处理完成，media_id: {cover_media_id}")

            # Add as draft using new API
            logger.info(f"开始添加到草稿箱...")
            media_id = await self._add_draft_with_options(
                title, content, cover_media_id, author, 
                need_open_comment, only_fans_can_comment
            )
            logger.info(f"草稿添加成功，media_id: {media_id}")
            
            result = self._build_publish_result(media_id, title, cover_media_id)
            logger.info(f"发布结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"发布到草稿箱失败: {str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise
    
    async def _get_or_create_cover(self, cover: str, content: str) -> str:
        """Get cover media ID from provided cover or create one."""
        if cover:
            # Always upload cover as permanent thumb material
            # This ensures it's available for future use and meets WeChat requirements
            return await self.upload_permanent_material(cover, 'thumb')
        elif self._extract_first_image(content):
            # Use first image in content as cover if no cover specified
            first_image = self._extract_first_image(content)
            return await self.upload_permanent_material(first_image, 'thumb')
        else:
            # Create a default cover if no image provided (WeChat API requires thumb_media_id)
            return await self._create_default_cover()
    
    def _build_publish_result(self, media_id: str, title: str, cover_media_id: str) -> Dict[str, str]:
        """Build publish result dictionary."""
        return {
            'media_id': media_id,
            'title': title,
            'status': 'success',
            'cover_media_id': cover_media_id
        }

    def _extract_first_image(self, html_content: str) -> Optional[str]:
        """Extract first image URL from HTML content."""
        import re
        img_pattern = r'<img[^>]+src="([^"]+)"'
        match = re.search(img_pattern, html_content)
        return match.group(1) if match else None

    async def _create_default_cover(self) -> str:
        """
        Create a default cover image for articles without images.
        
        Returns:
            Media ID of the created default cover
        """
        try:
            # Create a simple solid color image as default cover
            from PIL import Image, ImageDraw, ImageFont
            import tempfile
            import os
            
            # Create a 400x400 image with a gradient background
            width, height = 400, 400
            img = Image.new('RGB', (width, height), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Create gradient effect
            for y in range(height):
                color_value = int(240 - (y / height) * 50)  # Light gradient
                draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value + 20))
            
            # Add text to the image
            try:
                # Try to use a font, fall back to default if not available
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Add text
            text = "文颜书评"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(51, 51, 51), font=font)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            img.save(temp_path, 'JPEG', quality=85, optimize=True)
            
            # Upload as permanent thumb material
            media_id = await self.upload_permanent_material(temp_path, 'thumb')
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return media_id
            
        except ImportError:
            # If PIL is not available, use a simple 1x1 pixel image
            import tempfile
            import os
            
            # Create minimal JPEG file (1x1 pixel gray image)
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            
            # Minimal JPEG header for 1x1 gray pixel
            jpeg_data = bytes.fromhex(
                'ffd8ffe000104a4649460001010100h00h0000ffdb00c308090b0c090c0b0a0c0d10'
                '0e0c0d1114151413131418191e1d1a1a1d1e1d1a1c1c2024262e2720222c231c1c28'
                '37292c3031343434343434343434343434343434343434343434343434343434343434'
                '3434343434343434343434343434343434343434343434343434343434343434343434'
                '3434343434343434343434343434343434343434343434343434343434343434343434'
                '34ffc00011080001000103012200021101031101ffc40101000101010101000000000000'
                '0000000000000000000affc4001b0100010101010101010100000000000000000000000000'
                '00000000000003ffd9'
            )
            
            with open(temp_path, 'wb') as f:
                f.write(jpeg_data)
            
            # Upload as permanent thumb material
            media_id = await self.upload_permanent_material(temp_path, 'thumb')
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return media_id
            
        except Exception as e:
            # If all else fails, raise an exception
            raise Exception(f"Failed to create default cover: {str(e)}")

    async def get_draft_list(self) -> Dict:
        """Get list of drafts from WeChat."""
        import html
        import logging
        
        # 设置日志
        logger = logging.getLogger(__name__)
        
        access_token = await self._get_access_token()
        url = f"{self.base_url}/draft/batchget?access_token={access_token}"
        
        data = {
            "offset": 0,
            "count": 20,
            "no_content": 0
        }
        
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                # First check response status
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"HTTP error {response.status}: {error_text}")
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                # Get response text and try to parse as JSON regardless of content type
                response_text = await response.text()
                
                # Debug: Print first 200 chars of response for troubleshooting
                logger.debug(f"Draft list response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                    
                    # Fix content encoding issues - 更谨慎的策略
                    if 'item' in result:
                        logger.info(f"Found {len(result['item'])} drafts")
                        for i, item in enumerate(result['item']):
                            logger.debug(f"Processing draft {i+1}: {item.get('media_id', 'unknown')}")
                            if 'content' in item and 'news_item' in item['content']:
                                for news_item in item['content']['news_item']:
                                    if 'content' in news_item:
                                        # 检查是否真的需要修复
                                        original_content = news_item['content']
                                        if self._needs_encoding_fix(original_content):
                                            try:
                                                # 谨慎修复编码问题
                                                fixed_content = self._fix_encoding_carefully(original_content)
                                                if fixed_content != original_content:
                                                    news_item['content'] = fixed_content
                                                    logger.debug(f"已修复草稿 {i+1} 的编码问题")
                                                else:
                                                    logger.debug(f"草稿 {i+1} 编码正常，无需修复")
                                            except Exception as fix_error:
                                                logger.warning(f"修复草稿 {i+1} 编码时出错: {fix_error}")
                                                # 保持原始内容如果修复失败
                                                pass
                    
                    logger.info("Content encoding fix completed")
                    return result
                    
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    logger.error(f"Failed to parse JSON response from {content_type}: {e}")
                    logger.error(f"Response content: {response_text[:500]}")
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
    
    def _fix_common_encoding_issues(self, content):
        """修复常见编码问题"""
        # 修复常见的编码错误
        issues = [
            ('\\x3c', '<'),  # < 被错误编码
            ('\\x3e', '>'),  # > 被错误编码
            ('\\x22', '"'),  # " 被错误编码
            ('\\x27', "'"),  # ' 被错误编码
            ('\\x5c', '\\'),  # \ 被错误编码
        ]
        
        for wrong, right in issues:
            content = content.replace(wrong, right)
        
        return content
    
    def _needs_encoding_fix(self, content):
        """检测是否需要编码修复"""
        from ..utils.encoding import enconding_utils
        return enconding_utils.needs_encoding_fix(content)
    
    def _fix_encoding_carefully(self, content):
        """谨慎修复编码问题"""
        from ..utils.encoding import enconding_utils
        return enconding_utils.fix_encoding(content)

    # ========== Extended Media Upload Methods ==========
    
    async def upload_temp_media(self, media_path: str, media_type: str = 'image') -> str:
        """
        Upload temporary media file to WeChat server (valid for 3 days).
        
        Args:
            media_path: Path to media file (local or remote)
            media_type: Type of media ('image', 'voice', 'video', 'thumb')
            
        Returns:
            Media ID from WeChat server
        """
        return await self._upload_media(media_path, media_type, permanent=False)
    
    async def upload_permanent_material(self, media_path: str, media_type: str = 'image', 
                                       description: Optional[Dict] = None) -> str:
        """
        Upload permanent material to WeChat server.
        
        Args:
            media_path: Path to media file (local or remote)
            media_type: Type of media ('image', 'voice', 'video', 'thumb')
            description: Description for video material (required for video)
                       Format: {"title": "Video Title", "introduction": "Video Intro"}
            
        Returns:
            Media ID from WeChat server
        """
        if media_type == 'video' and not description:
            raise ValueError("Description is required for permanent video material")
        
        return await self._upload_media(media_path, media_type, permanent=True, description=description)
    
    async def upload_news_material(self, articles: List[Dict]) -> str:
        """
        Upload permanent news material (articles) to WeChat server.
        
        Args:
            articles: List of article dictionaries with keys:
                     - title: Article title
                     - content: HTML content
                     - digest: Article summary (optional)
                     - author: Article author (optional)
                     - source_url: Source URL (optional)
                     - thumb_media_id: Cover image media ID
                     - show_cover_pic: Show cover pic (0/1)
                     - need_open_comment: Enable comments (0/1)
                     - only_fans_can_comment: Only fans can comment (0/1)
            
        Returns:
            Media ID from WeChat server
        """
        access_token = await self._get_access_token()
        url = f"{self.base_url}/material/add_news?access_token={access_token}"
        
        data = {"articles": articles}
        
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                response_text = await response.text()
                
                # Debug: Log first 200 chars of response for troubleshooting
                logger.debug(f"News material upload response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "上传图文素材")
                
                if 'media_id' not in result:
                    raise Exception(f"Failed to upload news material: 缺少media_id字段")
                
                return result['media_id']
    
    async def upload_image_for_news(self, image_path: str) -> str:
        """
        Upload image specifically for use in news articles.
        This API returns a URL that can be used directly in news content.
        
        Args:
            image_path: Path to image file (local or remote)
            
        Returns:
            Image URL that can be used in news content
        """
        access_token = await self._get_access_token()
        url = f"{self.base_url}/media/uploadimg?access_token={access_token}"
        
        # Handle different media sources
        if image_path.startswith(('http://', 'https://')):
            # Download remote image first
            image_data, filename = await self._download_media(image_path)
        else:
            # Read local file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            filename = os.path.basename(image_path)
            with open(image_path, 'rb') as f:
                image_data = f.read()

        # Determine content type
        content_type = mimetypes.guess_type(filename)[0] or 'image/jpeg'
        
        # Upload to WeChat
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('media', image_data, filename=filename, content_type=content_type)
            
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                response_text = await response.text()
                
                # Debug: Log first 200 chars of response for troubleshooting
                logger.debug(f"Image upload response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "上传新闻图片")
                
                if 'url' not in result:
                    raise Exception(f"Failed to upload image for news: 缺少url字段")
                
                return result['url']
    
    async def get_media_list(self, media_type: str, permanent: bool = False, 
                           offset: int = 0, count: int = 20) -> Dict:
        """
        Get list of media materials from WeChat server.
        
        Args:
            media_type: Type of media ('image', 'voice', 'video', 'news')
            permanent: Whether to get permanent materials (True) or temporary (False)
            offset: Starting offset for pagination
            count: Number of items to retrieve
            
        Returns:
            Dictionary with material list and total count
        """
        access_token = await self._get_access_token()
        
        if permanent:
            url = f"{self.base_url}/material/batchget_material?access_token={access_token}"
            data = {
                "type": media_type,
                "offset": offset,
                "count": count
            }
        else:
            url = f"{self.base_url}/material/get_materialcount?access_token={access_token}"
            # For temporary materials, we can only get counts, not list
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP error {response.status}: {error_text}")
                    
                    return await response.json()
        
        # For permanent materials, get the actual list
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                return await response.json()
    
    async def delete_permanent_material(self, media_id: str) -> bool:
        """
        Delete permanent material from WeChat server.
        
        Args:
            media_id: Media ID of the material to delete
            
        Returns:
            True if deletion was successful
        """
        access_token = await self._get_access_token()
        url = f"{self.base_url}/material/del_material?access_token={access_token}"
        
        data = {"media_id": media_id}
        
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # 手动序列化JSON，确保中文字符不被转义
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            async with session.post(url, data=json_data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP error {response.status}: {error_text}")
                
                response_text = await response.text()
                
                # Debug: Log first 200 chars of response for troubleshooting
                logger.debug(f"Delete response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Handle API errors
                self._handle_wechat_api_error(result, "删除永久素材")
                
                return result.get('errcode') == 0