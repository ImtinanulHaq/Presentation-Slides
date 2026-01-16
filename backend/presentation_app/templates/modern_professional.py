"""
Modern Professional Template - Sleek Gradient Design
A contemporary, sophisticated template with gradient backgrounds
Designed for impactful, professional presentations
"""

from .template_base import PresentationTemplate
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


class ModernProfessionalTemplate(PresentationTemplate):
    """
    Modern Professional: Sleek template with gradient backgrounds
    
    Design Features:
    - Title slide: Purple/Blue gradient background, centered white text
    - Content slides: Clean white background with bold titles
    - Consistent typography and professional styling
    - Minimalist bullet points with clear hierarchy
    
    Color Palette:
    - Gradient: #6B5BA3 to #8B6BB6 (purple shades)
    - Text: #FFFFFF (white) on title slide
    - Text: #1A1A1A (dark gray) on content slides
    - Accents: #7B68EE (medium slate blue)
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Modern Professional"
        self.description = "Sleek template with gradient title slide and clean content layout"
        self.version = "1.0"
        
        # ========== COLOR PALETTE ==========
        self.colors = {
            # Gradient colors for title slide
            'gradient_start': '#6B5BA3',  # Purple gradient start
            'gradient_end': '#8B6BB6',  # Purple gradient end
            'gradient_mid': '#7A6BAA',  # Mid gradient color
            
            # Text colors
            'title_slide_text': '#FFFFFF',  # White text on title slide
            'content_slide_text': '#1A1A1A',  # Dark text on content slides
            'content_subtitle': '#4A4A4A',  # Gray subtitle text
            
            # Accents
            'accent_color': '#7B68EE',  # Medium slate blue
            'accent_light': '#9B88EE',  # Lighter accent
            'bullet_color': '#1A1A1A',  # Dark for bullets
            
            # Backgrounds
            'content_bg': '#FFFFFF',  # White background for content
            'secondary_bg': '#F5F5F5',  # Light gray for alternates
        }
        
        # ========== TYPOGRAPHY CONFIGURATION ==========
        self.fonts = {
            # Title Slide Heading
            'heading_font': 'Segoe UI',  # Clean, professional font
            'heading_size': 44,  # 44pt for title slide
            'heading_weight': 'Bold',  # Bold and impactful
            'heading_color': 'title_slide_text',  # White (#FFFFFF)
            'heading_line_spacing': 1.3,  # 1.3 for readability
            'heading_letter_spacing': 0.01,  # 1% letter spacing
            
            # Subtitle (for title slide)
            'subtitle_size': 24,  # 24pt for subtitle
            'subtitle_weight': 'Regular',
            'subtitle_color': 'title_slide_text',  # White
            
            # Content Slide Heading
            'content_heading_size': 40,  # 40pt for content titles
            'content_heading_color': 'content_slide_text',  # Dark gray (#1A1A1A)
            'content_heading_weight': 'Bold',
            
            # Body Text Configuration
            'body_font': 'Segoe UI',  # Clean, consistent font
            'body_size': 18,  # 18pt for body text
            'body_weight': 'Regular',  # Easy to read
            'body_color': 'content_slide_text',  # Dark gray (#1A1A1A)
            'body_line_spacing': 1.6,  # Generous for readability
            
            # Bullet Configuration
            'bullet_font': 'Segoe UI',  # Same as body
            'bullet_size': 18,  # 18pt for bullets
            'bullet_color': 'bullet_color',  # Dark gray
            'bullet_indent': 20,  # 20px indent
        }
        
        # ========== LAYOUT CONFIGURATION ==========
        self.layout = {
            'slide_ratio': '16:9',  # Standard widescreen
            'slide_width': 10,  # inches
            'slide_height': 7.5,  # inches
            'default_margin': 24,  # 24px margin
            
            # Title Slide Layout
            'title_slide_margin_top': 2.5,  # Inches from top
            'title_slide_width': 8,  # Inches width for title
            
            # Content Slide Layout
            'content_margin_left': 0.75,  # 0.75" from left
            'content_margin_right': 0.75,  # 0.75" from right
            'content_margin_top': 0.75,  # 0.75" from top
            'content_margin_bottom': 0.5,  # 0.5" from bottom
            'title_margin_bottom': 0.4,  # Space below title on content slides
        }
        
        # ========== TEXT STYLING ==========
        self.text_styling = {
            'heading_line_spacing': 1.3,
            'heading_letter_spacing': 0.01,
            'body_line_spacing': 1.6,
            'body_paragraph_spacing': 12,  # 12px between paragraphs
            'bullet_line_spacing': 1.4,
            'bullet_spacing': 8,  # Space between bullets
        }
        
        # ========== VISUAL ELEMENTS ==========
        self.visual = {
            'use_gradients': True,  # Use gradient on title slide
            'gradient_1': '#6B5BA3',  # Purple start
            'gradient_2': '#8B6BB6',  # Purple end
            'gradient_direction': 'diagonal',  # Diagonal gradient
            'border_radius': 0,  # No rounded corners
            'shadow_enabled': False,  # No shadows
        }
        
        # ========== BULLET CONFIGURATION ==========
        self.bullets = {
            'style': 'solid_circle',  # Solid circle bullets
            'level_1_color': '#7B68EE',  # Medium slate blue
            'level_2_color': '#9B88EE',  # Lighter accent with opacity
            'level_2_opacity': 0.7,  # 70% opacity for level 2
        }
    
    def apply_to_slide(self, prs, slide, slide_type='content'):
        """
        Apply Modern Professional template to slide
        
        Args:
            prs: PPTX Presentation object
            slide: Slide object
            slide_type: Type of slide ('title', 'content')
        """
        if slide_type == 'title':
            self._apply_title_slide(prs, slide)
        elif slide_type == 'content':
            self._apply_content_slide(prs, slide)
    
    def _apply_title_slide(self, prs, slide):
        """Apply gradient background and centered text to title slide"""
        # Set background to gradient
        background = slide.background
        fill = background.fill
        fill.gradient()
        fill.gradient_angle = 45.0  # Diagonal gradient
        
        # Set gradient colors (purple gradient)
        fill.gradient_stops[0].color.rgb = RGBColor(0x6B, 0x5B, 0xA3)  # #6B5BA3
        fill.gradient_stops[1].color.rgb = RGBColor(0x8B, 0x6B, 0xB6)  # #8B6BB6
    
    def _apply_content_slide(self, prs, slide):
        """Apply white background with clean layout to content slide"""
        # Set background to solid white
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)  # White
    
    def get_title_formatting(self):
        """Get title formatting for slides"""
        return {
            'font_name': self.fonts['heading_font'],
            'font_size': self.fonts['heading_size'],
            'font_bold': True,
            'font_color': self.colors['content_slide_text'],
            'alignment': PP_ALIGN.CENTER,
        }
    
    def get_bullet_formatting(self):
        """Get bullet formatting"""
        return {
            'font_name': self.fonts['bullet_font'],
            'font_size': self.fonts['bullet_size'],
            'font_color': self.colors['bullet_color'],
            'bullet_color': self.colors['accent_color'],
        }
    
    def get_body_formatting(self):
        """Get body text formatting"""
        return {
            'font_name': self.fonts['body_font'],
            'font_size': self.fonts['body_size'],
            'font_color': self.colors['content_slide_text'],
            'line_spacing': self.text_styling['body_line_spacing'],
        }
