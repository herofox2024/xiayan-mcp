#!/usr/bin/env python3
"""
xiayan-mcp核心功能集成
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录和src目录到Python路径
web_backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(web_backend_dir)
src_path = os.path.join(project_root, 'src')

# 先添加src目录到Python路径，然后添加项目根目录
sys.path.insert(0, src_path)
sys.path.insert(1, project_root)

# 从src目录下的xiayan_mcp包导入
from xiayan_mcp.core.formatter import MarkdownFormatter
from xiayan_mcp.core.publisher import WeChatPublisher
from xiayan_mcp.themes.theme_manager import ThemeManager
from xiayan_mcp.utils.encoding import enconding_utils

class XiayanMCP:
    """xiayan-mcp核心功能集成类"""

    def __init__(self):
        """初始化xiayan-mcp实例"""
        self.theme_manager = ThemeManager()
        self.formatter = MarkdownFormatter()
        self.publisher = WeChatPublisher()
        self.env_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / '.env'

    async def publish_article(self, **kwargs) -> Dict:
        """发布文章到微信公众号草稿箱"""
        try:
            print("=== 开始处理文章发布 ===")
            print(f"接收的参数: {kwargs}")
            
            # 获取必要参数
            content = kwargs.get("content", "")
            theme_id = kwargs.get("theme_id", "default")
            cover = kwargs.get("cover", "")
            permanent_cover = kwargs.get("permanent_cover", False)
            author = kwargs.get("author", "Xiayan MCP")
            need_open_comment = kwargs.get("need_open_comment", 0)
            only_fans_can_comment = kwargs.get("only_fans_can_comment", 0)
            
            # 从Markdown内容中提取标题
            print("提取标题...")
            title = kwargs.get("title", "")
            if not title:
                # 从Markdown内容中提取第一个H1标题
                import re
                title_match = re.match(r'^#\s+(.+)', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    print(f"从Markdown中提取到标题: {title}")
                else:
                    title = "未命名文章"
                    print("未提取到标题，使用默认标题")
            
            print(f"标题: {title}")
            print(f"主题ID: {theme_id}")
            print(f"内容长度: {len(content)} 字符")
            
            # 1. 格式化Markdown内容为HTML
            print("1. 将Markdown转换为HTML...")
            formatted_result = self.formatter.format(content, theme_id)
            print(f"格式化结果: {list(formatted_result.keys())}")
            
            # 提取格式化后的HTML内容
            html_content = formatted_result.get("content", "")
            print(f"HTML内容长度: {len(html_content)} 字符")
            
            # 2. 应用主题样式
            print(f"2. 应用主题 '{theme_id}'...")
            # 获取主题
            theme = self.theme_manager.get_theme(theme_id)
            print(f"获取到主题: {theme.name}")
            
            # 3. 渲染最终HTML内容
            print("3. 渲染最终HTML内容...")
            from jinja2 import Template
            template = Template(theme.template)
            final_content = template.render(
                content=html_content,
                css_styles=theme.css_styles
            )
            print(f"最终内容长度: {len(final_content)} 字符")
            
            # 4. 调用publisher的publish_to_draft方法发布到草稿箱
            print("4. 发布到微信公众号草稿箱...")
            result = await self.publisher.publish_to_draft(
                title=title,
                content=final_content,
                cover=cover,
                permanent_cover=permanent_cover,
                author=author,
                need_open_comment=need_open_comment,
                only_fans_can_comment=only_fans_can_comment
            )
            print(f"发布结果: {result}")
            
            return {
                "message": "文章已成功发布到微信公众号草稿箱",
                "media_id": result.get("media_id"),
                "cover_media_id": result.get("cover_media_id")
            }
        except Exception as e:
            print(f"发布文章失败: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            raise Exception(f"发布文章失败: {str(e)}")

    async def list_themes(self, detailed: bool = False) -> List[Dict]:
        """获取所有可用主题"""
        try:
            # 调试信息
            print(f"list_themes方法调用，detailed={detailed}")
            print(f"theme_manager: {self.theme_manager}")
            print(f"theme_manager._themes: {self.theme_manager._themes}")
            print(f"theme_manager._themes类型: {type(self.theme_manager._themes)}")
            
            if detailed:
                themes = self.theme_manager.get_available_themes()
                print(f"detailed=True时，themes: {themes}")
            else:
                # 简化主题信息
                themes = []
                for theme_id, theme in self.theme_manager._themes.items():
                    print(f"处理主题: {theme_id}, {theme.name}")
                    themes.append({
                        "id": theme.id,
                        "name": theme.name,
                        "description": theme.description
                    })
                print(f"detailed=False时，themes: {themes}")
                print(f"themes类型: {type(themes)}")
            
            return themes
        except Exception as e:
            print(f"list_themes方法异常: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"获取主题列表失败: {str(e)}")

    async def preview_theme(self, theme_id: str, sample_content: Optional[str] = None) -> str:
        """预览主题效果"""
        try:
            return self.theme_manager.get_theme_preview(theme_id, sample_content)
        except Exception as e:
            raise Exception(f"预览主题失败: {str(e)}")

    async def add_custom_theme(self, **kwargs) -> str:
        """添加自定义主题"""
        try:
            from src.xiayan_mcp.themes.theme import Theme
            
            custom_theme = Theme(
                id=kwargs.get("id"),
                name=kwargs.get("name"),
                description=kwargs.get("description"),
                template=kwargs.get("template", self.theme_manager._get_default_template()),
                css_styles=kwargs.get("css_styles", "")
            )
            
            self.theme_manager.add_custom_theme(custom_theme)
            return f"主题 '{kwargs.get('id')}' 添加成功"
        except Exception as e:
            raise Exception(f"添加主题失败: {str(e)}")

    async def update_theme(self, **kwargs) -> str:
        """更新现有主题"""
        try:
            updated_theme = self.theme_manager.update_theme(
                theme_id=kwargs.get("theme_id"),
                name=kwargs.get("name"),
                description=kwargs.get("description"),
                template=kwargs.get("template"),
                css_styles=kwargs.get("css_styles")
            )
            return f"主题 '{kwargs.get('theme_id')}' 更新成功"
        except Exception as e:
            raise Exception(f"更新主题失败: {str(e)}")

    async def upload_temp_media(self, **kwargs) -> str:
        """上传临时媒体文件"""
        try:
            media_id = await self.publisher.upload_temp_media(
                media_path=kwargs.get("media_path"),
                media_type=kwargs.get("media_type", "image")
            )
            return media_id
        except Exception as e:
            raise Exception(f"上传临时媒体失败: {str(e)}")

    async def upload_permanent_material(self, **kwargs) -> str:
        """上传永久媒体素材"""
        try:
            media_id = await self.publisher.upload_permanent_material(
                media_path=kwargs.get("media_path"),
                media_type=kwargs.get("media_type", "image"),
                description=kwargs.get("description")
            )
            return media_id
        except Exception as e:
            raise Exception(f"上传永久媒体素材失败: {str(e)}")

    async def upload_image_for_news(self, **kwargs) -> str:
        """上传新闻图片"""
        try:
            image_url = await self.publisher.upload_image_for_news(
                image_path=kwargs.get("image_path")
            )
            return image_url
        except Exception as e:
            raise Exception(f"上传新闻图片失败: {str(e)}")

    async def get_media_list(self, **kwargs) -> Dict:
        """获取媒体素材列表"""
        try:
            result = await self.publisher.get_media_list(
                media_type=kwargs.get("media_type", "image"),
                permanent=kwargs.get("permanent", True),
                offset=kwargs.get("offset", 0),
                count=kwargs.get("count", 20)
            )
            return result
        except Exception as e:
            raise Exception(f"获取媒体列表失败: {str(e)}")

    async def upload_cover_image(self, **kwargs) -> str:
        """上传封面图片"""
        try:
            media_id = await self.publisher.upload_cover_image(
                image_path=kwargs.get("image_path")
            )
            return media_id
        except Exception as e:
            raise Exception(f"上传封面图片失败: {str(e)}")

    async def delete_permanent_material(self, **kwargs) -> str:
        """删除永久媒体素材"""
        try:
            success = await self.publisher.delete_permanent_material(
                media_id=kwargs.get("media_id")
            )
            if success:
                return f"永久素材 {kwargs.get('media_id')} 删除成功"
            else:
                return f"永久素材 {kwargs.get('media_id')} 删除失败"
        except Exception as e:
            raise Exception(f"删除永久媒体素材失败: {str(e)}")

    async def get_credentials(self) -> Dict:
        """获取当前微信凭证信息"""
        try:
            app_id = os.getenv('WECHAT_APP_ID', '')
            app_secret = os.getenv('WECHAT_APP_SECRET', '')
            configured = bool(app_id and app_secret)
            return {
                "app_id": app_id,
                "app_secret": "***" if app_secret else "",
                "configured": configured,
                "message": "微信凭证已配置" if configured else "微信凭证未配置"
            }
        except Exception as e:
            raise Exception(f"获取凭证信息失败: {str(e)}")

    async def update_credentials(self, **kwargs) -> Dict:
        """更新微信凭证信息"""
        try:
            app_id = kwargs.get("app_id")
            app_secret = kwargs.get("app_secret")
            save_to_env = kwargs.get("save_to_env", True)
            
            # 设置环境变量
            os.environ['WECHAT_APP_ID'] = app_id
            os.environ['WECHAT_APP_SECRET'] = app_secret
            
            if save_to_env:
                # 保存到.env文件
                env_content = []
                if self.env_path.exists():
                    with open(self.env_path, 'r', encoding='utf-8') as f:
                        env_content = f.readlines()
                
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
                
                with open(self.env_path, 'w', encoding='utf-8') as f:
                    f.writelines(env_content)
            
            return {
                "app_id": app_id,
                "app_secret": "***",
                "configured": True,
                "message": "微信凭证已更新成功"
            }
        except Exception as e:
            raise Exception(f"更新凭证信息失败: {str(e)}")
