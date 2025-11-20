"""Theme class for styling markdown content."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Theme:
    """Theme definition for markdown styling."""
    
    id: str
    name: str
    description: str
    template: str
    css_styles: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.template is None:
            self.template = self._default_template()
    
    def _default_template(self) -> str:
        """Default HTML template for WeChat articles."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WeChat Article</title>
    {% if css_styles %}
    <style>
        {{ css_styles|safe }}
    </style>
    {% endif %}
</head>
<body>
    <div class="article-container">
        {{ content|safe }}
    </div>
</body>
</html>
        """