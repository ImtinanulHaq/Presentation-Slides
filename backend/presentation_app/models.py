from django.db import models
from django.contrib.auth.models import User
import json


class Presentation(models.Model):
    """Model for presentations"""
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
    speaker_notes = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'slide_number']

    def __str__(self):
        return f"{self.presentation.title} - Slide {self.slide_number}"
