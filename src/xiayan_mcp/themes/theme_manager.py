"""Theme manager for handling multiple themes."""

from typing import Dict, List

from .theme import Theme


class ThemeManager:
    """Manager for available themes."""

    def __init__(self):
        """Initialize theme manager with built-in themes."""
        self._themes = self._load_builtin_themes()

    def _load_builtin_themes(self) -> Dict[str, Theme]:
        """Load built-in themes."""
        themes = {
            "default": Theme(
                id="default",
                name="默认主题",
                description="简洁大方的默认主题",
                template=self._get_default_template(),
                css_styles=self._get_default_css()
            ),
            "orangeheart": Theme(
                id="orangeheart", 
                name="Orange Heart",
                description="温暖橙心主题，基于Typora的Orange Heart主题",
                template=self._get_default_template(),
                css_styles=self._get_orangeheart_css()
            ),
            "rainbow": Theme(
                id="rainbow",
                name="Rainbow", 
                description="彩虹主题，基于Typora的Rainbow主题",
                template=self._get_default_template(),
                css_styles=self._get_rainbow_css()
            ),
            "lapis": Theme(
                id="lapis",
                name="Lapis",
                description="青金石主题，基于Typora的Lapis主题", 
                template=self._get_default_template(),
                css_styles=self._get_lapis_css()
            ),
            "pie": Theme(
                id="pie",
                name="Pie",
                description="派主题，基于Typora的Pie主题",
                template=self._get_default_template(),
                css_styles=self._get_pie_css()
            ),
            "maize": Theme(
                id="maize", 
                name="Maize",
                description="玉米主题，基于Typora的Maize主题",
                template=self._get_default_template(),
                css_styles=self._get_maize_css()
            ),
            "purple": Theme(
                id="purple",
                name="Purple",
                description="紫色主题，基于Typora的Purple主题",
                template=self._get_default_template(),
                css_styles=self._get_purple_css()
            ),
            "phycat": Theme(
                id="phycat",
                name="物理猫薄荷",
                description="物理猫薄荷主题，清新自然",
                template=self._get_default_template(),
                css_styles=self._get_phycat_css()
            )
        }
        return themes

    def get_theme(self, theme_id: str) -> Theme:
        """Get theme by ID."""
        theme = self._themes.get(theme_id)
        if not theme:
            return self._themes["default"]
        return theme

    def get_available_themes(self) -> List[Dict]:
        """Get list of all available themes with detailed information."""
        return [{
            'id': theme.id,
            'name': theme.name,
            'description': theme.description,
            'has_custom_template': theme.template != self._get_default_template(),
            'has_custom_css': bool(theme.css_styles and theme.css_styles != self._get_default_css())
        } for theme in self._themes.values()]
    
    def get_theme_preview(self, theme_id: str, sample_content: str = "") -> str:
        """
        Get HTML preview of a theme with sample content.
        
        Args:
            theme_id: ID of the theme to preview
            sample_content: Optional sample content to use for preview
            
        Returns:
            HTML preview of the theme
        """
        theme = self.get_theme(theme_id)
        
        if not sample_content:
            sample_content = self._get_default_sample_content()
        
        # Render theme template with sample content
        from jinja2 import Template
        template = Template(theme.template)
        
        return template.render(
            content=sample_content,
            css_styles=self._combine_styles(theme.css_styles or "")
        )
    
    def add_custom_theme(self, theme: Theme) -> None:
        """
        Add a custom theme to the theme manager.
        
        Args:
            theme: Theme object to add
        """
        self._themes[theme.id] = theme
    
    def update_theme(self, theme_id: str, **kwargs) -> Theme:
        """
        Update an existing theme with new properties.
        
        Args:
            theme_id: ID of the theme to update
            **kwargs: Theme properties to update
            
        Returns:
            Updated Theme object
        """
        theme = self.get_theme(theme_id)
        
        # Create a new theme with updated properties
        updated_theme = Theme(
            id=theme.id,
            name=kwargs.get('name', theme.name),
            description=kwargs.get('description', theme.description),
            template=kwargs.get('template', theme.template),
            css_styles=kwargs.get('css_styles', theme.css_styles)
        )
        
        self._themes[theme_id] = updated_theme
        return updated_theme
    
    def _get_default_sample_content(self) -> str:
        """Get default sample content for theme preview."""
        return """
<h1>主题预览示例</h1>

<p>这是一个主题预览的示例内容，用于展示不同主题的样式效果。</p>

<h2>二级标题</h2>

<p>这是一段正文内容，包含一些 <strong>粗体文本</strong> 和 <em>斜体文本</em>。</p>

<h3>三级标题</h3>

<ul>
    <li>列表项 1</li>
    <li>列表项 2</li>
    <li>列表项 3</li>
</ul>

<ol>
    <li>有序列表项 1</li>
    <li>有序列表项 2</li>
    <li>有序列表项 3</li>
</ol>

<blockquote>
    这是一段引用文本，用于展示引用样式。
</blockquote>

<pre><code>这是一段代码块，用于展示代码样式。
print("Hello, World!")
</code></pre>

<p>以上是主题预览的全部内容。</p>
        """
    
    def _combine_styles(self, theme_css: str) -> str:
        """Combine default styles with theme-specific styles."""
        default_css = self._get_default_css()
        if theme_css:
            return f"{default_css}\n\n{theme_css}"
        return default_css

    def _get_default_template(self) -> str:
        """Get default HTML template."""
        return """
<section class="article-content" style="font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 100%; margin: 0; padding: 20px; text-align: justify;">
    {{ content|safe }}
</section>
        """

    def _get_default_css(self) -> str:
        """Get default CSS styles."""
        return """
/* 优化微信公众号显示样式 */
.article-content {
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Roboto, sans-serif;
    line-height: 1.8;
    color: #333;
    text-align: justify;
    font-size: 16px;
}

.article-content h1, .article-content h2, .article-content h3, 
.article-content h4, .article-content h5, .article-content h6 {
    margin: 1.5em 0 0.8em 0;
    font-weight: bold;
    line-height: 1.4;
    color: #222;
}

.article-content h1 { font-size: 24px; text-align: center; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.article-content h2 { font-size: 20px; }
.article-content h3 { font-size: 18px; }

.article-content p {
    margin-bottom: 1.2em;
    text-indent: 2em;
    line-height: 1.8;
}

.article-content ul, .article-content ol {
    margin: 1em 0;
    padding-left: 2.5em;
}

.article-content li {
    margin-bottom: 0.6em;
    line-height: 1.8;
}

.article-content img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5em auto;
    border-radius: 4px;
}

.article-content blockquote {
    margin: 1.5em 0;
    padding: 15px 20px;
    border-left: 4px solid #ddd;
    background-color: #f9f9f9;
    color: #666;
    font-style: italic;
}

.article-content code {
    background-color: #f4f4f4;
    padding: 3px 6px;
    border-radius: 3px;
    font-family: "Monaco", "Consolas", monospace;
    font-size: 14px;
}

.article-content pre {
    background-color: #f4f4f4;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    margin: 1em 0;
}

.article-content strong {
    font-weight: bold;
    color: #333;
}

.article-content em {
    font-style: italic;
    color: #555;
}
        """

    def _get_orangeheart_css(self) -> str:
        """Get Orange Heart theme CSS."""
        return """
.article-content {
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    color: #2c3e50;
    line-height: 1.8;
}

.article-content h1 { color: #e67e22; border-bottom: 2px solid #e67e22; }
.article-content h2 { color: #d35400; }
.article-content h3 { color: #e67e22; }
.article-content blockquote {
    background: linear-gradient(90deg, #fff5f0 0%, #fff 100%);
    border-left: 4px solid #e67e22;
}
        """

    def _get_rainbow_css(self) -> str:
        """Get Rainbow theme CSS."""
        return """
.article-content {
    font-family: "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 10px;
}

.article-content h1 { color: #ffd89b; }
.article-content h2 { color: #f9ca24; }
.article-content h3 { color: #f0932b; }
        """

    def _get_lapis_css(self) -> str:
        """Get Lapis theme CSS."""
        return """
.article-content {
    font-family: "SF Pro Display", -apple-system, sans-serif;
    color: #2c3e50;
}

.article-content h1 { color: #3498db; }
.article-content h2 { color: #2980b9; }
.article-content blockquote {
    background-color: #ecf0f1;
    border-left: 4px solid #3498db;
    padding: 15px;
}
        """

    def _get_pie_css(self) -> str:
        """Get Pie theme CSS."""
        return """
.article-content {
    font-family: "Georgia", serif;
    color: #34495e;
}

.article-content h1 { color: #8e44ad; }
.article-content h2 { color: #9b59b6; }
.article-content blockquote {
    font-style: italic;
    background: #f8f9fa;
    border-left: 3px solid #8e44ad;
}
        """

    def _get_maize_css(self) -> str:
        """Get Maize theme CSS."""
        return """
.article-content {
    font-family: "Ubuntu", sans-serif;
    color: #2c3e50;
}

.article-content h1 { color: #f39c12; }
.article-content h2 { color: #e67e22; }
.article-content blockquote {
    background-color: #fef9e7;
    border-left: 4px solid #f39c12;
}
        """

    def _get_purple_css(self) -> str:
        """Get Purple theme CSS."""
        return """
.article-content {
    font-family: "Avenir", "Helvetica Neue", sans-serif;
    color: #2c3e50;
}

.article-content h1 { color: #8e44ad; }
.article-content h2 { color: #9b59b6; }
.article-content h3 { color: #a569bd; }
.article-content blockquote {
    background: linear-gradient(90deg, #f4f3ff 0%, #fff 100%);
    border-left: 4px solid #8e44ad;
}
        """

    def _get_phycat_css(self) -> str:
        """Get PhyCat theme CSS."""
        return """
.article-content {
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    color: #27ae60;
    line-height: 1.7;
}

.article-content h1 { color: #16a085; }
.article-content h2 { color: #1abc9c; }
.article-content blockquote {
    background-color: #e8f5e8;
    border-left: 4px solid #27ae60;
    padding: 12px 20px;
}

.article-content code {
    background-color: #f0fff0;
    border: 1px solid #d5f4e6;
}
        """