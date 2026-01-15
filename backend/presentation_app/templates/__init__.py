"""
Presentation Templates Module
Professional template system for PowerPoint generation
"""

from .template_base import PresentationTemplate
from .rose_elegance import RoseEleganceTemplate
from .template_registry import TemplateRegistry

__all__ = [
    'PresentationTemplate',
    'RoseEleganceTemplate',
    'TemplateRegistry',
]
