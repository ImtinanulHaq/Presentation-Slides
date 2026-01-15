"""
Base Template Class for Presentation Templates
All templates inherit from this class to ensure consistency and compatibility
"""


class PresentationTemplate:
    """
    Base class for all presentation templates
    Defines the structure and required properties for templates
    """
    
    def __init__(self):
        self.name = None
        self.description = None
        self.version = "1.0"
        
        # Color Palette (all in hex format)
        self.colors = {
            'primary_background': None,  # Main background color
            'secondary_background': None,  # Alternate background
            'primary_text': None,  # Main heading text
            'secondary_text': None,  # Body text
            'accent_text': None,  # Highlighted/callout text
            'accent_color': None,  # For bullets, decorative elements
            'accent_secondary': None,  # Secondary accent
        }
        
        # Font Configuration
        self.fonts = {
            'heading_font': None,  # Font family for titles
            'heading_size': None,  # Title font size (pt)
            'heading_weight': None,  # Bold, SemiBold, etc.
            'heading_color': None,  # Heading color key
            
            'body_font': None,  # Font family for body text
            'body_size': None,  # Body font size (pt)
            'body_weight': None,  # Regular, Medium, etc.
            'body_color': None,  # Body text color key
            
            'bullet_font': None,  # Font for bullets
            'bullet_size': None,  # Bullet font size (pt)
            'bullet_color': None,  # Bullet color key
        }
        
        # Layout Configuration
        self.layout = {
            'slide_ratio': '16:9',  # Aspect ratio
            'default_margin': 24,  # Default margin in pixels
            'title_margin_top': 36,  # Title top margin
            'content_margin_top': 60,  # Content area top margin
            'content_height': 360,  # Content box height
        }
        
        # Text Styling
        self.text_styling = {
            'heading_line_spacing': 1.1,
            'heading_letter_spacing': 0.03,  # 3% letter spacing
            'body_line_spacing': 1.5,
            'body_paragraph_spacing': 10,
            'bullet_line_spacing': 1.4,
            'bullet_indent': 16,
        }
        
        # Bullet Point Configuration
        self.bullets = {
            'style': 'solid_circle',  # Type of bullet
            'level_1_color': None,  # Level 1 bullet color
            'level_2_color': None,  # Level 2 bullet color (with opacity)
            'level_2_opacity': 0.8,  # 80% opacity for level 2
        }
        
        # Visual Elements
        self.visual = {
            'use_gradients': False,  # Use gradient backgrounds
            'gradient_1': None,  # First gradient color
            'gradient_2': None,  # Second gradient color
            'gradient_direction': 'diagonal',  # horizontal, vertical, diagonal
            'border_radius': 8,  # Rounded corner radius
            'shadow_enabled': False,  # Use drop shadows
        }
    
    def apply_to_slide(self, prs, slide, slide_type='content'):
        """
        Apply template settings to a slide
        Override in subclass for specific implementations
        
        Args:
            prs: PPTX Presentation object
            slide: Slide object
            slide_type: Type of slide ('title', 'section', 'content')
        """
        raise NotImplementedError("Subclasses must implement apply_to_slide()")
    
    def get_title_formatting(self):
        """Get title formatting as dictionary"""
        return {
            'font_name': self.fonts['heading_font'],
            'font_size': self.fonts['heading_size'],
            'font_bold': self.fonts['heading_weight'] in ['Bold', 'SemiBold'],
            'font_color': self.colors[self.fonts['heading_color']],
            'line_spacing': self.text_styling['heading_line_spacing'],
            'letter_spacing': self.text_styling['heading_letter_spacing'],
        }
    
    def get_body_formatting(self):
        """Get body text formatting as dictionary"""
        return {
            'font_name': self.fonts['body_font'],
            'font_size': self.fonts['body_size'],
            'font_bold': self.fonts['body_weight'] in ['Bold', 'SemiBold'],
            'font_color': self.colors[self.fonts['body_color']],
            'line_spacing': self.text_styling['body_line_spacing'],
            'paragraph_spacing': self.text_styling['body_paragraph_spacing'],
        }
    
    def get_bullet_formatting(self):
        """Get bullet formatting as dictionary"""
        return {
            'font_name': self.fonts['bullet_font'],
            'font_size': self.fonts['bullet_size'],
            'font_color': self.colors[self.fonts['bullet_color']],
            'bullet_style': self.bullets['style'],
            'bullet_color': self.colors[self.bullets['level_1_color']],
            'line_spacing': self.text_styling['bullet_line_spacing'],
        }
    
    def validate(self):
        """Validate that all required template properties are set"""
        errors = []
        
        # Check colors
        required_colors = [
            'primary_background', 'secondary_background',
            'primary_text', 'secondary_text', 'accent_text'
        ]
        for color in required_colors:
            if not self.colors.get(color):
                errors.append(f"Missing color: {color}")
        
        # Check fonts
        required_fonts = [
            'heading_font', 'heading_size', 'body_font', 'body_size'
        ]
        for font in required_fonts:
            if not self.fonts.get(font):
                errors.append(f"Missing font: {font}")
        
        if errors:
            raise ValueError(f"Template validation failed:\n" + "\n".join(errors))
        
        return True
