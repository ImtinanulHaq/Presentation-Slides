"""
Template Registry and Loader
Manages all available templates and provides convenient access
"""

from .rose_elegance import RoseEleganceTemplate
from .warm_spectrum import WarmSpectrumTemplate
from .warm_blue import WarmBlueTemplate
from .modern_professional import ModernProfessionalTemplate
from .teal_modern import TealModernTemplate
from .navy_professional import NavyProfessionalTemplate
from .forest_green import ForestGreenTemplate
from .burgundy_elegance import BurgundyEleganceTemplate
from .slate_blue import SlateBluTemplate


class TemplateRegistry:
    """
    Registry for all presentation templates
    Provides centralized access and template management
    """
    
    # Available templates mapping
    TEMPLATES = {
        'warm_blue': WarmBlueTemplate,  # Default template
        'rose_elegance': RoseEleganceTemplate,
        'premium_blush': RoseEleganceTemplate,  # Alias for rose_elegance
        'warm_spectrum': WarmSpectrumTemplate,
        'ocean_sunset': WarmSpectrumTemplate,  # Alias for warm_spectrum
        'modern_professional': ModernProfessionalTemplate,
        'gradient_pro': ModernProfessionalTemplate,  # Alias for modern_professional
        'teal_modern': TealModernTemplate,
        'navy_professional': NavyProfessionalTemplate,
        'forest_green': ForestGreenTemplate,
        'burgundy_elegance': BurgundyEleganceTemplate,
        'slate_blue': SlateBluTemplate,
    }
    
    # Default template
    DEFAULT_TEMPLATE = 'modern_professional'
    
    @classmethod
    def get_template(cls, template_name=None):
        """
        Get a template instance by name
        
        Args:
            template_name: Name of template (default: 'rose_elegance')
            
        Returns:
            Template instance
        """
        if not template_name:
            template_name = cls.DEFAULT_TEMPLATE
        
        template_class = cls.TEMPLATES.get(template_name, RoseEleganceTemplate)
        return template_class()
    
    @classmethod
    def get_available_templates(cls):
        """Get list of all available template names"""
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def is_valid_template(cls, template_name):
        """Check if a template name is valid"""
        return template_name in cls.TEMPLATES
