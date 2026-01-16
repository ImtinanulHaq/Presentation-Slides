from django.db import models
from django.contrib.auth.models import User
import json


class Presentation(models.Model):
    """Model for presentations"""
    SUBJECT_CHOICES = [
        ('general', 'General'),
        ('english', 'English'),
        ('urdu', 'Urdu'),
        ('science', 'Science'),
        ('biology', 'Biology'),
        ('physics', 'Physics'),
        ('medical', 'Medical Field'),
        ('it', 'IT Field'),
        ('engineering', 'Engineering Field'),
    ]
    
    BULLET_STYLE_CHOICES = [
        ('numbered', 'Numbered (1, 2, 3...)'),
        ('bullet_elegant', 'Elegant Bullets (●)'),
        ('bullet_modern', 'Modern Bullets (▸)'),
        ('bullet_professional', 'Professional Bullets (■)'),
    ]
    
    FONT_CHOICES = [
        # Serif Fonts (Professional, Academic)
        ('georgia', 'Georgia'),
        ('times', 'Times New Roman'),
        ('garamond', 'Garamond'),
        ('palatino', 'Palatino Linotype'),
        ('book_antiqua', 'Book Antiqua'),
        ('cambria', 'Cambria'),
        
        # Sans-Serif Fonts (Modern, Clean)
        ('arial', 'Arial'),
        ('calibri', 'Calibri'),
        ('verdana', 'Verdana'),
        ('tahoma', 'Tahoma'),
        ('trebuchet', 'Trebuchet MS'),
        ('segoe', 'Segoe UI'),
        ('century_gothic', 'Century Gothic'),
        ('helvetica', 'Helvetica'),
        ('ubuntu', 'Ubuntu'),
        ('droid_sans', 'Droid Sans'),
        ('liberation_sans', 'Liberation Sans'),
        
        # Monospace Fonts (Code, Technical)
        ('courier', 'Courier New'),
        ('consolas', 'Consolas'),
        
        # Display Fonts (Creative, Casual)
        ('comic_sans', 'Comic Sans MS'),
        
        # Urdu & International Fonts
        ('noto_nastaliq', 'Noto Nastaliq Urdu'),
        ('noto_naskh', 'Noto Naskh Arabic'),
        ('segoe_urdu', 'Segoe UI (Urdu)'),
    ]
    
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255, default='')
    raw_content = models.TextField(blank=True)
    target_audience = models.CharField(max_length=255, default='')
    tone = models.CharField(
        max_length=50,
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual'),
            ('academic', 'Academic'),
            ('persuasive', 'Persuasive'),
        ],
        default='professional'
    )
    subject = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='general'
    )
    template = models.CharField(
        max_length=50,
        default='warm_blue',  # Changed to warm_blue
        help_text='Template name: warm_blue, rose_elegance, warm_spectrum, etc.'
    )
    slide_ratio = models.CharField(
        max_length=10,
        default='16:9',
        choices=[('16:9', '16:9'), ('4:3', '4:3'), ('1:1', '1:1'), ('2:3', '2:3')],
        help_text='Slide aspect ratio'
    )
    title_font = models.CharField(max_length=50, choices=FONT_CHOICES, default='calibri')
    heading_font = models.CharField(max_length=50, choices=FONT_CHOICES, default='calibri')
    content_font = models.CharField(max_length=50, choices=FONT_CHOICES, default='arial')
    bullet_style = models.CharField(
        max_length=50,
        choices=BULLET_STYLE_CHOICES,
        default='numbered',
        help_text='Style for bullet points: numbered, elegant, modern, or professional'
    )
    description = models.TextField(blank=True)
    json_structure = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Slide(models.Model):
    """Model for slides within presentations"""
    SLIDE_TYPES = [
        ('title', 'Title Slide'),
        ('content', 'Content Slide'),
        ('section', 'Section Divider'),
        ('conclusion', 'Conclusion Slide'),
    ]
    
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='slides')
    slide_number = models.IntegerField(default=1)
    slide_type = models.CharField(max_length=20, choices=SLIDE_TYPES, default='content')
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    bullets = models.JSONField(default=list, blank=True)
    visuals = models.JSONField(default=dict, blank=True)
    fonts = models.JSONField(default=dict, blank=True)  # {title_font, heading_font, content_font}
    speaker_notes = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'slide_number']

    def __str__(self):
        return f"{self.presentation.title} - Slide {self.slide_number}"
