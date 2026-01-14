#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from presentation_app.models import Presentation

p = Presentation.objects.get(id=25)
print(f'Title: {p.title}')
print(f'Total Slides in DB: {p.slides.count()}')
print(f'Total Slides in JSON: {p.json_structure.get("total_slides")}')
print()
print('Slide breakdown:')
for slide in p.slides.all():
    visuals_count = len(slide.visuals) if slide.visuals else 0
    bullets_count = len(slide.bullets) if slide.bullets else 0
    print(f'  Slide {slide.slide_number}: {slide.title} | Bullets: {bullets_count} | Visuals: {visuals_count}')
