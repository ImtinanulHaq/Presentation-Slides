#!/usr/bin/env python
"""Check what bullet format the Groq API is returning"""
import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from presentation_app.models import Presentation

# Get the most recent presentation
presentation = Presentation.objects.order_by('-id').first()

if presentation:
    print("\n" + "="*80)
    print(f"PRESENTATION ID: {presentation.id}")
    print(f"BULLET STYLE: {presentation.bullet_style}")
    print("="*80)
    
    # Get the JSON structure
    json_data = presentation.json_structure
    
    if json_data and 'slides' in json_data:
        for slide_idx, slide in enumerate(json_data['slides'][:2]):  # First 2 slides
            print(f"\nSlide {slide_idx + 1}:")
            print(f"  Type: {slide.get('slide_type')}")
            print(f"  Title: {slide.get('title')}")
            
            bullets = slide.get('bullets', [])
            if bullets:
                print(f"  Bullets ({len(bullets)}):")
                for bullet_idx, bullet in enumerate(bullets[:3]):
                    if isinstance(bullet, dict):
                        print(f"    [{bullet_idx}] {bullet}")
                    else:
                        print(f"    [{bullet_idx}] '{bullet}'")

print("\n" + "="*80)
