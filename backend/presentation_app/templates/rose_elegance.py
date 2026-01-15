"""
Rose Elegance Template - Professional Premium Template
A refined, sophisticated template with rose gold color palette
Designed for business, corporate, and executive presentations
"""

from .template_base import PresentationTemplate


class RoseEleganceTemplate(PresentationTemplate):
    """
    Rose Elegance: Premium professional template with rose gold palette
    
    Color Palette:
    - #d8e2dc: Soft sage (secondary text)
    - #ffe5d9: Warm cream (primary text/headings)
    - #ffcad4: Soft rose (accents, highlights)
    - #f4acb7: Medium rose (secondary accents)
    - #9d8189: Deep mauve (primary background)
    
    Typography:
    - Headings: Poppins SemiBold / Bold (modern, authoritative)
    - Body: Inter Regular (clean, readable)
    - Professional spacing and refined layout
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Rose Elegance"
        self.description = "Premium professional template with rose gold palette for business and corporate presentations"
        self.version = "1.0"
        
        # ========== COLOR PALETTE ==========
        # All colors in hex format for PPTX compatibility
        # Professional color scheme: Dark mauve headings with rich brownish-mauve body text
        self.colors = {
            'primary_background': '#9d8189',  # Deep mauve - main background
            'secondary_background': '#f4acb7',  # Medium rose - alternate background
            'accent_background': '#ffcad4',  # Soft rose - subtle backgrounds
            'primary_text': '#5B3A49',  # Dark mauve - headings (professional, pops against pink)
            'secondary_text': '#6E4B57',  # Rich brownish-mauve - body text (readable, soft)
            'accent_text': '#5B3A49',  # Dark mauve - highlights, keywords, callouts
            'accent_color_dark': '#5B3A49',  # Dark mauve - bullets (darker than body for contrast)
            'accent_color_light': '#6E4B57',  # Brownish-mauve - soft accents
            'white': '#ffffff',  # Pure white - for contrast
            'overlay_dark': '#9d8189',  # For overlays and gradients
        }
        
        # ========== TYPOGRAPHY CONFIGURATION ==========
        self.fonts = {
            # Heading Configuration
            'heading_font': 'Poppins',  # Modern, bold font
            'heading_size': 40,  # 40pt for main titles
            'heading_weight': 'SemiBold',  # Bold and authoritative
            'heading_color': 'primary_text',  # Use warm cream (#ffe5d9)
            'heading_line_spacing': 1.1,  # Tight, professional spacing
            'heading_letter_spacing': 0.03,  # 3% increased letter spacing
            
            # Body Text Configuration
            'body_font': 'Inter',  # Clean, readable font
            'body_size': 20,  # 20pt for body text
            'body_weight': 'Regular',  # Easy to read
            'body_color': 'secondary_text',  # Use soft sage (#d8e2dc)
            'body_line_spacing': 1.5,  # Generous line spacing for readability
            
            # Bullet Configuration
            'bullet_font': 'Inter',  # Same as body for consistency
            'bullet_size': 18,  # Slightly smaller than body
            'bullet_color': 'secondary_text',  # Use soft sage
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
            'title_line_spacing': 1.1,  # 1.1 for tight, professional appearance
            'title_letter_spacing': 0.03,  # 3% letter spacing
            'title_color': 'primary_text',  # Dark mauve (#5B3A49) - professional, pops
            'title_alignment': 'left',  # Left-aligned for professional look
            'title_bold': True,  # Make titles bold
            
            # Body Text Styling
            'body_font_size': 20,  # 20pt body
            'body_line_spacing': 1.5,  # 1.5 for breathing room
            'body_paragraph_spacing': 12,  # 12px between paragraphs
            'body_color': 'secondary_text',  # Rich brownish-mauve (#6E4B57)
            'body_alignment': 'left',  # Left alignment
            'body_word_wrap': True,  # Enable word wrapping
            
            # Subtitle Styling
            'subtitle_font_size': 24,  # 24pt for subtitles
            'subtitle_color': 'primary_text',  # Dark mauve (#5B3A49)
            'subtitle_weight': 'Regular',
            'subtitle_line_spacing': 1.3,
            
            # Metadata/Footer Styling
            'footer_font_size': 12,  # 12pt for footer text
            'footer_color': 'secondary_text',  # Rich brownish-mauve (#6E4B57)
            'footer_opacity': 0.7,  # 70% opacity for subtle appearance
        }
        
        # ========== BULLET POINT STYLING ==========
        self.bullets = {
            'style': 'solid_circle',  # ● solid circles
            'level_1_symbol': '●',  # Solid circle for level 1
            'level_1_size': 16,  # Slightly smaller than text
            'level_1_color': 'accent_color_dark',  # Dark mauve bullets (#5B3A49)
            'level_1_text_color': 'secondary_text',  # Rich brownish-mauve (#6E4B57) body text
            'level_1_font_size': 18,  # Standardized 18pt for all bullets
            'level_1_line_spacing': 1.5,  # 1.4-1.6 range
            
            'level_2_symbol': '○',  # Circle outline for level 2
            'level_2_size': 14,  # Smaller than level 1
            'level_2_color': 'accent_color_dark',  # Dark mauve (#5B3A49)
            'level_2_opacity': 0.8,  # 80% opacity
            'level_2_text_color': 'secondary_text',  # Rich brownish-mauve (#6E4B57)
            'level_2_font_size': 18,  # Same as level 1 - standardized 18pt
            'level_2_line_spacing': 1.5,  # 1.4-1.6 range
            'level_2_indent': 24,  # 24px indentation for level 2
            
            'bullet_spacing_before': 6,  # 6px before bullet
            'bullet_spacing_after': 8,  # 8px after bullet
            'max_bullets_per_slide': 8,  # Allow up to 8 bullets
        }
        
        # ========== GRADIENT & VISUAL ELEMENTS ==========
        self.visual = {
            'use_gradients': True,  # Enable gradients
            'gradient_type': 'soft_overlay',  # Soft gradient overlays
            'gradient_color_1': '#f4acb7',  # Medium rose
            'gradient_color_2': '#9d8189',  # Deep mauve
            'gradient_direction': 'diagonal',  # Diagonal gradient
            'gradient_opacity': 0.15,  # 15% opacity for subtlety
            'gradient_blur': 20,  # Soft blur for blending
            
            'use_shapes': True,  # Use decorative shapes
            'corner_radius': 8,  # 8px rounded corners
            'border_style': 'none',  # No visible borders
            'shadow_enabled': False,  # No drop shadows (keep clean)
            
            'text_container_background': '#9d8189',  # Deep mauve containers
            'text_container_opacity': 0.95,  # 95% opaque
            'text_container_border_radius': 12,  # 12px rounded corners
        }
        
        # ========== SLIDE-SPECIFIC STYLING ==========
        self.slide_styles = {
            'title_slide': {
                'background_color': '#9d8189',  # Deep mauve
                'title_size': 56,  # 56pt for title slide
                'title_color': '#5B3A49',  # Dark mauve (#5B3A49)
                'subtitle_size': 28,  # 28pt for subtitle
                'subtitle_color': '#6E4B57',  # Rich brownish-mauve (#6E4B57)
                'use_gradient_overlay': True,
            },
            'content_slide': {
                'background_color': '#9d8189',  # Deep mauve
                'title_bar_color': '#f4acb7',  # Medium rose
                'title_color': '#5B3A49',  # Dark mauve heading
                'content_background': '#9d8189',  # Deep mauve
                'text_color': '#6E4B57',  # Rich brownish-mauve body
                'use_gradient_overlay': True,
            },
            'section_slide': {
                'background_color': '#f4acb7',  # Medium rose
                'title_size': 52,  # 52pt
                'title_color': '#5B3A49',  # Dark mauve (#5B3A49)
                'subtitle_color': '#6E4B57',  # Rich brownish-mauve
                'use_gradient_overlay': True,
            },
        }
        
        # Validate template
        self.validate()
    
    def apply_to_slide(self, prs, slide, slide_type='content'):
        """
        Apply Rose Elegance template styling to a slide
        
        Args:
            prs: PPTX Presentation object
            slide: Slide object to apply styling to
            slide_type: Type of slide ('title', 'section', 'content')
        """
        # Set background color based on slide type
        background = slide.background
        fill = background.fill
        fill.solid()
        
        if slide_type == 'title':
            fill.fore_color.rgb = self.colors['primary_background']
        elif slide_type == 'section':
            fill.fore_color.rgb = self.colors['secondary_background']
        else:  # content
            fill.fore_color.rgb = self.colors['primary_background']
    
    def get_slide_config(self, slide_type='content'):
        """Get configuration for a specific slide type"""
        return self.slide_styles.get(slide_type, self.slide_styles['content_slide'])
    
    def get_color_hex(self, color_key):
        """Get hex color by key"""
        return self.colors.get(color_key, '#000000')
    
    def __str__(self):
        return f"{self.name} v{self.version} - {self.description}"
