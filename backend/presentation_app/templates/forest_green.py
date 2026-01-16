"""
Forest Green Template - Earthy Gradient Design
Natural template with forest green gradient backgrounds
Designed for environmental and sustainability presentations
"""

from .template_base import PresentationTemplate


class ForestGreenTemplate(PresentationTemplate):
    """
    Forest Green: Earthy green gradient backgrounds
    
    Design Features:
    - Title slide: Forest green gradient background (#1B4332 → #2D6A4F), centered white text
    - Content slides: White background with dark text centered in middle
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Forest Green"
        self.description = "Natural template with forest green gradient title slide"
        self.version = "1.0"
        
        # ========== COLOR PALETTE ==========
        self.colors = {
            # Gradient colors for title slide
            'gradient_start': '#1B4332',      # Forest green start
            'gradient_end': '#2D6A4F',        # Forest green end
            'gradient_mid': '#245038',        # Mid gradient color
            
            # PPTX Generator Required Keys
            'primary_background': '#1B4332',  # Forest green
            'secondary_background': '#2D6A4F',
            'primary_text': '#1A1A1A',        # Dark gray
            'secondary_text': '#4A4A4A',      # Light gray
            'accent_color_dark': '#1B4332',   # Forest green
            'accent_color_light': '#52B788',  # Light green
            'white': '#FFFFFF',               # Pure white
            
            # Text colors
            'title_slide_text': '#FFFFFF',    # White
            'content_slide_text': '#1A1A1A',  # Dark gray
            'content_subtitle': '#4A4A4A',    # Light gray
            
            # Backgrounds
            'content_bg': '#FFFFFF',          # White
            'secondary_bg': '#F5F5F5',        # Light gray
        }
        
        # ========== TYPOGRAPHY ==========
        self.fonts = {
            'heading_font': 'Segoe UI',
            'heading_size': 44,
            'heading_weight': 'Bold',
            'heading_color': 'title_slide_text',
            'heading_line_spacing': 1.3,
            
            'body_font': 'Segoe UI',
            'body_size': 18,
            'body_weight': 'Regular',
            'body_color': 'content_slide_text',
            'body_line_spacing': 1.6,
            
            'bullet_font': 'Segoe UI',
            'bullet_size': 18,
            'bullet_color': 'bullet_color',
            'bullet_indent': 20,
            'content_heading_size': 40,
        }
        
        # ========== LAYOUT ==========
        self.layout = {
            'slide_ratio': '16:9',
            'slide_width': 10,
            'slide_height': 7.5,
            'default_margin': 24,
        }
        
        # ========== TEXT STYLING ==========
        self.text_styling = {
            'heading_line_spacing': 1.3,
            'heading_letter_spacing': 0.01,
            'body_line_spacing': 1.6,
            'body_paragraph_spacing': 12,
            'bullet_line_spacing': 1.4,
            'bullet_spacing': 8,
        }
        
        # ========== BULLETS ==========
        self.bullets = {
            'style': 'solid_circle',
            'level_1_color': '#1B4332',
            'level_2_color': '#52B788',
            'level_2_opacity': 0.7,
        }
        
        # ========== VISUAL ==========
        self.visual = {
            'use_gradients': True,
            'gradient_1': '#1B4332',
            'gradient_2': '#2D6A4F',
            'gradient_direction': 'diagonal',
            'border_radius': 0,
            'shadow_enabled': False,
        }
