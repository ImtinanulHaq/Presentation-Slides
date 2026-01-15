"""
Warm Spectrum Template - Modern Professional Template
A vibrant, sophisticated template with ocean-to-sunset gradient color palette
Designed for creative, modern, and dynamic presentations
"""

from .template_base import PresentationTemplate


class WarmSpectrumTemplate(PresentationTemplate):
    """
    Warm Spectrum: Modern professional template with gradient color palette
    
    Color Palette (Ocean to Sunset Gradient):
    - #001219: Very dark navy/teal (backgrounds, deep elements)
    - #005f73: Dark teal (primary background)
    - #0a9396: Bright teal (accent, highlights)
    - #94d2bd: Light mint/turquoise (light accents)
    - #e9d8a6: Cream/beige (neutral, text)
    - #ee9b00: Golden yellow (vibrant accent)
    - #ca6702: Dark orange (secondary accent)
    - #bb3e03: Burnt orange (highlight)
    - #ae2012: Dark red (emphasis)
    - #9b2226: Deep maroon (dark elements)
    
    Typography:
    - Headings: Poppins Bold (modern, dynamic)
    - Body: Inter Regular (clean, modern)
    - Professional gradients and contemporary styling
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Warm Spectrum"
        self.description = "Modern professional template with ocean-to-sunset gradient palette for creative and dynamic presentations"
        self.version = "1.0"
        
        # ========== COLOR PALETTE ==========
        # Vibrant gradient from cool (teal) to warm (red)
        self.colors = {
            'primary_background': '#005f73',  # Dark teal - main background
            'secondary_background': '#0a9396',  # Bright teal - alternate background
            'accent_background': '#94d2bd',  # Light mint - subtle backgrounds
            'primary_text': '#001219',  # Very dark navy - headings (high contrast)
            'secondary_text': '#e9d8a6',  # Cream/beige - body text (warm, readable)
            'accent_text': '#ee9b00',  # Golden yellow - highlights, keywords
            'accent_color_dark': '#ca6702',  # Dark orange - bullets and emphasis
            'accent_color_light': '#94d2bd',  # Light mint - soft accents
            'white': '#ffffff',  # Pure white - for contrast
            'overlay_dark': '#001219',  # For overlays and gradients
        }
        
        # ========== TYPOGRAPHY CONFIGURATION ==========
        self.fonts = {
            # Heading Configuration
            'heading_font': 'Poppins',  # Modern, bold font
            'heading_size': 40,  # 40pt for main titles
            'heading_weight': 'Bold',  # Bold and dynamic
            'heading_color': 'primary_text',  # Very dark navy (#001219)
            'heading_line_spacing': 1.2,  # Tight, professional spacing
            'heading_letter_spacing': 0.02,  # 2% increased letter spacing
            
            # Body Text Configuration
            'body_font': 'Inter',  # Clean, modern font
            'body_size': 20,  # 20pt for body text
            'body_weight': 'Regular',  # Easy to read
            'body_color': 'secondary_text',  # Cream/beige (#e9d8a6)
            'body_line_spacing': 1.5,  # Generous line spacing for readability
            
            # Bullet Configuration
            'bullet_font': 'Inter',  # Same as body for consistency
            'bullet_size': 18,  # Slightly smaller than body
            'bullet_color': 'accent_color_dark',  # Dark orange (#ca6702)
        }
        
        # ========== LAYOUT CONFIGURATION ==========
        self.layout = {
            'slide_ratio': '16:9',  # Standard widescreen
            'slide_width': 10,  # inches
            'slide_height': 7.5,  # inches
            'default_margin': 24,  # 0.27" margin
            'title_margin_top': 36,  # Distance from top for title
            'title_margin_bottom': 12,  # Space below title
            'content_margin_left': 32,  # Left padding for content
            'content_margin_right': 32,  # Right padding for content
            'content_margin_top': 80,  # Distance from top for content
            'content_margin_bottom': 32,  # Distance from bottom
            'content_height': 380,  # Available height for content
            'text_container_border_radius': 8,  # Rounded corners for text boxes
            'text_container_padding': 20,  # Internal padding in text boxes
        }
        
        # ========== TEXT STYLING ==========
        self.text_styling = {
            # Title/Heading Styling
            'title_font_size': 44,  # 44pt for slide titles
            'title_line_spacing': 1.2,  # 1.2 for tight, modern appearance
            'title_letter_spacing': 0.02,  # 2% letter spacing
            'title_color': 'primary_text',  # Very dark navy (#001219) - high contrast
            'title_alignment': 'left',  # Left-aligned for modern look
            'title_bold': True,  # Make titles bold
            
            # Body Text Styling
            'body_font_size': 20,  # 20pt body
            'body_line_spacing': 1.5,  # 1.5 for readability
            'body_letter_spacing': 0.01,  # 1% letter spacing
            'body_color': 'secondary_text',  # Cream/beige (#e9d8a6)
            'body_alignment': 'left',  # Left-aligned for readability
            'body_bold': False,  # Regular weight
            
            # Subtitle Styling
            'subtitle_font_size': 24,  # 24pt for subtitles
            'subtitle_line_spacing': 1.3,  # Slightly tight
            'subtitle_color': 'accent_text',  # Golden yellow (#ee9b00) for vibrancy
            'subtitle_alignment': 'left',
            'subtitle_bold': False,
        }
        
        # ========== BULLET STYLING ==========
        self.bullets = {
            # Bullet Point Configuration
            'level_1_font_size': 18,  # 18pt for first-level bullets
            'level_1_color': 'primary_text',  # Very dark navy (#001219) - same as heading
            'level_1_font': 'Inter',  # Inter Regular
            'level_1_indent': 18,  # 18pt indent
            
            'level_2_font_size': 18,  # 18pt for second-level bullets (same as level 1)
            'level_2_color': 'primary_text',  # Very dark navy (#001219) - same as heading
            'level_2_font': 'Inter',  # Inter Regular
            'level_2_indent': 36,  # 36pt indent
            
            # Bullet spacing
            'text_color': 'secondary_text',  # Cream/beige (#e9d8a6) for bullet text
            'bullet_color': 'primary_text',  # Very dark navy (#001219) for bullet icon - same as heading
            'line_spacing': 1.4,  # Professional line spacing
            'space_before': 4,  # Space before bullet
            'space_after': 8,  # Space after bullet
        }
        
        # ========== GRADIENT CONFIGURATION ==========
        # Define gradient stops for professional backgrounds
        self.gradients = {
            'title_slide': {
                'start_color': '#005f73',  # Dark teal
                'end_color': '#0a9396',  # Bright teal
                'angle': 45,  # 45-degree diagonal
                'description': 'Cool teal gradient for title slides'
            },
            'section_slide': {
                'start_color': '#0a9396',  # Bright teal
                'end_color': '#ee9b00',  # Golden yellow
                'angle': 135,  # Opposite diagonal
                'description': 'Teal to golden gradient for section slides'
            },
            'content_slide': {
                'start_color': '#005f73',  # Dark teal
                'end_color': '#94d2bd',  # Light mint
                'angle': 45,  # Subtle gradient
                'description': 'Cool gradient for content slides'
            },
            'accent_bar': {
                'start_color': '#ca6702',  # Dark orange
                'end_color': '#ae2012',  # Dark red
                'angle': 90,  # Vertical gradient
                'description': 'Warm gradient for accent bars'
            }
        }
        
        # ========== ELEMENT STYLING ==========
        self.elements = {
            # Accent Bar Styling (for title bars, dividers)
            'accent_bar_color': '#ca6702',  # Dark orange
            'accent_bar_height': 0.08,  # 8% of slide height
            'accent_bar_gradient': True,  # Use gradient
            
            # Border Styling
            'border_color': '#0a9396',  # Bright teal
            'border_width': 2,  # 2px
            'border_radius': 4,  # Subtle rounding
            
            # Shadow Effects
            'shadow_enabled': True,
            'shadow_color': '#001219',  # Very dark navy
            'shadow_blur': 8,  # 8px blur
            'shadow_offset': (2, 2),  # 2px offset
        }
        
        # ========== OVERALL THEME CHARACTERISTICS ==========
        self.theme = {
            'mood': 'Modern, Creative, Dynamic',
            'use_case': 'Tech startups, creative agencies, innovative companies, modern business',
            'professional_level': 'High - sophisticated and contemporary',
            'energy_level': 'High - vibrant colors and gradients',
            'contrast': 'Very High - dark text on light backgrounds',
            'gradient_usage': 'Heavy - multiple gradient transitions',
            'accent_emphasis': 'Golden yellow and orange tones for key points',
        }


# Optional: Create alias for easy access
WarmSpectrumPresentation = WarmSpectrumTemplate
