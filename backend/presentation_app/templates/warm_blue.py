"""
Warm Blue Template - Professional Modern Template
A calm, sophisticated template with warm blue color palette
Designed for business, corporate, and professional presentations
"""

from .template_base import PresentationTemplate


class WarmBlueTemplate(PresentationTemplate):
    """
    Warm Blue: Professional modern template with warm blue palette
    
    Color Palette (Professional Blue):
    - #2f6690: Medium blue (primary background)
    - #3a7ca5: Lighter blue (secondary background)
    - #d9dcd6: Light gray/beige (text, neutral)
    - #16425b: Dark navy blue (headings, emphasis)
    - #81c3d7: Light cyan/sky blue (accents, highlights)
    
    Typography:
    - Headings: Poppins Bold (professional, authoritative)
    - Body: Inter Regular (clean, readable)
    - Professional styling with calm, trustworthy appearance
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Warm Blue"
        self.description = "Professional template with warm blue palette for business and corporate presentations"
        self.version = "1.0"
        
        # ========== COLOR PALETTE ==========
        # Professional warm blue palette
        self.colors = {
            'primary_background': '#2f6690',  # Medium blue - main background
            'secondary_background': '#3a7ca5',  # Lighter blue - alternate background
            'accent_background': '#81c3d7',  # Light cyan - subtle backgrounds
            'primary_text': '#16425b',  # Dark navy blue - headings (professional, high contrast)
            'secondary_text': '#d9dcd6',  # Light gray/beige - body text (readable, warm)
            'accent_text': '#81c3d7',  # Light cyan - highlights, keywords
            'accent_color_dark': '#16425b',  # Dark navy - bullets and emphasis
            'accent_color_light': '#81c3d7',  # Light cyan - soft accents
            'white': '#ffffff',  # Pure white - for contrast
            'overlay_dark': '#16425b',  # For overlays and gradients
        }
        
        # ========== TYPOGRAPHY CONFIGURATION ==========
        self.fonts = {
            # Heading Configuration
            'heading_font': 'Poppins',  # Professional, bold font
            'heading_size': 40,  # 40pt for main titles
            'heading_weight': 'Bold',  # Bold and authoritative
            'heading_color': 'primary_text',  # Dark navy blue (#16425b)
            'heading_line_spacing': 1.2,  # Tight, professional spacing
            'heading_letter_spacing': 0.02,  # 2% increased letter spacing
            
            # Body Text Configuration
            'body_font': 'Inter',  # Clean, professional font
            'body_size': 20,  # 20pt for body text
            'body_weight': 'Regular',  # Easy to read
            'body_color': 'secondary_text',  # Light gray/beige (#d9dcd6)
            'body_line_spacing': 1.5,  # Generous line spacing for readability
            
            # Bullet Configuration
            'bullet_font': 'Inter',  # Same as body for consistency
            'bullet_size': 18,  # Slightly smaller than body
            'bullet_color': 'primary_text',  # Dark navy blue (#16425b) - same as heading
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
            'title_line_spacing': 1.2,  # 1.2 for tight, professional appearance
            'title_letter_spacing': 0.02,  # 2% letter spacing
            'title_color': 'primary_text',  # Dark navy blue (#16425b) - professional
            'title_alignment': 'left',  # Left-aligned for professional look
            'title_bold': True,  # Make titles bold
            
            # Body Text Styling
            'body_font_size': 20,  # 20pt body
            'body_line_spacing': 1.5,  # 1.5 for readability
            'body_letter_spacing': 0.01,  # 1% letter spacing
            'body_color': 'secondary_text',  # Light gray/beige (#d9dcd6)
            'body_alignment': 'left',  # Left-aligned for readability
            'body_bold': False,  # Regular weight
            
            # Subtitle Styling
            'subtitle_font_size': 24,  # 24pt for subtitles
            'subtitle_line_spacing': 1.3,  # Slightly tight
            'subtitle_color': 'accent_text',  # Light cyan (#81c3d7) for accent
            'subtitle_alignment': 'left',
            'subtitle_bold': False,
        }
        
        # ========== BULLET STYLING ==========
        self.bullets = {
            # Bullet Point Configuration
            'level_1_font_size': 18,  # 18pt for first-level bullets
            'level_1_color': 'white',  # White (#ffffff) for visibility on blue background
            'level_1_font': 'Inter',  # Inter Regular
            'level_1_indent': 18,  # 18pt indent
            
            'level_2_font_size': 18,  # 18pt for second-level bullets (same as level 1)
            'level_2_color': 'white',  # White (#ffffff) for visibility on blue background
            'level_2_font': 'Inter',  # Inter Regular
            'level_2_indent': 36,  # 36pt indent
            
            # Bullet spacing
            'text_color': 'white',  # White (#ffffff) for bullet text
            'bullet_color': 'white',  # White (#ffffff) for bullet icon
            'line_spacing': 1.4,  # Professional line spacing
            'space_before': 4,  # Space before bullet
            'space_after': 8,  # Space after bullet
        }
        
        # ========== GRADIENT CONFIGURATION ==========
        # Define gradient stops for professional backgrounds
        self.gradients = {
            'title_slide': {
                'start_color': '#2f6690',  # Medium blue
                'end_color': '#3a7ca5',  # Lighter blue
                'angle': 45,  # 45-degree diagonal
                'description': 'Professional blue gradient for title slides'
            },
            'section_slide': {
                'start_color': '#3a7ca5',  # Lighter blue
                'end_color': '#81c3d7',  # Light cyan
                'angle': 135,  # Opposite diagonal
                'description': 'Blue to cyan gradient for section slides'
            },
            'content_slide': {
                'start_color': '#2f6690',  # Medium blue
                'end_color': '#81c3d7',  # Light cyan
                'angle': 45,  # Subtle gradient
                'description': 'Professional gradient for content slides'
            },
            'accent_bar': {
                'start_color': '#3a7ca5',  # Lighter blue
                'end_color': '#81c3d7',  # Light cyan
                'angle': 90,  # Vertical gradient
                'description': 'Professional gradient for accent bars'
            }
        }
        
        # ========== ELEMENT STYLING ==========
        self.elements = {
            # Accent Bar Styling (for title bars, dividers)
            'accent_bar_color': '#3a7ca5',  # Lighter blue
            'accent_bar_height': 0.08,  # 8% of slide height
            'accent_bar_gradient': True,  # Use gradient
            
            # Border Styling
            'border_color': '#81c3d7',  # Light cyan
            'border_width': 2,  # 2px
            'border_radius': 4,  # Subtle rounding
            
            # Shadow Effects
            'shadow_enabled': True,
            'shadow_color': '#16425b',  # Dark navy
            'shadow_blur': 8,  # 8px blur
            'shadow_offset': (2, 2),  # 2px offset
        }
        
        # ========== OVERALL THEME CHARACTERISTICS ==========
        self.theme = {
            'mood': 'Professional, Trustworthy, Corporate',
            'use_case': 'Business presentations, corporate meetings, professional training, enterprise',
            'professional_level': 'Very High - sophisticated and trustworthy',
            'energy_level': 'Calm - soothing blue palette',
            'contrast': 'High - dark navy on light backgrounds',
            'gradient_usage': 'Moderate - professional gradient transitions',
            'accent_emphasis': 'Light cyan tones for key points',
        }


# Optional: Create alias for easy access
WarmBluePresentationTemplate = WarmBlueTemplate
