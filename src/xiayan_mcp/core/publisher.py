"""WeChat Official Account publisher."""

import os
import asyncio
from typing import Dict, Optional, List, Union, Tuple
import aiohttp
import json
import mimetypes
import tempfile


class WeChatPublisher:
    """Publisher for WeChat Official Account."""

    def __init__(self):
        """Initialize the publisher with WeChat API credentials."""
        self.app_id = os.getenv('WECHAT_APP_ID', '')
        self.app_secret = os.getenv('WECHAT_APP_SECRET', '')
        self.base_url = 'https://api.weixin.qq.com/cgi-bin'
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[int] = None

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
                    
                    # Debug: Print response for troubleshooting
                    print(f"DEBUG: Token response: {response_text[:200]}")
                    
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        content_type = response.headers.get('content-type', '')
                        raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                    
                    if 'access_token' not in data:
                        error_msg = data.get('errmsg', 'Unknown error')
                        errcode = data.get('errcode', 'unknown')
                        raise Exception(f"Failed to get access token: {error_msg} (code: {errcode})")
                    
                    self.access_token = data['access_token']
                    expires_in = data.get('expires_in', 7200)
                    self.token_expires_at = time.time() + expires_in - 300  # Refresh 5 minutes before expiry
                    return self.access_token
                    
        except Exception as e:
            # If the old API fails, try the new stable access token API
            print("Falling back to stable access token API...")
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
                
                # Debug: Print response for troubleshooting
                print(f"DEBUG: Stable token response: {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Failed to get stable access token: {error_msg} (code: {result['errcode']})")
                
                if 'access_token' not in result or 'expires_in' not in result:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Invalid response from stable token API: {error_msg}")
                
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
            print("Warning: PIL not available, cannot resize image. Install Pillow for image resizing.")
            return image_path
        except Exception as e:
            print(f"Error resizing image: {e}")
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
                    
                    # Debug: Print first 200 chars of response for troubleshooting
                    print(f"DEBUG: Upload response (first 200 chars): {response_text[:200]}")
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        content_type = response.headers.get('content-type', '')
                        raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                    
                    # Check if response contains an error
                    if 'errcode' in result and result['errcode'] != 0:
                        error_msg = result.get('errmsg', 'Unknown error')
                        raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                    
                    if 'media_id' not in result:
                        error_msg = result.get('errmsg', 'Unknown error')
                        raise Exception(f"Failed to upload media: {error_msg}")
                    
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
                
                # Debug: Print first 200 chars of response for troubleshooting
                print(f"DEBUG: Response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                
                if 'media_id' not in result:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Failed to add draft: {error_msg}")
                
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
                
                # Debug: Print first 200 chars of response for troubleshooting
                print(f"DEBUG: Response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    content_type = response.headers.get('content-type', '')
                    raise Exception(f"Failed to parse JSON response from {content_type}: {e}\nResponse content: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                
                if 'media_id' not in result:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Failed to add draft: {error_msg}")
                
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
            # Upload cover image if provided
            cover_media_id = ''
            if cover:
                # Always upload cover as permanent thumb material
                # This ensures it's available for future use and meets WeChat requirements
                cover_media_id = await self.upload_permanent_material(cover, 'thumb')
            elif self._extract_first_image(content):
                # Use first image in content as cover if no cover specified
                first_image = self._extract_first_image(content)
                cover_media_id = await self.upload_permanent_material(first_image, 'thumb')
            else:
                # Create a default cover if no image provided (WeChat API requires thumb_media_id)
                cover_media_id = await self._create_default_cover()

            # Add as draft using new API
            media_id = await self._add_draft_with_options(
                title, content, cover_media_id, author, 
                need_open_comment, only_fans_can_comment
            )
            
            return {
                'media_id': media_id,
                'title': title,
                'status': 'success',
                'cover_media_id': cover_media_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to publish to draft: {str(e)}")

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
        if not content:
            return False
        
        # 检测常见的编码问题
        encoding_issues = [
            r'\\x[0-9a-fA-F]{2}',      # 十六进制编码如 \\x3c
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
    
    def _fix_encoding_carefully(self, content):
        """谨慎修复编码问题"""
        if not content or not isinstance(content, str):
            return content
        
        try:
            logger.debug(f"开始谨慎修复编码，内容长度: {len(content)}")
            
            # 修复十六进制编码错误（如 \\x3c -> <）
            content = re.sub(r'\\x3c', '<', content)
            content = re.sub(r'\\x3e', '>', content)
            content = re.sub(r'\\x22', '"', content)
            content = re.sub(r'\\x27', "'", content)
            content = re.sub(r'\\x5c', '\\\\', content)
            
            # 处理双反斜杠Unicode转义（如 \\\\u4e2d -> \\u4e2d）
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
            
            logger.debug(f"谨慎修复编码完成，内容长度: {len(content)}")
            return content
            
        except Exception as e:
            logger.warning(f"谨慎修复编码时出错: {e}")
            return content

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
                
                # Debug: Print first 200 chars of response for troubleshooting
                print(f"DEBUG: News material upload response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                
                if 'media_id' not in result:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Failed to upload news material: {error_msg}")
                
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
                
                # Debug: Print first 200 chars of response for troubleshooting
                print(f"DEBUG: Image upload response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                
                if 'url' not in result:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"Failed to upload image for news: {error_msg}")
                
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
                
                # Debug: Print first 200 chars of response for troubleshooting
                print(f"DEBUG: Delete response (first 200 chars): {response_text[:200]}")
                
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
                
                # Check if response contains an error
                if 'errcode' in result and result['errcode'] != 0:
                    error_msg = result.get('errmsg', 'Unknown error')
                    raise Exception(f"API error: {error_msg} (code: {result['errcode']})")
                
                return result.get('errcode') == 0